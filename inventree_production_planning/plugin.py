from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UrlsMixin, UserInterfaceMixin
from build.models import Build, BuildLine
from order.models import PurchaseOrderLineItem
from part.models import BomItem
from stock.models import StockItem
from stock.status_codes import StockStatus

from . import PLUGIN_VERSION


def D(value):
    try:
        return Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def day(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except Exception:
        return None


def add_days(start, count):
    d = day(start)
    if not d:
        return None
    n = max(0, int(count or 0))
    while n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def iso(value):
    d = day(value)
    return d.isoformat() if d else None


class ProductionPlanningPlugin(SettingsMixin, UrlsMixin, UserInterfaceMixin, InvenTreePlugin):
    NAME = "ProductionPlanning"
    SLUG = "production-planning"
    TITLE = "Production Planning"
    DESCRIPTION = "V1 BO material, board-stage and completion forecast."
    VERSION = PLUGIN_VERSION
    AUTHOR = "Per Vices Corporation"
    LICENSE = "MIT"

    SETTINGS = {
        "PCBA_DAYS": {"name": _("PCBA business days"), "default": 5, "validator": int},
        "VI_DAYS": {"name": _("Visual Inspection business days"), "default": 1, "validator": int},
        "BU_DAYS": {"name": _("Bring-Up business days"), "default": 3, "validator": int},
        "SW_DAYS": {"name": _("Software Test business days"), "default": 2, "validator": int},
        "COATING_DAYS": {"name": _("Conformal Coating business days"), "default": 2, "validator": int},
        "FINAL_ASSEMBLY_DAYS": {"name": _("Final Assembly business days"), "default": 3, "validator": int},
        "FINAL_TEST_DAYS": {"name": _("Final Test business days"), "default": 2, "validator": int},
    }

    STATUS_ALIASES = {
        "passvi": 1, "passedvi": 1,
        "passpressfit": 2, "passedpressfit": 2,
        "passbu": 3, "passedbu": 3,
        "eeprompass": 4, "passeeprom": 4,
        "passsw": 5, "passsoftware": 5, "passedsoftware": 5,
    }

    def setup_urls(self):
        return [path("build/<int:build_id>/", self.build_api, name="production-planning-build")]

    def get_ui_panels(self, request, context, **kwargs):
        context = context or {}
        model = str(context.get("target_model") or "").lower()
        pk = context.get("target_id")
        if "build" not in model or pk in (None, ""):
            return []
        try:
            pk = int(pk)
        except (TypeError, ValueError):
            return []
        # Keep panel discovery fast; planning runs only after the panel renders.
        return [{
            "key": "production-planning-panel",
            "title": _("Production Plan"),
            "description": _("Material readiness and forecast completion"),
            "icon": "ti:calendar-time",
            "source": self.plugin_static_file("production_planning.js:renderPanel"),
            "context": {"build_id": pk, "data_url": f"/plugin/{self.SLUG}/build/{pk}/"},
        }]

    def setting(self, key):
        try:
            return max(0, int(self.get_setting(key) or 0))
        except Exception:
            return 0

    @staticmethod
    def norm(value):
        return "".join(ch for ch in str(value or "").lower() if ch.isalnum())

    @staticmethod
    def custom_statuses():
        out = {}
        try:
            for s in StockStatus.custom_queryset():
                out[int(s.key)] = str(s.label or s.name or "")
        except Exception:
            pass
        return out

    def status_label(self, item, custom):
        key = getattr(item, "status_custom_key", None)
        try:
            if key is not None and int(key) in custom:
                return custom[int(key)]
        except Exception:
            pass
        try:
            return str(StockStatus.text(int(item.status)))
        except Exception:
            return str(getattr(item, "status", ""))

    @staticmethod
    def ipn(part):
        return str(getattr(part, "IPN", "") or "")

    @staticmethod
    def build_ref(build):
        return str(getattr(build, "reference", "") or f"Build {build.pk}")

    def stock(self, part):
        try:
            return list(StockItem.objects.filter(part=part, quantity__gt=0).only(
                "pk", "part_id", "quantity", "status", "status_custom_key"))
        except Exception:
            return list(StockItem.objects.filter(part=part))

    def available_qty(self, part):
        # InvenTree availability is represented by logical stock status. Custom
        # unavailable statuses (e.g. Quarantine) resolve to an unavailable logical key.
        custom = {}
        try:
            for s in StockStatus.custom_queryset():
                custom[int(s.key)] = int(s.logical_key)
        except Exception:
            pass
        total = D(0)
        for item in self.stock(part):
            logical = int(getattr(item, "status", 0) or 0)
            ckey = getattr(item, "status_custom_key", None)
            try:
                if ckey is not None and int(ckey) in custom:
                    logical = custom[int(ckey)]
            except Exception:
                pass
            try:
                available = bool(StockStatus.is_available(logical))
            except Exception:
                available = logical not in (50, 75, 100)
            if available:
                total += D(item.quantity)
        return total

    def pipeline(self, part):
        custom = self.custom_statuses()
        exact = {1:D(0),2:D(0),3:D(0),4:D(0),5:D(0)}
        bad = D(0)
        for item in self.stock(part):
            label = self.status_label(item, custom)
            key = self.norm(label)
            qty = D(item.quantity)
            stage = self.STATUS_ALIASES.get(key)
            if stage:
                exact[stage] += qty
            elif "fail" in key or "rework" in key or "quarantine" in key:
                bad += qty
        cumulative, running = {}, D(0)
        for stage in range(5, 0, -1):
            running += exact[stage]
            cumulative[stage] = running
        return {
            "pass_vi": cumulative[1], "pass_press_fit": cumulative[2],
            "pass_bu": cumulative[3], "eeprom_pass": cumulative[4],
            "pass_sw": cumulative[5], "failed_rework": bad,
            "exact": exact,
        }

    def bom(self, part):
        try:
            return list(BomItem.objects.filter(part=part).select_related("sub_part").order_by("id"))
        except Exception:
            return list(BomItem.objects.filter(part=part).order_by("id"))

    @staticmethod
    def subpart(item):
        return getattr(item, "sub_part", None)

    def child_builds(self, part, parent_id):
        qs = Build.objects.filter(part=part).exclude(pk=parent_id)
        try:
            from build.status_codes import BuildStatus
            qs = qs.filter(status=BuildStatus.PRODUCTION.value)
        except Exception:
            try: qs = qs.filter(status=20)
            except Exception: pass
        return list(qs.order_by("id"))

    def bare_part(self, build):
        try:
            for line in BuildLine.objects.filter(build=build).select_related("bom_item__sub_part"):
                p = getattr(getattr(line, "bom_item", None), "sub_part", None)
                if p and self.ipn(p).upper().endswith("-BARE"):
                    return p
        except Exception:
            pass
        p = getattr(build, "part", None)
        if p:
            for item in self.bom(p):
                sub = self.subpart(item)
                if sub and self.ipn(sub).upper().endswith("-BARE"):
                    return sub
        return None

    def po_coverage(self, part, need):
        try:
            qs = PurchaseOrderLineItem.objects.filter(part__part_id=part.pk).select_related("order", "part", "part__supplier")
            try:
                from order.status_codes import PurchaseOrderStatusGroups
                qs = qs.filter(order__status__in=PurchaseOrderStatusGroups.OPEN)
            except Exception:
                qs = qs.filter(order__status__in=[10,20,25])
        except Exception:
            return {"open":D(0),"earliest":None,"full":None,"refs":[],"lines":[]}
        rows=[]
        for line in qs:
            ordered=D(getattr(line,"quantity",0))
            received=D(getattr(line,"received",None) or getattr(line,"received_quantity",None) or 0)
            outstanding=max(D(0),ordered-received)
            if outstanding <= 0: continue
            order=getattr(line,"order",None)
            po_target=day(getattr(order,"target_date",None))
            line_target=day(getattr(line,"target_date",None))
            target=line_target or po_target
            rows.append({
                "effective":target,
                "po_target":po_target,
                "line_target":line_target,
                "qty":outstanding,
                "ref":str(getattr(order,"reference","") or ""),
            })
        rows.sort(key=lambda x:(x["effective"] is None,x["effective"] or date.max))
        remaining=max(D(0),D(need)); full=None; refs=[]
        for row in rows:
            if row["ref"] and row["ref"] not in refs: refs.append(row["ref"])
            remaining-=row["qty"]
            if remaining <= 0:
                full=row["effective"]; break
        return {
            "open":sum((x["qty"] for x in rows),D(0)),
            "earliest":next((x["effective"] for x in rows if x["effective"]),None),
            "full":full,
            "refs":refs,
            "lines":[{
                "po":x["ref"],
                "qty":float(x["qty"]),
                "po_target_date":iso(x["po_target"]),
                "line_target_date":iso(x["line_target"]),
                "effective_date":iso(x["effective"]),
            } for x in rows],
        }

    def board_forecast(self, part, required_shortage, builds):
        p=self.pipeline(part); ready=p["pass_sw"]
        need=max(D(0),D(required_shortage)-ready)
        result={
            "pipeline":{k:float(v) for k,v in p.items() if k!="exact"},
            "ready_now":float(ready),"need_after_ready":float(need),
            "forecast_ready":None,"basis":"","bare":[],
        }
        if need <= 0:
            result["basis"]="Existing Pass SW quantity covers the requirement."
            result["forecast_ready"]=iso(date.today())
            return result
        today=date.today(); candidates=[]; ex=p["exact"]
        # Quantity physically at each current stage. Later-stage quantities were
        # already removed by using exact buckets here.
        if ex[4]>0: candidates.append((ex[4],add_days(today,self.setting("SW_DAYS")+self.setting("COATING_DAYS")),"EEPROM Pass"))
        if ex[3]>0: candidates.append((ex[3],add_days(today,self.setting("SW_DAYS")+self.setting("COATING_DAYS")),"Pass BU"))
        if ex[2]>0: candidates.append((ex[2],add_days(today,self.setting("BU_DAYS")+self.setting("SW_DAYS")+self.setting("COATING_DAYS")),"Pass Press Fit"))
        if ex[1]>0: candidates.append((ex[1],add_days(today,self.setting("BU_DAYS")+self.setting("SW_DAYS")+self.setting("COATING_DAYS")),"Pass VI"))
        for b in builds:
            bare=self.bare_part(b)
            if not bare: continue
            bqty=D(getattr(b,"quantity",0)); bavail=self.available_qty(bare)
            bneed=max(D(0),bqty-bavail); po=self.po_coverage(bare,bneed)
            start=None; why=""
            if bneed<=0:
                start=add_days(today,1); why="-BARE stock available"
            elif po["full"]:
                start=add_days(po["full"],1); why="full -BARE PO coverage"
            elif po["earliest"]:
                start=add_days(po["earliest"],1); why="earliest -BARE PO (partial coverage)"
            if start:
                finish=add_days(start,self.setting("PCBA_DAYS")+self.setting("VI_DAYS")+self.setting("BU_DAYS")+self.setting("SW_DAYS")+self.setting("COATING_DAYS"))
                candidates.append((bqty,finish,why))
            result["bare"].append({
                "child_build":self.build_ref(b),"ipn":self.ipn(bare),
                "available":float(bavail),"needed":float(bneed),"open_po_qty":float(po["open"]),
                "earliest_po_date":iso(po["earliest"]),"full_coverage_po_date":iso(po["full"]),"po_references":po["refs"],
                "po_lines":po.get("lines",[]),
            })
        candidates.sort(key=lambda x:(x[1] is None,x[1] or date.max))
        remaining=need; chosen=None; basis=[]
        for qty,when,why in candidates:
            if not when or qty<=0: continue
            take=min(remaining,qty); remaining-=take; chosen=when
            basis.append(f"{float(take):g} from {why}")
            if remaining<=0: break
        if chosen and remaining<=0:
            result["forecast_ready"]=iso(chosen); result["basis"]="; ".join(basis)
        else:
            result["basis"]=(f"Only {float(need-remaining):g} of {float(need):g} additional boards can currently be dated; {float(remaining):g} remain unscheduled.")
        return result

    def requirement(self, build, item):
        part=self.subpart(item)
        if not part: return None
        required=D(getattr(item,"quantity",0))*D(getattr(build,"quantity",0))
        available=self.available_qty(part); shortage=max(D(0),required-available)
        builds=self.child_builds(part,build.pk); pipe=self.pipeline(part)
        board_like=bool(builds and (any(self.bare_part(b) for b in builds) or any(pipe[k]>0 for k in ("pass_vi","pass_bu","pass_sw"))))
        forecast=self.board_forecast(part,shortage,builds) if board_like and shortage>0 else None
        return {
            "part_id":part.pk,"ipn":self.ipn(part),"name":str(getattr(part,"name","") or ""),
            "required":float(required),"available":float(available),"shortage":float(shortage),
            "board_like":board_like,
            "child_builds":[{"id":b.pk,"reference":self.build_ref(b),"quantity":float(D(getattr(b,"quantity",0)))} for b in builds],
            "forecast":forecast,
        }

    def plan(self, build_id):
        build=Build.objects.select_related("part").get(pk=build_id); part=getattr(build,"part",None)
        if not part: raise ValueError("Build Order has no output part")
        rows=[]
        for item in self.bom(part):
            if bool(getattr(item,"optional",False)): continue
            row=self.requirement(build,item)
            if row: rows.append(row)
        material=date.today(); critical=None; unresolved=[]
        for row in rows:
            if row["shortage"]<=0: continue
            fd=day((row.get("forecast") or {}).get("forecast_ready"))
            if fd:
                if fd>=material: material=fd; critical=row["ipn"] or row["name"]
            else: unresolved.append(row["ipn"] or row["name"])
        ready=None if unresolved else add_days(material,self.setting("FINAL_ASSEMBLY_DAYS")+self.setting("FINAL_TEST_DAYS"))
        target=day(getattr(build,"target_date",None))
        status="BLOCKED / UNSCHEDULED" if unresolved else ("ON TRACK" if target and ready<=target else "LATE" if target and ready>target else "FORECAST")
        return {
            "plugin_version":self.VERSION,
            "build":{"id":build.pk,"reference":self.build_ref(build),"ipn":self.ipn(part),"name":str(getattr(part,"name","") or ""),"quantity":float(D(getattr(build,"quantity",0))),"target_date":iso(target)},
            "requirements":rows,
            "summary":{"material_ready":None if unresolved else iso(material),"forecast_ready":iso(ready),"critical_requirement":critical,"unresolved":unresolved,"status":status},
            "settings":{k.lower():self.setting(k) for k in self.SETTINGS},
            "notes":["V1 uses Monday-Friday business days only.","Board progress comes from current stock status and later pass states count toward earlier stages.","-BARE PO timing uses the current line target date when set; otherwise the line inherits the current PO target date.","V1 does not yet model shared technician or assembly-house capacity."],
        }

    def build_api(self, request, build_id, **kwargs):
        try: return JsonResponse(self.plan(int(build_id)))
        except Build.DoesNotExist: return JsonResponse({"error":"Build Order not found"},status=404)
        except Exception as exc: return JsonResponse({"error":f"{type(exc).__name__}: {exc}"},status=500)

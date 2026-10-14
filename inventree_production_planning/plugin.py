from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UrlsMixin, UserInterfaceMixin
from build.models import Build
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


def add_business_days(start, count):
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
    DESCRIPTION = "V2.1 recursive BO planning with leaf blockers and quantity-selectable optional BOM items."
    VERSION = PLUGIN_VERSION
    AUTHOR = "Per Vices Corporation"
    LICENSE = "MIT"

    SETTINGS = {
        "WORK_HOURS_DAY": {"name": _("Working hours per business day"), "default": 8, "validator": int},
        "PCBA_DAYS": {"name": _("Assembly lead time after inspected material is ready (business days)"), "default": 10, "validator": int},
        "BARE_VI_MIN": {"name": _("-BARE incoming VI minutes per stock item"), "default": 60, "validator": int},
        "MECH_VI_MIN": {"name": _("-MECH incoming VI minutes per stock item requiring VI"), "default": 12, "validator": int},
        "BOARD_VI_MIN": {"name": _("Assembled-board VI minutes per board"), "default": 90, "validator": int},
        "PRESS_FIT_MIN": {"name": _("Press Fit minutes per board"), "default": 30, "validator": int},
        "BU_MIN": {"name": _("Bring-Up minutes per board"), "default": 60, "validator": int},
        "EEPROM_MIN": {"name": _("EEPROM programming/test minutes per board"), "default": 15, "validator": int},
        "SW_MIN": {"name": _("Software Test minutes per board"), "default": 120, "validator": int},
        "FINAL_ASSEMBLY_MIN": {"name": _("Final assembly minutes per finished unit"), "default": 240, "validator": int},
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

    def add_hours(self, start, hours):
        """Date-level planning: any work consumes business-day capacity.

        Eight hours starting on Nov 5 therefore makes the next operation available
        Nov 6, matching the shop-floor planning convention used by this plugin.
        """
        h = max(D(0), D(hours))
        if h <= 0:
            return day(start)
        per_day = max(1, self.setting("WORK_HOURS_DAY"))
        days = int((h / D(per_day)).to_integral_value(rounding="ROUND_CEILING"))
        return add_business_days(start, days)

    @staticmethod
    def norm(value):
        return "".join(ch for ch in str(value or "").lower() if ch.isalnum())

    @staticmethod
    def ipn(part):
        return str(getattr(part, "IPN", "") or "")

    @staticmethod
    def build_ref(build):
        return str(getattr(build, "reference", "") or f"Build {build.pk}")

    @staticmethod
    def custom_statuses():
        out = {}
        try:
            for s in StockStatus.custom_queryset():
                out[int(s.key)] = str(s.label or s.name or "")
        except Exception:
            pass
        return out

    @staticmethod
    def custom_logical_statuses():
        out = {}
        try:
            for s in StockStatus.custom_queryset():
                out[int(s.key)] = int(s.logical_key)
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

    def stock(self, part):
        qs = StockItem.objects.filter(part=part, quantity__gt=0)
        fields = ["pk", "part_id", "quantity", "status", "status_custom_key"]
        # StockItem.build is the InvenTree link between a BO and its output item.
        try:
            StockItem._meta.get_field("build")
            fields.append("build_id")
        except Exception:
            pass
        try:
            return list(qs.only(*fields))
        except Exception:
            return list(qs)

    def is_build_output(self, item):
        return bool(getattr(item, "build_id", None) or getattr(item, "build", None))

    def logical_available(self, item, custom_logical):
        logical = int(getattr(item, "status", 0) or 0)
        ckey = getattr(item, "status_custom_key", None)
        try:
            if ckey is not None and int(ckey) in custom_logical:
                logical = custom_logical[int(ckey)]
        except Exception:
            pass
        try:
            return bool(StockStatus.is_available(logical))
        except Exception:
            return logical not in (50, 75, 100)

    def stock_state(self, part):
        """Separate finished usable stock from BO-created incomplete outputs.

        BO output items are WIP regardless of when they were created. They become
        usable for a parent BO only at Pass SW. Non-output stock follows normal
        InvenTree availability semantics.
        """
        custom = self.custom_statuses()
        custom_logical = self.custom_logical_statuses()
        finished = D(0)
        exact = {0:D(0), 1:D(0), 2:D(0), 3:D(0), 4:D(0), 5:D(0)}
        bad = D(0)
        for item in self.stock(part):
            qty = D(item.quantity)
            label = self.status_label(item, custom)
            key = self.norm(label)
            stage = self.STATUS_ALIASES.get(key)
            output = self.is_build_output(item)
            if output:
                if stage == 5:
                    finished += qty
                    exact[5] += qty
                elif stage:
                    exact[stage] += qty
                elif "fail" in key or "rework" in key or "quarantine" in key:
                    bad += qty
                else:
                    # An output may be created at any time; creation alone is not
                    # evidence that assembly or testing has happened.
                    exact[0] += qty
            elif self.logical_available(item, custom_logical):
                finished += qty
        return {"finished":finished, "exact":exact, "failed_rework":bad}

    def available_qty(self, part):
        return self.stock_state(part)["finished"]

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
            qs = qs.filter(status=20)
        return list(qs.order_by("id"))

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
            if outstanding <= 0:
                continue
            order=getattr(line,"order",None)
            po_target=day(getattr(order,"target_date",None))
            line_target=day(getattr(line,"target_date",None))
            target=line_target or po_target
            rows.append({"effective":target,"po_target":po_target,"line_target":line_target,"qty":outstanding,"ref":str(getattr(order,"reference","") or "")})
        rows.sort(key=lambda x:(x["effective"] is None,x["effective"] or date.max))
        remaining=max(D(0),D(need)); full=None; refs=[]
        for row in rows:
            if row["ref"] and row["ref"] not in refs:
                refs.append(row["ref"])
            remaining-=row["qty"]
            if remaining <= 0:
                full=row["effective"]
                break
        return {"open":sum((x["qty"] for x in rows),D(0)),"earliest":next((x["effective"] for x in rows if x["effective"]),None),"full":full,"refs":refs,
                "lines":[{"po":x["ref"],"qty":float(x["qty"]),"po_target_date":iso(x["po_target"]),"line_target_date":iso(x["line_target"]),"effective_date":iso(x["effective"])} for x in rows]}

    def inspection_hours(self, part, quantity):
        ipn = self.ipn(part).upper()
        qty = D(quantity)
        if ipn.endswith("-BARE"):
            return qty * D(self.setting("BARE_VI_MIN")) / D(60), "-BARE VI"
        # Mechanical incoming inspection applies to material in a -MECH BOM.
        if "-MECH" in ipn:
            return qty * D(self.setting("MECH_VI_MIN")) / D(60), "-MECH VI"
        return D(0), ""

    def material_requirement(self, part, need):
        """Forecast when a purchased/raw material quantity is received + inspected."""
        available = self.available_qty(part)
        shortage = max(D(0), D(need) - available)
        po = self.po_coverage(part, shortage) if shortage > 0 else {"open":D(0),"earliest":None,"full":None,"refs":[],"lines":[]}
        received_date = date.today() if shortage <= 0 else po.get("full")
        inspection_qty = shortage if shortage > 0 else D(0)
        # Existing stock is already assumed inspected; only incoming shortage adds VI.
        hours, inspection = self.inspection_hours(part, inspection_qty)
        ready = self.add_hours(received_date, hours) if received_date else None
        return {"ipn":self.ipn(part),"required":float(D(need)),"available":float(available),"shortage":float(shortage),
                "received_date":iso(received_date),"inspection_hours":float(hours),"inspection":inspection,"ready_date":iso(ready),
                "open_po_qty":float(po.get("open",0)),"po_references":po.get("refs",[]),"po_lines":po.get("lines",[])}

    def board_bom_material_ready(self, board_part, board_qty, depth=0, trail=None):
        """Return material-ready date and only the true leaf-level constraints.

        Satisfied BOM components are intentionally not returned to the UI. If a
        shortage is itself an assembly/subassembly with a BOM, recurse through it
        instead of reporting that intermediate assembly as the blocker.
        """
        trail = list(trail or [])
        if depth > 6:
            name = self.ipn(board_part) or str(getattr(board_part, "name", "") or board_part.pk)
            return None, [], [{"ipn": name, "reason": "recursion_limit"}]
        if board_part.pk in trail:
            name = self.ipn(board_part) or str(getattr(board_part, "name", "") or board_part.pk)
            return None, [], [{"ipn": name, "reason": "bom_cycle"}]
        trail.append(board_part.pk)

        blockers=[]
        latest=date.today()
        for item in self.bom(board_part):
            if bool(getattr(item,"optional",False)):
                continue
            sub=self.subpart(item)
            if not sub:
                continue
            qty=D(getattr(item,"quantity",0))*D(board_qty)
            available=self.available_qty(sub)
            shortage=max(D(0),qty-available)
            if shortage <= 0:
                continue

            # Intermediate assemblies are not useful blockers. Drill down until
            # we reach the actual purchased/raw material constraint(s).
            child_bom=self.bom(sub)
            if child_bom:
                child_ready,child_blockers,child_unresolved=self.board_bom_material_ready(
                    sub, shortage, depth+1, trail
                )
                blockers.extend(child_blockers)
                blockers.extend(child_unresolved)
                if child_ready and child_ready > latest:
                    latest=child_ready
                continue

            m=self.material_requirement(sub,qty)
            if m["shortage"] <= 0:
                continue
            m["path"] = " > ".join(
                [self.ipn(board_part) or str(board_part.pk), self.ipn(sub) or str(sub.pk)]
            )
            if m.get("ready_date"):
                blockers.append(m)
                rd=day(m.get("ready_date"))
                if rd and rd>latest:
                    latest=rd
            else:
                m["reason"]="no_dated_full_coverage"
                blockers.append(m)

        unresolved=[b for b in blockers if not b.get("ready_date")]
        return (None if unresolved else latest), blockers, unresolved

    def remaining_stage_hours(self, stage, qty):
        q=D(qty)
        mins=D(0)
        if stage < 1: mins += D(self.setting("BOARD_VI_MIN"))*q
        if stage < 2: mins += D(self.setting("PRESS_FIT_MIN"))*q
        if stage < 3: mins += D(self.setting("BU_MIN"))*q
        if stage < 4: mins += D(self.setting("EEPROM_MIN"))*q
        if stage < 5: mins += D(self.setting("SW_MIN"))*q
        return mins / D(60)

    def board_forecast(self, part, required_shortage, builds):
        state=self.stock_state(part); ex=state["exact"]
        # available_qty already includes Pass SW outputs, so shortage is only what
        # still has to become ready.
        need=max(D(0),D(required_shortage))
        result={"pipeline":{"unstarted_output":float(ex[0]),"pass_vi":float(ex[1]),"pass_press_fit":float(ex[2]),"pass_bu":float(ex[3]),"eeprom_pass":float(ex[4]),"pass_sw":float(ex[5]),"failed_rework":float(state["failed_rework"])},
                "ready_now":float(state["finished"]),"need_after_ready":float(need),"forecast_ready":None,"basis":"","material":[]}
        if need<=0:
            result["forecast_ready"]=iso(date.today()); result["basis"]="Finished / Pass SW stock covers the requirement."; return result
        today=date.today(); candidates=[]
        # Existing WIP with a proven test stage can be forecast directly from its
        # current stage. Unstarted BO outputs are intentionally NOT treated as assembled.
        for stage,label in [(4,"EEPROM Pass"),(3,"Pass BU"),(2,"Pass Press Fit"),(1,"Pass VI")]:
            qty=ex[stage]
            if qty>0:
                hrs=self.remaining_stage_hours(stage,qty)
                candidates.append((qty,self.add_hours(today,hrs),f"{label} WIP + {float(hrs):g}h remaining test"))
        staged=sum((ex[s] for s in (1,2,3,4)),D(0))
        remaining_unassembled=max(D(0),need-staged)
        if remaining_unassembled>0:
            material_ready,blockers,unresolved=self.board_bom_material_ready(part,remaining_unassembled)
            result["material"]=blockers
            if material_ready and not unresolved:
                assembled=add_business_days(material_ready,self.setting("PCBA_DAYS"))
                test_hours=self.remaining_stage_hours(0,remaining_unassembled)
                finish=self.add_hours(assembled,test_hours)
                candidates.append((remaining_unassembled,finish,f"materials inspected {iso(material_ready)} + {self.setting('PCBA_DAYS')} business days assembly + {float(test_hours):g}h VI/Press Fit/BU/EEPROM/SW"))
            elif unresolved:
                names=[]
                for blocker in unresolved:
                    name=blocker.get("ipn") or "Unknown material"
                    if name not in names:
                        names.append(name)
                result["basis"]="Material blocker(s) without dated full coverage: " + ", ".join(names)
        candidates.sort(key=lambda x:(x[1] is None,x[1] or date.max))
        remaining=need; chosen=None; basis=[]
        for qty,when,why in candidates:
            if not when or qty<=0: continue
            take=min(remaining,qty); remaining-=take; chosen=when; basis.append(f"{float(take):g} from {why}")
            if remaining<=0: break
        if chosen and remaining<=0:
            result["forecast_ready"]=iso(chosen); result["basis"]="; ".join(basis)
        elif not result["basis"]:
            result["basis"]=f"Only {float(need-remaining):g} of {float(need):g} additional boards can currently be dated; {float(remaining):g} remain unscheduled."
        return result

    def requirement(self, build, item, optional_total_qty=None):
        part=self.subpart(item)
        if not part: return None
        if optional_total_qty is not None:
            required=max(D(0),D(optional_total_qty))
        else:
            required=D(getattr(item,"quantity",0))*D(getattr(build,"quantity",0))
        available=self.available_qty(part); shortage=max(D(0),required-available)
        builds=self.child_builds(part,build.pk); state=self.stock_state(part)
        board_like=bool(builds or any(state["exact"][s]>0 for s in range(0,6))) and bool(self.bom(part))
        forecast=self.board_forecast(part,shortage,builds) if board_like and shortage>0 else None
        return {"bom_item_id":item.pk,"optional":bool(getattr(item,"optional",False)),"part_id":part.pk,"ipn":self.ipn(part),"name":str(getattr(part,"name","") or ""),
                "required":float(required),"available":float(available),"shortage":float(shortage),"board_like":board_like,
                "child_builds":[{"id":b.pk,"reference":self.build_ref(b),"quantity":float(D(getattr(b,"quantity",0)))} for b in builds],"forecast":forecast}

    def plan(self, build_id, optional_quantities=None):
        build=Build.objects.select_related("part").get(pk=build_id); part=getattr(build,"part",None)
        if not part: raise ValueError("Build Order has no output part")
        optional_quantities={int(k):max(D(0),D(v)) for k,v in (optional_quantities or {}).items()}
        rows=[]; optional_rows=[]
        build_qty=D(getattr(build,"quantity",0))
        for item in self.bom(part):
            if bool(getattr(item,"optional",False)):
                sub=self.subpart(item)
                per_unit=D(getattr(item,"quantity",0))
                max_total=per_unit*build_qty
                selected=min(max_total,optional_quantities.get(item.pk,D(0)))
                optional_rows.append({"bom_item_id":item.pk,"ipn":self.ipn(sub),"name":str(getattr(sub,"name","") or ""),"quantity_per_build":float(per_unit),"max_total":float(max_total),"selected_quantity":float(selected)})
                if selected <= 0:
                    continue
                row=self.requirement(build,item,optional_total_qty=selected)
            else:
                row=self.requirement(build,item)
            if row: rows.append(row)
        material=date.today(); critical=None; unresolved=[]
        for row in rows:
            if row["shortage"]<=0: continue
            fd=day((row.get("forecast") or {}).get("forecast_ready"))
            if fd:
                if fd>=material: material=fd; critical=row["ipn"] or row["name"]
            else: unresolved.append(row["ipn"] or row["name"])
        final_hours=D(self.setting("FINAL_ASSEMBLY_MIN"))*D(getattr(build,"quantity",0))/D(60)
        ready=None if unresolved else self.add_hours(material,final_hours)
        target=day(getattr(build,"target_date",None))
        status="BLOCKED / UNSCHEDULED" if unresolved else ("ON TRACK" if target and ready<=target else "LATE" if target and ready>target else "FORECAST")
        return {"plugin_version":self.VERSION,"build":{"id":build.pk,"reference":self.build_ref(build),"ipn":self.ipn(part),"name":str(getattr(part,"name","") or ""),"quantity":float(D(getattr(build,"quantity",0))),"target_date":iso(target)},
                "requirements":rows,"optional_requirements":optional_rows,"selected_optional_quantities":{str(k):float(v) for k,v in optional_quantities.items()},
                "summary":{"material_ready":None if unresolved else iso(material),"forecast_ready":iso(ready),"critical_requirement":critical,"unresolved":unresolved,"status":status,"final_assembly_hours":float(final_hours)},
                "settings":{k.lower():self.setting(k) for k in self.SETTINGS},
                "notes":["V2: BO-created incomplete outputs never count as available merely because they exist.","Pass SW is the board-ready state and counts as usable stock.","Unstaged incomplete outputs recurse into the board BOM to find material blockers.","Incoming -BARE shortage adds 1.0 hour VI per stock item before assembly can start.","-MECH incoming VI default is 0.2 hour per stock item when applicable.","Assembly starts only after all required material is received and inspected; default lead time is 10 business days.","Board defaults: VI 1.5h, Press Fit 0.5h, BU 1.0h, EEPROM 0.25h, SW 2.0h per board.","Final assembly defaults to 4.0h per finished unit.","8 working hours = 1 business day; weekends are skipped.","Optional top-level BOM quantities are selectable from 0 to the BOM maximum and stored in this browser per Build Order.","PO timing uses line target date when set, otherwise PO header target date."]}

    def build_api(self, request, build_id, **kwargs):
        try:
            raw=request.GET.get("optional","")
            optional_quantities={}
            # V2.1 format: BOM_ITEM_ID:TOTAL_QTY,BOM_ITEM_ID:TOTAL_QTY
            # V2 checkbox URLs are still accepted as quantity 1 for compatibility.
            for value in raw.split(","):
                value=value.strip()
                if not value:
                    continue
                try:
                    if ":" in value:
                        key,qty=value.split(":",1)
                        optional_quantities[int(key)]=max(D(0),D(qty))
                    else:
                        optional_quantities[int(value)]=D(1)
                except Exception:
                    pass
            return JsonResponse(self.plan(int(build_id),optional_quantities=optional_quantities))
        except Build.DoesNotExist:
            return JsonResponse({"error":"Build Order not found"},status=404)
        except Exception as exc:
            return JsonResponse({"error":f"{type(exc).__name__}: {exc}"},status=500)

# Production Planning v3.4.1 Test Plan

## Primary regression: BO-0182 / FR2TSC

1. Run BO-0182 alone and confirm existing non-FR2TSC forecasts remain sensible.
2. Inspect FR2TSC. Failed VI / rework / quarantine FR2TS must not count as usable source-board supply.
3. If additional FR2TS must be manufactured, the readiness path must explicitly show the source-board production calculation: material-ready date, 10 business days PCBA assembly (default), and VI / Press Fit / BU / EEPROM / SW hours.
4. If the missing FR2TS cannot be manufactured because of leaf material shortages, those leaf parts must be shown as blockers rather than only reporting FR2TS or FR2TSC as the blocker.

## Multi-build regression

1. Select BO-0182, BO-0179 and the FR2TS BO in the same priority order used for v3.2.x testing.
2. Confirm higher-priority BOs consume shared virtual source-board/component/PO supply first.
3. Confirm the FR2TS BO is forecast as PCBA manufacture, not generic final assembly: BOM material readiness -> PCBA assembly -> VI -> Press Fit -> BU -> EEPROM -> SW.
4. Confirm Build Forecast detail continues to show only shortages / production requirements that matter, not the complete satisfied BOM.
5. Confirm Combined Material Shortages contains every unresolved leaf-material shortage found in any selected BO, including shortages from the selected FR2TS BO.
6. Reverse priorities and confirm shortage ownership changes without modifying InvenTree allocations.

## Expected invariants

- Planning is simulation-only.
- `* Assembly` BOM lines remain costing-only and never become material blockers.
- Ordinary leaf components use InvenTree variant-aware availability.
- Pass SW is board-ready; merely creating an incomplete output is not evidence of assembly completion.
- Failed VI / rework / quarantine stock is unavailable for production or conformal conversion.
- Optional BOM selection behavior remains unchanged.


## v3.3.1 bare-PCB status regression
- TR8D-BARE: with physical stock present but all stock marked Failed VI, verify usable availability is zero.
- With no credible future PO fully covering TR8D-BARE, verify the planner uses the 28-calendar-day PCB fabrication/remake fallback, then incoming VI, then 10 business days PCBA assembly and board tests.
- Pending `-BARE` stock must schedule incoming VI rather than fabrication.
- OK/passed `-BARE` stock must be usable immediately.
- A credible PO which covers the shortage earlier than new fabrication must be selected instead.

## v3.4.1 Gantt and wording regression

1. Run the same multi-BO plan used to validate v3.3.1. Confirm a **Production Gantt (Forecast)** appears above Combined Material Shortages.
2. Confirm every selected BO appears in the same priority order as the planner and its bar ends on the BO forecast-complete date.
3. Confirm dated shortage requirements appear beneath their BO and unscheduled requirements are explicitly labelled `UNSCHEDULED`.
4. For a BO with a target date, confirm the target-date marker is visible and does not change the forecast.
5. For a normal top-level product BO with separately known material-ready and final-ready dates, confirm Final assembly is shown as its own phase.
6. Re-test TR8DC with Failed VI TR8D-BARE and no credible PO coverage. The blocker must say `PCB fabrication fallback: 28 calendar days -> estimated receipt ...`, followed by incoming VI and the material-ready date. It must not call the fallback an existing PO receipt.
7. Confirm the Gantt is display-only: calculating or opening it must not create allocations or modify BOs, StockItems or POs.

# Production Planning v3.2.0 Test Plan

## Primary regression: shared FR2TS -> FR2TSC source boards

1. Select BO-0182 as Priority 1 and BO-0183 (FR2TSC) as a later priority.
2. Confirm BO-0182 claims the 40 ready FR2TS source boards required for its 40 FR2TSC requirement.
3. Confirm BO-0183 does **not** reuse those same 40 FR2TS boards.
4. BO-0183 must forecast manufacture of its required FR2TS source boards before conformal coating.
5. If the remaining FR2TS BOM material is sufficient, the readiness path should explicitly state that all required source-board BOM material is covered by remaining virtual supply, and include PCBA assembly + VI / Press Fit / BU / EEPROM / SW timing before coating.
6. If any shared component is insufficient after higher-priority BO claims, it must appear as a material blocker for BO-0183 with the applicable remaining PO coverage / unscheduled state.
7. Reverse BO priority and confirm the shared source-board/component claims move with priority.

## Shared WIP regression

Use two selected BOs which compete for staged WIP of the same source board. Confirm the same Pass VI / Press Fit / BU / EEPROM WIP quantity is not used by both plans.

## Existing v3.1 regressions

- Optional BOM lines still prompt per selected BO before combined calculation.
- Ordinary component stock remains variant-aware.
- Shared PO quantities are not promised twice.
- No allocations or Build Orders are modified.
- Single-BO parent-product forecasts remain consistent with v3.1 except where they directly plan a conformal-coated output BO.

## Planning Assumptions UI

Confirm the panel heading is simply **Planning Assumptions** and contains the grouped sections **Time Related Assumptions**, **Inventory & Material Assumptions**, and **Planning Behavior**. Historical V2/V3 release notes must not appear in this UI section.

# Production Planning v3.1 Test Plan

1. Regression: run BO-0182 alone and confirm the forecast remains consistent with v0.2.10/v3.0.
2. Select a BO containing optional top-level BOM lines. Click Continue to Production Plan and confirm an Optional BOM Requirements prompt appears before the combined calculation.
3. Set an optional quantity to 0 and confirm it is excluded. Set it above 0 and confirm the selected total quantity is included in that BO only.
4. Select two or more BOs sharing a constrained component. Confirm Combined Material Shortages shows the part, total demand, affected BOs, and per-priority Need / Available / Short values.
5. Reverse BO priority and recalculate. Confirm shared virtual stock / PO supply is consumed in the new order and shortages move accordingly.
6. Expand each Build Forecast and confirm top-level requirements, readiness paths, material blockers, PO details and UNSCHEDULED causes are visible.
7. Confirm no real stock allocations, BuildItems, Build Orders, or Purchase Orders are changed by calculation.
8. Confirm variant-aware ordinary material availability still matches InvenTree available_stock behavior.
9. Confirm conformal-coated board forecasting, WIP stage handling, incoming inspection and final assembly timing remain unchanged.

No database migration is required.

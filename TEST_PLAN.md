# Production Planning v3.1 Test Plan

1. Regression: run BO-0182 alone and confirm the forecast remains consistent with v0.2.10/v3.0.
2. Select a BO containing optional top-level BOM lines. Click Continue to Production Plan and confirm an Optional BOM Requirements prompt appears before the combined calculation.
3. Set an optional quantity to 0 and confirm it is excluded. Set it above 0 and confirm the selected total quantity is included in that BO only.
4. Select two or more BOs sharing a constrained component. Confirm Combined Material / Resource Detail shows the part, total demand, affected BOs, and per-priority Need / Available / Short values.
5. Reverse BO priority and recalculate. Confirm shared virtual stock / PO supply is consumed in the new order and shortages move accordingly.
6. Expand each Build Forecast and confirm top-level requirements, readiness paths, material blockers, PO details and UNSCHEDULED causes are visible.
7. Confirm no real stock allocations, BuildItems, Build Orders, or Purchase Orders are changed by calculation.
8. Confirm variant-aware ordinary material availability still matches InvenTree available_stock behavior.
9. Confirm conformal-coated board forecasting, WIP stage handling, incoming inspection and final assembly timing remain unchanged.

No database migration is required.

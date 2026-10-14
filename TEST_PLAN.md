# Production Planning v0.2.3 Test Plan

## Primary acceptance test — BO-0179 / TR8D

1. Open BO-0179 Production Plan.
2. Confirm TR8D is clickable and opens the TR8D Part page.
3. Confirm the TR8D child-build analysis credits material already allocated / consumed against BO-0128.
4. Confirm allocated components such as resistors, ICs, connectors, etc. are not rediscovered as shortages merely because little or no globally free stock remains.
5. Confirm `TR8D Assembly` is not displayed as a blocker and is not used for PO coverage.
6. If TR8D-BARE is the only remaining uncovered requirement, confirm TR8D-BARE is the only material blocker shown.
7. Confirm TR8D-BARE is clickable and opens its Part page.
8. Confirm any dated PO coverage, incoming VI, material-ready date, 10-business-day assembly and remaining board-test forecast are still shown correctly.

## Assembly costing-line test

Confirm each of the following patterns is excluded when present as a BOM item:
- TR8D Assembly
- TR8DP Assembly
- TR8R Assembly
- FR2TS Assembly

The rule is suffix-based (` Assembly`), not based on IPN length.

## Allocation test

For an existing child BO, allocate enough stock to fully cover a BOM component. Confirm that component is not a blocker even when there is no additional unallocated stock. Partially allocate another component and confirm only its uncovered remainder is evaluated against unallocated stock / PO coverage.

## Regression

Confirm optional quantities, Pass SW readiness, WIP stage forecasts, PO effective-date fallback, inspection durations, final assembly and unresolved critical-requirement behavior remain unchanged from V2.2.

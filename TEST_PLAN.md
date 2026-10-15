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


## V2.4 allocation regression

1. Open BO-0179 Production Plan and inspect TR8D / child BO-0128.
2. Confirm components whose BO-0128 BuildLines are fully allocated do not appear as blockers.
3. Confirm a partially allocated BuildLine is evaluated only for `unallocated_quantity()`, not its full BOM quantity.
4. Confirm `TR8D Assembly` (and any IPN/name ending in ` Assembly`) remains excluded.
5. Confirm genuine uncovered material still shows free-stock and PO coverage.
6. Confirm part and Build Order links remain clickable.

## V0.2.5 status-aware tests
1. Set allocated `TR8D-BARE` StockItems to OK: they should be treated as assembly-ready material.
2. Set them to Pending: the plan should show TR8D-BARE as the current constraint and add configured `-BARE` incoming VI time before assembly.
3. Set them to Failed VI: the plan should not call them inspected or ready. It should show Failed VI and compare open PO coverage with the configured replacement-fabrication date.
4. With a future PO that covers the required replacement quantity sooner than 28 days, the PO should win.
5. Without a credible future PO, new fabrication should win at today + 28 calendar days, followed by incoming VI.
6. A past-due PO target may remain visible in details but must not beat the new-fabrication forecast.
7. Quarantined / damaged / otherwise unavailable allocated material must remain unresolved.
8. Confirm TR8D-BARE is recognized as `-BARE` from Part Name even though its IPN is blank.
9. Confirm a parent needing 3 boards forecasts only enough replacement / inspection capacity for 3, even if the child BO is for 13.

## V0.2.6 regression checks

- Set allocated/on-hand `TR8D-BARE` stock to `Failed VI`; with no credible future PO, verify a 28-calendar-day replacement fabrication date is forecast, followed by incoming VI, 10 business days PCBA assembly, and board testing.
- Verify a future PO that fully covers the BARE shortage and arrives sooner than the 28-day fabrication fallback is selected instead.
- Verify past-due open PO ETAs remain visible but do not create historical material-ready dates.
- Verify TR8M/TR8P/TR8B readiness paths show `10 business days assembly`.


## V0.2.8 conformal coating tests

1. Create/use a coated PCBA variant such as TR8RC whose `variant_of` is TR8R. Verify a top-level BOM requiring TR8RC does not recurse directly to TR8R bare-PCB manufacture when enough ready TR8R exists.
2. With 0 TR8RC and at least 3 ready TR8R, require 3 TR8RC. Verify the readiness path shows 14 calendar days conformal coating, Convert to TR8RC, 4.5h VI-POST-CC, and 6h SW-POST-CC.
3. With fewer than 3 ready TR8R, verify the missing source quantity is first forecast through the existing TR8R production path, then coating and post-CC tests are added.
4. Verify a variant ending in C but without the InvenTree variant relationship is not treated as conformal coated.
5. Verify a variant relation with neither trailing-C convention nor `Conformal Coated` in the Part name is not automatically treated as coated.
6. Verify existing ready TR8RC stock satisfies the requirement immediately.
7. Expand Planning Assumptions and verify the 14-day coating, 1.5h VI-POST-CC, and 2.0h SW-POST-CC defaults are stated.


## V0.2.9 location-neutral / child-BO allocation regression

1. Put otherwise usable component stock in an External location and confirm it satisfies the requirement.
2. Confirm Pending, Failed VI, Quarantine and damaged stock remain governed by status and do not become usable merely because of location.
3. Forecast a coated variant whose source board has an existing production BO; confirm the existing BO BuildLines / allocations are used before generic BOM shortage recursion.
4. Confirm BuildItem allocations belonging only to completed/cancelled builds do not reduce current available stock.
5. Re-test BO-0182 TR8RC: the TR8R source forecast should reduce to genuine uncovered material (expected BTL-0026SMG-1-PV / its PO) rather than unrelated false blockers.

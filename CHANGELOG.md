## 3.4.1
- Move Gantt generation to an explicit **Generate Gantt** action after a Production Plan is calculated.
- Support Gantt generation for a single Build Order.
- Multi-build plans render all selected Build Orders on the same Gantt in planning-priority order.
- Gantt remains a forecast visualization only and does not allocate stock or reserve capacity.

# Changelog

## 3.4.1
- Add an inline **Production Gantt (Forecast)** to multi-build planning.
- Show selected Build Orders in priority order with forecast-completion bars, shortage-requirement forecast rows, target-date markers, and final-assembly phases where separately known.
- Gantt dates come from the same shared virtual-stock / recursive production simulation as the combined plan; the chart is planning-only and does not reserve labor or equipment capacity.
- Clarify bare-PCB fallback wording: when no credible PO covers a `-BARE` shortage, show the configured fabrication lead time and estimated replacement receipt explicitly instead of labeling it generic expected coverage.
- Preserve v3.3.1 status-aware `-BARE` PCB planning and recursive source-board forecasting.

## 3.3.1
- Treat `-BARE` PCB stock by live VI status instead of generic `Part.available_stock`.
- `Failed VI`, rework, quarantine and damaged bare PCBs never satisfy material demand.
- `Pending` bare PCBs are physically present but require configured incoming VI before becoming ready.
- When passing bare-PCB stock is insufficient, use credible dated PO coverage or the configured 28-calendar-day fabrication/remake fallback, whichever provides the earlier viable replacement path.
- Preserve recursive source-board production, shared multi-build priority pools and consolidated leaf-material shortages from v3.3.0.

## 3.0.0 - 2026-10-15

- Add multi-Build-Order production planning from the Production Plan panel.
- Select active Production BOs and explicitly reorder them by planning priority.
- Combined planning is simulation-only and never creates or changes InvenTree allocations.
- Selected BOs share virtual ordinary-component stock, including InvenTree-compatible variant stock, so the same inventory cannot satisfy multiple plans.
- Selected BOs share exact finished-board stock and WIP stage quantities without treating manufacturing variants as interchangeable finished boards.
- Dated open-PO supply is shared in priority order so the same incoming quantity cannot cover multiple selected BOs.
- Preserve v0.2.10 single-BO planning and all existing conformal-coating, WIP, inspection, child-BO, status, and timing rules.
- Add combined forecast summary, shared-constraint summary, and per-BO forecasts in priority order.
- No database migration.

## 0.2.10 - 2026-10-15

- Use InvenTree's native `Part.available_stock` for ordinary purchased/raw BOM material availability.
- Component availability now matches the Build Order UI and includes compatible variant stock.
- Preserve exact-part stock-state logic for finished PCBAs, WIP stages, conformal-coated conversions, Failed VI, Pending inspection, and other manufacturing-state handling.
- Prevent valid component variants from appearing as false leaf blockers in recursive board forecasts.
- No database migration.

## 0.2.9 - 2026-10-15

- Treat usable stock as location-neutral for Production Planning; stock in External / assembly-house locations can satisfy requirements.
- Continue to use live StockItem status to determine whether material is usable, pending inspection, Failed VI, quarantined, or otherwise blocked.
- Preserve existing child BuildLines / allocations as the authoritative material state when forecasting additional source PCBAs.
- Count only active-build allocations when subtracting globally committed stock; historical completed/cancelled BuildItem records no longer create false shortages.
- Preserve v0.2.8 conformal-coated variant forecasting and all timing assumptions.
- No database migration.

## 0.2.8 - 2026-10-15

- Fix conformal-coated variant recognition when board identifiers are stored in Part Name and IPN is blank.
- Resolve the conversion source directly from InvenTree `variant_of` (e.g. TR8MC -> TR8M).
- Keep the trailing-C / Conformal Coated check as the workflow qualifier.
- Preserve the v0.2.7 assumptions: 14 calendar days coating, 1.5h/board VI-POST-CC, and 2.0h/board SW-POST-CC.
- No database migration.

## 0.2.7 - 2026-10-15

- Forecast conformal-coated PCBA variants from their standard-PCBA variant source.
- Recognize coating only when the InvenTree variant relationship is present and the coated Part follows the trailing `C` IPN convention or includes `Conformal Coated` in its name.
- Add configurable 14-calendar-day conformal coating lead time.
- Add post-coating VI and software-test assumptions using 1.5 h/board and 2.0 h/board defaults.
- Forecast source-board manufacture first when insufficient standard PCBAs are ready, then add coating and post-CC testing.
- Document all conformal-coating timing assumptions in the Production Plan assumptions panel.
- No database migration.

## 0.2.5
- Make existing child-BO allocated material stock-status aware.
- `OK` / usable allocated stock remains assembly-ready.
- `Pending` allocated stock is treated as physically received but awaiting incoming inspection; `-BARE` inspection uses the configured VI minutes per item.
- `Failed VI` allocated stock is unusable and triggers replacement planning.
- Replacement planning compares credible dated open-PO coverage with a configurable new-fabrication lead time (default 28 calendar days) and uses the earlier path.
- Replacement material still receives required incoming VI before becoming assembly-ready.
- Unavailable / quarantined / damaged allocated material remains unresolved rather than being treated as ready.
- `-BARE` / `-MECH` inspection classification now checks Part Name as well as IPN, supporting parts such as TR8D-BARE with a blank IPN.
- Forecast only the quantity needed by the parent requirement when a larger child BO exists.
- Update Planning Assumptions heading to the actual plugin version.
- No database migration.

## 0.2.6 - 2026-10-14

- Forecast `-BARE` replacement fabrication at 28 calendar days when Failed VI stock blocks the build and no earlier credible PO coverage exists.
- Apply the same fabrication fallback to undated `-BARE` shortages so PCB material does not remain permanently unscheduled.
- Ignore past-due open PO dates as forecast supply dates while retaining them in PO detail as stale information.
- Reset the PCBA assembly setting under a new key with a 10-business-day default, avoiding legacy saved 5-day values.

## 3.5.0
- Added expandable activity-level rows to the Production Gantt for both single- and multi-build plans.
- Manufactured requirements now expose dated schedule segments for PCB fabrication/remake, incoming VI, PCBA assembly, Board VI, Press Fit, Bring-Up, EEPROM, Software Test, conformal coating, VI-POST-CC and SW-POST-CC when applicable.
- Added Expand All / Collapse All controls while keeping the default Gantt compact.
- Existing WIP begins at its proven production stage rather than displaying already-completed phases.
- Gantt remains a planning visualization only and does not allocate stock or reserve capacity.

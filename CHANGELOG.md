## 3.2.0 - 2026-10-15

- Treat a selected Build Order whose output is a conformal-coated PCBA as production demand for the full BO quantity, rather than as a generic top-level BOM/final-assembly plan.
- Consume standard source-PCBA stock in shared priority order. Source boards already promised to a higher-priority coated requirement cannot be reused by a later BO.
- When source PCBAs are exhausted, forecast manufacture of the missing standard boards from the remaining shared WIP, component stock / variants and dated PO supply before coating.
- Fix staged-WIP sharing so later BOs cannot reduce their assembly quantity using WIP already claimed by a higher-priority BO.
- Make successful source-board material coverage explicit in the readiness path when all required BOM material is covered by remaining virtual supply.
- Replace version-history-style notes with a clean Planning Assumptions section grouped into Time Related Assumptions, Inventory & Material Assumptions, and Planning Behavior.
- No database migration.

## 3.1.0 - 2026-10-15

- Add an explicit optional-BOM selection step before a combined production plan is calculated.
- Optional quantities are set independently for each selected Build Order; 0 excludes the line.
- Pass optional selections into each priority-ordered BO forecast instead of silently assuming zero.
- Add combined material/resource detail showing total demand, unresolved quantity, open-PO quantity, affected BOs, priority, available quantity seen by that priority, shortage, path and material-ready date.
- Make each Build Forecast expandable and show its full top-level requirements, readiness paths and material blockers rather than only a summary date/status.
- Tag virtual stock/WIP/PO claims with Build Order and priority for traceability.
- Planning remains simulation-only; no InvenTree allocations or Build Orders are changed.
- No database migration.

# Changelog

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

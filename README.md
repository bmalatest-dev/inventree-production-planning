# InvenTree Production Planning v3.0.0

Production Planning forecasts when active Build Orders can be completed from finished stock, WIP test stages, child Build Orders, material availability, PO dates, incoming inspection, assembly lead time and final test.

## V2.4 material-planning rules

Existing child Build Orders are treated as the authoritative production work already in progress. Material already allocated or consumed against those child BOs is committed coverage and is not reported again as a shortage. Only the remaining uncovered requirement is checked against unallocated usable stock and then against open purchase orders.

BOM entries whose IPN or name ends with ` Assembly` are costing-only entries. They remain in the InvenTree BOM so product cost remains complete, but Production Planning ignores them as physical material requirements because assembly time is forecast separately.

Displayed part references are navigable links to the corresponding InvenTree Part page.

## Default planning assumptions

- 8 working hours per business day
- 10 business days assembly after all required material is received and inspected
- `-BARE` incoming VI: 1 hour per stock item
- `-MECH` incoming VI: 0.2 hours per stock item when VI is required
- assembled-board VI: 1.5 hours per board
- Press Fit: 0.5 hours per board
- Bring-Up: 1 hour per board
- EEPROM programming/test: 0.25 hours per board
- Software Test: 2 hours per board
- Pass SW means the board is ready
- final assembly: 4 hours per finished top-level unit

These values are plugin settings and can be tuned later.


## V2.4 allocation behavior

When an existing child Build Order is available, Production Planning now uses InvenTree's native BuildLine allocation state. `BuildLine.unallocated_quantity()` is authoritative. A fully allocated or consumed BuildLine is excluded from blocker analysis; only its remaining unallocated quantity can be tested against free stock and PO coverage.

## V0.2.5 stock-status planning
Allocation and readiness are separate concepts. For an existing child BO, native BuildLine allocation state remains authoritative for committed quantity, but the allocated StockItem status determines whether that material is actually usable. Pending material schedules incoming inspection. Failed VI material cannot satisfy the build and is replaced using the earlier of credible open-PO coverage or the configured replacement fabrication lead time (default 28 calendar days). Replacement material must still pass incoming inspection before assembly begins.


## V0.2.9 conformal coating planning

A conformal-coated PCBA is recognized when it is an InvenTree variant of a standard PCBA and either follows the documented trailing-`C` IPN convention (for example `TR8R` -> `TR8RC`) or has `Conformal Coated` in its Part name. When coated stock is short, Production Planning uses ready standard boards first, forecasts any missing standard boards through the existing board-planning logic, then adds 14 calendar days for conformal coating and the configured post-CC VI and software-test time. Defaults are 90 minutes/board for `VI-POST-CC` and 120 minutes/board for `SW-POST-CC`.


## V0.2.10 variant-aware component availability

For ordinary purchased/raw BOM material, Production Planning uses InvenTree's native `Part.available_stock` value. This intentionally matches the availability shown on InvenTree Build Order lines and includes compatible Part variants. Finished PCBAs and WIP continue to use exact-part stock-state logic so manufacturing variants such as conformal-coated boards are not treated as interchangeable finished stock.


## V3.0 multi-build production planning

V3.0 adds a planning-only multi-Build-Order view inside the Production Plan panel. Select active Production BOs, place them in explicit priority order, and calculate them as one shared production scenario. Priority 1 receives first claim on the virtual supply pool, followed by Priority 2, and so on.

The shared planning pool covers ordinary component stock (using InvenTree variant-aware availability), exact finished-board stock, WIP test-stage quantities, and dated open-PO supply. These are virtual claims only: Production Planning does not create, modify, or commit InvenTree allocations. Reordering the selected BOs and recalculating is therefore safe and can be used to compare production priorities.

The combined result shows the overall forecast completion date, unresolved BO count, shared constraints, and each BO forecast in priority order. The existing single-BO Production Plan remains available and unchanged.


## v3.1 multi-build detail

Multi-build planning now pauses for optional BOM quantities when any selected BO contains optional top-level lines. Each optional quantity is scoped to its BO and a quantity of 0 excludes it. The combined result includes expandable per-BO forecasts plus combined material/resource detail so priority-driven shortages can be traced to the affected BO and BOM path. The planner remains simulation-only and never allocates stock.


## v3.2 shared source-board planning

When a selected BO produces a conformal-coated PCBA, the planner treats the BO quantity as new production demand. Higher-priority requirements first claim ready standard source boards. A later coated-board BO then sees only the remaining source boards and must forecast any missing source PCBAs through assembly and test using the remaining shared component / WIP / PO pools. This is simulation-only and does not create allocations.

The UI now presents a concise **Planning Assumptions** section grouped by timing, inventory/material rules, and planning behavior rather than listing historical version changes.

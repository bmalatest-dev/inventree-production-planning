# InvenTree Production Planning v3.4.1

## v3.4.1 forecast Gantt

Multi-build results now include an inline **Production Gantt (Forecast)**. Each selected BO is shown in planning priority order from the planning date to its forecast completion date, with dated shortage requirements beneath it, target-date markers, and a separate final-assembly phase when that boundary is available from the forecast. Unscheduled requirements remain visibly marked rather than receiving invented dates.

The Gantt is a visualization of the existing production forecast. It does not allocate inventory or reserve technician / machine capacity. A future capacity-planning phase can extend the structured schedule with resource-constrained start dates.

Bare-PCB fallback wording now explicitly distinguishes a new PCB fabrication/remake estimate from an actual PO receipt date.

## v3.3.1 status-aware bare-PCB planning

v3.3.1 keeps the recursive production path from v3.3.0 and adds live `-BARE` PCB status handling. Failed VI boards are known-bad and excluded; Pending boards require incoming VI; shortages use credible PO coverage or the configured fabrication/remake fallback.

v3.3.0 uses one recursive production path for selected PCBA BOs and manufactured subassemblies. When a conformal-coated requirement is short of usable standard source boards, the planner forecasts the missing source boards through their BOM, material readiness, PCBA assembly, VI, Press Fit, Bring-Up, EEPROM and Software Test before adding conformal coating and post-coating tests. Failed VI / rework / quarantine boards do not count as usable source supply.

Combined Material Shortages is fed by the same leaf-material planning path, including direct material shortages from selected PCBA BOs. Multi-build planning remains simulation-only and does not create or change allocations.

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
- TX Waveform Testing: 0.25 hours per board
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


### Multi-build report detail

Per-BO material detail in the combined planner displays only requirements with a remaining shortage. Satisfied BOM lines are still evaluated internally but are hidden from the report. BOM entries ending in ` Assembly` are costing-only and are excluded from material planning entirely.

### Expandable production Gantt
After calculating either a single-build or multi-build Production Plan, select **Generate Gantt**. The chart initially shows the compact build/requirement view. Manufactured requirements with detailed schedule data have an expand arrow; use it to reveal the forecast activity breakdown. **Expand All** and **Collapse All** control all detailed rows at once.

Activity rows are generated by the same forecast calculation used by the Production Plan. Depending on the actual path, these can include PCB fabrication/remake or PO waiting, incoming VI, PCBA assembly, Board VI, Press Fit, Bring-Up, EEPROM, Software Test, conformal coating, VI-POST-CC, and SW-POST-CC. Existing WIP begins from its current proven stage, so completed operations are not re-shown as future work.


## Scenario timing overrides
After a plan is calculated, **Adjust Planning Times** allows temporary what-if changes to fabrication, incoming VI, PCBA assembly, board test, coating, post-coating test and final assembly durations. Blank values retain configured defaults. Overrides can apply to the whole plan or to an individual board and are not persisted to InvenTree.


### Planning-time editor UI (v3.6.2)
Board-specific timing sections are collapsed by default and can be expanded independently. The plan-wide timing table remains visible. Boards with scenario overrides show an override count while collapsed.


In v3.6.2, board-specific timing tables are native collapsed sections; the plan-wide table remains visible. The frontend asset is versioned to avoid stale browser caching.

### Status-aware board outputs and Part-specific test flows (v3.7.0)
For a selected board Build Order, Production Planning now evaluates the BO's own output StockItems before forecasting new production. `Pass SW` outputs are ready immediately. Outputs at intermediate states such as `Pass VI`, `Pass BU`, or `EEPROM Pass` are WIP and only receive the remaining required test time. Failed, rework, quarantined, or damaged outputs do not count as ready.

The required board-test sequence is driven by the Part's InvenTree Test Templates. Recognized production stages are Visual Inspection, Press Fit, Bring Up, EEPROM, and Software Test. A stage that is not configured for the Part is omitted from the forecast, Gantt, and board-specific timing editor. For example, a board such as TR8L with no Press Fit test template does not receive Press Fit time. If no recognizable production test templates exist, the plugin falls back to the full legacy sequence to avoid silently omitting work.


### Assembled-board rework and WIP rules (v3.7.1)
- Pass SW is Ready. Intermediate passing stages are WIP and only receive the mandatory tests still remaining.
- The core assembled-board sequence is VI -> Bring-Up -> EEPROM -> Software Test. Press Fit is added only for Parts with a Press Fit Test Template.
- Any assembled-board failed test (VI, Press Fit, BU, EEPROM, SW) forecasts configurable rework (default 2 business days), then restarts the complete mandatory test sequence at VI. It does not repeat PCBA assembly.
- `-BARE` Failed VI remains unusable raw material and follows replacement/remanufacture logic instead of assembled-board rework.

### Manufactured assembly timing (v3.9.0)
Production Planning distinguishes PCB assembly from generic/mechanical assembly. PCBAs retain the configured PCBA assembly lead time. Other manufacturable subassemblies use a configurable 20-business-day generic/mechanical default which can be overridden per planning scenario and per Part. Testing is driven only by mandatory Part Test Templates; Parts without mandatory tests receive no test time. Assembled-PCBA failure/rework behavior remains unchanged.


### Completed generic assembly stock (v3.9.1)
For non-PCBA manufactured parts, Production Planning distinguishes incomplete BO outputs from completed stock using InvenTree `StockItem.is_building`. Completed usable stock satisfies demand first. If the Part has mandatory tests, all mandatory tests must pass before that completed stock is ready. Only the remaining shortage is sent through generic/mechanical assembly. PCBA readiness continues to use the validated Pass SW / WIP-stage rules.


### Qualified mandatory test names (v3.9.3)
Production Planning uses the ordered mandatory InvenTree Test Templates applicable to each Part. For variants, the planner merges enabled Test Templates across the `variant_of` chain by stable test key. Child templates override matching parent templates while retaining the workflow position, so both fully inherited and partially overridden test workflows are supported. Multiple tests in one family remain separate (for example Bring Up Stage 1 and Bring Up Stage 2). StockItem results are matched by template ID or stable test key. Recognized timed tests include VI, Press Fit, Bring-Up, EEPROM, TX Waveform Testing (0.25 h/board default), and Software Test. Optional/admin templates remain excluded.


### v3.9.7 TEMPLATE test de-duplication
Legacy template/variant families may expose both a placeholder test such as `TEMPLATE Bring Up` and the concrete `Bring Up` test. Production Planning treats those as the same production operation and keeps the non-TEMPLATE definition. Existing assembled StockItems are evaluated against this de-duplicated workflow, so duplicate inherited template tests cannot force completed/WIP PCB outputs back through PCBA assembly.

### v3.9.10 canonical workflow ordering and Ready/WIP accounting

Variant inheritance can place child and parent test templates in a database order which is not the actual production sequence. v3.9.10 orders recognized mandatory production tests by workflow semantics after inheritance and TEMPLATE de-duplication. Production Requirements also reports Ready and WIP as mutually exclusive quantities; failed assembled boards count as WIP/rework and follow rework plus the full mandatory retest sequence without repeating PCBA assembly.

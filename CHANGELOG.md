## v3.9.12

- Unknown mandatory Test Templates now default to 60 minutes per item instead of zero time.
- Forecasts retain the actual InvenTree Test Template name (for example, RandomTest).
- Added configurable `Other / unknown mandatory test` timing and per-part/test scenario overrides.
- No migration required.

## v3.9.11
- Distinguishes full overdue PO coverage from true unscheduled supply: overdue full coverage is **LATE / REQUIRES ATTENTION** with **ETA REQUIRED**, while partial/no coverage remains blocked.
- Multi-build Build Forecasts now include a per-BO collapsible **Ready Requirements (N)** section so later-priority BOs have the same requirement visibility as the first BO.
- No planning quantity, recursion, shared-pool, assembly, or test-timing behavior changed.

# v3.9.11

- Production-safe packaging release of the validated v3.9.9 planning logic.
- Reuses the last known-good collected frontend asset name (`production_planning_v398.js`) because the frontend code is byte-for-byte identical to v3.9.8.
- Avoids requiring a newly named static asset or manual `collectstatic` / shell access during production deployment.
- No planning-logic changes and no database migration.

## v3.9.9

- Fix final mandatory-test stage being double-counted as both Ready stock and WIP.
- Ready stock is now removed from the final-stage WIP pool before stage claims.
- This allows unresolved failed assembled boards to reach the rework path instead of being hidden by already-ready boards.
- BO-0133 regression: 21 Ready + 1 Failed BU must forecast 1 Rework -> full retest from VI, never Software Test WIP + 0h.

## v3.9.9

- Fix inherited/variant mandatory-test ordering so recognized production tests follow the canonical workflow: VI → Press Fit → Bring Up Stage 1 / Bring Up → EEPROM → Bring Up Stage 2 → TX Waveform → Software Test.
- Preserve distinct mandatory tests while continuing to de-duplicate equivalent `TEMPLATE` tests in favor of the real/non-TEMPLATE definition.
- Fix Production Requirements WIP reporting so Ready and WIP are mutually exclusive. Failed assembled boards are included in WIP/rework, while fully qualified boards are counted only as Ready.
- Preserve assembled-board failure behavior: rework lead time followed by the complete mandatory test workflow, without repeating PCBA assembly.
- No database migration required.
## v3.9.7

- Filter optional Test Templates before semantic TEMPLATE de-duplication so an optional duplicate can never suppress a mandatory inherited production test.
- Merge mandatory tests across the full variant/template chain and retain one effective test per normalized identity, preferring the non-`TEMPLATE` definition when a genuine duplicate exists.
- Restore TR8R-style partial workflows: direct Visual Inspection plus inherited Bring Up, EEPROM, and Software Test remain mandatory.
- A failed mandatory test on an assembled PCB remains failed WIP: forecast configured rework, then restart the complete effective mandatory test sequence from VI without repeating PCBA assembly.
- Existing assembled WIP with a passed intermediate stage schedules only its remaining mandatory tests; PCBA assembly is reserved for genuinely unassembled shortage quantity.
- Preserve FR2TS inherited multi-stage workflow and TX Waveform timing.
- No database migration required.

## v3.9.6

- De-duplicate inherited test templates semantically when an ancestor test is explicitly prefixed `TEMPLATE` and an equivalent concrete test exists in the Part/variant workflow.
- Prefer the concrete non-`TEMPLATE` test over its placeholder duplicate.
- Match historical StockItem test results using the same semantic test identity so inherited/template-linked results still qualify the actual assembled PCB.
- Prevent duplicate TEMPLATE phases from making already-assembled WIP appear to require PCBA assembly again.
- Preserve v3.9.5 merged child/parent mandatory workflows, FR2TS inherited tests, and assembled-board rework/full-retest behavior.

## v3.9.5
- Merge mandatory Test Templates across a Part's `variant_of` chain instead of inheriting only when the child has no mandatory templates.
- Child templates override matching parent templates by stable test key while preserving the parent workflow position.
- Fix TR8R-style partial workflows where Visual Inspection is defined on the child but Bring Up, EEPROM, and Software Test are defined on the generic parent.
- Preserve v3.9.4 FR2TS inherited workflow behavior, TX Waveform timing, and assembled-board rework/full-retest behavior.
- No database migration required.

# Changelog

## v3.9.4
- Fixed mandatory test discovery for InvenTree variant parts: when a variant has no direct mandatory Test Templates, Production Planning now uses the first mandatory template set found on its `variant_of` chain.
- Mandatory board tests are now kept as an ordered per-template workflow instead of collapsing multiple tests into one generic stage. This preserves distinct tests such as Bring Up Stage 1 and Bring Up Stage 2.
- StockItem progress is derived from the actual mandatory test results, matched by template ID or stable test key, so inherited/synced historical results remain usable.
- Added TX Waveform Testing timing with a default of 15 minutes (0.25 h) per board.
- Optional tests such as Rework remain excluded from the normal mandatory test sequence; assembled-board failure still uses the configured rework path followed by the full mandatory retest sequence.
- No database migration required.

## 3.9.3
- Fixed mandatory board-test stage discovery when InvenTree Test Template names contain qualifiers such as `Bring Up Stage 1`.
- Mandatory template names are now read defensively across supported model attribute names instead of silently collapsing to an empty test sequence.
- Qualified production-test names are matched by test family for VI, Press Fit, Bring-Up, EEPROM, and Software Test.
- Preserves v3.9.1 generic/mechanical completed-stock readiness and all assembled-board rework rules.
- BO-0136 regression target: Pass BU WIP must retain every later mandatory test (including Software Test when configured); post-rework units must receive the complete mandatory retest sequence.


## 3.9.1
- Count completed non-PCBA build outputs as ready stock when InvenTree marks `is_building = false`.
- Completed generic/mechanical outputs with no mandatory tests are ready immediately when their stock status is usable.
- Completed generic/mechanical outputs with mandatory tests still require passing results for every mandatory template.
- Incomplete outputs remain WIP and never become ready merely because a StockItem exists.
- Preserve PCBA Pass SW / staged WIP / rework behavior unchanged.

## 3.9.0
- Stock status alone no longer makes testable material Ready. A specific StockItem must pass every mandatory Part Test Template.
- Usable-status stock with missing mandatory test results is forecast through the required inspection/testing before becoming Ready.
- Optional/admin Test Templates remain excluded.
- Ready requirements are collapsed by default so Blocked / WIP / Forecast requirements remain prominent.
- Preserves validated PCBA WIP, rework, and Failed VI `-BARE` behavior from v3.7.1/v3.8.0.

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

## 3.6.0
- Added expandable activity-level rows to the Production Gantt for both single- and multi-build plans.
- Manufactured requirements now expose dated schedule segments for PCB fabrication/remake, incoming VI, PCBA assembly, Board VI, Press Fit, Bring-Up, EEPROM, Software Test, conformal coating, VI-POST-CC and SW-POST-CC when applicable.
- Added Expand All / Collapse All controls while keeping the default Gantt compact.
- Existing WIP begins at its proven production stage rather than displaying already-completed phases.
- Gantt remains a planning visualization only and does not allocate stock or reserve capacity.

## 3.7.0
- Completed Build Outputs at **Pass SW** now satisfy the selected board Build Order quantity before any future production is forecast.
- Intermediate completed/incomplete Build Outputs remain WIP and are forecast from their current passed stage rather than restarted from assembly.
- Selected board BO output state is scoped to that BO, preventing unrelated finished warehouse stock from falsely completing the BO.
- Board test flow is now derived from the Part's Test Templates. VI, Press Fit, Bring-Up, EEPROM, and Software Test are included only when configured for that Part; legacy parts with no recognizable templates retain the full historical flow as a safe fallback.
- Gantt segments, remaining-test hours, readiness text, and board-specific timing overrides use the same Part-specific test flow.
- Fully satisfied board BOs display **READY / READY NOW** rather than a future forecast.
- No database migration required.


## 3.7.1
- Fixed intermediate Pass VI / Pass BU / EEPROM WIP so remaining core board tests are not accidentally omitted when a Part has a sparse Test Template set.
- Core assembled-board flow is VI -> Bring-Up -> EEPROM -> Software Test; Press Fit is included only when the Part explicitly has a Press Fit Test Template.
- Failed tests on assembled-board outputs now forecast 2 business days of rework (configurable), followed by the complete mandatory test flow restarting at VI.
- Failed VI on `-BARE` remains a replacement/remanufacture case and continues to use PO coverage or the PCB fabrication fallback.
- Added Rework to scenario-wide and board-specific planning-time overrides and to Gantt activity detail.
- No database migration required.

## v3.9.0
- Split manufactured-subassembly timing into PCBA assembly (10 business days default) and generic/mechanical assembly (20 business days default).
- Added scenario-wide and Part-specific Generic / mechanical assembly timing overrides.
- Manufactured Parts now schedule only mandatory Part Test Templates; optional/admin templates do not create forecast work.
- Parts with no mandatory tests receive no board-test phases or test time.
- Preserved assembled-PCBA failure handling: 2 business days rework, then restart all mandatory tests from VI.
- Preserved Failed VI `-BARE` replacement/remanufacture behavior.
- Mechanical `*-MECH` Build Orders are planned as manufactured outputs rather than final-product assembly.

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

## v3.6.0 expandable Gantt regression
1. Calculate BO-0182 and generate its Gantt. Confirm each manufactured requirement with a forecast path has an expand arrow.
2. Expand TR8DC. Confirm the detailed rows include the 28-calendar-day TR8D-BARE fabrication/remake fallback, incoming VI, PCBA assembly, Board VI, Press Fit, Bring-Up, EEPROM, Software Test, conformal coating, VI-POST-CC and SW-POST-CC, with dates consistent with the Production Plan.
3. Expand a requirement supplied from existing WIP. Confirm the chart starts at the remaining stage and does not invent completed fabrication/assembly/test phases.
4. Confirm Expand All reveals all available activity rows and Collapse All returns to the compact view.
5. Run a multi-build plan and generate the Gantt. Confirm all selected BOs remain on one chart and their expandable activity rows reflect the same priority-aware simulation.
6. Confirm Generate/Hide Gantt and plan recalculation still work and no InvenTree allocations or Build Orders are changed.


## v3.6.0 adjustable timing tests
1. Calculate BO-0182 with no overrides and confirm the forecast matches the v3.5 baseline.
2. Open Adjust Planning Times, change the plan-wide PCBA assembly duration, recalculate, and confirm affected readiness dates and Gantt bars move.
3. Set a TR8R-specific Software Test override and confirm TR8R/TR8RC uses it while TR8D/TR8DC remains on the plan-wide/default value.
4. Change a board-specific PCBA assembly duration and confirm it takes precedence over the plan-wide PCBA assembly value.
5. Reset Overrides and confirm the original configured-default forecast returns.
6. Repeat in multi-build planning and confirm the same board override applies wherever that board is used across selected BOs.
7. Confirm no stock allocations, BO data, or persistent plugin settings are changed.


## v3.6.1 board-specific timing editor UI
1. Open Adjust Planning Times and confirm **This plan — all boards** is immediately visible.
2. Confirm each board-specific section is collapsed by default.
3. Expand one board, enter one or more overrides, collapse it, and confirm the values persist and the row shows the override count.
4. Re-open the board and confirm the entered values remain.
5. Recalculate and confirm the timing override still affects only the intended board.
6. Reset Overrides and confirm counts/values clear.


## v3.6.2 collapsed board timing regression

1. Open a Production Plan and click **Adjust Planning Times**.
2. Confirm **This plan — all boards** remains fully visible.
3. Confirm every board-specific row is collapsed by default.
4. Expand one board and confirm only that board table opens.
5. Enter an override, collapse the board, reopen it, and confirm the value remains.
6. Recalculate and confirm the override changes the forecast while unrelated boards retain their timings.
7. Refresh the page after installing v3.6.2 and confirm the collapsed UI is present without clearing the browser cache.

## v3.7.0 acceptance tests

### BO-0131 — all outputs finished
- Build quantity: 110 TR8L.
- Precondition: all 110 BO outputs are current status `Pass SW`.
- Expected: Need 110, Ready 110, WIP 0, Status READY, Forecast Product Ready `READY NOW`.
- Expected: no future PCBA assembly or board-test Gantt work is generated for the satisfied quantity.

### BO-0136 — completed-output classification
- Inspect the 40 FR2TS completed outputs and compare their current stock statuses with Production Planning.
- Expected: Pass SW outputs count Ready; intermediate statuses count WIP at their actual stage; failed/rework/quarantine outputs do not count Ready.
- This remains an explicit regression test before production deployment.

### TR8L — Part-specific stages
- Test Templates include Visual Inspection, Bring Up, EEPROM Flashed, and Software Test, with no Press Fit test.
- Expected: TR8L forecast/Gantt/timing overrides omit Press Fit.
- Pass VI TR8L WIP should forecast Bring-Up -> EEPROM -> Software Test only.
- Pass BU TR8L WIP should forecast EEPROM -> Software Test only.
- Pass SW TR8L should require no further test time.

### Mixed-stage quantity test
Create or identify a board BO with quantities distributed across Pass SW, Pass BU, Pass VI, and untested assembled output.
- Pass SW quantity is Ready.
- Pass BU quantity receives only later configured stages.
- Pass VI quantity receives only later configured stages.
- Untested assembled output receives all configured board-test stages.
- Total forecast demand must not exceed the BO quantity.


## v3.7.1 acceptance tests

### BO-0133 — mixed Ready / WIP / failed assembled board
- Build quantity: 22 TR8R.
- Precondition: 20 outputs Pass SW, 1 output Pass VI, 1 output Failed BU.
- Expected Ready: 20.
- Expected Pass VI WIP: 1; it skips VI and receives remaining mandatory tests (Bring-Up, EEPROM, Software Test, plus Press Fit only if TR8R has a Press Fit Test Template).
- Expected Failed BU: 1; it does NOT repeat materials or PCBA assembly. It receives 2 business days Rework, then restarts mandatory testing at VI and continues through every mandatory stage.
- Gantt should show the Pass VI WIP path and a separate Rework -> full retest path.
- Forecast quantity must total exactly 22 boards.

### Failed `-BARE` regression
- A `-BARE` stock item at Failed VI must NOT use assembled-board rework.
- It remains unusable and requires replacement/remanufacture via credible PO coverage or the configured PCB fabrication fallback, followed by incoming VI.

### Press Fit applicability regression
- TR8L (no Press Fit template) must omit Press Fit from forecast, Gantt and board-specific timing stages.
- A board with a Press Fit Test Template must include Press Fit.

## v3.9.0 acceptance cases

### BO-0177 / generic and mechanical assemblies
- PVFAN-40mmx28mm-4P-26CFM-65cm-NIL-1-PV has no mandatory test templates: forecast must show Generic / mechanical assembly only, with no VI / Press Fit / BU / EEPROM / SW.
- Default generic/mechanical assembly duration is 20 business days.
- Override the fan to 5 business days in Adjust Planning Times and confirm only that Part's forecast moves.
- For a mechanical Part with mandatory VI only, forecast assembly + VI only. Optional `Failed VI Admin` must not add time.
- Expand the Gantt and confirm BOM blockers remain visible for manufactured subassemblies.

### Board regression
- BO-0136 remains stage-aware.
- BO-0133 remains 20 Pass SW ready + 1 Pass VI continuing remaining mandatory tests + 1 Failed BU using 2 business days rework then full mandatory retest from VI.
- Failed VI `-BARE` still uses replacement/remanufacture, not assembled-board rework.


## v3.9.0 stock-item test readiness
- BO-0177 / CHAS-TR3-RUG-PV: 10 units with usable `OK` status, mandatory VI template, and no VI result must be **0 Ready / 10 awaiting test**, with VI time forecast.
- After all 10 specific StockItems have passing VI results, the requirement must become **10 Ready / Now**.
- A Part with no mandatory Test Templates remains Ready from usable stock status alone.
- Optional/admin templates (for example `Failed VI Admin`) must not block readiness or add time.
- Mixed stock test state must be quantity-aware (e.g. 10 passed + 5 untested for Need 15 => 10 Ready + 5 inspection WIP).
- Recheck BO-0133 and BO-0136 to confirm assembled-board stage and rework behavior is unchanged.
- Production Requirements must show actionable rows first and place fully Ready rows under the collapsed `Ready Requirements` section.


## v3.9.1 completed generic-output stock
1. BO-0177 / PVFAN-40mmx28mm-4P-26CFM-65cm-NIL-1-PV: with at least 20 completed usable outputs and no mandatory tests, Need 20 must report Ready 20, WIP 0, READY; no generic assembly forecast.
2. Create/locate an incomplete output for the same generic Part: it must remain WIP and must not become Ready merely because its StockItem exists.
3. CHAS-TR3-RUG-PV: completed/usable stock with mandatory VI but no VI pass must remain pending inspection; after VI passes it becomes Ready.
4. Recheck BO-0133 and BO-0136 to confirm PCBA Pass SW, staged WIP and rework behavior is unchanged.


## v3.9.3 qualified mandatory-test regression
- BO-0136 / FR2TS: 39 Pass BU WIP must not report `0h remaining test` when a later mandatory Software Test exists.
- Confirm the 39 Pass BU units receive all mandatory stages after BU (Software Test, and EEPROM if configured after BU for FR2TS).
- Confirm the failed/rework unit receives 2 business days rework followed by the complete mandatory FR2TS test sequence from VI.
- Confirm qualified names such as `Bring Up Stage 1` map to Bring-Up.
- Re-run BO-0133 and BO-0177 to confirm board rework and generic/mechanical stock readiness remain unchanged.


## v3.9.4 Variant / inherited mandatory-test regression

1. Open BO-0136 / FR2TS. FR2TS has no direct Test Templates and is a variant of Tate BBTX PCBA. Confirm Production Planning inherits the parent mandatory workflow.
2. Confirm the effective ordered workflow includes Visual Inspection, Bring Up Stage 1, EEPROM Programmed, Bring Up Stage 2, TX Waveform Testing, and Software Test. Rework must not appear as a normal mandatory stage.
3. For the 39 FR2TS StockItems which have passed through Bring Up Stage 2 / EEPROM but have no TX Waveform Testing or Software Test result, confirm the planner schedules 0.25 h TX Waveform + 2.0 h Software Test per board (2.25 h/board remaining).
4. Confirm any failed assembled FR2TS board follows 2 business days rework and then restarts the complete mandatory test sequence; PCBA assembly is not repeated.
5. Regression-test BO-0133: Pass VI WIP continues through only its remaining mandatory tests and failed assembled-board WIP uses rework + full retest.
6. Regression-test BO-0177: fan finished stock with no mandatory tests remains Ready; CHAS-TR3-RUG-PV stock with mandatory VI but no pass remains inspection/test WIP.
7. Confirm board-specific/scenario timing controls include TX Waveform Testing at 0.25 h/board by default.

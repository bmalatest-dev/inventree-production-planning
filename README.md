# InvenTree Production Planning v0.1.0

A deliberately lightweight V1 production-planning plugin for Per Vices.

For a top-level Build Order it calculates direct BOM requirements as BOM quantity × BO quantity, compares them with usable stock, finds active child BOs for shortages, reads current board stock statuses, finds `-BARE` requirements and their open PO dates, and forecasts when the finished product can be ready.

## V1 flow

`-BARE PO/stock -> PCBA -> VI -> BU -> SW -> conformal coating -> board ready -> final assembly -> final test`

Pass Press Fit and EEPROM Pass are recognized as intermediate progress states. Later pass states count cumulatively toward earlier stages.

## Settings

PCBA, VI, BU, SW, conformal coating, final assembly and final test are configurable in business days.

## Intentional V1 limitations

- Monday-Friday only; statutory holidays are not modeled yet.
- No technician / assembly-house capacity model yet.
- Batch-oriented forecast rather than unit-by-unit resource scheduling.
- Top-level requirements are shown; shortages are followed into child BOs and `-BARE` PO timing.
- Optional BOM items are ignored.
- Panel calculation is asynchronous so it does not block InvenTree's shared plugin-panel load.

## PO target-date convention

- PO Target Date is the current baseline.
- Blank line Target Date inherits the PO Target Date.
- Populated line Target Date is the current line-specific supplier ETA.
- The line Target Date can be revised repeatedly as the supplier forecast changes.
- Production Planning always uses the current effective expected receipt date.
- Supplier lateness is measured in calendar days; manufacturing durations are business days.

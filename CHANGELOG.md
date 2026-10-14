# Changelog

## 0.2.1
- Optional BOM items now accept a total quantity per Build Order (0 to BOM maximum) instead of a checkbox.
- Recursive material analysis now hides satisfied components and reports only true leaf-level blockers.
- Intermediate subassemblies with their own BOM are drilled into rather than reported as material blockers.
- Top-level requirements remain visible, while detailed forecast basis shows only constraints which actually prevent progress.
- Retains V2 WIP, inspection, PO-date and production-time assumptions.

## 0.2.0
- BO-created incomplete output StockItems no longer count as available simply because they exist.
- Pass SW is the board-ready state.
- Added recursive board BOM material-blocker forecasting for unstaged/incomplete outputs.
- Incoming material inspection is included before assembly can start.
- Defaults: 10 business days assembly after inspected material is ready; -BARE VI 1h/item; -MECH VI 0.2h/item; assembled-board VI 1.5h; Press Fit 0.5h; BU 1h; EEPROM 0.25h; SW 2h; final assembly 4h/unit.
- 8 working hours = one business day; weekends skipped.
- Added selectable top-level optional BOM requirements, remembered per BO in the browser.
- Preserved PO line target date -> PO header target date fallback.

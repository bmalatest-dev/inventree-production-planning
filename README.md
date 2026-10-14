# InvenTree Production Planning

Production Planning V2 forecasts Build Order material readiness and completion from finished stock, BO-created WIP outputs, BOM material availability, open PO dates, incoming inspection, assembly lead time, and remaining board test stages.

## V2 planning rules

- A BO-created incomplete output never counts as available merely because the StockItem exists.
- A board becomes ready for a parent BO at **Pass SW**.
- WIP at Pass VI / Pass Press Fit / Pass BU / EEPROM Pass is forecast from its remaining operations.
- An unstaged incomplete output causes the planner to inspect the next BOM layer for blockers rather than assuming assembly is complete.
- Incoming shortages must be received and complete required incoming VI before the 10-business-day assembly lead time starts.
- `-BARE`: 1.0 hour incoming VI per incoming stock item.
- `-MECH`: 0.2 hour incoming VI per applicable incoming stock item.
- Assembled board: VI 1.5h, Press Fit 0.5h, BU 1h, EEPROM 0.25h, SW 2h per board.
- Final assembly: 4h per finished top-level unit.
- 8 working hours = one business day; weekends are skipped.
- PO expected date = line target date when set, otherwise PO header target date.
- Optional top-level BOM items can be selected in the panel and are remembered per BO in that browser.

All defaults are plugin settings and can be adjusted later as measured production data improves.

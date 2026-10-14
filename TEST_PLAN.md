# V2 Test Plan

1. Open a BO whose required board has BO-created incomplete outputs with no passed stage. Confirm those outputs do **not** appear as Available.
2. Confirm a Pass SW output **does** count as Available.
3. For a board at Pass BU, confirm the forecast includes EEPROM + SW only.
4. For an unstaged board shortage, confirm the forecast shows the board BOM material blockers.
5. For a `-BARE` shortage covered by a PO, confirm effective PO date uses line target when present, otherwise PO header target.
6. Confirm 8 incoming `-BARE` stock items add 8h VI and move assembly start to the next business day.
7. Confirm assembly adds 10 business days only after all required material is received and inspected.
8. Confirm board test defaults are VI 1.5h, Press Fit 0.5h, BU 1h, EEPROM 0.25h, SW 2h per board.
9. Confirm final assembly adds 4h per top-level unit.
10. Select an optional BOM item, confirm it appears as a requirement and remains selected after refresh in the same browser.

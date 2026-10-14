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


## V2.1 acceptance checks
- For CYAN optional radio boards, set different total quantities (for example Rx 4, Tx 4, LO 8) and confirm Need matches those totals.
- Set an optional quantity to 0 and confirm it is excluded.
- For TR8D, confirm satisfied BOM components are hidden from Forecast basis.
- If TR8D-BARE is the only true leaf shortage, confirm it is the only material blocker displayed.
- Confirm intermediate assembly parts are recursively expanded rather than shown as blockers when their own BOM can identify the actual shortage.

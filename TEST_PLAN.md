# V0.1.0 test plan

Use a known top-level Production BO such as Crimson TNG RTM15.

1. Install and activate Production Planning.
2. Open the top-level BO and select **Production Plan**.
3. Confirm requirements equal BOM × BO quantity (e.g. VR16R, VR16T, VR16D, VR16M, VR16P, VR16-MECH).
4. Confirm requirements covered by usable stock show READY.
5. For a short board, confirm the expected child BO(s) are shown.
6. Confirm the child BO's `-BARE` part is found.
7. Confirm open PO quantity and dates agree with Build Blockers.
8. Confirm Pass VI / Pass BU / Pass SW quantities agree with Quality Report.
9. Confirm the critical requirement and forecast dates are sensible.
10. Hard-refresh several times and confirm existing BO plugin panels still load.

If it errors, capture the panel error and server log lines for `/plugin/production-planning/build/<id>/`.

## PO target-date tests

- With no `-BARE` line target date, confirm the PO header target date is used.
- Add a later line target date and confirm the downstream forecast moves.
- Change the line target date again and confirm the newest ETA is used.
- Clear the line target date and confirm it falls back to the PO target date.
- Where multiple PO lines are required, confirm full coverage uses the effective date of the line which completes the required quantity.

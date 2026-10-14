# Changelog

## 0.2.4

- Use `BuildLine.unallocated_quantity()` as the source of truth for existing child-BO material requirements.
- Capture native BuildLine required, allocated, consumed and unallocated quantities for traceability.
- Fully allocated / consumed child-BO lines are no longer rediscovered as material blockers.
- Retain unallocated-stock and PO analysis only for the true uncovered remainder.
- Retain V2.3 clickable parts and `* Assembly` costing-line exclusion.

# Changelog

## 0.2.3

- Make displayed production requirement parts, optional parts, and material blockers clickable links to their InvenTree Part pages.
- Treat any BOM part whose IPN or name ends with ` Assembly` as a costing-only assembly line. These remain in the BOM for costing but are excluded from material availability, PO coverage, and blocker calculations.
- Make existing child-build material analysis allocation-aware. BuildItem quantities already committed to the relevant child BOs are credited before calculating remaining material requirements.
- Evaluate only the remaining uncovered quantity against unallocated usable stock, preventing already-allocated stock from being reported again as a new blocker.
- Preserve the V2.2 readiness, PO ETA, inspection, assembly and test forecasting model.

## 0.2.2

- Added actionable named blocker details, PO ETA visibility, WIP and readiness-path reporting.

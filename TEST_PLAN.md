# v3.9.8 focused regression

## BO-0133 — TR8R
- Effective mandatory workflow must be ordered: Visual Inspection → Bring Up → EEPROM → Software Test.
- Current database evidence: 21 outputs have all four mandatory tests passed; TR8R-1V has VI pass + Bring Up fail.
- Expected summary: Need 22 | Ready 21 | WIP 1.
- Failed board path: 2 business days Rework → VI → Bring Up → EEPROM → Software Test.
- No PCBA assembly for either existing ready stock or the failed assembled board.

## BO-0136 — FR2TS
- Preserve inherited parent workflow and distinct Bring Up Stage 1 / Bring Up Stage 2 tests.
- Preserve TX Waveform Testing at 0.25 h/board and Software Test timing.
- Existing assembled WIP must continue from actual passed-test state; no repeat PCBA assembly.

## BO-0177 — generic/mechanical regression
- Finished usable manufactured stock with no mandatory tests remains Ready.
- Mandatory-test mechanical stock (e.g. chassis VI) remains WIP until required tests pass.

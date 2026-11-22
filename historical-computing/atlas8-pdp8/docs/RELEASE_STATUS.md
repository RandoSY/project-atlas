
## v0.6.0 - Clocked virtual paper tape

- Three rate modes (10, 300, unrestricted), clocked byte delivery through emulated device-01 reader IOTs.
- Pause/resume and rewind without skipped frames; pending read preserved. Tape state reports nominal and measured effective rate.
- Synthetic RIM tape fixture loaded by native 17-word DEC loader. Browser keeps the tape screen visible while reading and shows position/progress.
- Corrected earlier undefined browser `poll()` call when starting the tape.
- Windows Pico installer now includes mandatory `bootstrap.py`.
- **52 CPython tests pass**, including eight new reader-clock and native-loader tests. Physical Pico untested; FOCAL/OS8 not validated.

# ATLAS-8 0.5.3 historical panel release

- Functional PDP-8/I-inspired browser front panel, default dashboard view; original calculator remains a separate tab.
- Real backend command behavior for LOAD ADD, incremental DEP/EXAM, START versus CONT, and single instruction stepping.
- Five-word switch-programming demonstration from video and new `FRONT_PANEL_LESSON.md`.
- Pikuma architecture article, Hackaday demonstration, PDP8Online and DEC manual cited as explanatory sources.
- No page-level scroll at tested desktop viewports.
- 44 CPython tests validate native PDP-8 program execution, LINK rollover, panel state, and host behavior; independent headless-Chromium smoke tests validate the calculator, Teletype, historical panel and desktop no-scroll layout in SIM mode.
- Pico USB remains not hardware-validated; original FOCAL/OS8 and machine-cycle timing not validated.

# ATLAS-8 v0.5.2 — Release status

**Checkpoint:** 2026-11-22

This directory contains the complete v0.5 educational PDP-8 emulator source, tabbed browser dashboard, two transport implementations, tests, Windows launcher, and operator/programmer manual.

## Verified
- `python -m unittest discover -s tests -v`: **26 tests passing** on CPython.
- Prior browser smoke tests exercised calculator 7+6, 7×6, Teletype `HELLO PDP-8`, and a desktop no-scroll layout.
- The dedicated PC may run simulation mode without a Pico.

## Not yet verified
- Physical RP2040 MicroPython serial operation and long-duration reliability.
- Historical software compatibility (FOCAL-69, OS/8, DEC tape images).
- PDP-12 LINC mode, AGC, MSP430 scientific I/O.

## How to run
- Windows: double click `START_DASHBOARD_WINDOWS.bat`.
- Other systems: `python pc_dashboard_server.py --mode sim --open`.
- Browser: `http://127.0.0.1:8878/` with Python 3.
- Before Pico use, follow `docs/DASHBOARD_PROTOCOL.md` for exact firmware file list.

The PDF in the root folder documents the observed release; the machine compatibility claims above are intentionally limited.

## v0.5.2 localhost port collision fix

- ATLAS-8 defaults to dedicated port **8878**, not 8765 (Active Independence).
- When the default port is occupied, automatic fallback selects 8879–8898.
- The browser is opened only after validating the ATLAS-8 identity endpoint.
- An explicit `--http-port` remains strict and fails instead of opening a foreign application.

## v0.5.2 Pico installer and two-mode clarification

- The full CPython suite now passes **35 tests**, including 5 installation/documentation consistency checks.

- `INSTALL_PICO_WINDOWS.bat` + `INSTALL_PICO.ps1` deploy dashboard mode by default and support optional monitor mode.
- Pico existing files are backed up to PC before upload; upload integrity is checked by readback SHA-256; entry `main.py` is copied last.
- `main_dashboard.py` is the dashboard source that is **renamed to `main.py` on Pico**. Repository `main.py` is **only for standalone text monitor**. The earlier INSTALL guide referred to standalone installation and is corrected.
- `docs/PICO_DEPLOYMENT.md`, `docs/INSTALL.md`, `docs/OPERATOR.md`, README and the manual now state the distinction prominently.
- Script execution on actual RP2040 remains unverified. This update should not be interpreted as successful hardware deployment.

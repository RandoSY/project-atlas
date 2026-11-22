# ATLAS-8 v0.5 — Release status

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
- Browser: `http://127.0.0.1:8765/` with Python 3.
- Before Pico use, follow `docs/DASHBOARD_PROTOCOL.md` for exact firmware file list.

The PDF in the root folder documents the observed release; the machine compatibility claims above are intentionally limited.

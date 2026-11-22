# ATLAS-8 v0.5.1 — Release status

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

## v0.5.1 localhost port collision fix

- ATLAS-8 defaults to dedicated port **8878**, not 8765 (Active Independence).
- When the default port is occupied, automatic fallback selects 8879–8898.
- The browser is opened only after validating the ATLAS-8 identity endpoint.
- An explicit `--http-port` remains strict and fails instead of opening a foreign application.

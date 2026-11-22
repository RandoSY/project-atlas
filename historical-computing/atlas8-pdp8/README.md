![ATLAS-8 logo](assets/atlas8-brand.svg)

# ATLAS-8 — PDP-8 Dashboard & MicroPython Emulator

**Project Atlas · Historical Computing · v0.5 (development release)**

ATLAS-8 reconstructs a 12-bit Digital Equipment Corporation PDP-8 as an educational, inspectable software-defined laboratory. The RP2040 runs the MicroPython CPU core; the dedicated PC supplies a Chrome/JavaScript operator's console.

## Start here

1. For the **complete tabbed dashboard**, use the ATLAS-8 v0.5 ZIP bundle provided in the originating ChatGPT conversation; not every runtime file has been committed to GitHub yet.
2. Install Python 3 on a Windows PC.
3. Run `START_DASHBOARD_WINDOWS.bat` and open `http://127.0.0.1:8765/` in Chrome.
4. Select **SIMULATE** for PC-hosted exercises or **LIVE PICO** when an RP2040 is connected through USB serial.
5. Begin with **Calculator** and examine genuine PDP-8 octal instructions and register changes.

**Dashboard design:** Five viewport-fitted, no-scroll tabs — Calculator · Front Panel · Programs · Teletype · Guide.

## System architecture

```text
Chrome/JavaScript dashboard (dedicated PC)
           |
           +-- PC simulation transport --> PDP-8 Python core (desktop)
           |
           +-- USB serial transport -----> RP2040 running MicroPython
                                            PDP-8 CPU, memory, IOT
                                                    |
                                             future MSP430 laboratory I/O
```

The programmable calculator runs authentic PDP-8 instruction sequences, including addition, subtraction, and multiplication by repeated addition. A Teletype exercise emits `HELLO PDP-8`.

## Intended repository layout

- `dashboard/` — Browser console (HTML, CSS, JS)
- `pdp8.py` — 12-bit CPU implementation
- `dashboard_bridge.py`, `pc_dashboard_server.py` — Communications and host
- `monitor.py`, `tape.py`, `programs.py` — Monitor, loading and examples
- `tests/` — CPU and dashboard tests
- `docs/` — Installation, operation, protocol and compatibility documentation
- `ATLAS8_Operators_and_Programmers_Manual_v0.5.pdf` — Complete manual
- `assets/` — ATLAS-8 identity and dashboard preview

## What has been verified

- Initial desktop software checks: **26 tests passing**.
- Browser smoke exercises: 7+6 = 13; 7×6 = 42; Teletype prints HELLO PDP-8.
- Desktop no-scroll tab interface tested.

**Not verified:** Physical Pico USB serial operation, original FOCAL-69, OS/8 booting, or a complete PDP-12/LINC implementation. The first release is a teaching and development emulator, not a claim of full historical device coverage.

## Educational sequence

**Experience before equation · Need before technology · History before abstraction**

Start with the PDP-8 as a programmable calculator; progress to machine language, the front panel, Teletype, historically native programs, and instrument I/O. ATLAS-8 is the historical-computing entry point for the broader SDL curriculum.

## Standalone calculator exercise (already in this repository)

With Python 3 and no hardware required:

```bash
python examples/quickstart.py
```

The example exercises machine-language addition, subtraction and repeated-addition multiplication and prints PDP-8 register state. Source: [pdp8.py](pdp8.py) · [programs.py](programs.py).

**Publication status:** The GitHub directory is a **partial staging checkout**, not yet a complete installable release. The verified full dashboard and PDF manual remain available as downloadable artifacts in the originating ChatGPT conversation. See [release status](docs/RELEASE_STATUS.md).

See the umbrella repository: https://github.com/RandoSY/project-atlas

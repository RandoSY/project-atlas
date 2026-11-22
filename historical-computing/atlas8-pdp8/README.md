![ATLAS-8 historical front-panel mark](assets/atlas8-brand.svg)

# ATLAS-8 — PDP-8 Dashboard and MicroPython Emulator

**Project Atlas | Historical Computing | v0.5.1 educational alpha — localhost port fix**

A working, inspectable PDP-8 educational emulator. Run it directly on a dedicated PC with a professional, five-tab Chrome dashboard, or select a Raspberry Pi Pico running the **same Python CPU core** under MicroPython. The computer being emulated is a DEC PDP-8-style 12-bit machine; the Raspberry Pi Pico is its modern physical host.

> **Compatibility warning:** 26 PC automated tests pass, and calculator/Teletype browser exercises were smoke-tested. Physical RP2040 USB serial, native FOCAL and OS/8 execution have **not yet been demonstrated**. This is a development/teaching release, not a certified complete PDP-8 implementation.

## Quick start — no hardware required

1. Clone or download this repository and open `historical-computing/atlas8-pdp8/`.
2. Install Python 3.
3. On Windows, run `START_DASHBOARD_WINDOWS.bat`. On macOS or Linux, run `python3 pc_dashboard_server.py --mode sim --open`.
4. If the browser does not open automatically, use the **exact URL printed in the server window** (normally **http://127.0.0.1:8878/**). Port 8765 is used by other Atlas tools. If 8878 is occupied, ATLAS-8 selects another available port automatically.
5. Begin in **Calculator**, run 7+6, 7−6, or 7×6, then single-step PDP-8 instructions while watching the accumulator (AC), link (L), and program counter (PC).

### Five tabs — no page scrolling

**Calculator | Front Panel | Programs | Teletype | Guide**

The header switches between **SIMULATE** (CPU executes in Python on your PC) and **LIVE PICO** (the same CPU code executes in MicroPython on RP2040, connected over USB serial). No second JavaScript CPU implementation is maintained.

## What is included

| Component | Path | Purpose |
|---|---|---|
| PDP-8 CPU | [`pdp8.py`](pdp8.py) | 12-bit registers, memory addressing, IOT and OPR instruction execution |
| Browser dashboard | [`dashboard/`](dashboard/) | Responsive fixed-viewport UI: lamps, switches, trace, Teletype and calculator |
| PC host | [`pc_dashboard_server.py`](pc_dashboard_server.py) | localhost HTTP API and optional USB-serial transport |
| Shared transport | [`dashboard_bridge.py`](dashboard_bridge.py) | Identical JSON-line operations for PC/Pico |
| Pico boot | [`main_dashboard.py`](main_dashboard.py) | Copy to Pico as `main.py` for live dashboard mode |
| Native programs | [`programs.py`](programs.py) | PDP-8 machine-code examples and arithmetic |
| Loader and monitor | [`tape.py`](tape.py), [`monitor.py`](monitor.py) | RIM/BIN experiments and octal operator shell |
| Test suite | [`tests/`](tests/) | 26 CPU, loader and dashboard-host tests; optional browser smoke |
| PDF manual | [`ATLAS8_Operators_and_Programmers_Manual_v0.5.1.pdf`](ATLAS8_Operators_and_Programmers_Manual_v0.5.1.pdf) | Operator, programmer, installation and troubleshooting guide |
| Documentation | [`docs/`](docs/) | Protocol, installation, operator procedures, compatibility and release status |

## Pico LIVE mode

1. Install a board-matched MicroPython UF2 on the Raspberry Pi Pico.
2. Copy `pdp8.py`, `programs.py`, `dashboard_bridge.py` and **`main_dashboard.py` renamed as `main.py`** to the Pico filesystem. Do not copy `main.py` from the stand-alone monitor for dashboard operation.
3. Close Thonny/mpremote serial REPLs, attach the Pico via USB, select **LIVE PICO** in the dashboard header, enter the port (e.g. `COM7`) and connect.
4. On the PC, install `pyserial` with `python -m pip install pyserial` if it is not already installed.

See [dashboard communication protocol](docs/DASHBOARD_PROTOCOL.md), [installation](docs/INSTALL.md), [operator walkthrough](docs/OPERATOR.md), and [limitations](docs/COMPATIBILITY.md).

## Tests

```bash
python -m unittest discover -s tests -v
```

The original v0.5 suite had 26 passing checks; v0.5.1 adds port-conflict and startup-identity regression tests. The optional `tests/browser_smoke.py` requires an appropriate browser automation setup and is not included in that unittest count. No physical Pico test result is claimed.

## Architecture

```text
Chrome / JavaScript frontend (no-scroll five-tab dashboard)
                  | localhost JSON HTTP
      pc_dashboard_server.py
                  |
            target selector
        /                    \
   SIMULATE                 LIVE PICO
   Python CPU             USB serial bridge
   on PC                  MicroPython RP2040
        \                    /
              pdp8.py
  12-bit instructions, memory, TTY IOT, core state
```

Hardware MSP430 I/O, LINC/PDP-12 mode and original FOCAL/OS/8 demonstrations are **future work**.

## Origin and educational goal

ATLAS-8 begins with a programmable calculator and leads to actual PDP-8 machine instructions, operating a historically inspired front panel, I/O and Teletype. It is the PDP-8 chapter of Project Atlas's history-first Software-Defined Laboratory curriculum.

**Experience before equation. Need before technology. History before abstraction.**

[Project Atlas root](https://github.com/RandoSY/project-atlas) · [Release status](docs/RELEASE_STATUS.md) · [Manual PDF](ATLAS8_Operators_and_Programmers_Manual_v0.5.1.pdf)

## License

New original code is MIT-licensed; see [`LICENSE`](LICENSE). Historical software media and external reference projects are not bundled and retain their original rights.

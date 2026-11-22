# ATLAS-8 v0.5 compatibility and verification matrix

## Terminology

- **Desktop simulation:** The dedicated PC hosts `pdp8.py` in CPython. Chrome renders the operator interface. This is *not* a second JavaScript CPU implementation.
- **Live Pico:** The same `pdp8.py` runs under MicroPython on the RP2040. `dashboard_bridge.py` communicates using newline-delimited JSON over USB CDC through the dedicated PC host.
- **Native PDP-8 program:** Its words are 12-bit historical PDP-8 opcodes executed by the emulated machine. Such a program is not native ARM code and is not a cross-compiled MicroPython application.

| Capability | Implemented | Verified in this environment | Limitations |
|---|---|---|---|
| 12-bit core memory, 4K to 32K | Yes | 4K and memory-field unit tests | 32K Pico memory consumption not hardware-tested |
| MRI: AND TAD ISZ DCA JMS JMP | Yes | Yes, CPython tests | PDP-8/E nuances may still need further validation |
| OPR group 1/2, limited group 3 | Yes | Yes, selected tests | EAE instructions deliberately unsupported |
| TTY keyboard and printer IOT | Yes | Yes, CPython and browser smoke tests | Not physical ASR-33 baud/timing behavior |
| Interrupts and memory extension | Partial | Selected unit tests | Not full production OS/8-level device and timing fidelity |
| Octal load and snapshots | Yes | Yes, selected tests | Browser loads 1–64 octal words per request |
| RIM/BIN tape image loading | Provisional | Synthetic fixture tests | No original DEC tape corpus compatibility confirmation |
| Calculator addition/subtraction/multiplication | Yes | Yes, desktop/browser tests | 12-bit wrapping, multiply loop restricted to B <= 256 by browser |
| Host tabbed no-scroll interface | Yes | Browser smoke at 1440x1000 and 390x844 | Individual data regions may paginate/clip; not all device/browser dimensions checked |
| PC SIM/LIVE selector | Yes | SIM restart and failure retention tests | Physical Pico serial still untested |
| Live physical RP2040 MicroPython | Implemented path | **No** | Flash, serial and runtime tests still needed |
| Original FOCAL/PAL/OS/8 | No verified compatibility | **No** | Require actual historic media, more IOTs and timing fidelity |
| LINC, PDP-12, AGC, MSP430 lab I/O | No | **No** | Future modules; not included in this PDP-8 alpha |

## Scope of the release

This is a testable **educational PDP-8 core and browser operator console**. No claim is made that OS/8 boots, that original FOCAL runs, or that all PDP-8 variants are emulated faithfully. An unknown IOT or EAE instruction triggers an explicit error rather than silently being ignored. The PC simulator should be treated as the principal test bench; the Pico is the intended authoritative embedded demonstration after hardware acceptance.

## Acceptance sequence for a physical Pico

1. Load matching MicroPython UF2 onto the Pico.
2. Copy `pdp8.py`, `programs.py`, `dashboard_bridge.py`, and `main_dashboard.py` renamed to `main.py` **last**.
3. Open a serial monitor and confirm that sending one JSON line with `{"id":1,"op":"hello","args":{}}` produces a JSON reply with matching ID.
4. Close that monitor before starting the dedicated PC dashboard in LIVE PICO mode.
5. In Chrome, load calculator 7+6; step to HLT; verify 13 decimal / 0015 octal.
6. Load 7x6, run to HLT; verify 42 decimal / 0052 octal.
7. Load HELLO and verify terminal text. Toggle switches and load address.
8. Disconnect/reconnect USB; verify safe error handling and recovery. Record firmware version, Pico model and USB port.

Known issue: `dashboard_bridge.py` uses standard REPL stdin/stdout as USB CDC transport. Firmware-specific REPL input behavior may interfere with JSON-line handling and will require bench validation. Some boards may benefit from a dedicated `USBDevice` CDC interface or a framed transport in a later release.

## v0.6.0 clocked paper tape

Device-01 high-speed reader IOTs (`RSF/RRB/RFC`) and the 17-word native RIM loader are exercised with a synthetic tape fixture. Reader wall-clock modes: **ASR-33 RATE = 10 cps**, **HIGH-SPEED = 300 cps**, **TURBO = no artificial delay**. The ASR-33 selection is timing only; the separate low-speed reader hardware/device is **not** emulated. Files up to 32 KiB can be transferred as raw eight-channel frames, with transport PLAY/PAUSE/REWIND and observed-rate telemetry. **Physical Pico operation, arbitrary archival RIM/BIN images and native FOCAL-69 remain unverified.**

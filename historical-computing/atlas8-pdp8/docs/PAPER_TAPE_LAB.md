# ATLAS-8 v0.6.0 - Virtual paper tape and reader speed lab

**Status:** CPython emulator and Chrome SIM tests; physical RP2040 not yet tested. This is an educational reconstruction of the DEC PDP-8/I **device 01 high-speed paper-tape reader**. It uses real PDP-8 guest IOT instructions, not a host shortcut that deposits program words into memory.

## Three speed modes

| Selection | Maximum nominal rate | Reader frame period | What is modeled |
| --- | ---: | ---: | --- |
| **ASR-33 RATE** | 10 characters/second | 100,000 microseconds | ASR-33 slow *mechanical timing applied to the device 01 reader*. **Not an emulation of the ASR-33 low-speed reader IOT/device**. |
| **HIGH-SPEED** | 300 characters/second | 3,334 microseconds | Approximate historical high-speed reader throughput, with PDP-8 device-01 handshake. |
| **TURBO** | Uncapped | No artificial waiting | Rapid loading, but still one guest IOT request per frame and reader flag. |

Rates are **upper bounds for the reader mechanism**. Observed throughput can be lower because the PC host drives the emulator in bounded instruction batches and because USB, browser, Python execution and OS scheduling impose overhead. The onscreen `observed cps` is calculated from actual frame delivery timestamps, not from a promised rate. In TURBO, the displayed observed rate is limited by the emulator's execution rate, not an emulated motor. Tape bytes are eight-channel hole patterns, not Teletype ASCII characters.

## Run the native RIM loader

1. Double-click **START_DASHBOARD_WINDOWS.bat** and select **Programs -> Paper tape**. The address should be `127.0.0.1:8878` unless that port is occupied.
2. Press **ENTER RIM LOADER** to place the 17 original PDP-8 words at octal `7756`–`7776`. This is a *console-deposit convenience*. For maximum authenticity, enter those words manually via the front-panel switches. This step is distinct from tape loading.
3. Press **USE TEST TAPE**. This mounts a synthetic eight-channel RIM tape with an address/data fixture at `0200`–`0203`. The direct memory loader is not used.
4. Select **ASR-33 RATE (10 cps)**, **HIGH-SPEED (300 cps)** or **TURBO**. Start with 10 cps for students, then switch to TURBO to compare behavior.
5. Press **START AT 7756**. Keep the Programs/Paper tape screen visible to observe tape position, frames delivered, reader flag, and observed rate. The actual PDP-8 native RIM loader executes `6014`, `6011`, `6016` to request, poll and read each tape frame.
6. **PAUSE READER** stops additional frame delivery without losing the pending request or already-read bytes. **PLAY READER** resumes; the next pending frame begins a fresh period. **REWIND** is available only while the CPU is stopped.
7. At end-of-tape, the original loader ordinarily **waits for another frame**; it does not automatically branch to the loaded program. Press **STOP** to halt the CPU. Use Programs -> Core memory and EXAMINE `0200` to confirm `7301 7001 7001 7402`.
8. To run the loaded example, set address `0200` on the front panel and press START. It increments AC to `0003` and halts.

For a real tape, click **MOUNT FILE** and choose a *raw binary frame image* (`.rim`, `.bin`, `.pt` or `.tape`, max **32 KiB**). This interface does not parse a PDF, OCR a scanned tape, convert an assembly listing or guarantee every archived tape format. **No historical FOCAL image is bundled**, and a successful RIM load does not prove FOCAL or OS/8 compatibility.

## Commands and correct boot entry

The dashboard calls `tape_begin`, `tape_chunk` (up to 192 integer bytes), `tape_end`, `tape_rewind`, `tape_status`, `tape_speed` with `speed` = `asr33`, `high`, or `turbo`, and `tape_transport` with `action` = `play` or `pause`. The optional `rim_fixture` mounts the four-word demonstration tape; `rim_install` deposits the native RIM loader only. `state.tape` includes `size`, `position`, `delivered`, `ready`, `pending`, `paused`, `speed`, `nominal_cps`, `effective_cps` and `eof`.

Pico dashboard installation **must include `bootstrap.py`** with `pdp8.py`, `programs.py`, `tape.py`, `monitor.py` and `dashboard_bridge.py`; then copy `main_dashboard.py` to the Pico **as `main.py` last**. The Windows Pico installer includes and verifies this dependency. **Never use the standalone text monitor `main.py` to start the Chrome LIVE PICO dashboard.**

## Limits and experiments

- Only **device 01** fast-reader IOT protocol is implemented. The ASR-33 speed selection does not implement ASR-33 low-speed reader electronics or its separate instructions.
- No analog motor inertia, acceleration, tape tension, physical paper holes, hardware timebase, or tape punch hardware is simulated.
- The emulator's CPU remains instruction-driven; 10 and 300 cps are wall-clock reader timing rather than an accurate PDP-8 CPU clock.
- Reader transport state is independent of CPU STOP; pressing CPU STOP interrupts instruction execution. Pause only stops frame delivery. A guest waiting for a byte stays in its polling loop.
- This v0.6 milestone **does not include a validated native FOCAL-69 execution**. That requires independent compatibility work and a legally sourced tape image.

**Teaching measurement:** Compare the total load times for the 64-frame fixture at 10 cps (~6.4 seconds nominal), at 300 cps (~0.21 seconds nominal), and TURBO. Record observed effective cps, identify the wait loop, explain the distinction between program-loader instructions and the mechanical reader speed. Real observed durations depend on host overhead and frame scheduling.

References: DEC PDP-8 Family Paper Tape System User's Guide (RIM-2 high-speed loader), original PDP-8/I documentation, [Pikuma PDP-8 overview](https://pikuma.com/blog/pdp-8-minicomputer), and [Hackaday front-panel tutorial](https://hackaday.com/2017/08/10/getting-started-with-blinking-lights-on-old-iron/).

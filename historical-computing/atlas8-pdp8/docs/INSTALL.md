# Installation and recovery — operator checklist

## Hardware

- Raspberry Pi Pico (RP2040), Pico W or compatible board capable of running MicroPython.
- USB data cable (a charge-only cable will not work).
- Windows, macOS or Linux computer with Python 3 and a USB serial-capable terminal or Thonny.
- No MSP430 required for this release; physical experimental I/O comes in a subsequent project phase.

## Firmware

1. Confirm the exact RP2040 board model.
2. Obtain the corresponding MicroPython UF2: <https://micropython.org/download/RPI_PICO/>.
3. With BOOTSEL held, connect the board to USB. Copy the UF2 to the firmware mass-storage drive.
4. Wait for the board to reset and enumerate as a serial device.
5. Install `mpremote` with `python -m pip install mpremote`.
6. Verify the serial REPL with `mpremote repl`; press `Ctrl-B` if needed to display the ordinary REPL banner.

## Copy files to the Pico

From the unzipped project directory, run:

```bash
mpremote fs cp pdp8.py :pdp8.py
mpremote fs cp tape.py :tape.py
mpremote fs cp programs.py :programs.py
mpremote fs cp monitor.py :monitor.py
mpremote fs cp main.py :main.py
```

Only the five root-level `.py` files belong on Pico for basic operation. `docs` and `tests` stay on the PC. Copy `main.py` last because it autoruns a command loop when the board resets.

## First boot

Open a serial terminal or use `mpremote repl`, restart the board, then:

```text
SDL Atlas PDP-8 / MicroPython RP2040 | Type help
pdp8> demo hello
pdp8> run 1000
HELLO PDP-8
pdp8> regs
```

Expected program halts at a `HLT` instruction. See OPERATOR.md for an annotated transcript.

## Optional 32K memory

Edit `main.py` before copying:

```python
from monitor import main
main(fields=8)
```

Each field is 4096 words; eight fields are 32768 12-bit words stored in 16-bit cells (~64KiB just for memory). Larger configurations should be tested on your actual firmware build because usable MicroPython heap depends on the firmware and other loaded modules. For first boot, use `fields=1`.

## Original tape file installation

For original historical tape images supplied separately:

```bash
mpremote fs cp focal.rim :focal.rim
```

Then in the operator console:

```text
pdp8> reset clear
pdp8> load rim focal.rim
pdp8> pc 0200
pdp8> run 20000
```

`0200` is **not universal**: use the original program's documented entry point. Unknown original programs may stop at an unsupported IOT, and native FOCAL is **not yet verified** on this emulator.

## Troubleshooting

| Symptom | Diagnosis / action |
|---|---|
| No `RPI-RP2` drive | Reconnect while pressing BOOTSEL; confirm data cable |
| No serial port after UF2 copy | Check model-specific UF2 and USB cable |
| `ImportError: no module named ...` | Confirm all root `.py` modules were copied before `main.py` |
| Starts monitor automatically while uploading | Press Ctrl-C or remove `main.py` temporarily |
| MemoryError | Use 4K (`fields=1`) and disable unnecessary apps |
| `unattached IOT` | Guest attempted peripheral not implemented; record opcode and software name |
| Program prints nothing | Verify TTY program uses 604x and is actually running; inspect `regs` |
| `BUDGET` | CPU is still running; issue `run` again or single-step |
| Native program hangs in reader loop | Reader/punch IOTs aren't implemented yet; loading memory alone does not provide the runtime peripheral |
| Keyboard ignored during `live` | `select.poll()` may not function for your USB host/firmware combination; use `run` + `key` batch interaction |

## Recovery to MicroPython REPL

Press Ctrl-C. If the monitor restarts after a reset, remove its autorun file: `mpremote fs rm :main.py` after interrupting it. Alternatively use BOOTSEL to reflash firmware; **do not** reflash unless simpler recovery has failed.

## Uninstall

Remove `main.py` or delete the transferred `.py` modules from the Pico flash; the regular MicroPython firmware remains intact.

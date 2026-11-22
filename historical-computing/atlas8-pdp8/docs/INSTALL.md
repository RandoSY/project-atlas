# Installation and recovery — operator checklist

> **IMPORTANT — two different Pico `main.py` sources:** This guide previously described the **standalone monitor** installation only. For **Chrome LIVE PICO** the Pico must run the JSON dashboard bridge instead. Read [PICO_DEPLOYMENT.md](PICO_DEPLOYMENT.md) before copying anything.
>
> | Intended operation | Repository file | Pico boot filename | Interface |
> |---|---|---|---|
> | **Chrome LIVE PICO (recommended)** | **`main_dashboard.py`** | **`main.py`** | JSON-lines over USB for PC dashboard |
> | Standalone text monitor | `main.py` | `main.py` | Human-readable `pdp8>` serial terminal |
>
**Do not copy the repository's `main.py` for dashboard mode. Do not omit Pico `main.py` either.** Instead, **copy `main_dashboard.py` and rename it to `main.py` on the Pico.** The installer does this automatically. These are mutually exclusive startup modes, not two files that coexist on Pico as `main.py`.

**Recommended Windows installation:** Run `INSTALL_PICO_WINDOWS.bat` from the project root. It defaults to Dashboard mode, backs up existing Pico files, uploads the six required files, verifies each transfer byte-for-byte, and resets the Pico. For explicit port selection: `powershell -ExecutionPolicy Bypass -File .\INSTALL_PICO.ps1 -Port COM7`. See [PICO_DEPLOYMENT.md](PICO_DEPLOYMENT.md).


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

## Copy files to the Pico — choose one startup mode

### A. Chrome LIVE PICO (recommended)

Do **not** copy the repository `main.py` to the Pico. Copy **`main_dashboard.py` as `main.py`**. It launches the USB JSON bridge; the PC remains responsible for the tabbed browser interface.

With one connected Pico, the explicit commands are:

```text
py -3 -m pip install mpremote pyserial
py -3 -m mpremote fs cp pdp8.py :pdp8.py
py -3 -m mpremote fs cp programs.py :programs.py
py -3 -m mpremote fs cp tape.py :tape.py
py -3 -m mpremote fs cp monitor.py :monitor.py
py -3 -m mpremote fs cp dashboard_bridge.py :dashboard_bridge.py
py -3 -m mpremote fs cp main_dashboard.py :main.py
py -3 -m mpremote reset
```

The PowerShell installer is safer because it backs up old files and verifies the copies; use it unless you have a specific reason to copy manually.

### B. Standalone text monitor (optional)

Only in this mode, copy repository `main.py` as `:main.py`, which starts `monitor.main` and prints `pdp8>`. Use `INSTALL_PICO_WINDOWS.bat -Mode Monitor` to install this variant. **This is not compatible with the Chrome LIVE PICO protocol.** It remains available for instruction and serial-terminal demonstrations.

### First boot

After installing Dashboard mode, close any serial tools and open `START_DASHBOARD_WINDOWS.bat` on the PC. Use the exact URL printed (normally port 8878), select LIVE PICO, and connect to the Pico COM port. No `pdp8>` text prompt should appear in dashboard mode. The dashboard sends JSON requests.

After installing Monitor mode, enter the serial terminal and run:

```text
SDL Atlas PDP-8 / MicroPython RP2040 | Type help
pdp8> demo hello
pdp8> run 1000
HELLO PDP-8
pdp8> regs
```

**Do not attempt to open both programs on the serial port at once.**

## Optional 32K memory

For standalone Monitor mode, edit repository `main.py` before copying:

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

Press Ctrl-C. If the monitor restarts after a reset, remove its autorun file: `mpremote fs rm :main.py` after interrupting it. Then reinstall the correct boot mode with `INSTALL_PICO_WINDOWS.bat`. Alternatively use BOOTSEL to reflash firmware; **do not** reflash unless simpler recovery has failed.

## Uninstall

Remove `main.py` or delete the transferred `.py` modules from the Pico flash; the regular MicroPython firmware remains intact.

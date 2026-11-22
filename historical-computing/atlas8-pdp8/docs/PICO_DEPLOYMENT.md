# Deploy ATLAS-8 to RP2040 Pico — choose the correct `main.py`

**Read this before copying any files.** There are **two different entry-point sources** in the ATLAS-8 repository; on the Pico they both install under the **same filename**, `main.py`, because MicroPython executes `main.py` automatically after boot.

| Mode | File in GitHub checkout | File on Pico | What starts at boot |
|---|---|---|---|
| **Chrome dashboard / LIVE PICO (recommended)** | **`main_dashboard.py`** | **`:main.py`** | USB JSON-lines server (`dashboard_bridge.serve`) |
| Standalone serial command monitor | `main.py` | `:main.py` | Human-readable `pdp8>` monitor (`monitor.main`) |

**Do NOT copy repository `main.py` when using Chrome LIVE PICO.** Doing so starts the standalone monitor, whose text commands cannot speak the dashboard's JSON protocol. **Do copy `main_dashboard.py` as `:main.py`.** This does *not* mean the Pico should have no `main.py`—it means it needs the correct one for the selected mode.

## Quick start — dedicated PC + Chrome (recommended)

1. Flash the correct RP2040 MicroPython `.uf2` for your board. `RPI-RP2` is the **firmware-installation drive only**, not the place to copy these Python scripts. After flashing, the Pico appears as a **USB serial COM port**; MicroPython files are transferred with `mpremote`.
2. On your Windows PC, install Python 3. Run `py -3 -m pip install mpremote pyserial` once, if needed.
3. Close Thonny, any serial monitor, any `mpremote repl`, and disconnect the dashboard's existing LIVE PICO serial session. These compete for the same USB port.
4. In the full ATLAS-8 checkout, double-click **`INSTALL_PICO_WINDOWS.bat`**. This installs **Dashboard mode** by default. If several MicroPython devices are connected, use a terminal and run `powershell -ExecutionPolicy Bypass -File .\INSTALL_PICO.ps1 -Port COM7` (substitute the Pico's actual port).
5. The installer backs up any existing Pico files to `pico-backups/YYYYMMDD-HHMMSS` on your PC, uploads the dependencies first, **copies `main_dashboard.py` as `main.py` last**, and reads every copied file back to verify its SHA-256. It then requests a Pico reset.
6. Close the installer or any serial tools. Start `START_DASHBOARD_WINDOWS.bat` on your PC. Open the URL printed by that server (normally `http://127.0.0.1:8878/`). Select **LIVE PICO** and enter the Pico's COM port. The PC retains the browser UI; the Pico runs the PDP-8 engine.

The files uploaded by the dashboard installer are: `pdp8.py`, `programs.py`, `tape.py`, `monitor.py`, `dashboard_bridge.py`, and `main.py` (sourced from `main_dashboard.py`). The last two support different user interfaces; providing the inactive monitor module does not make it auto-run.

**Do not copy** `dashboard/`, `pc_dashboard_server.py`, PDF manuals, or `tests/` to the Pico. Those stay on the dedicated PC.

## Manual commands if you prefer not to run PowerShell

From the project root, with only one Pico connected:

```text
py -3 -m mpremote fs cp pdp8.py :pdp8.py
py -3 -m mpremote fs cp programs.py :programs.py
py -3 -m mpremote fs cp tape.py :tape.py
py -3 -m mpremote fs cp monitor.py :monitor.py
py -3 -m mpremote fs cp dashboard_bridge.py :dashboard_bridge.py
py -3 -m mpremote fs cp main_dashboard.py :main.py
py -3 -m mpremote reset
```

These are the explicit **dashboard-mode** commands. Unlike the installer, they do not back up files or verify hashes. Use `py -3 -m mpremote connect COM7 fs cp ...` when you must select a particular board.

## Standalone monitor instead of Chrome

Run `INSTALL_PICO_WINDOWS.bat -Mode Monitor -Port COM7` or:

```text
powershell -ExecutionPolicy Bypass -File .\INSTALL_PICO.ps1 -Mode Monitor -Port COM7
```

This differs only in which file becomes Pico's `main.py`: the repository's `main.py` starts `monitor.main` and prints a `pdp8>` prompt. **It will not respond to LIVE PICO dashboard commands.** Use a serial REPL/terminal instead of the dashboard for this mode.

## Verification, backups and recovery

- Installer `-WhatIf` lists the file plan and makes **no** Pico changes.
- `-Port COM7` selects a device when auto-discovery is ambiguous; port numbers vary by PC.
- `-BackupDirectory C:\some-folder` selects the backup location; `-SkipBackup` is available but not recommended.
- On a copy/verification failure, do not assume the Pico is ready; earlier files may have been replaced. Backups stay on the PC.
- For `ImportError` at boot, re-run the installer to ensure all modules are present and verified.
- For the wrong boot mode or a stuck program, stop the PC dashboard, connect a MicroPython REPL, press Ctrl-C, and use `mpremote fs rm :main.py` if necessary. Then re-run the installer in the intended mode. As a last resort, reflash firmware with BOOTSEL.
- If the Pico COM port is busy, close Thonny and any other serial application before using LIVE PICO.
- If you get the **Active Independence dashboard** instead of ATLAS-8, you are using the wrong **PC HTTP port**, a separate issue from the Pico `main.py`. ATLAS-8 normally uses 8878, never 8765.

**Validation status:** this deployment script has been reviewed and exercised via local static/dry-run checks; a real Pico hardware installation and original FOCAL/OS/8 compatibility remain unverified.

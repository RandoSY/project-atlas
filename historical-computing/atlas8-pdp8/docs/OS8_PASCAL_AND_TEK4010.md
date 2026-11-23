# ATLAS-8: OS/8 and Pascal-S compatibility track
**Engineering preview — 2026-11-23. No successful OS/8 boot claim.**

## Purpose
Extend the existing shared Python PDP-8 CPU so the PC-hosted ATLAS-8
can boot DEC OS/8 and execute historical Pascal-S. Preserve the same
CPU in CPython and RP2040 MicroPython. The Chrome dashboard remains a
terminal/front panel, not a second CPU.

## User-visible entry points
From this directory on Linux/macOS/Git Bash:

```bash
bash run-atlas8.sh pc
bash run-atlas8.sh os8 /path/to/working-copy.rk05
bash run-atlas8.sh pico /dev/ttyACM0
```

On Windows CMD/PowerShell the existing launcher is unchanged:
```
START_DASHBOARD_WINDOWS.bat
```

The `os8` command merely attaches the image to the experimental
RK8-E controller in the PC simulator. **It does not yet auto-boot OS/8.**
All run modes require Python 3 on the PC. Pico mode also requires
PySerial and flashed compatible MicroPython firmware.

## Implementation increment (experimental feature branch)
- `rk8e.py`: seekable RK05 images, low-memory 12-bit image representation,
  basic 6741–6747 RK8-E IOT dispatch and DMA-style transfers; read-only default.
- `pdp8.py`: optional disk IOT device and interrupt source.
- `dashboard_bridge.py`: optional disk state available to dashboard API.
- `pc_dashboard_server.py`: `--rk05` attach and optional `--rk05-write` (working copies only).
- `run-atlas8.sh`: one Bash command for PC, OS/8 experiment, or Pico.
- `tests/test_rk8e.py`: synthetic disk and IOT unit tests.
- `.github/workflows/atlas8-os8-experimental.yml`: planned CI regression suite.

### Testing and limitations
The simulator has **not** yet booted OS/8, mounted a verified historical RK05
distribution, compiled Pascal-S, or rendered `HILBER.PS`. The new disk
controller is synchronous and ignores real spindle seek/rotational timing.
Treat it as an unverified software increment, not a production RK8-E clone.
Pico disk support is not wired into the MicroPython boot/USB bridge.

### Historic two-word RK8-E bootstrap (DEC OS/8 Handbook, Table 1-8)
On a PDP-8 with drive 0, deposit:
- `0030: 6743` — DLAG: start disk block 0 read (AC=0)
- `0031: 5031` — spin until the disk DMA overwrites instruction 0031

Set AC=0, PC=0030, continue. We must later demonstrate that this
works against an actual OS/8 system image before enabling one-button boot.

## Acceptance gates
1. Existing 65-test v0.7 regression suite remains green; new RK8-E tests pass
   under both Python 3.11 and 3.13.
2. A synthetic RK05 fixture performs read/write/half-sector, memory-field,
   wraparound, write-protect, nonexistent drive and interrupt tests.
3. A known-good *historical* OS/8 RK05 disk image reaches the `.` prompt
   via the genuine two-word bootstrap in PC SIM mode; capture the execution trace.
4. OS/8 directory listing, file read/write on a disposable disk copy, and
   restarts work. Validate disk image layout against SIMH on the same media.
5. Pascal-S compiler loads and runs a sum program and recursive program.
6. Compare CPU and disk traces with SIMH for a reproducible acceptance log.
7. Only then investigate Pico MicroPython memory budget, performance and
   PC-hosted disk image proxy/storage model. No OS/8/Pascal claim for Pico
   before actual USB-hardware acceptance.

## Next phase — Hilbert and historic Tektronix terminal
Track in https://github.com/RandoSY/project-atlas/issues/1 .
The surviving Pascal Hilbert source outputs Tektronix 4010 vector protocol
through `TEK:` rather than using the DEC VC8-E device. Add a dedicated
browser graphics-terminal view that retains original control bytes,
interprets Tek 4010 coordinate sequences, and preserves storage-tube
semantics. Verify a vector-fixture trace, then the genuine `HILBER.PS`
program under Pascal-S. VC8-E emulation is an independent future option.

## Reference implementations and primary sources
- SIMH RK8-E source: https://github.com/simh/simh/blob/master/PDP8/pdp8_rk.c
- DEC OS/8 boot handbook: https://bitsavers.org/pdf/dec/pdp8/os8/OS8_Handbook_Apr1974.pdf
- PDP-8/e Pascal-S quickstart: https://www.bernhard-baehr.de/pdp8e/quickstart20.html
- RK8-E controller explanation: https://www.pdp8online.com/pdp8em/pdp8em.shtml

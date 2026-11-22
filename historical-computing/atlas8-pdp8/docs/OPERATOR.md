> **Mode selection:** This page documents the **standalone serial `pdp8>` monitor**. For the Chrome dashboard and LIVE PICO, install **`main_dashboard.py` onto the Pico as `main.py`**, not the repository `main.py`. Use `INSTALL_PICO_WINDOWS.bat` (default Dashboard) and read [PICO_DEPLOYMENT.md](PICO_DEPLOYMENT.md). The two modes cannot share the same `main.py` at boot.

# PDP-8 operator guide

## Conventions

The PDP-8 is a **12-bit octal machine**. `0200` means octal 200, or decimal 128. All *machine addresses and deposited instruction words* are octal, with no `0o` prefix. The `run`/`step` budget is a count of instructions, entered in decimal. Memory is organized in 4K-word fields and the default initial PC is zero.

The terminal is a virtual ASR-33-style Teletype interface over the Pico USB serial port. This alpha display implements only textual output, not mechanical delays or exact 1960s character transfer timing.

## Command reference

| Command | Action | Example |
|---|---|---|
| `help` | Complete built-in command help | `help` |
| `regs` | CPU registers and status | `regs` |
| `reset [clear]` | Reset registers (and erase memory if clear) | `reset clear` |
| `pc` | Set program counter, resume-ready | `pc 0200` |
| `if`, `df` | Change memory field | `df 1` |
| `sr` | Set 12-bit switches | `sr 3777` |
| `peek` | Examine one word | `peek 0200` |
| `poke` | Deposit one word | `poke 0200 7300` |
| `dump` | Show memory in IF | `dump 0200 16` |
| `demo` | Load an example | `demo hello` |
| `step` | Execute a few instructions | `step 1` |
| `run` | Execute up to a budget | `run 10000` |
| `live` | Run continuously with best-effort keyboard polling | `live` |
| `key` | Queue text plus carriage return for guest | `key HELLO` |
| `break` | Set a field-aware breakpoint | `break 0210` |
| `unbreak` | Remove all breakpoints | `unbreak` |
| `load` | Load original-machine bytes/words | `load rim /focal.rim` |
| `save` / `restore` | Save and restore memory | `save /work.p8core` |
| `quit` | Return to MicroPython | `quit` |

## Hello world in real PDP-8 words

```
Addr  Word  Meaning
0010  0277  auto-index pointer (first read goes to 0300)
0200  6040  TFL  mark TTY output ready (PDP-8/E convenience)
0201  7200  CLA  clear AC
0202  1410  TAD I 0010  fetch next ASCII character
0203  7440  SZA  skip if end-of-string zero
0204  5206  JMP 0206  send character
0205  7402  HLT  stop
0206  6041  TSF  skip if printer flag is ready
0207  5206  JMP 0206  wait
0210  6046  TLS  send ASCII character
0211  5201  JMP 0201  next character
0300  ....  'HELLO PDP-8' in octal ASCII, ending 0000
```

The byte stream displayed on the host is generated only by PDP-8 `TLS` instructions operating on characters loaded through `TAD`. It is not a Python `print('HELLO')` shortcut.

Use:

```text
pdp8> demo hello
pdp8> step 1
pdp8> regs
pdp8> run 1000
HELLO PDP-8
pdp8> regs
```

## Front panel — manual deposit and execute

Without using a demo:

```text
pdp8> reset clear
pdp8> poke 0200 7200
pdp8> poke 0201 7001
pdp8> poke 0202 7402
pdp8> pc 0200
pdp8> step 1
pdp8> regs
pdp8> run 100
pdp8> regs
```

At the end: `AC=0001`, `PC=0203`, the emulator is halted, and the only executed native guest instructions were `CLA`, `IAC`, and `HLT`.

## Native input from the terminal

The guest's keyboard is an 8-bit character buffer and a ready flag; KSF (`6031`) tests ready and KRB (`6036`) fetches the character. `key HELLO` queues those bytes and a terminating carriage return. While guest code is running, the monitor's `live` mode *attempts* to receive USB keyboard characters non-blockingly; this is firmware-dependent. For predictable testing, use batches (`run`), then queue `key`, then continue (`run`).

## Why this is native PDP-8 software

Original binary/word images are placed in the emulated core without translation. The CPU dispatches them by their PDP-8 opcode. The Pico executes only the MicroPython emulator, not the PDP-8 binary as RP2040 instructions. In historical terminology this is emulation, not a cross-compiled port.

## Inspecting a failed software load

When an IOT is unsupported, the CPU halts with an explicit message identifying its octal opcode and device number. Write down `PC`, `IR`, `AC`, `IF`, `DF`, and the loaded tape. Compare that instruction with a period DEC reference manual and SIMH before making changes. Avoid silently ignoring instructions because this makes programs appear to run when they do not.

# ATLAS-8 unified dashboard transport (ATLAS-PDP8/1)

## Architecture

Chrome `dashboard/app.js` -> local HTTP `pc_dashboard_server.py` -> one selected target:

- SIMULATE: in-process `dashboard_bridge.Bridge` + `pdp8.PDP8` running on the dedicated PC in CPython.
- LIVE PICO: JSON-line serial transport to MicroPython `dashboard_bridge.serve()` on an RP2040 Pico.

Both targets run the **same Python PDP-8 CPU source**. Chrome never executes the calculator arithmetic directly; it merely renders state, initiates commands, and formats values.

The server binds only to `127.0.0.1` and serves the known static dashboard files. No framework, internet access, scripting endpoint, or file uploads are needed. Use current local host security practices; this is still development software.

## Pico startup — required for this protocol

On the Pico, MicroPython runs `main.py` at boot. For Chrome LIVE PICO, the **source is `main_dashboard.py`, copied to Pico as `:main.py`**. The repo's own `main.py` boots a *different*, text-only monitor, so **do not install that one for the dashboard**. The recommended Windows installer `INSTALL_PICO_WINDOWS.bat` selects the correct entry point. [Full guide](PICO_DEPLOYMENT.md).

## Starting the server

```bash
python pc_dashboard_server.py --mode sim --open
python pc_dashboard_server.py --mode sim --port COM7 --open
python pc_dashboard_server.py --mode serial --port COM7 --open
python pc_dashboard_server.py --mode serial --port /dev/ttyACM0 --open
```

Without `--open`, navigate to the **actual URL printed by the server** (normally `http://127.0.0.1:8878/`) in Chrome. ATLAS-8 never defaults to port 8765, which is used by other Project Atlas applications. If the default port is occupied, the server chooses the next free port from 8879–8898. An explicit `--http-port NUMBER` is strict and fails clearly if occupied. When launching a browser, the host first verifies `/api/info` reports `app_id: ATLAS8-PDP8`; a foreign application is never opened as ATLAS-8. The topbar has `ENGINE: SIMULATE / LIVE PICO` and a Connect button. Selecting LIVE PICO requires a serial port name. Failed serial acquisition retains the previously active engine. Switching to either engine starts a *new, independent machine state*; programs are not transferred between engines. Do not have Thonny, mpremote, and the PC host open the same USB serial port concurrently.

## HTTP endpoints

- `GET /api/info` returns current mode, port, protocol and `app_id: ATLAS8-PDP8` host identity.
- `POST /api/mode` JSON: `{"mode":"sim"}` or `{"mode":"serial","port":"COM7"}`. The connection is established before the previous backend is retired. Switching mode deliberately resets the session state.
- `POST /api/command` sends `{"id":1,"op":"hello","args":{}}` and receives an object with corresponding `id`, `ok`, `state`, optional `data`, optional `tty`, or `error`.

The Pi/Pico bridge consumes one JSON object per line and emits one response per line. Request ID matching is mandatory. Do not send unbounded guest loops; `start` followed by repeated bounded `tick` calls allows the UI to remain responsive.

## Exposed commands

`hello`, `status`, `calculator`, `demo`, `reset`, `switches`, `panel_addr`, `pc`, `field`, `examine`, `deposit`, `load_words`, `keyboard`, `breakpoint`, `breakpoints_clear`, `step`, `start`, `resume`, `tick`, `halt`.

Important parameters:

| Operation | Arguments | Notes |
|---|---|---|
| `calculator` | `operation`, `a`, `b` | operation: `add`, `subtract`, or `multiply`; 12-bit unsigned inputs |
| `demo` | `name` | `hello`, `add`, `count`, `switchadd` |
| `switches` | `value` | Decimal JSON integer holding 12-bit switch word |
| `panel_addr` | `address`, `field` | Set panel cursor and PC; address integer 0..4095 |
| `examine` | `address`, `field`, `count` | 1..128 words returned |
| `deposit` | `address`, `field`, `value` | Write a 12-bit word |
| `load_words` | `origin`, `field`, `words` | 1..64 decimal JSON integers representing PDP-8 instruction words |
| `step` | `count` | 1..64 instructions per call; optional trace |
| `start` | optional `address` | Marks guest running; does not block |
| `tick` | `count` | 1..4096 instructions per call |
| `keyboard` | `text` | Up to 512 characters |
| `halt` | none | Stops guest execution |

**Numeric conventions:** Browser panels show octal. The JSON protocol sends numbers as ordinary decimal JSON integers. An octal machine word `7300` is sent in JSON as the integer **3776**, not the string `"7300"`; the JavaScript client converts user octal text to integer before sending.

## Running without browser

After starting a PC simulation server:

```bash
curl -s http://127.0.0.1:8878/api/info
curl -s -X POST http://127.0.0.1:8878/api/command \
  -H 'Content-Type: application/json' \
  -d '{"id":1,"op":"hello","args":{}}'
```

To switch modes:

```bash
curl -s -X POST http://127.0.0.1:8878/api/mode \
  -H 'Content-Type: application/json' \
  -d '{"mode":"sim"}'
```

Do not attempt a network connection directly to the Pico; this release communicates over USB CDC through the dedicated PC host.


## v0.5.3 PDP-8/I operator panel commands

All commands go to the same emulator core in SIMULATE or LIVE PICO; the host owns only transport and drawing.

| Operation | Arguments | Action |
|---|---|---|
| `panel_fields` | `ifield`, `dfield` | Set three-bit field selectors (rejects unavailable fields and changes while RUN) |
| `panel_addr` | `address`, optional `ifield`, `dfield` | LOAD ADD: select console address and fields without clearing accumulator or LINK |
| `deposit` | `panel:true`, optional `address`, `field`, `value` | DEP: deposit word, advance address counter and PC |
| `examine` | `panel:true`, optional `address`, `field`, `count:1` | EXAM: read memory into MB, advance address counter and PC |
| `panel_start` | `single_instruction: bool` | START: load PC from 12-bit switch register, clear AC and LINK, begin/run one native instruction |
| `panel_continue` | `single_instruction: bool` | CONT: resume from current PC with AC and LINK unchanged |

`state.panel_next_addr` is the next address for DEP/EXAM; `state.ma` is its mirror in this educational reconstruction. `state.mb` is the last examined/deposited word. `SING STEP` is intentionally disabled; PDP-8/I microcycles are not emulated. See [the operator programming lesson](FRONT_PANEL_LESSON.md) for the historical procedure.

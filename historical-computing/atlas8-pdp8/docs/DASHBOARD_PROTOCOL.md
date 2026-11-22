# ATLAS-8 unified dashboard transport (ATLAS-PDP8/1)

## Architecture

Chrome `dashboard/app.js` -> local HTTP `pc_dashboard_server.py` -> one selected target:

- SIMULATE: in-process `dashboard_bridge.Bridge` + `pdp8.PDP8` running on the dedicated PC in CPython.
- LIVE PICO: JSON-line serial transport to MicroPython `dashboard_bridge.serve()` on an RP2040 Pico.

Both targets run the **same Python PDP-8 CPU source**. Chrome never executes the calculator arithmetic directly; it merely renders state, initiates commands, and formats values.

The server binds only to `127.0.0.1` and serves the known static dashboard files. No framework, internet access, scripting endpoint, or file uploads are needed. Use current local host security practices; this is still development software.

## Starting the server

```bash
python pc_dashboard_server.py --mode sim --open
python pc_dashboard_server.py --mode sim --port COM7 --open
python pc_dashboard_server.py --mode serial --port COM7 --open
python pc_dashboard_server.py --mode serial --port /dev/ttyACM0 --open
```

Without `--open`, navigate to `http://127.0.0.1:8765/` in Chrome. The topbar has `ENGINE: SIMULATE / LIVE PICO` and a Connect button. Selecting LIVE PICO requires a serial port name. Failed serial acquisition retains the previously active engine. Switching to either engine starts a *new, independent machine state*; programs are not transferred between engines. Do not have Thonny, mpremote, and the PC host open the same USB serial port concurrently.

## HTTP endpoints

- `GET /api/info` returns current mode, port, protocol and host identity.
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
curl -s http://127.0.0.1:8765/api/info
curl -s -X POST http://127.0.0.1:8765/api/command \
  -H 'Content-Type: application/json' \
  -d '{"id":1,"op":"hello","args":{}}'
```

To switch modes:

```bash
curl -s -X POST http://127.0.0.1:8765/api/mode \
  -H 'Content-Type: application/json' \
  -d '{"mode":"sim"}'
```

Do not attempt a network connection directly to the Pico; this release communicates over USB CDC through the dedicated PC host.

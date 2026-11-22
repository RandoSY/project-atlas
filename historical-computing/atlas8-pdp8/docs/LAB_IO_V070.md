# ATLAS-8 v0.7 — Intelligent Laboratory I/O (engineering preview)

**Status:** CPython simulated PDP-8 guest and packet protocol tested. **MSP430 target compile, RP2040 physical connection and real measurements are not yet verified.** This version extends ATLAS-8; it does not claim that these IOTs existed on a DEC PDP-8/I.

## Purpose

Follow a measurement from a native 12-bit PDP-8 instruction through an emulated device controller, an RP2040 UART, and an autonomous MSP430G2553 peripheral. Preserve the PDP-8 instruction set and historical front-panel lessons, while adding one educational device number `54` (octal) in an ATLAS-specific namespace.

- PC SIMULATE mode instantiates a **clearly labeled synthetic controller** returning A0=512, A3=515 counts; timer fixture = 1000 ticks. No actual voltage or frequency is sampled.
- LIVE PICO mode uses RP2040 `machine.UART(0)` on GP0/GP1, hardware READY GP2. No fallback from missing hardware to synthetic measurements.
- The existing Chrome USB JSON transport is separate from the internal Pico-to-MSP430 binary UART; all legacy PDP-8 programs and paper tape continue through the same CPU.

## Native PDP-8 instructions

ATLAS-specific IOT words; device selector `54` (octal). Not original or universally unallocated DEC assignments.

| Octal word | Symbol | Semantics |
|---|---|---|
| 6540 | LABCLR | Clear device operation and status |
| 6541 | LABGO | Request ADC10 conversion; AC low 3 bits select channel |
| 6542 | LABRDY | Skip next guest instruction if completed measurement ready |
| 6543 | LABTIM | Start Timer_A measurement of two rising edges |
| 6544 | LABGET | OR low 12 bits of result into AC; clears READY |
| 6545 | LABSTS | OR status bitmask into AC (1 ready, 2 busy, 4 error, 8 online) |
| 6546 | LABHI | OR timer bits 12..23 into AC, before LABGET |
| 6547 | LABTOP | OR timer bits 24..31 into AC, before LABGET |

Use `CLA` before LABGET/LABHI/LABTOP. These are IOTs decoded by `pdp8.py`, not UART commands embedded in PDP-8 machine code. The MSP430 firmware sees ordinary device operations such as `ADC_START` but has no knowledge of PAL labels. `LABRDY` does not skip on error. A guest program must either check `LABSTS` or be stopped by the operator if a device is absent; the interactive dashboard remains responsive.

## Wire protocol (ATLAS-LAB/1)

| Byte offset | Field | Description |
|---|---|---|
| 0 | `A5` | Sync |
| 1 | `01` | Protocol version |
| 2 | `SEQ` | 8-bit command sequence |
| 3 | `OP` | Operation code |
| 4 | `LEN` | Payload length 0..8 |
| 5.. | Payload | Binary command-specific data |
| trailing two | CRC16 | CRC-16/CCITT-FALSE, init FFFF, poly 1021, high byte first; covers bytes 1 through payload |

Replies use `OP | 0x80` and payload byte 0 is status: 0 OK; 1 BUSY; 2 NOT_READY; 3 BAD_ARGUMENT; 4 UNSUPPORTED; 5 FAULT. Replies must match request sequence and opcode and pass CRC. Requests use one outstanding transaction, protecting the limited 512-byte MSP430 RAM. Timeouts must mark a disconnected controller, not substitute simulated readings.

Commands: `IDENTIFY=01`, `ADC_START=10`, `ADC_READ=11`, `TIMER_START=20`, `TIMER_READ=21`, `STATUS=30`, `CLEAR=31` (all hex). ADC_READ returns two little-endian bytes; TIMER_READ returns four. The physical timer nominal clock is 1 MHz, uncalibrated. The test fixtures make deterministic values for educational testing, not claims of metrological accuracy.

## Installation

- On Windows run `INSTALL_PICO_WINDOWS.bat` from this complete repository checkout; it now includes **`lab_protocol.py`, `lab_device.py`, `lab_uart.py`**, and `main_dashboard.py` renamed to Pico `main.py` **last**. The installer backs up prior Pico files and verifies transfers. Existing `main.py` in the repo remains the standalone monitor source and must not overwrite the dashboard entry point.
- Create and flash the independent MSP430 C project under `msp430-lab/` using TI tools. The Pico installer **does not flash the MSP430**.
- Wire UART GP0/GP1 ↔ P1.1/P1.2, GP2 ← P2.0 READY, shared ground, and protected experimental sensor input. Read `msp430-lab/README.md` before connecting.
- Run the local Chrome dashboard, select **Programs → Laboratory I/O**, load a native demonstration and run it; inspect PDP-8 address `0210` for the stored raw value. In SIM mode the result is synthetic and labeled; in LIVE PICO mode the physical MSP430 is required.

## Acceptance criteria

1. CPython and MicroPython-compatible protocol encoder/decoder tests pass; C wire codec builds and passes host tests.
2. Original 52 PDP-8 tests remain green, including front-panel, Teletype, calculator and paper tape.
3. A native guest ADC loop running against simulated device 54 stores 512 at `0210` (test fixture).
4. A native guest timer loop stores 1000 ticks (test fixture).
5. Real MSP430 can respond to `IDENTIFY`, `ADC_START`, `ADC_READ`, `TIMER_START` and `TIMER_READ`, and reject corrupted frames.
6. Live Pico reads actual ADC/TIMER results into memory and recovers cleanly from disconnection.

Steps 1–4 have automated evidence in this release. **Steps 5–6 are outstanding and must be verified on your hardware.**

## Sources and authority

TI MSP430G2553 datasheet and technical reference (GPIO, USCI_A0, ADC10, Timer1_A); Raspberry Pi Pico RP2040 documentation; DEC PDP-8/I and LINC/PDP-12 programming references. Pin assignments and ATLAS-LAB binary protocol are new design decisions, not historical original-device opcodes.

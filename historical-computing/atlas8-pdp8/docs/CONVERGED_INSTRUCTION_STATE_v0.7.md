---
title: "ATLAS-8: Converged Instruction and Instructional State"
subtitle: "Canonical reference at v0.7.0 engineering preview"
author: "Project Atlas | Historical Computing"
date: "22 November 2026"
geometry: margin=0.80in
fontsize: 10pt
colorlinks: true
linkcolor: MidnightBlue
---

# Purpose and scope

This is the **converged reference** for two related meanings of *instruction state*:

1. **Machine-instruction state:** Which operations are actually recognized by the ATLAS-8 PDP-8 emulator, how the laboratory instructions work, and where each request goes.
2. **Instructional state:** What a student can actually demonstrate now, what is represented only by a simulator, and what remains to be validated on physical hardware.

**Reference baseline:** Project Atlas `historical-computing/atlas8-pdp8`, release **v0.7.0-lab-preview**, GitHub commit [`ab3e875`](https://github.com/RandoSY/project-atlas/commit/ab3e875e42176393da8a35ccf71dda5417e92eb1), 22 November 2026. This document is based on the repository's actual Python, C, PAL-style examples, tests and deployment guides—not on intended capabilities alone. ATLAS-specific IOTs are **new educational extensions, not original DEC instructions**.

## At-a-glance reference

| Layer | Processor / language | Student's view | Implemented role | Evidence / boundary |
|:--|:--|:--|:--|:--|
| Operator | Chrome + JavaScript / PC | PDP-8/I-inspired switches, lamps, Teletype, programs | Controls a real emulator instance; does not evaluate guest instructions | Desktop browser tests reported in v0.7 release |
| Historical CPU | PDP-8 12-bit guest ISA | Octal words and PAL-style mnemonics | `pdp8.py` fetches/executes MRI, IOT, OPR | 65 Python tests pass locally |
| Emulator host | RP2040 / MicroPython | Device-54 looks like an I/O controller | `lab_device.py` dispatches IOTs and maintains status; `lab_uart.py` supplies hardware UART | Software path present; physical Pico link unverified |
| Instrument controller | MSP430G2553 / C | ADC, timer and digital control as an autonomous device | `main.c` operates ADC10, Timer1_A, UART and READY | C wire codec host-tested; target build and board operation unverified |
| Physical world | Instrumentation and sensors | Voltage or measured time | Protected analog and digital connections | Real values not yet demonstrated end-to-end |

**Architectural rule:** `PDP-8 guest instruction -> emulated IOT device -> ATLAS-LAB/1 UART request -> MSP430 measurement -> CRC-checked reply -> guest state/memory`. Chrome is a monitor, not the CPU. The RP2040 and MSP430 run separate programs. The same controller is intended to support a future LINC/PDP-12 instruction front-end; **PDP-12 mode is not implemented**.

# 1. Historical computer: what has converged

## 1.1 PDP-8 architectural basics

- **Word:** 12 bits. Register and memory words are displayed in **four octal digits** (`0000`–`7777`).
- **Primary registers/state:** AC (12-bit accumulator), LINK (1-bit carry/rotate extension), PC, instruction register (last fetched IR), MQ (partial group-3 support), memory and memory-field registers (IF/DF/IB).
- **Memory:** nominal 4,096 words per field. The software permits one through eight fields (4K–32K words); the Pico dashboard boot uses **one field by default**. Eight-field physical Pico memory usage has not been bench-validated.
- **Instruction families:** six memory-reference instructions (MRI), IOT, and OPR. In a standard 12-bit word, the top three bits select the instruction family; memory-reference instructions also encode indirect/current-page selection and a seven-bit offset. IOT instructions instead identify a device and its operation.

| Opcode group | PDP-8 mnemonic | Core meaning | Status in ATLAS-8 |
|:--|:--|:--|:--|
| `0` | `AND` | Bitwise AND operand into AC | Implemented |
| `1` | `TAD` | Add operand to AC, carry through LINK | Implemented |
| `2` | `ISZ` | Increment memory word; skip if zero | Implemented |
| `3` | `DCA` | Store AC to memory and clear AC | Implemented |
| `4` | `JMS` | Jump to subroutine, store return PC | Implemented |
| `5` | `JMP` | Jump | Implemented |
| `6` | `IOT` | Control or test a selected peripheral | Selected real-device codes plus ATLAS device 54 |
| `7` | `OPR` | Register/micro-operation combinations | Groups 1 and 2, limited group 3; not complete EAE |

The emulator also supports selected console, memory-extension and interrupt operations, Teletype keyboard/printer, and high-speed paper reader/punch IOTs. It is a practical *instruction-level educational emulator*, **not a transistor-level or machine-cycle-accurate PDP-8/I**. Some PDP-8/E operations are supported; this should not be confused with a verified implementation of every PDP-8 model.

## 1.2 Front panel and bootstrap sequence

The existing PDP-8/I-style panel provides twelve toggle switches and operative **LOAD ADD, DEPOSIT, EXAMINE, START, CONTINUE, STOP, SINGLE INSTRUCTION** controls. `START` clears AC/LINK for a fresh program; `CONTINUE` retains the calculation state. Individual hardware *microcycle* stepping is not implemented.

The original five-word switch-entry exercise remains the canonical first lesson:

| Octal address | Octal word | Meaning |
|:--|:--|:--|
| `0000` | `7301` | Clear AC/LINK, increment AC to 1 |
| `0001` | `7001` | Increment AC |
| `0002` | `7430` | Skip next instruction when LINK = 0 |
| `0003` | `7402` | Halt |
| `0004` | `5001` | Jump back to address `0001` |

The native instruction test halts after **12,286 guest instructions**, with AC `0000`, LINK `1` and PC `0004` (the PC is the next instruction address). This teaches machine state independently of the browser.

The next lesson uses the **17-word historical RIM high-speed loader** starting at `7756`. The emulated PDP-8 executes reader IOTs, consuming virtual tape frames at **10 cps**, **300 cps**, or **TURBO**. The 10 cps setting models transport timing only, *not the complete ASR-33 low-speed reader electronics*. Original historical tape collections and FOCAL/OS-8 have not yet passed compatibility testing.

# 2. New ATLAS-8 laboratory instruction family

## 2.1 Instruction encoding and authority

An IOT word has the octal shape `6 D D F`, where `DD` is a two-digit octal device selector and `F` is the device-specific function digit. ATLAS-8 uses **device `54` (octal)**. Its instructions occupy `6540`–`6547`, and the emulator dispatches them through `lab_device.LabPeripheral`.

> **Historical boundary:** These eight words are **ATLAS-8-defined extensions**. Their numerical assignments are implementation choices, not claims that DEC standardized an ADC controller at device 54 or that the code is unallocated on every historical system.

| Exact octal word | Symbol | Effect on PDP-8 and laboratory device | Important qualification |
|:--|:--|:--|:--|
| `6540` | `LABCLR` | Clear local lab state; send wire-level `CLEAR` if transport exists | Does not erase guest RAM |
| `6541` | `LABGO` | Start ADC10 conversion; channel = low three AC bits | A1/A2 cannot be selected while UART pins are used |
| `6542` | `LABRDY` | **Skip the next PDP-8 instruction** if validated result is ready | Does *not* skip merely because an error occurred |
| `6543` | `LABTIM` | Start Timer1_A two-rising-edge period capture | Result is an integer **tick count**, not calibrated seconds |
| `6544` | `LABGET` | Bitwise **OR** low 12 result bits into AC, then clear READY | **Use `CLA` first**; returns only low 12 timer bits |
| `6545` | `LABSTS` | OR the four status flags into AC | **Use `CLA` first** for an unambiguous status value |
| `6546` | `LABHI` | OR timer bits 12–23 into AC | Requires timer result ready; does not clear READY |
| `6547` | `LABTOP` | OR timer bits 24–31 into AC (upper eight bits) | Requires timer result ready; does not clear READY |

**LABSTS status bits:** bit 0 (`0001`) = READY; bit 1 (`0002`) = BUSY; bit 2 (`0004`) = ERROR; bit 3 (`0010`) = ONLINE. These are guest-visible status bits, not serial UART register bits. ONLINE means an appropriate protocol response has been seen—not a guarantee that every subsequent operation will succeed.

**Important state rule:** `LABRDY` tests the emulator's **latched, validated** measurement flag. It is not a direct read of the MSP430 GPIO and must not stop the PDP-8 while waiting. The GPIO READY line helps the Pico know when to request the measurement; the MCU response is accepted only after packet validation. The currently implemented Pico GPIO is **polled**, not serviced by a registered GPIO interrupt handler.

## 2.2 Exact ADC demonstration executed by the release

The built-in `lab_demo` ADC program is loaded at octal `0200` and uses channel A0. The listing below matches **`dashboard_bridge.py`**, rather than pretending a separately provided PAL source has already been assembled.

| Address | Word | Symbolic intent |
|:--|:--|:--|
| `0200` | `7200` | `CLA`: AC = 0; selects channel A0 |
| `0201` | `6541` | `LABGO`: request conversion |
| `0202` | `6542` | `LABRDY`: if ready, skip address `0203` |
| `0203` | `5202` | `JMP 0202`: poll while not ready |
| `0204` | `7200` | `CLA`: prepare for OR transfer |
| `0205` | `6544` | `LABGET`: read low result word |
| `0206` | `3210` | `DCA 0210`: store result and clear AC |
| `0207` | `7402` | `HLT` |
| `0210` | `0000` | Result storage location (initial) |

In **PC SIMULATE mode**, the deterministic test fixture returns **512 raw counts** for A0, or **515** for A3. The resulting value is stored at guest memory `0210`. These numbers are **synthetic test values, not measurements of actual voltage**. The equivalent built-in timer demo substitutes `LABTIM` for `LABGO` and stores **only the low twelve bits** of its 1,000-tick fixture at `0210`.

For a full 32-bit timer result, the PAL-style example `examples/lab_timer.pal` reads `LABTOP`, then `LABHI`, then `LABGET` into three memory locations. Reassemble as

`TICKS = (TOP << 24) | (UPPER << 12) | LOWER`, where TOP is 8 bits and UPPER/LOWER are 12 bits each.

**Do not equate PAL-style source with a validated assembler implementation.** The repository includes symbolic `.pal` examples, but **does not yet bundle a validated PAL assembler or demonstrate compiling those files into runnable machine words**. The built-in examples are already encoded as native guest machine words.

# 3. Convergence across three programming languages

Each level has its own instruction set and its own responsibility. The convergence is **semantic**, not binary compatibility.

| Scientific action | PDP-8 guest mnemonic | RP2040 MicroPython layer | Wire-level command | MSP430 C or assembly concept |
|:--|:--|:--|:--|:--|
| Request analog sample | `LABGO` | `LabPeripheral.start(channel)` | `ADC_START` (`0x10`) | `begin_adc()`; `ADC_START` macro illustrates ADC10SC |
| Check result completion | `LABRDY` | Test `LabPeripheral.ready` | No wire transaction in the IOT itself | ADC completion sets READY P2.0 |
| Retrieve sample | `LABGET` | OR latched measurement into AC | Driver previously issued `ADC_READ` (`0x11`) | Return ADC10 result as 2 little-endian bytes |
| Request time interval | `LABTIM` | `start(mode='timer')` | `TIMER_START` (`0x20`) | `begin_timer()`, Timer1_A capture |
| Retrieve full interval | `LABTOP`, `LABHI`, `LABGET` | Slice latched 32-bit tick count | Driver previously issued `TIMER_READ` (`0x21`) | 4 little-endian timer-result bytes |
| Clear instrument | `LABCLR` | `LabPeripheral.clear()` | `CLEAR` (`0x31`) | Reset operation and READY flag |
| Inspect status | `LABSTS` | Read local latched status mask | `STATUS` (`0x30`) exists, but **LABSTS does not send it directly** | Firmware has its own status register |
| Establish compatibility | No dedicated guest IOT | Initialization `IDENTIFY` handshake | `IDENTIFY` (`0x01`) | Report protocol and capability bytes |

**Symbolic design rule:** Reuse understandable *verbs* (`START`, `READY`, `READ`, `CLEAR`, `STATUS`) across PDP-8 PAL mnemonics, MicroPython names, C functions and TI assembler macros. Do **not** make students believe `LABGO` is a native MSP430 instruction or `ADC_START` is a DEC instruction. Each translation step is a teachable boundary.

The production MSP430 controller is currently written in **C**, appropriate for its constrained 16 KB flash / 512 B RAM environment. `msp430-lab/asm/lab_macros.asm` provides **illustrative TI-syntax macros** for ADC start and READY GPIO operations. These macros are **not** a second complete, target-compiled MSP430 firmware implementation.

# 4. The modern interprocessor link: ATLAS-LAB/1

## 4.1 Physical channel

- **RP2040 Pico:** UART0 TX GP0, UART0 RX GP1; digital input GP2 for READY; USB connection to Chrome host stays separate.
- **MSP430G2553:** UCA0 RX P1.1, UCA0 TX P1.2; READY output P2.0 active high; ADC channel A0 on P1.0; Timer1_A capture input P2.1.
- **Electrical:** 3.3 V logic, short common-ground interconnect, independent regulated power where appropriate. Check LaunchPad backchannel-UART jumpers; avoid tying powered 3.3 V outputs together. Externally sourced experiment signals need conditioning/protection.
- **Transport:** 38,400 baud, 8 data bits, no parity, one stop bit; simple request/reply, one outstanding operation. The physical baud rate and complete electronic path remain to be verified on the board.

**Important pin convergence:** P2.1 is reserved for **Timer1_A capture** in v0.7, **not** the previously proposed optional Pico-to-MSP430 trigger. The software and wiring guide agree on this choice.

## 4.2 Binary frame and errors

ATLAS-LAB/1 is **not** the USB dashboard JSON protocol. It is a compact, versioned wire format:

`A5 | 01 | SEQ | OP | LEN | payload[0..8] | CRC_H | CRC_L`

- `A5`: sync marker; `01`: protocol version; sequence number and operation code: one byte each.
- Payload: zero through eight bytes.
- CRC: **CRC-16/CCITT-FALSE**, polynomial `0x1021`, initial `0xFFFF`, over **version through end of payload** (not including sync), transmitted **high byte first**.
- Replies: operation code `OP | 0x80`; **first reply payload byte is status**. Remaining bytes contain any result.
- Reply status: `0` OK, `1` BUSY, `2` NOT_READY, `3` BAD_ARGUMENT, `4` UNSUPPORTED, `5` FAULT.
- Sequence and opcode must match the outstanding request. The driver checks CRC. The software timeout is approximately **1,200 ms** for an unanswered transaction; it reports failure rather than manufacturing a sample.

| Operation | Code (hex) | Request payload | Successful result payload after status byte |
|:--|:--|:--|:--|
| `IDENTIFY` | `01` | None | Protocol major, minor, capability bits |
| `ADC_START` | `10` | One byte: ADC channel | None (ACK) |
| `ADC_READ` | `11` | None | 2 bytes, **little-endian** unsigned ADC10 result |
| `TIMER_START` | `20` | None | None (ACK) |
| `TIMER_READ` | `21` | None | 4 bytes, **little-endian** unsigned tick count |
| `STATUS` | `30` | None | One device-status byte |
| `CLEAR` | `31` | None | None (ACK) |

**Golden request frames:** IDENTIFY sequence 01 = `A5 01 01 01 00 F6 75`; ADC_START A0 sequence 01 = `A5 01 01 10 01 00 BD BB`. The familiar CRC test string `123456789` produces `0x29B1`. These fixtures are in `msp430-lab/tests/PROTOCOL_VECTORS.md`.

## 4.3 Device readiness and fault states

The MSP430 may acknowledge **starting** an operation before the measurement is complete. When the ADC or timer completes, it asserts READY. The MicroPython driver polls READY and requests the result; only after a matching, CRC-valid reply does the laboratory IOT device set its own READY flag. Then `LABRDY` can skip, and `LABGET` can transfer the value to AC.

A missing controller, malformed frame, bad checksum, response mismatch or timeout must **not** become a plausible sensor value. The emulator reports an offline/error condition. An unguarded guest `LABRDY` polling loop can continue indefinitely after an error, so the operator must STOP or the program should explicitly check `LABSTS` and implement an error exit.

# 5. The student-facing instructional sequence

| Stage | Student action | What is learned | Evidence today |
|:--|:--|:--|:--|
| A — Machine state | Toggle five 12-bit words, EXAMINE and single-step | AC, LINK, PC, arithmetic rollover, control flow | Implemented and software-tested |
| B — Bootstrap | Enter/run RIM loader and mount virtual paper tape | Bootstrapping and IOT-driven peripheral operation | Synthetic tape and three-speed loader tested |
| C — Native scientific code | Use the native calculator, Teletype, and guest lab-IOT programs | High-level intent decomposes into executable guest words | Calculator and lab simulation tested |
| D — Intelligent I/O | Follow `LABGO` through UART to MSP430 and back | Processor/controller separation, asynchronous READY, error handling | Software paths and C codec exist; two-board proof pending |
| E — Historical scientific language | Boot original FOCAL and calculate transcendental functions | Floating-point scientific programming on the PDP-8 | **Not yet demonstrated in ATLAS-8** |
| F — LINC/PDP-12 lab | Map the same controller behind the documented LINC/PDP-12 interface | Historical lab-computer architecture and measurement | **Future separate machine mode** |

This sequence respects the Project Atlas instructional principle **Experience Before Equation**. The same physical instrument can remain constant while the student moves from raw machine code to symbolic instructions and eventually an original high-level language.

# 6. Code ownership, deployment and verification

| Path | Responsibility |
|:--|:--|
| `pdp8.py` | Guest 12-bit CPU and IOT dispatch, including device 54 |
| `lab_device.py` | Guest-facing instrument state, simulated controller, READY and result latching |
| `lab_protocol.py` | Binary framing, CRC and incremental decoder (CPython/MicroPython) |
| `lab_uart.py` | Pico UART0 and READY GPIO transport |
| `dashboard_bridge.py` | JSON host commands, state/reporting, native demonstration-word loading |
| `main_dashboard.py` | Pico dashboard-mode entry point, installed **as `main.py`** |
| `msp430-lab/src/main.c` | G2553 UART, ADC10, Timer1_A and READY firmware |
| `msp430-lab/src/lab_protocol.[ch]` | Portable C framing and decoder |
| `msp430-lab/asm/lab_macros.asm` | Illustrative symbolic MSP430 assembler macros |
| `examples/lab_adc.pal`, `examples/lab_timer.pal` | PAL-style student-readable examples |
| `tests/test_lab.py` | Native guest IOT and protocol regression tests |

**PC SIMULATE:** `START_DASHBOARD_WINDOWS.bat` starts the PC host, which uses a labeled `SimTransport` fixture. **LIVE PICO:** `main_dashboard.py` becomes Pico `main.py`; it calls `serve(fields=1, lab_mode='uart')`. Pico MicroPython files are installed with `INSTALL_PICO_WINDOWS.bat`, including `bootstrap.py` and the three lab modules. MSP430 C is a **separate target project** and must be built/flashed using an MSP430 toolchain/debugger; the Pico installer does not install it.

The full v0.7 release suite was reported at **65 CPython tests**. For this reference, the same 65 tests and the portable **C packet-codec** host test were rerun locally and passed. Browser tests at 1440×900 and 1280×720 were recorded in the release, but not rerun as part of this document review.

### State categories (do not merge them)

**Verified in software:** basic PDP-8 instruction execution, front-panel program, synthetic RIM/virtual-tape demonstration, deterministic simulated ADC/timer capture, native IOT tests, protocol CRC/decoder tests, portable C packet-codec test.

**Implemented but not hardware-verified:** physical Pico USB dashboard operation, Pico UART-to-MSP430 transport, MSP430G2553 firmware target build and flash, analog voltage accuracy, actual timer/capture accuracy, disconnect/reconnect behavior on real wires.

**Not implemented or not yet demonstrated:** a validated original FOCAL boot, OS/8, disk/DECtape, complete EAE, a native PAL assembler inside ATLAS-8, machine-cycle stepping, LINC/PDP-12 `SAM`, and an operating PDP-12/AGC/GT40 emulator within ATLAS-8.

# 7. Completion gate for a feature freeze

A reliable, reproducible laboratory handoff should establish the following **on the actual RP2040 and MSP430G2553**:

1. Compile the unmodified G2553 C firmware using the target compiler, record flash/RAM map, flash successfully and read firmware `IDENTIFY` at 38,400 baud.
2. Confirm CRC rejection, partial-packet recovery, timeouts, sequence matching, device removal and reconnection.
3. Confirm GP2 sees MSP430 P2.0 READY only after completed measurement; verify the G2553 pin mux and LaunchPad UART jumpers.
4. Measure a known protected voltage with ADC10 A0; report the raw code and a **calibrated** reference voltage. Do not claim ten-bit accuracy beyond demonstrated electrical limits.
5. Measure a known pulse period on P2.1; compare timer counts against an independently timed reference, including repeated periods and overflow boundaries.
6. Run `0200: LABGO ... LABGET ... DCA 0210` in **LIVE PICO** and confirm the physical reading reaches guest core memory and the Chrome monitor.
7. Run all regression tests and repeat the entire experiment from clean installation instructions, without developer intervention.

**Decision:** The major **instructional architecture is converged and can be feature-frozen**. The **hardware validation is not complete**, so v0.7 must remain explicitly an *engineering preview*, not a finished scientific instrument.

# 8. Authoritative source index

All links below are relative to the canonical `historical-computing/atlas8-pdp8` tree.

- [`pdp8.py`](../pdp8.py) — fetch/execute core and device-54 dispatch.
- [`lab_device.py`](../lab_device.py) — exact semantics of LABCLR through LABTOP.
- [`lab_protocol.py`](../lab_protocol.py) — exact wire framing and CRC.
- [`dashboard_bridge.py`](../dashboard_bridge.py) — machine-code demonstration listing and UI bridge.
- [`main_dashboard.py`](../main_dashboard.py) and [`lab_uart.py`](../lab_uart.py) — Pico entry point and transport.
- [`msp430-lab/README.md`](../msp430-lab/README.md) — wiring and independent firmware instructions.
- [`msp430-lab/src/main.c`](../msp430-lab/src/main.c) — device behavior.
- [`examples/lab_adc.pal`](../examples/lab_adc.pal) and [`examples/lab_timer.pal`](../examples/lab_timer.pal) — symbolic lesson programs.
- [`docs/LAB_IO_V070.md`](LAB_IO_V070.md) — original v0.7 lab interface specification.
- [`docs/FRONT_PANEL_LESSON.md`](FRONT_PANEL_LESSON.md) and [`docs/PAPER_TAPE_LAB.md`](PAPER_TAPE_LAB.md) — earlier teaching stages.
- [`docs/COMPATIBILITY.md`](COMPATIBILITY.md) and [`docs/RELEASE_STATUS.md`](RELEASE_STATUS.md) — versioned limitations and release evidence.

*This reference states the repository's observed v0.7 behavior. Where historical DEC behavior or proposed future work is mentioned, it is clearly distinguished from ATLAS-8's current tested capabilities.*
# ATLAS-8 MSP430G2553 Intelligent Laboratory Controller

This directory contains **proposed reference firmware** for the device-54 ATLAS-8 laboratory extension. It is *not* a historical DEC peripheral. The MSP430 runs C, independently acquires sensor/timing data, asserts READY, and exchanges CRC-protected frames with the RP2040 MicroPython driver.

## Required build and flash

- MSP430G2553, preferably MSP-EXP430G2ET LaunchPad with debugger; use TI Code Composer Studio with the correct G2553 device headers, or an MSP430 cross compiler providing `msp430.h`.
- Create a bare-metal MSP430G2553 project. Add `src/main.c` and `src/lab_protocol.c`; include `src/lab_protocol.h`. There is no bootloader to run on the host PC; **flash using the LaunchPad debugger**.
- **Not hardware-verified:** this deliverable has passed host tests of the portable wire codec. The G2553-specific UART, ADC, timer and ISR code has not been built with a target MSP430 compiler or tested electrically. Treat it as a bench-validation starting point, not a finished instrument.

## Wiring (short, common-ground, 3.3 V)

| Pico RP2040 | MSP430G2553 | Purpose |
|---|---|---|
| GP0 / UART0 TX | P1.1 / UCA0 RX | Command packets |
| GP1 / UART0 RX | P1.2 / UCA0 TX | Responses |
| GP2 / GPIO input | P2.0 / GPIO output | READY active HIGH |
| GND | GND | Required common reference |
| -- | P1.0 / A0 | ADC voltage input, 0..AVCC |
| -- | P2.1 / TA1.1 CCI1A | Rising-edge capture input |

The earlier optional Pico GP3 -> MSP430 P2.1 trigger arrangement is **not used** here: P2.1 is reserved for Timer_A capture. Never connect the Pico's 3.3V output to a second board's powered 3.3V output. Power the G2553 through its intended regulated supply. Check/remove LaunchPad eZ-FET backchannel UART jumpers when wiring the Pico to P1.1/P1.2. All analog inputs require protection and signal conditioning for non-3.3V experiments.

## Behavior

- 38400 baud, 8-N-1, binary frames, CRC16/CCITT-FALSE, single request/reply, one outstanding request.
- `ADC_START` selects A0 or A3..A7. A1 and A2 are unavailable while the hardware UART uses their pins. Returns ACK immediately; the MSP430 ADC10 converts independently and then asserts READY.
- `ADC_READ` returns an unsigned 10-bit integer, little-endian in two bytes. Reference is AVCC and **not a precision reference**; calibrate before reporting voltages.
- `TIMER_START` arms Timer1_A capture on P2.1 (two rising edges), nominal SMCLK/DCO 1 MHz. READY asserts on the second edge. `TIMER_READ` returns a 32-bit little-endian elapsed tick count. Timer ISR includes overflow tracking; precise accuracy, high-frequency limits and overflow boundary behavior remain to be hardware-qualified.
- `CLEAR` cancels a pending operation; `STATUS` returns ready/busy/error flags; `IDENTIFY` returns protocol 1.0 and capability bits.
- An MSP430 READY line indicates data availability, **not a successful packet CRC**. The RP2040 verifies both READY and the CRC-bearing UART response before exposing data to the guest PDP-8.

## Student-friendly assembly

`asm/lab_macros.asm` demonstrates TI macro declarations `ADC_START`, `LAB_READY_ON`, `LAB_READY_OFF`. These are educational counterparts to the PDP-8 symbolic IOT words in `../examples/lab_adc.pal`; they are not the same processor instructions.

## Verification sequence

1. Use `gcc` on a desktop to run the **portable codec** test: `gcc -std=c99 -Wall -Wextra -Werror -pedantic src/lab_protocol.c tests/protocol_host_test.c -o protocol_test` then run `protocol_test`.
2. Compile and flash the target C files with the G2553 toolchain; confirm flash/stack/RAM usage.
3. Verify `IDENTIFY`, CRC rejection, and timeout/reconnection at 38400 baud with a USB-UART adapter.
4. Verify ADC10 A0 with 0V and a known safe voltage, and Timer1 capture with a known logic waveform.
5. Connect to the Pico; run the native device-54 PDP-8 program and compare values recorded in core memory.
6. Re-run all PDP-8, paper-tape, calculator and Teletype tests after physical integration.

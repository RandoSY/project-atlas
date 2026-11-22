# Lesson: Program the PDP-8/I through its front panel

**ATLAS-8 v0.5.3 | 22 November 2026**  
**Hardware model:** PDP-8/I (circa 1968), rather than PDP-8/E or PDP-8/A.

## Objective

Enter *actual 12-bit PDP-8 machine words* through virtual hardware switches, run the original five-word video demonstration, examine the memory just as on the real machine, and learn why the LINK bit matters. The program executes in the same Python/MicroPython PDP-8 CPU in both PC simulator and LIVE PICO modes; the browser does not calculate the answer in JavaScript.

## The video exercise

Source: [Hackaday, Getting Started With Blinking Lights On Old Iron](https://hackaday.com/2017/08/10/getting-started-with-blinking-lights-on-old-iron/) and [How to Program a Vintage PDP-8 via the Front Panel](https://www.youtube.com/watch?v=yUZrn7qTGcs).

| Octal location | Octal word | Meaning |
|---|---|---|
| `0000` | `7301` | Clear accumulator and LINK; add one (`CLA CLL IAC`) |
| `0001` | `7001` | Increment accumulator (`IAC`) |
| `0002` | `7430` | Skip the next instruction while LINK is zero (`SZL`) |
| `0003` | `7402` | Halt (`HLT`) |
| `0004` | `5001` | Jump back to `0001` (`JMP 0001`) |

The machine increments its 12-bit accumulator repeatedly. When the value wraps from octal `7777` to `0000`, the LINK flips to one. The conditional skip at `0002` no longer skips the halt at `0003`, so the program terminates. It should perform **12,286 machine instructions** and finish with AC = `0000`, LINK = `1`, PC = `0004` (assuming no breakpoints).

## Operator procedure (SIMULATE or LIVE PICO)

1. Launch `START_DASHBOARD_WINDOWS.bat`, select **Front Panel**, and press **STOP**. The front panel is the default starting tab and fits the desktop screen without scrolling.
2. Put all twelve address/data toggles **up** to form octal `0000`; press **LOAD ADD**. This selects memory address 0000. Field switches are inactive when the emulator has only one memory field.
3. Toggle octal `7301` and press **DEP** (the physical PDP-8/I deposit key was operated upward). It deposits at 0000 and advances to 0001.
4. Repeat DEP with `7001`, `7430`, `7402`, `5001` in sequence. The PC/address lamps advance after each deposit.
5. Toggle `0000` and press **LOAD ADD** again. Press **EXAM** repeatedly to verify the five words in the memory buffer lamps. Reload address `0000` afterward.
6. With switches at `0000`, press **START**. It clears AC and LINK and begins the program from the switch-selected address; **CONT** instead resumes execution without clearing AC or LINK.
7. To see the process, choose **SING INST**, reload `0000`, press **START** once and then **CONT** for successive instructions. Watch PC, AC, LINK and the instruction lamps.
8. **SING STEP** is disabled because the emulator does not simulate the PDP-8/I's individual microcycles. **SING INST** is real one-instruction stepping. Do not infer cycle-accurate operation from LED animations.

The **SET SWITCHES FOR THIS STEP** aid sets a target 12-bit word but never deposits or runs it for you. The manual toggles operate the same CPU. A locked panel ignores changes until you unlock it.

## Historical engineering lessons

The front panel makes visible the roles of the accumulator (AC), the one-bit LINK, the program counter, instruction decoding, twelve physical data switches and memory. There are only eight primary opcode groups: AND, TAD, ISZ, DCA, JMS, JMP, IOT and OPR. Most real work used a loader, a paper-tape image, and eventually assemblers; a few words entered by switches were a bootstrap, not a practical replacement for an assembler.

Next, compare the exercise with the no-hardware **Calculator** tab, followed by an authentic paper-tape loader and the eventual native PAL/FOCAL programming environment. The latter are future compatibility milestones, not presently validated.

## Model fidelity and boundaries

- The panel layout follows **PDP-8/I**, including its three data-field and three instruction-field switches, a twelve-bit switch register, momentary LOAD ADD/DEP/EXAM/START/CONT/STOP and latched SING INST.
- The panel is a functional browser reconstruction, not a licensed photograph or a transistor-level simulation. Lamp intensities, microcycle timing, device-specific delays and physical contacts are not emulated.
- On the one-field default configuration, DF/IF switches are visible but disabled. A multi-field configuration must be explicitly enabled on **both** PC and Pico configurations.
- Both SIMULATE and LIVE PICO use the same JSON command protocol. Physical Pico hardware remains separately unverified; do not advertise it as fully validated.

## Reading and references

1. [Pikuma — From Front Panel to Program: Thinking Like a PDP-8](https://pikuma.com/blog/pdp-8-minicomputer). Especially the eight opcode groups, AC/LINK, front-panel input, paper tape, native assembly. Excellent conceptual background; not a substitute for DEC specifications.
2. [Hackaday — Getting Started With Blinking Lights On Old Iron](https://hackaday.com/2017/08/10/getting-started-with-blinking-lights-on-old-iron/). Source for the example and the demonstrated panel procedure.
3. [PDP8Online — PDP-8/I Front Panel](https://www.pdp8online.com/pdp8i/pics/pdp8i_frontpanel.shtml). Model-specific indicator and control reference.
4. [DEC PDP-8/I & PDP-8/L Small Computer Handbook (1970)](https://deramp.com/downloads/mfe_archive/011-Digital%20Equipment%20Corporation/00%20Digital%20Handbooks/08%20PDP-8%20Family/Small%20Computer%20Handbook/PDP8i%20l%20SmallComputerHandbook_1970.pdf). Primary reference for instruction and control semantics.

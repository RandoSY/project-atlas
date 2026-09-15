# Canonical Public Project Inventory

**Control date:** 15 September 2026

This is the public decision inventory derived from Project Atlas. Platform ports, experiments, and historical names are folded beneath durable systems rather than treated as separate current obligations.

Maturity labels describe the strongest currently recorded state, not a promise that every artifact has already been migrated into the new estate.

## CORE / SDL

| System | Maturity | Priority / disposition | Canonical home |
|---|---|---|---|
| SDL — Software-Defined Laboratory | Bench-tested | P1 FINISH | `software-defined-laboratory` |
| SDL PC MCP Gateway / Python Bridge | Bench-tested | P1 FINISH | `software-defined-laboratory` |
| Traffic Cop Communications Monitor | Bench-tested | P2 PACKAGE | `software-defined-laboratory` |
| SUPER Reference Hardware | Implemented | P2 REFERENCE | `software-defined-laboratory` |
| UNO + Multi-Function Shield Starter Node | Validated / deployed | P1 PACKAGE | `software-defined-laboratory` |
| Pico W SDL Runtime / Reference Node | Bench-tested | P1 FINISH | `software-defined-laboratory` |
| micro:bit v2 / MicroBlocks Dynamic Node | Implemented | P3 HOLD | `software-defined-laboratory` |
| YMP — Young Measurement Protocol | Bench-tested | P2 PACKAGE | `embedded-tools` + SDL use |
| Web Serial / WebBLE Console Family | Validated / deployed | P2 PACKAGE | `software-defined-laboratory` |
| Virtual Device Atlas / Browser-Native Virtual Lab | Bench-tested | P2 PACKAGE | `software-defined-laboratory` |
| UMA Workbench / DeviceOps / Dashboard Commander | Implemented | P3 CONSOLIDATE | `software-defined-laboratory` |

## CORE / Instruments

| System | Maturity | Priority / disposition | Canonical home |
|---|---|---|---|
| Physics Motion Lab / IMU Motion Puck | Implemented | P3 PACKAGE | `measured-world-lab` |
| eScale / HX711 Instrument Family | Validated / deployed | P2 PACKAGE | `measured-world-lab` |
| Temperature / DS18B20 Instrument Family | Validated / deployed | P1 PACKAGE | `measured-world-lab` + SDL reference |
| Distance / HC-SR04 / ToF Instrument Family | Bench-tested | P3 PACKAGE | `measured-world-lab` |
| Low-Cost Conductivity Meter | Implemented | P2 PACKAGE | `measured-world-lab` |
| Beer-Lambert / Colorimetry Instrument | Implemented | P2 PACKAGE | `measured-world-lab` |

## CORE / Curriculum

| System | Maturity | Priority / disposition | Canonical home |
|---|---|---|---|
| CORE 10 | Implemented | P1 FINISH | `core-10` |
| Kitchen Inquiry Lab | Implemented | P1 PACKAGE | `core-10` |
| One Cup Chemistry | Implemented | P1 FINISH | `core-10` |
| NOTHING IS FREE / Personal Energy Laboratory | Implemented | P1 PACKAGE | `core-10` |
| Microwave Water Heating + Electricity Cost | Bench-tested | P1 PROTECT | `core-10` |
| Measurement Ladder: Ruler -> Water Clock -> e | Implemented | P2 PACKAGE | `core-10` |
| Three Mirrors: Physical / Paper / Analog / Digital | Implemented | P2 PACKAGE | `core-10` |
| TeaTime / Beer-Lambert Learning Activity | Implemented | P2 PACKAGE | `core-10` |
| Newton Cooling / Brine / Solution-Chemistry Sequence | Implemented | P2 PACKAGE | `core-10` |

## CORE / Measured Machine

| System | Maturity | Priority / disposition | Canonical home |
|---|---|---|---|
| Nugget / Initiator Learning Ladder | Bench-tested | P2 PACKAGE | `nugget-physical-computing` |
| nugget-fwlib | Validated / deployed | P2 PUBLISH | `nugget-physical-computing` lineage |
| px-fwlib STM32G0 / CLI Explorer | Validated / deployed | P3 UPSTREAM | `computing-observatories` / upstream |
| CH32V003 Observatory / CLI Explorer | Validated / deployed | P3 PACKAGE | `computing-observatories` |
| AVR eForth Observatory + MFS Emulation | Validated / deployed | P2 PACKAGE | `computing-observatories` |
| MSP430 eForth Observatory | Implemented | P4 ARCHIVE | `computing-observatories` |
| CRCL / CIRCLE | Bench-tested | P2 PACKAGE | `computing-observatories` |
| 65C02 IDE / Simulator | Bench-tested | P3 ARCHIVE | `computing-observatories` |
| RCA COSMAC 1802 / Galileo / microForth | Validated / deployed | P2 PACKAGE | `computing-observatories` |

## CORE / Tools

| System | Maturity | Priority / disposition | Canonical home |
|---|---|---|---|
| DebugWire LIGHTENING | Bench-tested | P2 PROTECT | `embedded-tools` |
| RP2040 Common Tool: SWD/JTAG + Virtual CPUs | Designed | P4 ARCHIVE | `embedded-tools` |
| PIC12F1571 RP2040 Programmer | Bench-tested | P3 PACKAGE | `embedded-tools` |

## CORE / Robotics

| System | Maturity | Priority / disposition | Canonical home |
|---|---|---|---|
| Bargain Bin Robotics | Implemented | P2 PACKAGE | `bargain-bin-robotics` |
| Lazy LiDAR | Bench-tested | P2 PACKAGE | `bargain-bin-robotics` |
| STC15W Low-Cost Rover / NIF Robot | Implemented | P2 FINISH | `bargain-bin-robotics` + `core-10` NIF |
| Alvik -> RP2040 / XRP / Maker Pi Ports | Designed | P4 HOLD | `bargain-bin-robotics` lineage |

## APPS

| System | Maturity | Priority / disposition | Canonical home |
|---|---|---|---|
| FFT — Fair Fitness Testing / Fair Fitness Scout | Validated / deployed | P1 FINISH | `measured-human-performance` |
| SQM+ / WALKWISE | Bench-tested | P2 CONSOLIDATE | `measured-human-performance` |
| Tone Trainer | Bench-tested | P3 HOLD | `measured-human-performance` |
| PlateLab | Bench-tested | P3 HOLD | `measured-human-performance` |
| Q-Meter / MAX_Q / WiseWalking lineage | Bench-tested | P4 ARCHIVE | SQM+ lineage |
| Dropper Guard / MedDock lineage | Bench-tested | P4 ARCHIVE | historical APPS lineage |
| ESMR / Recovery Program concepts | Designed | P4 ARCHIVE | historical APPS lineage |

## TRANSMISSION

| System | Maturity | Priority / disposition | Canonical home |
|---|---|---|---|
| Project Atlas | Bench-tested | P1 MAINTAIN | `project-atlas` |
| NOT TALK, DO — Integrated Concept Systems Brief | Validated / deployed | P2 PUBLISH | `works-and-publications` |
| Full Measure (Enough) | Designed | P2 WRITE | `works-and-publications` |
| CORE 10 Teacher / Student Guides | Implemented | P1 FINISH | `works-and-publications` + `core-10` |
| SDL User / Programmer Guides | Bench-tested | P1 FINISH | `works-and-publications` + SDL |
| Zigbee Textbook / Courseware | Implemented | P4 ARCHIVE | `works-and-publications` |
| Infographics / Comics / Visual Explainers | Validated / deployed | P3 PACKAGE | `works-and-publications` + canonical projects |
| AI-Laboratory Research / Writing Program | Implemented | P2 PACKAGE | `works-and-publications` |
| Master Project Catalog / Historical Inventories | Validated / deployed | P3 ARCHIVE | `works-and-publications` / provenance |

## Protected system

**IAS — Independence Assurance System:** proprietary / off-GitHub. No implementation inventory is published here.

## Reading the inventory

- `FINISH` means spend active finishing energy now.
- `PACKAGE` / `PUBLISH` means turn existing work into a durable release without broadening scope.
- `MAINTAIN` means reliability and preservation only.
- `CONSOLIDATE` means merge variants beneath a durable parent.
- `HOLD` means preserve but do not actively grow.
- `ARCHIVE` means deliberate closure, not failure.
- `UPSTREAM` means the work primarily belongs to another project and estate-specific contributions should remain clearly attributed.
- `PROTECT` means preserve with special boundaries and deliberate public-release decisions.

The purpose of this inventory is to reduce obligations by making the disposition of each durable idea explicit.

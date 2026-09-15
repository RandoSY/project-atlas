# Intellectual Estate Migration Ledger

**Migration date:** 15 September 2026

This ledger records what the automated GitHub migration actually did. It distinguishes directly copied canonical material from exact pinned legacy snapshots, upstream/reference material, and deliberately withheld repositories.

## Preservation model

The migration uses two complementary methods:

1. **Canonical copy** — selected human-readable source or documentation is copied into the new durable parent when its role, provenance, and public suitability are clear.
2. **Pinned source snapshot** — the canonical repository contains a Git submodule fixed to an exact legacy commit. This preserves the complete historical source tree, including files that are impractical or undesirable to retype, while leaving the original repository intact.

A pinned snapshot is not a claim that the legacy taxonomy remains current. It is provenance and recoverability.

## Exact legacy snapshots now attached to the estate

| Canonical repository | Historical source | Pinned commit | Treatment |
|---|---|---|---|
| `project-atlas` | `UMA_ARCHIVE_2026` | `576e24291290800b5bb0f9512b42b01957688279` | whole historical estate archive; provenance only |
| `software-defined-laboratory` | `cloud-gsa-prototype` | `6c05739e72dcb1e56aac3662c5965567c9bbb3ad` | SDL/GSA architectural ancestor |
| `software-defined-laboratory` | `DEXIS-Lab` | `3fbaf19ebc66293c61c3f15982d4680d0623474c` | browser/remote-lab lineage; licensing remains historical/incomplete |
| `nugget-physical-computing` | `nugget-fwlib` | `f0d491436380be912a7321633d4df47bb9d36881` | validated Nugget firmware lineage |
| `nugget-physical-computing` | `rg_show_tipper` | `4f830745f055dc46fed3491e65bb1bc63f64674b` | small micro:bit binary/ADC teaching lineage |
| `measured-human-performance` | `FFT-HRM-Simulator-Microbit-V2` | `9aa2691eefa572fc94585aa4f75568f29354a282` | validated FFT simulator/test infrastructure |
| `measured-human-performance` | `movement-data-logger` | `24e6d51301cca6866d4ad5e042226618f739b787` | early raw inertial-measurement lineage |
| `bargain-bin-robotics` | `balance-bot` | `258b4eb0ea6fe03cb43f2e954135f6a7cc325ed2` | complete Bala2 control/simulation/test lineage |
| `bargain-bin-robotics` | `rekabit-testdemo-program` | `e6eeb51ea8a98c0ba3ceb4f88510329207c7599e` | low-cost robotics platform lineage |
| `computing-observatories` | `Interactive_Arduino` | `28977c8b696af05dd14bc52145e1732a646547d9` | Forth/Arduino PDF + firmware image lineage |
| `computing-observatories` | `STEM-Fusion` | `41b1766c4f721a13312de9200c6c221c61155d8d` | 65C02 trainer project record |
| `embedded-tools` | `avr-asm-revelator` | `28aab2cd3ecbbfb8d22c51bcc9d76e0f850d25a9` | AVR source/assembly analysis tool lineage |
| `embedded-tools` | `xc8-asm-revelator` | `258db1b771dd9aa99f5e10f0c4b4a5d2b751d3a2` | PIC/XC8/GCBASIC analysis tool lineage |
| `embedded-tools` | `rp2040_Experiments` | `00a205622929f83993ed9f59f66fb0e764cd0e7b` | historical experimental debug template; explicitly not validated |
| `embedded-tools` | `microbit_v2_ble_uart` | `1afddf83c6fa7bc869e9028a3287b4ed43ade858` | BLE UART infrastructure lineage |
| `embedded-tools` | `ble-uart-echo-demo` | `34b16a42a39b9d0a18f587511731d8f5a51eb27f` | BLE UART demonstration lineage |

**Total exact pinned legacy snapshots: 16.**

## Material directly copied into canonical repositories

### Measured Human Performance

`lineage/movement-data-logger/` contains the surviving human-readable MakeCode project source and metadata, including `main.ts`, `pxt.json`, build commands, TypeScript configuration, and test placeholder, plus a provenance README.

`fft/simulators/microbit-v2/README.md` registers the validated FFT HRM simulator and its test role while the exact full source is preserved by snapshot.

### Software-Defined Laboratory

`lineage/cloud-gsa-prototype/` contains the surviving FastAPI entry point, dependency record, and an architectural/provenance note. The note explicitly records that the historical README described additional files that are absent from the inspected GitHub snapshot.

### Bargain Bin Robotics

`exemplars/balance-bot/` contains a canonical exemplar record, the original M5Stack MIT license, the main firmware, UDP telemetry implementation, motor/encoder interface, PID implementation, calibration code, and IMU filtering code. The full repository snapshot preserves the remaining simulation, dashboard, documentation, tests, generated files, and sensor-fusion source.

### Computing Observatories

`processors/65c02/nugget-trainer/README.md` preserves the documented validated-v6 record while explicitly stating that the simulator/test/manual artifacts named by the old README were not present in that GitHub repository snapshot and therefore were not fabricated during migration.

### Nugget Physical Computing

`legacy/nugget-fwlib/README.md` records canonical ownership, attribution requirements, and the future reproducibility test while the full firmware library remains available through its pinned snapshot.

## Confirmed third-party / upstream material not absorbed as estate-authored work

The migration deliberately did **not** copy third-party forks or imported projects into canonical source trees as though they were original work. Confirmed examples include:

- `embedded_pedometer` — GitHub fork of another project;
- `science-journal-arduino` — fork of Google's Science Journal Arduino project;
- `boardlab` — fork/upstream project;
- `CodeCell` — fork/upstream project;
- `runRemote` — fork/upstream lineage;
- `tiny-basic` — fork/upstream project;
- `perfect-pic-plaground` — not marked as a GitHub fork, but its inspected historical commit is authored by `vogonpoet42`, so it is treated as imported/upstream rather than estate-authored.

Large ecosystem repositories and mirrors remain references unless an estate-specific patch, guide, or demonstrable derivative needs preservation.

## Deliberately withheld

- **IAS / Independence Assurance System:** never migrated. It remains off GitHub by governing policy.
- **`ndd2`:** private repository; not touched by this autonomous public-estate migration.

## Historical archive check

Before pinning `UMA_ARCHIVE_2026`, the migration checked its public index and searched the repository for IAS-specific terms including `IAS`, `Independence Assurance`, residence-server language, and known IAS identifiers. No matching IAS material was found in those checks. The archive is therefore pinned once under Project Atlas as provenance rather than redistributed throughout the new estate.

## What "done" means for this migration pass

The public estate now has:

- canonical homes;
- a finite control map;
- selected important source physically copied into canonical folders;
- exact immutable pointers to the complete current snapshots of the clearly relevant original public legacy repositories;
- explicit upstream/third-party boundaries;
- explicit missing-artifact notes where old documentation and old GitHub contents disagree;
- no deletion of the source repositories;
- no IAS migration.

Future work should be **verification and editorial consolidation**, not another bulk rescue operation.

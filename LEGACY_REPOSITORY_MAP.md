# Legacy Repository Map

This is a **migration map, not a deletion list**. Existing repositories remain historical evidence until their useful content is reviewed and either linked, migrated, archived, or identified as upstream.

Do not copy a repository wholesale merely because its name appears below. Preserve provenance and review public suitability first.

## Clear migration candidates

| Existing repository | Canonical estate home | Intended treatment |
|---|---|---|
| `nugget-fwlib` | `nugget-physical-computing` | preserve as validated/active lineage; migrate selected teaching material |
| `Interactive_Arduino` | `nugget-physical-computing` / `software-defined-laboratory` | classify examples by teaching vs SDL role |
| `rp2040_Experiments` | `nugget-physical-computing` / `embedded-tools` | migrate only durable examples/tools |
| `FFT-HRM-Simulator-Microbit-V2` | `measured-human-performance` | preserve simulator as FFT test infrastructure |
| `movement-data-logger` | `measured-human-performance` | review as shared measurement lineage |
| `embedded_pedometer` | `measured-human-performance` | review as gait/step lineage |
| `forth-documents` | `computing-observatories` | preserve documentation lineage |
| `eforth-stm32f4x-a` | `computing-observatories` | classify as Forth-observatory lineage/upstream |
| `zeptoforth` | `computing-observatories` | treat primarily as upstream unless estate-specific additions exist |
| `4e4th05a` | `computing-observatories` | classify as observatory lineage |
| `tachyon` | `computing-observatories` | classify as observatory/upstream lineage |
| `balance-bot` | `bargain-bin-robotics` | preserve as robotics exemplar/lineage |
| `pico_drone` | `bargain-bin-robotics` | preserve as robotics lineage |
| `wifi-car-esp8266` | `bargain-bin-robotics` | classify as historical platform target |
| `Microbit-Smart-Car` | `bargain-bin-robotics` | classify as historical platform target/upstream |
| `Tiny-bit` | `bargain-bin-robotics` | classify as historical platform target/upstream |
| `Arduino_Alvik` | `bargain-bin-robotics` | platform lineage; preserve only estate-specific work |
| `Arduino_AlvikCarrier` | `bargain-bin-robotics` | platform lineage; preserve only estate-specific work |
| `arduino-alvik-mpy` | `bargain-bin-robotics` | platform lineage; preserve only estate-specific work |
| `xrp-wpilib-firmware` | `bargain-bin-robotics` | platform lineage/upstream |
| `ESP32-Bus-Pirate` | `embedded-tools` | tool lineage; identify original vs upstream material |
| `BusPirate5-firmware` | `embedded-tools` | primarily upstream unless estate-specific work exists |
| `STC15lib` | `embedded-tools` / `nugget-physical-computing` | classify library/tool vs teaching examples |
| `pc-nrfconnect-ble` | `embedded-tools` | upstream/reference; do not duplicate wholesale |
| `NimBLE-Arduino` | `embedded-tools` | upstream/reference; do not duplicate wholesale |
| `circuitpython-ble` | `embedded-tools` | upstream/reference; do not duplicate wholesale |
| `science-journal-arduino` | `measured-world-lab` / `core-10` | historical measurement/education reference |
| `STEM-Fusion` | `core-10` | historical curriculum lineage |

## Likely upstream/reference repositories

Large third-party or ecosystem repositories such as `micropython`, `circuitpython-org`, `Arduino_Core_STM32`, `Espruino`, and `jallib` should normally remain links/upstream references rather than being copied into the estate. Estate-specific patches or teaching notes can be preserved separately with attribution.

## Needs classification before migration

The following names require content review before assigning a durable home:

- `boardlab`
- `DEXIS-Lab`
- `cloud-gsa-prototype`
- `CodeCell`
- `runRemote`
- `PhotoPizza`
- `rg_show_tipper`
- `UMA_ARCHIVE_2026`
- `no-pressure-sandbox`
- `ndd2`

## Migration decision for each legacy repository

Assign exactly one of these dispositions after review:

- **link as upstream** — external project/reference; estate depends on it but does not own its identity;
- **preserve as lineage** — useful historical evidence, no active migration needed;
- **migrate selected material** — estate-specific source/docs move under the canonical parent;
- **archive** — retain history, no current development commitment;
- **hold for classification** — insufficient evidence to decide safely.

The goal is fewer durable identities, not fewer historical records.

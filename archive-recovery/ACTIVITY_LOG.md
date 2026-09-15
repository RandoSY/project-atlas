# Archive Recovery Activity Log

**Estate recovery date:** 15 September 2026  
**Owner:** RandoSY / Randall Young  
**Purpose:** permanent, human-readable record of what was inspected, copied, pinned, classified, withheld, or left for forensic recovery during the Intellectual Estate migration.

This is a **living log**. It records meaningful archival actions, not every low-level API request. Failed or rejected connector calls that changed nothing are not treated as archival actions.

## Recovery rules used throughout

1. Preserve provenance before consolidation.
2. Never claim third-party forked code as estate-authored work.
3. Prefer exact source over summaries when recoverable.
4. Preserve old names when they are part of historical provenance, while documenting current canonical names.
5. Do not silently upgrade an untested design into a validated release.
6. Preserve missing-artifact evidence: if a source file is named in surviving documentation but cannot be recovered, record the exact filename and known context.
7. Keep IAS / Independence Assurance implementation material off GitHub.
8. Preserve old repositories until their canonical landing place and provenance are secure.

---

## Phase 1 — Canonical estate created and documented

Canonical public repositories established:

- `project-atlas`
- `software-defined-laboratory`
- `core-10`
- `nugget-physical-computing`
- `measured-world-lab`
- `measured-human-performance`
- `bargain-bin-robotics`
- `computing-observatories`
- `embedded-tools`
- `works-and-publications`

Substantive README files replaced the bootstrap placeholders in all ten repositories.

Project Atlas was made the control center with:

- `CANONICAL_INVENTORY.md`
- `LEGACY_REPOSITORY_MAP.md`
- `MIGRATION_QUEUE.md`
- `MIGRATION_LEDGER.md`
- `PROJECT_CARD_TEMPLATE.md`
- `SOURCE_SNAPSHOTS.md`
- `AUTOMATION_STATUS.md`
- `archive-recovery/PUBLIC_PROJECT_CENSUS.md`
- `archive-recovery/UPSTREAM_REFERENCES.md`
- this `archive-recovery/ACTIVITY_LOG.md`

## Phase 2 — Legacy repository ownership and provenance sweep

Original estate repositories were separated from forks/upstream material before migration.

### Verified upstream / fork references

Recorded as references rather than absorbed as estate-authored source:

- `forth-documents` -> `larsbrinkhoff/forth-documents`
- `MotioSuit` -> `alvaroferran/MotioSuit` / `bqlabs/MotioSuit`
- `PhotoPizza` -> `MakerDrive/PhotoPizza`
- `pxt-blelog` -> `bsiever/pxt-blelog`
- `tachyon` -> `forth2020/tachyon`
- `STC15lib` -> `mgoblin/STC15lib`
- `M5Stack-Core2-FactoryDemo-Upgrade` -> upstream M5Stack example lineage
- `ESP32-Bus-Pirate` -> `geo-tp/ESP32-Bit-Pirate`
- `embedded_pedometer` -> `nerajbobra/embedded_pedometer`
- `CodeCell`, `runRemote`, `tiny-basic`, `boardlab`, `science-journal-arduino`, and `perfect-pic-plaground` classified as upstream/reference or imported lineage unless file-level estate-authored additions are later demonstrated.

### Original repositories preserved as exact pinned snapshots

Complete legacy source trees were pinned at exact commits under their canonical parents where appropriate. This preserves byte-exact historical recoverability while avoiding blind duplication.

Examples include:

- `FFT-HRM-Simulator-Microbit-V2`
- `movement-data-logger`
- `nugget-fwlib`
- `rg_show_tipper`
- `balance-bot`
- Reka:Bit test/demo lineage
- `cloud-gsa-prototype`
- `DEXIS-Lab`
- Interactive Arduino/Forth package
- 65C02 STEM-Fusion record
- AVR ASM Revelator
- XC8 ASM Revelator
- RP2040 historical experiment/template repository
- micro:bit BLE UART work
- BLE UART echo/demo work
- `UMA_ARCHIVE_2026` as a single historical provenance snapshot after targeted screening for IAS terms

Pinned snapshots count as one Git tree entry in the canonical repository even when they represent many files in the original repository. This is why GitHub's visible file count substantially understates the amount of legacy source preserved by snapshot.

## Phase 3 — Selected source copied into canonical repositories

### `measured-human-performance`

- movement-data-logger MakeCode/TypeScript source and metadata copied into canonical lineage
- FFT HRM simulator registered as known-good source lineage and exact repository snapshot pinned
- original simulator validation status preserved rather than rewritten

### `nugget-physical-computing`

- `nugget-fwlib` lineage registered and complete source snapshot pinned
- `rg_show_tipper` historical teaching example pinned
- recovered Catch-the-Clock Great Cow BASIC source copied to:
  - `archive/catch-the-clock/catch_the_clock_observer_extended_metrics.gcb.txt`
- recovered Catch-the-Clock simulator copied to:
  - `archive/catch-the-clock/static_spst_555_7400_pic_simulator.html`

The Catch-the-Clock firmware preserves the architecture in which the 555 and 74LS00 remain the real timing/logic/latch hardware while the PIC observes, measures, scores, and reports. It includes 10 ms timing, period/frequency, duty cycle, attempts, hits, misses, response offset, press duration, and dashboard summary records.

### `software-defined-laboratory`

- Cloud GSA README/source/dependencies copied into `lineage/cloud-gsa-prototype/`
- exact Cloud GSA and DEXIS historical repositories pinned as source snapshots
- missing files advertised by old documentation were noted rather than invented

### `bargain-bin-robotics`

- Balance-Bot main firmware and low-level motor/encoder/control portions copied
- original M5Stack MIT attribution retained
- complete Balance-Bot source tree pinned
- Reka:Bit historical source snapshot pinned
- recovered archival text editions added:
  - `docs/archive/Bargain_Bin_Robotics_User_Guide_v0.2.0.md`
  - `docs/archive/Bargain_Bin_Robotics_Design_and_Roadmap_v0.2.0.md`

### `core-10`

Recovered runnable browser laboratories:

- `archive/virtual-labs/core12_heater_dashboard.html`
  - historical CORE12 name retained as provenance
  - current canonical curriculum root documented as CORE 10
  - thermostat/PID/open-loop thermal plant model
  - measured CSV overlay, residual/RMSE analysis, CSV/JSON/config/chart export
- `archive/probability/loaded_deck_detective_game.html`
- `archive/probability/loaded_deck_inquiry_bench.html`
- `archive/virtual-labs/README.md`

Recovered measurement artifact:

- `measurement-ladder/itty-bitty/Itty_Bitty_Teacher_Guide.pdf`

### `measured-world-lab`

Recovered searchable source editions:

- `archive/itty-bitty/teacher-guide-text-edition.md`
- `archive/singing-rule/Singing_Ruler_Microbit_Executive_Summary.md`
- `archive/singing-rule/analysis_summary_recovered.md`

The Singing Rule analysis recovery preserves surviving measured-run information from the original M5StickC Plus2 capture, including:

- input filename `m5stick_plus2_motion_2026-05-10T01-35-02-644Z.csv`
- 500 samples
- 49.90 s duration
- 10.00 Hz sample rate
- ~5 Hz Nyquist limit
- dominant ringdown estimates near 2.24 Hz
- PCA/eigen-analysis showing overwhelming one-dimensional mode dominance
- explicit statement that the raw CSV and reproduction script remain unrecovered as standalone files

### `works-and-publications`

Recovered publication:

- `papers/Executable_Transparency_Principle.md`

This preserves the physical experience -> visible executable code -> compact formal mathematics teaching framework developed around the Loaded Deck Inquiry Bench.

### `computing-observatories`

Historical Interactive Arduino/Forth and 65C02 lineage preserved as exact source snapshots. The 65C02 legacy README advertised a richer v6 package than the surviving legacy repository actually contains; that mismatch is explicitly recorded as a missing-artifact recovery problem rather than silently treating the repository as complete.

### `embedded-tools`

Exact historical snapshots pinned for:

- AVR ASM Revelator
- XC8 ASM Revelator
- RP2040 historical experiment/debug template
- micro:bit BLE UART work
- BLE UART echo/demo work

DebugWire LIGHTENING remains a protected-priority tool family whose detailed publication requires deliberate public/private review rather than automatic dumping.

## Phase 4 — Deep forensic census

A sanitized public recovery census was built from master project catalogs, historical architecture documents, GitHub, and Library artifacts. It intentionally includes dormant and nearly forgotten projects so project identity no longer depends on memory.

Recovered/named families include, among many others:

- Catch-the-Clock
- Itty Bitty / 3D Itty Bitty
- TeaTime / Beer-Lambert
- CandleLab
- Tapeless Ruler
- Singing Rule
- Loaded Deck Probability Labs
- Ghost Hand / Ghost Amp
- BrightStar Solar Tracker
- LARKIT / LARKIN
- Reciprocating-Motion Analyzer
- BLE PumpOff
- M-Chain
- Q-Meter / MAX_Q
- WiseWalking / WALKWISE
- Physics Motion Lab / IMU Motion Puck
- DeviceOps Console
- UMA Workbench
- Dashboard Commander
- Three-Tier Virtual Device Architecture
- Virtual Device Atlas / browser-native labs
- Green Robot EDU and multiple robot laboratories
- computing observatories and Forth execution environments

IAS and closely coupled private assurance/medication material are deliberately omitted from the public census and require protected off-GitHub preservation.

## Phase 5 — Exact filename forensic recovery

Old architecture appendices were mined for source trails and exact filenames. This produced recoverable evidence for artifacts whose current folder location was otherwise unknown.

### Singing Rule forensic targets

Named in surviving source trails:

- `m5stick_plus2_motion_2026-05-10T01-35-02-644Z.csv`
- `analysis_summary.txt`
- `reproduce_cantilever_analysis.py`
- `cantilever_beam_motion_analysis.zip`
- analysis image series such as `01_acceleration_components_full.png`, `07_fft_dynamic_g_ringdown.png`, `08_fft_gx_ringdown.png`, PCA plates, and related figures

The embedded `analysis_summary.txt` content was recovered even though the standalone raw CSV/script have not yet surfaced.

### Loaded Deck

Recovered actual runnable HTML, not merely documentation:

- `loaded_deck_detective_game.html`
- `loaded_deck_inquiry_bench.html`

Associated paper recovered as searchable text:

- `Executable_Transparency_Principle_Academic_Paper.pdf` -> GitHub Markdown edition

### Catch-the-Clock

Historical appendix exposed numerous exact browser-dashboard filenames plus firmware/tutorial filenames. The Great Cow BASIC source was then found as an actual standalone Library file and copied into GitHub.

Still-targeted dashboard files include historical variants such as:

- `dark_catch_the_clock_dashboard_feedback.html`
- `dark_catch_the_clock_dashboard_inputs_fixed.html`
- `dark_catch_the_clock_dashboard_logicclear.html`
- `dark_catch_the_clock_dashboard_no_output_qclear.html`
- `dark_catch_the_clock_dashboard_realtime.html`
- `dark_catch_the_clock_dashboard_redinputs.html`
- `dark_catch_the_clock_dashboard_slowclocks.html`
- `dark_catch_the_clock_dashboard_stateaware_schematic.html`
- `gsa_555_7400_pic_blackbox_sim.html`
- `gsa_555_7400_pic_blackbox_sim_active_schematic.html`
- `pastel_block_dashboard_simulator.html`
- `reworked_pushbutton_7400_pic_simulator.html`
- `static_pushbutton_555_7400_pic_simulator.html`
- `static_spst_555_7400_pic_simulator.html`

### Virtual Breadboard Thermal Control Lab

Located surviving `README_virtual_breadboard_v2_3.txt`, documenting v2.3 with four workspaces:

- Breadboard
- Program + Diagnose
- Scope + Data
- Plant + Model

The README records simulated ADC/PWM/serial activity, Arduino/CircuitPython teaching subsets, diagnostics/exports, and the RC thermal plant model. Runnable package/source remains an active recovery target.

### MSP430 Forth Observatory

Located surviving checksum record:

- `Forth_Observatory_MSP430G2553_v0.4.11_Studio_Branding_SHA256.txt`

It records the SHA-256 for:

- `Forth_Observatory_MSP430G2553_v0.4.11_Studio_Branding.zip`

The ZIP itself remains an active recovery target.

## Phase 6 — Documents and Library material

The Library has been mined for project manuals, curricula, papers, source trails, HTML applications, code, and evidence packages.

Large image-heavy PDFs/DOCX cannot always be pushed safely through the available GitHub text-oriented connector. Where byte-for-byte binary transfer is unsafe or unavailable, repository-native searchable text editions are being created with provenance notes rather than pretending a binary upload succeeded.

Mixed synthesis documents containing substantive IAS material are withheld from public GitHub rather than uploaded wholesale.

## Current recovery state

### Structurally complete or largely complete

- canonical ten-repository estate exists
- public governance and recovery rules exist
- major legacy repositories are mapped
- many original repositories are pinned at exact commits
- upstream/fork provenance is explicitly recorded
- public project census exists
- hard IAS GitHub exclusion remains intact

### Still in active deep recovery

- standalone source and binary packages named by historical documents
- old browser dashboards and virtual laboratories
- Forth Observatory ZIP/releases and checksum-matched packages
- MURL Prospector reference package/manual decomposition
- Catch-the-Clock teacher/dashboard package
- Singing Rule raw CSV/reproduction script/analysis archive
- remaining public curricula, programmer guides, simulator source, and project-specific documentation
- reconstruction of source trails for dormant projects that have only screenshots or reports remaining

## Why GitHub file counts may look low

Three reasons:

1. **Pinned repository snapshots count as one tree entry** even if the referenced repository contains dozens or hundreds of files.
2. Much of the early pass was **classification and provenance protection**, deliberately preventing accidental duplication or misattribution.
3. Some Library artifacts are **large binaries** that cannot safely be pushed by the available connector, so their content is being converted into searchable text/source editions where appropriate.

The next phase deliberately favors visible canonical file growth: recover actual source, manuals, HTML applications, text editions, manifests, and README/runbook material into canonical folders while keeping snapshot pointers for byte-exact historical provenance.

## Completion criterion

The recovery is not considered done merely when every known repository has a pointer. It is done when each known public project family has one of these explicit outcomes:

- source recovered and placed canonically;
- exact historical snapshot preserved;
- documentation/evidence recovered and source marked missing;
- verified upstream/reference only;
- deliberately archived/held;
- or deliberately excluded from public GitHub under the protected-system boundary.

No named project should simply disappear from the record.

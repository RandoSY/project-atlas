# Intellectual Estate Deep-Recovery Log — 16 September 2026

This dated supplement continues `ACTIVITY_LOG.md`. It records substantive archival outcomes, not every connector/API call.

## Public/protected boundary maintained

- IAS / Independence Assurance System remains excluded from public GitHub.
- Comics or synthesis documents that cross the IAS boundary are preserved in the protected Library recovery area rather than published.
- DebugWire LIGHTENING implementation remains protected from automatic source publication.
- No original Library files or legacy repositories were deleted.

## Comic and illustrated-story recovery

The visual corpus was treated as first-class estate material rather than decoration. Generic generated filenames were grouped by timestamp and visually classified so multi-page sets were not separated.

Organized preservation reached approximately **150 copies**, about **127 public-safe** and **23 protected/off-GitHub**. Complete public sets identified/preserved include, among others:

- NOTHING IS FREE — 10 pages
- SUPER + MCP + AI — 10 pages
- Why Build SUPER? — 10 pages
- ChairBreak MFS — 6 pages
- Entropy in a Pop-Can Calorimeter — 10 pages
- Entropy Made Visible — 10 pages
- The Fidelity Progression — 6 pages
- One Phenomenon, Many Realizations — 6 pages
- The Core Twelve — Revised — 10 pages, preserved as historical naming
- One Relationship, Three Experiments — 10 pages
- From Simple Activities to the Story of Physics — 10 pages
- Entropy: More Than a Messy Sock Drawer — complete sequence recovered

`Entropy: Why It Had To Be Discovered` remains 9/10 with page 10 a named forensic target.

Large bound/standalone illustrated artifacts preserved include *From One Bit to Wireless Wonders*, the Agnes Pockels graphic novel, Experience Before Equation, Microcontroller Senses, M5Chain/UART material, surface-tension stories, and related visual teaching pieces.

## CORE 10 corpus physically populated

Repository-native text/source recovery materially expanded `core-10`:

- Curricular Threads Architecture Proposal — four ordered parts + index
- Kitchen Inquiry Lab — two ordered parts + index
- Six-Lab Learning Trajectory — three ordered parts + index
- One Cup Chemistry Teacher Manual v0.2 — complete ordered text edition
- One Cup Chemistry Student Lab Book v0.2 — complete ordered text edition
- Loaded Deck Inquiry Bench — runnable HTML
- Loaded Deck Detective Game — runnable HTML
- historical CORE12 thermal-control browser lab — runnable HTML with provenance note that CORE 10 is current
- Itty Bitty teacher material

Historical CORE12 wording is retained where it is part of source provenance; it is not treated as the current curriculum root.

## SUPER SDL / CRCL / Observatory recovery

`software-defined-laboratory` now contains recovered SUPER SDL v0.7.0 guide/hash/versioning material in addition to the Cloud GSA and DEXIS lineage snapshots.

`computing-observatories` recovery added:

- CRCL v0.6.1 classroom guide
- CRCL v0.6.1 validation record
- Reality View template/schema
- recovered CRCL translator source
- DP17 checksum record
- DP17 QA run record
- additional Forth Observatory executive/bundle/QA/checksum records

## Virtual Breadboard Thermal Control Lab

Recovered the actual standalone Virtual Breadboard Thermal Control Lab application and its programmer documentation. The browser application is preserved losslessly in the estate recovery path with provenance/usage documentation. It models the measure → convert → decide → PWM → wait control loop and supports Arduino/CircuitPython teaching subsets while explicitly remaining a teaching interpreter rather than a full compiler/runtime.

## MURL Prospector recovery

`bargain-bin-robotics` now contains both a decomposed searchable manual and surviving MicroBlocks source modules for MURL Prospector:

- main Robot Passport project
- MURL Core
- Safety Service
- Evidence Service
- Motion Service
- Cutebot adapter
- Cutebot profile

The recovered profile's `COMMISSIONING-UNVERIFIED` status is preserved; recovery did not upgrade it to validated.

## Catch-the-Clock recovery

`nugget-physical-computing` was expanded from one historical observer/source record into a much fuller teaching package. Newly recovered and committed:

- reviewed PIC16F18424 Great Cow BASIC observer/reporter firmware
- original extended-metrics observer source
- multiple runnable browser simulators including static pushbutton and GSA 555/7400/PIC black-box variants
- firmware applied-review text edition
- two-part *From 555 Timer to Reaction-Time Instrument* teacher tutorial

The architectural principle is preserved: the 555 remains the timing hardware, the 74LS00 latch remains authoritative logic/memory, and the PIC observes/reports rather than pretending to replace the physical lesson.

## 65C02 Nugget major forensic recovery

The original legacy GitHub snapshot contained only a README, but the Library still held the missing application/curriculum lineage.

### Validated v6 recovered

Recovered:

- `65c02_nugget_simulator_validated_v6.html` — actual 151,577-byte standalone browser simulator
- `EXTERNAL_VALIDATION_REPORT_v6.md`
- `TEST_RESULTS.md`
- Instructor Curriculum Guide
- Student Laboratory Workbook
- Assessments, Rubrics and Answer Key
- complete bound curriculum volume

The exact v6 simulator is preserved on GitHub as a deterministic gzip/base64 chunk archive with reconstruction instructions and integrity verification. The migrated project README was corrected so it no longer says those artifacts are missing.

The curriculum describes 36 lessons, 24 primary labs, 6 projects, 8 unit checks, midterm, final, capstone and oral defense using the Predict → Execute → Observe → Explain → Rewind → Modify → Validate instructional model.

### v7 lineage recovered

Committed surviving release records for:

- Version 7 VIA experiment-board release
- v7 compact tabbed workspace revision

Recorded validation includes JavaScript syntax/browser checks, integrated Test Lab 8/8, and representative VIA functional tests. These v7 records remain distinct from v6's validation claims.

### v8 Forth Lab lineage recovered

Recovered the v8 Forth Lab lineage and committed its `START_HERE` guide. It explicitly distinguishes the interactive host-side bring-up Forth from a historical CPU-resident FIG kernel and provides a separate compatibility route for historical 64K images.

Latest located representative HTML: `65c02_nugget_forth_lab_v8_5.html` (155,330 bytes), SHA-256 `0c1308426aa542786db01ececa2be9c5b34f14c0e06bd904fb8960b1ec94a69c`.

### v9 Studio lineage recovered

Recovered the v9 Studio sequence through v9.4.1. Committed:

- `QUALITY_AUDIT_v9_4_1.md`
- `DEBUGGER_STUDIO_GUIDE.md`
- `RG_SHOW_10BIT.asm`
- `RG_SHOW_10BIT.fth`

The audit records repaired debugger side effects, STP behavior, reversible trace branching, interrupt trace origin and W65C02 decimal ADC flag handling, plus a 25/25 built-in self-test and representative R&G protocol matrix.

Latest located representative HTML: `65c02_nugget_studio_v9_4_1.html` (232,872 bytes), SHA-256 `997e97dbbbf3ae38b4031f08012fd40d966e22b8711c0606b08d13a90c70f382`.

The large v8/v9 HTML originals remain safely located in the Library/recovery workspace; exact GitHub mirroring remains an active transfer item.

## Known unresolved forensic targets after this pass

- Singing Rule raw CSV `m5stick_plus2_motion_2026-05-10T01-35-02-644Z.csv`
- Singing Rule `reproduce_cantilever_analysis.py`
- Singing Rule full analysis ZIP/images
- missing page 10 of *Entropy: Why It Had To Be Discovered*
- remaining Catch-the-Clock historical dashboard variants
- exact current Forth Observatory ZIP packages matching recovered checksum records
- further large browser applications and release ZIPs whose names are now known but whose exact GitHub transfer is pending
- public-safe comic image mirroring to GitHub (organized Library preservation is substantially further ahead than GitHub image mirroring)

## Recovery-method note

The deep-recovery method now uses surviving manuals, architecture appendices, manifests, screenshots, release notes and exact filenames as forensic indexes. A project is not treated as absent simply because its old GitHub repository is sparse. Exact filenames are searched across the Library; executable/source artifacts take priority over summaries; and missing files are logged explicitly rather than silently disappearing.

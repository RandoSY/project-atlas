# Intellectual Estate Recovery — Evening Checkpoint

**Date:** 16 September 2026  
**Status:** ACTIVE  
**Working overall estimate:** ~55% of the recoverable public-safe estate organized and/or physically represented in the canonical preservation system.

This checkpoint supplements `ACTIVITY_LOG.md` with the major recoveries completed after the earlier log sections were written.

## Major recoveries completed in this pass

### Comic / illustrated estate

A recursive Library census verifies:

- **131 public-safe preservation copies**
- **23 protected/off-GitHub preservation copies**
- **154 total organized preservation copies**

Complete multi-page sets, bound graphic novels, standalone illustrated explanations, and historical curriculum comics are preserved. `Entropy: Why It Had To Be Discovered` remains 9/10; page 10 is an explicit forensic target. Protected visual material remains deliberately off GitHub.

### CORE 10 and sibling curriculum

The canonical `core-10` repository now physically contains substantial recovered curriculum rather than only an inventory:

- Curricular Threads Architecture Proposal — four ordered text parts plus index
- Kitchen Inquiry Lab — two ordered parts plus index
- Six-Lab Learning Trajectory — three ordered parts plus index
- One Cup Chemistry Teacher Manual v0.2 — complete ordered text edition
- One Cup Chemistry Student Lab Book — complete ordered text edition
- Loaded Deck runnable probability laboratories
- historical thermal-control browser laboratory
- Itty Bitty measurement material

Historical CORE12 filenames are retained where they document provenance; CORE 10 remains the current canonical curriculum root.

### Bargain Bin Robotics / MURL Prospector

Recovered and placed canonically:

- Bargain Bin Robotics user guide and design/roadmap
- Balance-Bot source lineage with original attribution
- MURL Prospector operator/programming manual split into browsable chapters
- MURL main Robot Passport source
- Core, Safety, Evidence and Motion services
- Cutebot adapter and profile

The recovered MURL profile remains explicitly `COMMISSIONING-UNVERIFIED`; recovery did not upgrade its validation status.

### Virtual Breadboard Thermal Control Lab

The surviving v2.3 browser laboratory and programmer documentation were recovered. The application implements the Breadboard, Program + Diagnose, Scope + Data, and Plant + Model workspaces and preserves the teaching-subset Arduino/CircuitPython transfer model.

### CRCL / Forth Observatory

Recovered material now includes:

- CRCL v0.6.1 classroom/release validation material
- Reality View schema
- recovered CRCL translator source
- Forth Observatory DP17 QA and checksum records
- MSP430 bundle/checksum and later QA evidence
- surviving Forth Observatory executive/start-here documentation

### Catch-the-Clock

This project is now represented by actual source and runnable artifacts, not merely historical descriptions:

- original extended-metrics Great Cow BASIC PIC observer
- reviewed PIC16F18424 observer/reporter firmware
- `static_spst_555_7400_pic_simulator.html`
- `static_pushbutton_555_7400_pic_simulator.html`
- `gsa_555_7400_pic_blackbox_sim.html`
- recovered teacher tutorial text edition
- recovered firmware applied-review text edition

The physical 555 + 74LS00 timing/logic/latch remains authoritative in the recovered architecture; the PIC observes and reports rather than replacing the lesson.

### 65C02 Nugget — major deep recovery

The sparse legacy GitHub snapshot did **not** represent the surviving estate. Deep Library recovery found and preserved a much richer body of work.

Recovered validated-v6 baseline:

- actual standalone `65c02_nugget_simulator_validated_v6.html`
- external validation report
- test results
- exact reconstructable compressed simulator archive with hashes and reassembly instructions
- project README corrected so it no longer incorrectly reports the simulator as missing

Recovered curriculum:

- 52-page Instructor Curriculum Guide
- 73-page Student Laboratory Workbook
- 13-page Assessments / Rubrics / Answer Key
- bound complete-curriculum edition discovered
- complete extracted text of the three principal curriculum volumes preserved as deterministic gzip/Base64 GitHub archives with reconstruction instructions

Recovered later lineage:

- v7 release-note material
- v8 Forth-Lab documentation / descendants
- v9 Debugger Studio documentation, quality audit, and example assembly/Forth sources
- surviving exact `65c02_nugget_forth_lab_v8_5.html` and `65c02_nugget_studio_v9_4.html` located in the Library and staged for exact archival transfer

The validated-v6 baseline and later descendants are kept distinct so validation claims do not silently propagate to later revisions.

## Important still-open forensic targets

- Singing Rule raw CSV `m5stick_plus2_motion_2026-05-10T01-35-02-644Z.csv`
- Singing Rule `reproduce_cantilever_analysis.py`
- Singing Rule complete analysis ZIP / original figure set
- `Entropy: Why It Had To Be Discovered` page 10
- remaining named Catch-the-Clock historical dashboards
- exact Forth Observatory package ZIPs where only checksum/QA records currently survive
- additional dormant-project source named by the Public Project Census

## Public/private boundary remains intact

- IAS / Independence Assurance implementation material is not published to GitHub.
- Mixed IAS-containing documents and comics are preserved in the protected Library archive rather than uploaded wholesale.
- DebugWire LIGHTENING implementation remains protected from automatic publication.
- third-party upstream/fork material remains attributed as upstream/reference.

## Completion marker

Recovery is **not complete**. `archive-recovery/RECOVERY_STATUS.md` is the live status file.

Final closure will be represented by a root-level `RECOVERY_COMPLETE.md`. Until that file exists, the estate recovery should be regarded as active.

# CORE 10 / CORE 12 Intellectual-Estate Preservation — Progress Addendum
**Checkpoint:** 2026-11-03. **Scope:** Public author-owned curriculum and physical-computing source; protected/private and third-party licensed material excluded.

> This addendum updates the *state of publication* without rewriting the original dated baseline. Historical SHA-verified manifests remain frozen. It is not a declaration that every project in the user's Library has been recovered.

## Verified original publications newly preserved

| Family | Original publication state | Location |
|---|---|---|
| One Cup Chemistry v0.2 | Original branded teacher and student PDFs and exact complete 4,311,975-byte source ZIP preserved in 5 verified binary parts; reconstruction script tested by GitHub Actions | [Original PDFs](https://github.com/RandoSY/core-10/tree/main/one-cup-chemistry/original-editions), [complete release parts and rebuilder](https://github.com/RandoSY/core-10/tree/main/one-cup-chemistry/releases/v0.2) |
| One Cup Chemistry OCC-00..19 | Complete teacher experiment compendium plus 15 independent standalone guides. Original 8 teacher and 10 student Markdown archive segments retained | [Experiment index](https://github.com/RandoSY/core-10/blob/main/one-cup-chemistry/experiments/README.md) |
| Core12 PRO Unit 8, Flux | Illustrated original 18-page, 7,152,568-byte PDF preserved in 8 verified binary parts, with a working rebuilder | [Original illustrated PDF recovery](https://github.com/RandoSY/core-10/tree/main/recovered-publications/CORE12_PRO_Unit_8_Flux_Original_2026) |
| Kitchen Inquiry Lab | Original editable DOCX and four exact original PDF guides for measurement, energy and the Human Candle; plus cooling-to-living-molecules PDF | [Kitchen originals](https://github.com/RandoSY/core-10/tree/main/kitchen-inquiry-lab/original-editions), [One Cup originals](https://github.com/RandoSY/core-10/tree/main/one-cup-chemistry/original-editions) |
| Cooling Curves, Brines and AI | Original PDF, byte-identical source archived | [Original PDF](https://github.com/RandoSY/core-10/blob/main/one-cup-chemistry/original-editions/Cooling_Curves_Brines_AI_Reasoning_Teachers_Guide.pdf) |
| Microwave Water Heating | Original v0.1 authored Markdown handoff committed; still labeled draft without independent classroom evidence | [Core10 handoff](https://github.com/RandoSY/core-10/blob/main/kitchen-inquiry-lab/CORE10_Microwave_Water_Heating_Handoff_Packet_v0.1.md) |
| NIF Web Lab v0.3 | Exact author-source ZIP archived; README warns that historical development secrets/cookie defaults require hardening before deployment | [NIF release](https://github.com/RandoSY/core-10/tree/main/nothing-is-free/releases/v0.3) |
| SUPER SDL v0.5 | Exact archived source ZIP with dynamic Newton Cooling experimental capability and MCP simulation | [SUPER v0.5 archive](https://github.com/RandoSY/software-defined-laboratory/tree/main/archive/super-sdl-v0.5.0) |
| LAB-12 v1.2 | Chrome dashboard, Pico firmware, MSP430 acquisition, protocol/teacher/wiring docs and tests; curated direct 93,091-byte ZIP with 45 original source/documentation files | [LAB-12 tree](https://github.com/RandoSY/software-defined-laboratory/tree/main/platforms/lab12-pdp12-linc/v1.2) |
| UNO/MFS Desktop Lab Controller v1.2 | Original 610,228-byte professional user PDF published alongside existing v1.2 source recovery | [Professional user guide PDF](https://github.com/RandoSY/nugget-physical-computing/blob/main/archive/uno-mfs-desktop-lab-controller/v1.2.0/docs/UNO_MFS_Desktop_Lab_Controller_Professional_User_Guide_v1.2.0.pdf) |

## Verification and monitoring

- **89 public files** were covered by six Project Atlas manifests at this checkpoint (39 prior baseline + 27 original One Cup files + 12 Core12/LAB12 files + 6 Kitchen originals + 5 NIF/SUPER/UNO release entries).
- [Project Atlas automated SHA-1 Git blob verification passed](https://github.com/RandoSY/project-atlas/actions/runs/41706695665); checks pinned historical bytes weekly and on relevant manifest changes. A successful check means **tracked** files still match; it is not evidence that all Library assets are tracked.
- [Core10 reconstruction test passed](https://github.com/RandoSY/core-10/actions/runs/41705399540), verifying exact full SHA-256 of the reconstructed One Cup ZIP and original illustrated Flux PDF from stored binary pieces.
- A separate weekly ChatGPT archive-gap audit was set up to compare recently surfaced curriculum/project resources with GitHub publication, with human review before publishing candidates.

## Important remaining gaps — do not overclaim

1. The complete historic **409-entry LAB-12 v1.2 original ZIP** remains in the ChatGPT recovery copy, not GitHub as a single byte-identical original. The committed **curated 45-file source ZIP** retains the important code/docs but excludes compiler outputs, large images and other historical material.
2. Other early Core12 experiments and related editions remain in the Library/history and must be triaged against the public repositories. Priority candidates include **NIF v0.2**, **OCC thermal bar v3**, **UNO/MFS controller editable v1.2 documents**, **SUPER v0.4 and Pico W experiments**, **pendulum/water-clock**, **TeaTime/Beer-Lambert**, **pop-can calorimeter** and **Purple Power**.
3. Source archival, physical build validation, classroom-ready student/teacher release, app-store distribution and **off-GitHub immutable backup** are separate completion criteria. This archive pass does not certify them.
4. Avoid publishing historical third-party PDP-12/LINC manuals, private project tracking, student/health data, credentials, or vendor binaries without rights assessment.

## Long-term policy
Treat source as the provenance reference, retain original byte hashes, use new paths rather than overwrite historical versions, keep a running experiment ID registry, flag safety/provenance/reproducibility levels accurately, test reconstructed releases and run independent backups beyond GitHub.

**Recommended preservation priority:** publish missing original authored guides and code from the backlog; keep development/private work unlisted until privacy and rights review; continue weekly automated check and proactive gap audit.

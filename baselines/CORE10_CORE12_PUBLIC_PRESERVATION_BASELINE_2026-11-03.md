# Public Intellectual Estate Baseline — 2026-11-03

**Scope:** CORE 10 (including historical CORE 12), Kitchen Inquiry Lab, One Cup Chemistry, shared SDL/SUPER instruments, and complementary physical-computing curricula.  
**Owner:** RandoSY. **State:** verified partial public baseline, not a claim of complete archival publication.

## Preservation contract
- Preserve **experience before equation**, **need before technology**, and the learner's actual measured evidence.
- Never overwrite a working version simply to modernize it. Keep chronology, sources, limits, instructions, and checksums.
- Every experiment deserves a permanent ID, question, materials, procedure, safety, hardware/firmware/browser files, raw observations, analysis, teaching guide, and reproducibility evidence.
- Distinguish *indexed*, *source archived*, *formatted artifact published*, *hardware verified*, and *release reproduced*. They are different claims.
- Respect third-party copyright: link to historical manuals; do not republish copies without distribution rights.
- Keep protected/private systems **out of public GitHub**. Do not include sensitive configurations, credentials, personal health records or private measurements.

## Canonical public GitHub homes
- [CORE 10](https://github.com/RandoSY/core-10): Kitchen Inquiry Lab, One Cup Chemistry, Nothing Is Free, curriculum maps, historical CORE12 thread
- [Software-Defined Laboratory](https://github.com/RandoSY/software-defined-laboratory): SUPER/MCP, dynamic instruments, the new LAB-12/PDP-12/LINC cooling instrumentation
- [Measured World Lab](https://github.com/RandoSY/measured-world-lab): foundational measurement and sensor/virtual-lab material
- [Nugget Physical Computing](https://github.com/RandoSY/nugget-physical-computing): UNO/MFS, MSP430 sensor/learning laboratories and controller code
- [Bargain Bin Robotics](https://github.com/RandoSY/bargain-bin-robotics): low-cost realization and science missions
- [Computing Observatories](https://github.com/RandoSY/computing-observatories): historical computer/language teaching observatories
- [Works and Publications](https://github.com/RandoSY/works-and-publications): authored publication inventory (release editions require audit)

## Verified published and committed
1. **OCC Teacher Manual v0.2** is archived as eight Markdown parts, and **Student Lab Book v0.2** as ten parts in CORE 10. [Newton Cooling OCC-02 teaching text](https://github.com/RandoSY/core-10/blob/main/one-cup-chemistry/archive/Teacher_Manual_v0.2/part-03.md).
2. CORE 10's Kitchen Inquiry Lab canonical map and curriculum historical sections exist.
3. CORE 10's thermal-control virtual breadboard (compressed source), heater dashboard, and Core12 fidelity-mirror ESP32-C3 source exist.
4. Core10 microwave water-heating handoff v0.1 is committed as [Markdown](https://github.com/RandoSY/core-10/blob/main/kitchen-inquiry-lab/CORE10_Microwave_Water_Heating_Handoff_Packet_v0.1.md); source explicitly labels it a draft, independent handoff not yet recorded.
5. [CORE12 PRO Unit 8: It's All About the Flux — text-only transcription](https://github.com/RandoSY/core-10/blob/main/recovered-publications/CORE12_PRO_Unit_8_Its_All_About_the_Flux.text.txt). This is not the illustrated PDF.
6. [LAB-12 v1.2 Chrome Web Serial dashboard](https://github.com/RandoSY/software-defined-laboratory/blob/main/platforms/lab12-pdp12-linc/v1.2/dashboard/lab12_dashboard.html) and [precision graph guide](https://github.com/RandoSY/software-defined-laboratory/blob/main/platforms/lab12-pdp12-linc/v1.2/documentation/PRECISION_GRAPH_GUIDE.md) are committed.
7. MSP430G2553 learning-lab source tree, guides, releases, and checksum text exist within Nugget Physical Computing.
8. SDL SUPER v0.7 archival guide, SUPER v0.8 integrity evidence, and current SDL bridge/platform structure exist. They need a separate reproducible-release test.

## Protected curriculum experiment inventory (preserve these identities)
| ID / family | Scientific question or primary activity | Baseline status |
|---|---|---|
| Water Standard | mass, volume, reference measurement and uncertainty | indexed; verify standalone lesson |
| Galileo ramp / water clock | time, motion, calibration | indexed; locate complete package |
| Predictive Mixing | energy accounting before equation | indexed; locate complete package |
| Newton Cooling / OCC-02 | time series, cooling constant, ambient, residuals | teacher text committed; LAB-12 work in progress |
| Microwave Water Heating | heat, useful energy, cost, input versus output | v0.1 handoff committed; verify classroom data |
| Tea-light / pop-can calorimeter | transfer of fuel energy to water | indexed; complete illustrated guide needs audit |
| TeaTime / Beer-Lambert | color, concentration, light intensity | indexed; locate source + experiment |
| Vinegar / baking soda and yeast CO2 | gas production and quantity | indexed; locate source + experiments |
| Purple Power | chemistry/color reaction | indexed; locate source |
| Singing Rule | frequency, vibration, calibration | indexed; locate source |
| Avogadro / monolayer / surface film | geometry, counting, molecule estimate | One Cup Chemistry bundle contains OCC-07 soap-film edition; binary upload pending |
| Diffusion / Boltzmann / Entropy | distribution and statistical behavior | indexed; locate source |
| Oak Tree / Open Systems | energy and matter flux | indexed; locate source |
| Newton/RC thermal analog, insulation, thermostat | dynamic systems and heating control | indexed; virtual-lab source in CORE10 |
| Nothing Is Free | batteries, motors, devices, charging, household energy | canonical map present, release pending |

An index entry does **not** assert that the associated PDF, code or data has been published.

## Verified original binary artifacts awaiting a GitHub upload path
The following author-source originals exist in the Library and have been inspected or checksum-verified, but their complete bytes are **not** shown as published in this baseline:
- `LAB12_PDP12_LINC_Cooling_Lab_Compilation_v1_2.zip` — **3,396,254 bytes**, SHA-256 `2f7e3ab946e3e495895293abf5c1a3dcd063c87bae75fa88356a1c9078fce381`, 409 ZIP entries. The release itself says new hardware integration is not target/bench verified.
- `One_Cup_Chemistry_Complete_Bundle_v0_2.zip` — **4,311,975 bytes**, SHA-256 `047d7bd32a49b7bd78137736b270d699263c8c0ac859424398373988ce86525b`; includes formatted teacher/student editions, DOCX source, teaching package and publication art.
- `CORE12_PRO_Unit_8_Its_All_About_the_Flux.pdf` — **7,152,568 bytes**, SHA-256 `68e58cd5cc4434b7466b32509782b1fe792c9bd1e6caf168d427f0f3a23bc100`; illustrations are not in the text transcription.
- `Cooling_Curves_Brines_AI_Reasoning_Teachers_Guide.pdf` — **492,368 bytes**, SHA-256 `5c0f4703c4eee64b95a1044019d422ebf3a1a66dd22d31736d78161bdc577792`.
- `CORE10_Microwave_Water_Heating_Handoff_Packet_v0.1.md` — **6,164 bytes**, SHA-256 `1e61e25caeaebfba57211be49cceb6d7ff7cf0aa47ca5eabfc1c9a1028a6dac8`; Markdown published separately.

## Publication acceptance gate
A public `complete` badge requires: original or reconstructable source + checksum, licenses/rights, dependency manifest, teachable run instructions, recorded sample data, test evidence and (where claimed) a physical bench run. No badge should be inferred just from a repository URL.

## Next recovery queue
1. Publish complete author's LAB-12 v1.2 source and test files, add hardware verification separately.
2. Publish the formatted One Cup Chemistry PDFs and source DOCXs as a versioned release, preserving visual fidelity.
3. Finish recovery of older Core12 illustrated guides and Kitchen Inquiry Lab lesson packages.
4. Consolidate experiment IDs, source files, checksums, license notes and evidence without erasing older branches.
5. Verify release reproducibility and archive off-site immutable copies.

**Status methodology:** repository trees and specific files were inspected on 2026-11-03; Library originals were recovered and checksum-verified. This baseline is deliberately an *audit receipt*, not a substitute for the missing source files.

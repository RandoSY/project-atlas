# Idea Card — Laboratory Legible to AI

## Name

**When the AI Can See the Experiment** / **STEP + SUPER** / **continuous intelligent assistance as a laboratory design assumption**.

## Problem

Most educational AI sits outside the physical experiment. It explains, chats or analyzes data after a learner manually transfers information. This keeps AI disconnected from the instrument-derived evidence that actually constrains scientific claims.

## Central idea

Make the laboratory **legible to AI** through bounded, self-describing instrument capabilities while keeping the same measurements visible to the learner.

The AI becomes another client of the measurement layer, not the source of evidence.

## Why it matters

Instrument-connected assistance can reduce the friction between a spontaneous question and a valid experiment. Curiosity that would normally die because procedure, analysis or code would take too long can become an evidence-producing branch while the experiment is still active.

## How it works

STEP cycle:

**Sense → Test → Explain → Propose → repeat**

Architecture:

**physical instrument layer → common semantic functions → human dashboard + bounded AI tool interface**

Measured, simulated, calculated and inferred values remain distinguishable.

## Why this design

The architecture deliberately keeps AI from becoming the laboratory itself.

- instruments provide measurements;
- AI proposes, calculates, compares and coordinates permitted tools;
- humans retain goals, safety authority and consequential authorization;
- physical limits belong in deterministic tool/firmware layers;
- the human instrument remains fully usable without AI.

## Distinctive contribution

The key construct is **intellectual branching cost**: the effort required to transform an unanticipated question into a scientifically coherent evidence-producing extension.

The proposed educational value of AI is primarily lowering that cost while preserving evidentiary discipline—not automation for its own sake.

## Representative evidence

- `works-and-publications/papers/When_AI_Can_See_the_Experiment_IDEA_RECORD.md`
- `software-defined-laboratory/IDEAS.md`
- SUPER SDL guides and protocol records
- Cloud GSA / DEXIS lineage
- browser instrument and MCP concepts
- cooling/brine reference experiment

## Evolution

The work progressed from declaratory dashboards and networked laboratory nodes toward a shared evidence layer that both humans and AI can access. MCP became a useful implementation mechanism, but the durable idea is broader than MCP.

## Limits / unfinished work

The framework is a research proposition, not evidence that AI-connected labs improve learning. Risks include over-trust, reduced learner agency, unsafe actions, network/privacy issues, measurement errors and decorative rather than productive branching.

## Reconstruction path

1. Build one reliable physical measurement.
2. Give the learner a direct visible dashboard.
3. Expose the same logical measurement through a small machine-readable tool interface.
4. Label provenance and units.
5. Begin read-only/read-heavy.
6. Require human confirmation for consequential actions.
7. Create a simulator with the same tool names.
8. Compare dashboard-only, ordinary-chat, and instrument-connected inquiry behavior.

## Compact rule

**Do not add AI to the laboratory as a separate attraction. Make the laboratory legible to AI, then let AI earn its place against real evidence.**

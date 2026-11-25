# Research trace audit protocol — initial specification

**Purpose:** convert the history behind Architectural Economy V7 into an auditable dataset for The Augmented Investigator. This is a proposed protocol, not a completed audit or preregistration.

## Evidence collection and privacy

Retain complete relevant ChatGPT and Gemini/Antigravity exports, manuscript versions, commits, execution logs, datasets, generated code, corrections, failed runs, negative findings and author decisions. Record source pointer, SHA-256, timestamp/timezone, model/version if known, data license and access status. Preserve private originals; publish only consented and redacted records. Do not include unrelated personal information or any protected estate implementation. Do not treat missing evidence as proof of absence.

## Episode coding

An episode consists of a recorded question, proposed method, execution/evaluation and decision. Proposed CSV schema:

```csv
episode_id,source_id,start_timestamp,end_timestamp,active_minutes,question_origin,method_origin,implementation_origin,decision_origin,method,artifact_ref,execution_ref,verification_status,error_type,correction_ref,result_direction,disposition,missing_fields
```

Use human / ChatGPT / Gemini-Antigravity / other / joint / unclear categories for attribution. Use observed evidence rather than inference; distinguish cosmetic edits from substantive changes. Independently double-code and report agreement; retain adjudication records. Distinguish wall-clock latency from active effort, and manuscript-reported results from independently executed outputs.

## Metrics

| Construct | Operational measure |
|---|---|
| Scientific agility | Question-to-reviewable-evidence latency; wall-clock and active effort separately |
| Methodological reach | Distinct validated methods and evidence of prior capability |
| Iteration | Trace-linked substantive changes to hypotheses, methods or interpretations |
| Human agency | Origin and disposition of decisions; joint or unclear allowed |
| Epistemic integrity | Errors, corrections, unfavorable outcomes, uncertainty and reproduction |
| Research economy | Active effort, compute and external review costs, error remediation |

## Verification

Independently reproduce network and PDP-8 benchmarks and genomic H2 pilot with pinned data, dependency versions and documented commands. Check data licensing, cohort flow, statistical specification, leakage and results. Record discrepancy and resolution. Verify manuscript citations before submission.

## Prospective comparison

Compare equivalent tasks under human-only and AI-assisted conditions, with randomized or counterbalanced order where feasible, equivalent resources, blinded expert quality ratings, time, errors and correction cost. Account for learning/carryover. N-of-1 results are not a population estimate. Seek applicable ethical review and approval before collecting new participant data.

## Current completion

Selected manuscript excerpts and author statements inspected; V7 canonical publication text and manifest located. No full transcript audit, independent reproduction, counterfactual comparison or corpus-wide timing analysis completed.

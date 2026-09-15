# Source Snapshots and Recovery

The canonical Intellectual Estate repositories use Git submodules under `source-snapshots/` to preserve exact legacy repository commits without flattening their history into the new taxonomy.

## Clone a canonical repository with its historical snapshots

```bash
git clone --recurse-submodules https://github.com/RandoSY/project-atlas.git
```

Use the same `--recurse-submodules` option for any canonical repository that contains a `source-snapshots/` directory.

If a canonical repository was cloned without submodules:

```bash
git submodule update --init --recursive
```

## Why snapshots are pinned this way

A legacy repository may contain:

- binaries, images, PDFs, generated artifacts, or old editor formats;
- an independent commit history worth preserving;
- third-party attribution that should not be obscured;
- historical naming that should remain recoverable but should not define the current architecture.

A Git submodule records the exact source commit while allowing Project Atlas to place that history beneath a durable current parent.

## Important limitation

A gitlink is an exact commit reference, not a physical duplicate of the legacy repository's objects inside the canonical repository. The original legacy repositories are therefore intentionally being left intact. Do not delete them merely because a snapshot has been registered.

For especially important projects, selected source and documentation are also copied directly into canonical folders. The pinned source repository remains the provenance record until a later integrity-preserving archival process deliberately makes a self-contained mirror.

## Current snapshot homes

- `project-atlas/source-snapshots/` — broad historical archive provenance
- `software-defined-laboratory/source-snapshots/` — SDL/GSA/lab ancestors
- `nugget-physical-computing/source-snapshots/` — Nugget learning/firmware lineage
- `measured-human-performance/source-snapshots/` — FFT and movement-measurement lineage
- `bargain-bin-robotics/source-snapshots/` — robot exemplars/platform lineage
- `computing-observatories/source-snapshots/` — visible-computing/Forth/processor lineage
- `embedded-tools/source-snapshots/` — debuggers, analyzers, bridges, and experimental tools

See `MIGRATION_LEDGER.md` for the exact repository and commit assigned to every snapshot.

## Preservation rule

A snapshot answers: **what exactly existed?**

A canonical folder answers: **what should a future person use and maintain?**

Those are different questions. Keeping them different is intentional.

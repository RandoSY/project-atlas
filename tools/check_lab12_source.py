#!/usr/bin/env python3
"""Verify the published LAB-12 v1.2 source snapshot.

This check is separate from the Core 10 curriculum baseline. It pins Git blob
identities of committed source files, without claiming that the complete
original ZIP or unverified hardware behavior has been released.
"""
import json
import pathlib
import sys
from check_public_archive_baseline import fetch_entry, git_blob_sha1

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "baselines" / "verified_LAB12_source_2026-11-03.json"

def main() -> int:
    index = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    for e in index["artifacts"]:
        name = e["repo"] + ":" + e["path"]
        try:
            data = fetch_entry(e)
            actual = git_blob_sha1(data)
            if not data or actual != e["expected_git_blob_sha1"]:
                raise ValueError("missing, empty or modified Git blob")
            print("OK ", name)
        except Exception as exc:
            failures.append((name, str(exc)))
            print("FAIL", name, str(exc), file=sys.stderr)
    print(f"LAB-12 checked {len(index['artifacts'])} paths, {len(failures)} failures")
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())

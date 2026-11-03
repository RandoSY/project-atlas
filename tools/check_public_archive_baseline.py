#!/usr/bin/env python3
"""Verify published public curriculum archive files against a dated Git baseline.

This program is intentionally read-only: it does not update, rewrite, publish,
or remove files. It distinguishes an immutable archive's exact content from a
living canonical map's requirement to exist.

Usage: python tools/check_public_archive_baseline.py
"""
import hashlib
import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "baselines" / "verified_public_files_2026-11-03.json"


def git_blob_sha1(data: bytes) -> str:
    # Git's object identity = SHA1(b"blob <length>\0" + raw bytes).
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data).hexdigest()


def fetch_entry(entry: dict) -> bytes:
    repo = entry["repo"]
    if not repo.startswith("RandoSY/") or ".." in entry["path"].split("/"):
        raise ValueError("Unexpected repository or invalid path")
    branch = urllib.parse.quote(entry.get("branch", "main"), safe="")
    path = urllib.parse.quote(entry["path"], safe="/")
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "RandoSY-public-archive-check/1.0"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read()


def main() -> int:
    manifest = json.loads(INDEX.read_text(encoding="utf-8"))
    bad = 0
    entries = manifest["artifacts"]
    print(f"Baseline {manifest['baseline_date']}; {len(entries)} published paths")
    for e in entries:
        identifier = f"{e['repo']}:{e['path']}"
        try:
            data = fetch_entry(e)
            if not data:
                raise ValueError("Published file is empty")
            expected = e.get("expected_git_blob_sha1")
            actual = git_blob_sha1(data)
            if expected and expected.lower() != actual:
                raise ValueError(f"blob SHA1 changed; expected {expected}, found {actual}")
            print(f"OK  {identifier} [{len(data)} bytes]")
        except (OSError, urllib.error.URLError, ValueError) as exc:
            bad += 1
            print(f"FAIL {identifier}: {exc}", file=sys.stderr)
    print(f"Checked {len(entries)}: {len(entries)-bad} OK, {bad} failed")
    if bad:
        print("A failing check means a path changed, was lost, or could not be reached.", file=sys.stderr)
        print("Review before changing the baseline; never silently update hashes.", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

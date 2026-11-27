#!/usr/bin/env python3
"""Safely deploy the upgraded Project Atlas homepage and navigation stylesheet."""
import argparse
import os
import shutil
import tempfile
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class HomeInspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = set()
        self.ids = set()
        self.duplicates = set()
        self.h1_count = 0
        self.missing_alt = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if name := a.get("id"):
            if name in self.ids:
                self.duplicates.add(name)
            self.ids.add(name)
        if tag in {"a", "link"} and "href" in a:
            self.refs.add(a["href"])
        if tag in {"img", "script", "source"} and "src" in a:
            self.refs.add(a["src"])
        if tag == "img" and "alt" not in a:
            self.missing_alt += 1
        if tag == "h1":
            self.h1_count += 1


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".atlas-home-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=os.environ.get("ATLAS_SITE", "/var/www/html/atlas"))
    parser.add_argument("--url", default=os.environ.get("ATLAS_URL", "https://project-atlas-lab.duckdns.org/atlas"))
    parser.add_argument("--local-only", action="store_true", help="Skip live HTTP checks (local test only)")
    parser.add_argument("--backup-dir", default=str(Path.home()), help="Directory to store timestamped backup")
    args = parser.parse_args()

    src = Path(__file__).resolve().parent / "atlas"
    site = Path(args.site).resolve()
    if not (site / "index.html").is_file() or not (site / "assets/navigation.css").is_file():
        raise SystemExit(f"Atlas site not found: {site}")

    targets = ["index.html", "assets/navigation.css", "assets/randall-young.webp"]
    payload = {rel: (src / rel).read_bytes() for rel in targets}

    inspector = HomeInspector()
    inspector.feed(payload["index.html"].decode("utf-8"))
    if inspector.h1_count != 1 or inspector.missing_alt or inspector.duplicates:
        raise SystemExit(
            f"Homepage structure check failed: h1={inspector.h1_count}, "
            f"missing_alt={inspector.missing_alt}, duplicates={inspector.duplicates}"
        )

    # Verify every local destination referenced by the new homepage already exists on the live site.
    missing = []
    for ref in sorted(inspector.refs):
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path == "./":
            continue
        rel = unquote(parsed.path.lstrip("./"))
        if rel in targets:
            continue
        target = site / rel
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            missing.append(ref)
    if missing:
        raise SystemExit("Missing referenced live assets/pages (no changes made): " + ", ".join(missing))

    backup = Path(tempfile.mkdtemp(prefix="atlas-home-backup-", dir=args.backup_dir))
    for rel in targets:
        if (site / rel).exists():
            dest = backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(site / rel, dest)

    changed = []
    try:
        for rel in targets:
            atomic_write(site / rel, payload[rel])
            changed.append(rel)
            if (site / rel).read_bytes() != payload[rel]:
                raise IOError(f"Local verification failed: {rel}")

        if not args.local_only:
            stamp = str(int(datetime.now(timezone.utc).timestamp()))
            for rel in targets:
                url = args.url.rstrip("/") + "/" + rel + "?atlas=" + stamp
                with urllib.request.urlopen(url, timeout=25) as response:
                    if response.status != 200 or response.read() != payload[rel]:
                        raise IOError(f"Live byte verification failed: {url}")
                print("HTTP VERIFIED:", rel)
    except BaseException as exc:
        for rel in reversed(changed):
            if (backup / rel).is_file():
                atomic_write(site / rel, (backup / rel).read_bytes())
            else:
                (site / rel).unlink(missing_ok=True)
        raise SystemExit(f"Deployment rolled back: {exc} | Backup: {backup}")

    print("ATLAS HOMEPAGE DEPLOYED" if not args.local_only else "ATLAS HOMEPAGE LOCAL TEST INSTALLED")
    print("Backup:", backup)
    print(args.url.rstrip("/") + "/")


if __name__ == "__main__":
    main()

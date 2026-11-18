#!/usr/bin/env python3
"""Check generated Atlas navigation, local assets, and the exhibit paths."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse

ROOT = Path(__file__).resolve().parent / "atlas"
EDITION_LINKS = {
    "": {"explore/"},
    "start-here": {"../explore/", "/atlas/sphericity-meter/", "/atlas/fair-fitness-testing/", "../lazy-lidar/", "../cutebot-motion-evidence/#ai-assistance"},
    "exhibits": {"../sphericity-meter/", "../fair-fitness-testing/", "../lazy-lidar/", "../cutebot-motion-evidence/"},
    "inventory": {"../cutebot-motion-evidence/"},
    "explore": {"../sphericity-meter/", "../fair-fitness-testing/", "../core-10/", "../sqm-plus/", "../lazy-lidar/"},
    "core-10": {"../sphericity-meter/"},
    "ideas": {"../fair-fitness-testing/", "../lazy-lidar/"},
    "sphericity-meter": {"Invent_a_Sphericity_Meter_Teachers_Guide.pdf", "../sqm-plus/"},
    "fair-fitness-testing": {"../ideas/#22-fair-fitness--dynametics", "../sqm-plus/"},
    "cutebot-motion-evidence": {"viewer.html", "media/cutebot.webp", "media/floor-trial.svg", "media/viewer-synthetic.svg", "../lazy-lidar/", "../sqm-plus/"},
    "lazy-lidar": {"model.html", "media/virtual-lab.webp", "media/cutebot-console.webp", "../ideas/#19-lazy--patient-lidar"},
}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.refs = set()
        self.ids = set()
        self.tabs = set()
        self.duplicates = set()
        self.headings = 0
        self.images_without_alt = 0
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if name := attrs.get("id"):
            if name in self.ids:
                self.duplicates.add(name)
            self.ids.add(name)
        if "data-tab" in attrs:
            self.tabs.add(attrs["data-tab"])
        if tag in {"a", "link"} and "href" in attrs:
            self.refs.add(attrs["href"])
        if tag in {"img", "script", "source", "iframe"} and "src" in attrs:
            self.refs.add(attrs["src"])
        if tag == "img" and "alt" not in attrs:
            self.images_without_alt += 1
        if tag == "h1":
            self.headings += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, help="Directory containing atlas/ and the separate calculus/ site")
    args = parser.parse_args()
    root = (args.site_root / "atlas" if args.site_root else ROOT).resolve()
    site_root = args.site_root.resolve() if args.site_root else root.parent
    pages = {p: Page(p) for p in sorted(root.rglob("index.html"))}
    for slug, links in EDITION_LINKS.items():
        missing = links - pages[root / slug / "index.html"].refs
        assert not missing, (slug or "Home", missing)
    local = 0
    for path, page in pages.items():
        assert page.headings == 1, path
        assert not page.images_without_alt, path
        assert not page.duplicates, (path, page.duplicates)
        for ref in page.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            if not args.site_root and url.path.startswith("/calculus/"):
                continue
            if url.path.startswith("/atlas/"):
                target = root / unquote(url.path.removeprefix("/atlas/"))
            elif url.path.startswith("/"):
                target = site_root / unquote(url.path.lstrip("/"))
            else:
                target = path.parent / unquote(url.path) if url.path else path
            if target.is_dir():
                target = target / "index.html"
            target = target.resolve()
            assert target.is_file(), (path, ref)
            if url.fragment and target.suffix == ".html":
                destination = pages.get(target) or Page(target)
                assert unquote(url.fragment) in destination.ids | destination.tabs, (path, ref)
            local += 1
    print(f"Checked {len(pages)} generated pages and {local} local links/assets.")


if __name__ == "__main__":
    main()

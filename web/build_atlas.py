#!/usr/bin/env python3
"""Build the Project Atlas static exhibition. Requires Python 3 and Pandoc."""
import argparse
import csv
import datetime
import html
import json
from pathlib import Path
import re
import subprocess
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

WEB = Path(__file__).resolve().parent
OUT = WEB / "atlas"
MANIFEST = WEB / "public-repos.json"
OWNER = "RandoSY"
ESTATE = f"https://github.com/{OWNER}"
ATLAS = f"{ESTATE}/project-atlas"
CORE = f"{ESTATE}/core-10"
ATLAS_MAIN = f"{ATLAS}/blob/main"
CORE_MAIN = f"{CORE}/blob/main"
CORE_RAW = f"https://raw.githubusercontent.com/{OWNER}/core-10/main"
CALCULUS = "http://74.208.252.58/calculus/"
FAMILIES = {
    "software-defined-laboratory": ("Software-Defined Laboratory", "Make instruments and experiments work across hardware, dashboards, and AI clients."),
    "core-10": ("CORE 10", "Teach science with ordinary phenomena and real measurements."),
    "nugget-physical-computing": ("Nugget Physical Computing", "Start with inexpensive hardware and expose more of how the machine works as learners progress."),
    "measured-world-lab": ("Measured World Lab", "Build instruments to investigate the things we encounter every day."),
    "measured-human-performance": ("Measured Human Performance", "Make fitness and movement measurements interpretable and repeatable."),
    "bargain-bin-robotics": ("Bargain Bin Robotics", "Use low-cost robots as both machines and instruments."),
    "computing-observatories": ("Computing Observatories", "Make execution visible through simulators, Forth, and observable CPUs."),
    "embedded-tools": ("Embedded Tools", "Find the bridges, protocols, programmers, and debugging tools behind the work."),
    "works-and-publications": ("Works and Publications", "Find the guides, papers, and visual explanations that help someone else carry the work forward."),
}
EXPERIMENT = "kitchen-inquiry-lab/CORE10_Microwave_Water_Heating_Handoff_Packet_v0.1.md"

def esc(value):
    return html.escape(str(value), quote=True)

def link(label, url):
    return f'<a href="{esc(url)}">{esc(label)}</a>'

def public_manifest():
    rows = []
    for page in range(1, 101):
        url = f"https://api.github.com/users/{OWNER}/repos?per_page=100&page={page}&sort=full_name"
        with urlopen(Request(url, headers={"User-Agent": "ProjectAtlasStaticBuild"}), timeout=20) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("GitHub did not return a repository list")
        rows.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError("Unexpectedly long public repository listing")
    return filter_manifest(rows, datetime.datetime.now(ZoneInfo("America/Indiana/Indianapolis")).date().isoformat())

def filter_manifest(rows, as_of):
    selected = {}
    for row in rows:
        name = row.get("name", "")
        if (row.get("owner", {}).get("login") != OWNER or row.get("private") is not False or
                row.get("visibility") != "public" or not re.fullmatch(r"[\w.-]+", name, re.ASCII)):
            continue
        selected[name.casefold()] = {
            "name": name, "fork": bool(row.get("fork")),
            "archived": bool(row.get("archived")),
            "description": (row.get("description") or "").strip(),
        }
    if not selected:
        raise ValueError("No public repositories found; refusing to replace the snapshot")
    return {"as_of": as_of, "repositories": [selected[key] for key in sorted(selected)]}

def page(directory, title, description, body, source=ATLAS, extra="", header="PROJECT ATLAS"):
    prefix = "../" if directory else ""
    current = {"": "Atlas home", "core-10": "CORE 10", "ideas": "Idea index",
               "inventory": "Project inventory", "repositories": "All repositories"}[directory]
    nav = []
    for name, dest in [("Atlas home", ""), ("CORE 10", "core-10"), ("Idea index", "ideas"),
                       ("Project inventory", "inventory"), ("All repositories", "repositories")]:
        attr = ' aria-current="page"' if name == current else ''
        url = (prefix or "./") + ((dest + "/") if dest else "")
        nav.append(f'<a href="{url}"{attr}>{name}</a>')
    full = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(description)}">
<title>{esc(title)} · Randall Young</title>
<link rel="stylesheet" href="{prefix}assets/calculus-theme.css">
<link rel="stylesheet" href="{prefix}assets/atlas.css">
{extra}</head>
<body><main>
<p>RANDALL YOUNG · {esc(header)}</p>
<h1>{esc(title)}</h1>
<p>{esc(description)}</p>
{body}
<footer>
<nav aria-label="Project Atlas">{' '.join(nav)}</nav>
<p>{link('View the source on GitHub', source)}</p>
</footer>
</main></body>
</html>
"""
    target = OUT / directory / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(full, encoding="utf-8")

def cover(filename, alt):
    return f'<img src="{filename}" width="1600" height="800" alt="{esc(alt)}">'

def homes():
    sections = [
        ("CORE", ["core-10", "software-defined-laboratory", "nugget-physical-computing",
                  "measured-world-lab", "bargain-bin-robotics", "computing-observatories", "embedded-tools"]),
        ("APPS", ["measured-human-performance"]),
        ("TRANSMISSION", ["works-and-publications"]),
    ]
    output = []
    for heading, slugs in sections:
        entries = []
        for slug in slugs:
            title, summary = FAMILIES[slug]
            url = "core-10/" if slug == "core-10" else f"{ESTATE}/{slug}"
            entries.append(f"<li>{link(title, url)} · {esc(summary)}</li>")
        output.append(f"<h3>{heading}</h3><ul>{''.join(entries)}</ul>")
    return "\n".join(output)

def home(n):
    page("", "Project Atlas", "Randall Young’s public working archive of experiments, instruments, teaching materials, and the ideas that connect them.", f"""
{cover('assets/atlas-cover.svg', 'A compass connects a laboratory flask, an instrument trace, and a book.')}
<section aria-labelledby="start">
<h2 id="start">Start here</h2>
<p><strong>How much? Enough?</strong> Measure what happened. Then decide whether it was enough for the purpose. Two places to see that kind of thinking at work:</p>
<ul>
<li><a href="core-10/">CORE 10 · One cup of water, two energy readings</a>. Compare the heat gained by the water with the electricity the appliance used.</li>
<li>{link('Ten Problems That Teach Calculus', CALCULUS)}. Start with the cart that reverses direction. It teaches why distance traveled and net change are not the same thing.</li>
</ul>
</section>
<section aria-labelledby="read">
<h2 id="read">Read the Atlas</h2>
<p>This is an idea backup. The point is to leave enough of the reasoning, evidence, and working material for someone else to pick up the work.</p>
<ul>
<li><a href="ideas/">Idea index</a> · the principles and designs that recur across projects</li>
<li><a href="inventory/">Project inventory</a> · the documented systems, their maturity, and their current homes</li>
<li><a href="repositories/">All {n} public repositories</a> · searchable index including earlier versions and upstream forks</li>
</ul>
</section>
<section aria-labelledby="families"><h2 id="families">Explore the work</h2>{homes()}</section>
""", header="HOW MUCH? ENOUGH?")

def core():
    page("core-10", "CORE 10", "A practical science and engineering curriculum that starts with something you can see, measure, and investigate.", f"""
{cover('../assets/core10-cover.svg', 'Electrical energy enters a heating system while a thermometer measures the heat gained by the water.')}
<section aria-labelledby="start">
<h2 id="start">Start here</h2>
<p>Heat a measured amount of water and record its temperature rise. Compare the heat it gained with the electricity the microwave used. Which number tells you what happened to the water, and which tells you what you paid for?</p>
<p>{link('Microwave water heating handoff packet', f'{CORE_MAIN}/{EXPERIMENT}')} · materials, method, calculations, and a one-run record. This is a documented reference experiment. The packet does not yet record an independent handoff run.</p>
</section>
<section aria-labelledby="paths">
<h2 id="paths">Three ways into CORE 10</h2>
<ul>
<li>{link('Kitchen Inquiry Lab', f'{CORE_MAIN}/kitchen-inquiry-lab/Kitchen_Inquiry_Lab_Canonical_Map.md')} · turn everyday heating, cooling, and other household phenomena into experiments.</li>
<li>{link('One Cup Chemistry', f'{CORE_MAIN}/one-cup-chemistry/experiments/README.md')} · use the same small toolkit to study solutions, cooling, conductivity, and more.</li>
<li>{link('NOTHING IS FREE / Personal Energy Laboratory', f'{CORE_MAIN}/nothing-is-free/NOTHING_IS_FREE_Canonical_Map.md')} · follow energy through batteries, motors, heating, and household costs.</li>
</ul>
</section>
<section aria-labelledby="downloads">
<h2 id="downloads">Guides and downloads</h2>
<ul>
<li>{link('Measured Energy Teacher Guide', f'{CORE_RAW}/kitchen-inquiry-lab/original-editions/Measured_Energy_Teacher_Guide_v4.pdf')} · PDF</li>
<li>{link('One Cup Chemistry student lab book', f'{CORE_RAW}/one-cup-chemistry/original-editions/One_Cup_Chemistry_Student_Lab_Book_v0_2_BRANDED.pdf')} · PDF</li>
<li>{link('One Cup Chemistry teacher manual', f'{CORE_RAW}/one-cup-chemistry/original-editions/One_Cup_Chemistry_Teacher_Manual_v0_2_BRANDED.pdf')} · PDF</li>
<li>{link('CORE 10 idea record', f'{CORE_MAIN}/IDEAS.md')} · design rationale and measurement ladder</li>
</ul>
</section>
""", source=CORE, header="EXPERIENCE BEFORE EQUATION")

def legacy_homes(path):
    mapping = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r'^\| `([^`]+)` \| (.*?) \|', line)
        if match:
            name, targets = match.groups()
            mapping[name.casefold()] = [s for s in re.findall(r'`([^`]+)`', targets) if s in FAMILIES]
    return mapping

def repo_archive(manifest, source_path):
    mapping = legacy_homes(source_path)
    entries = []
    for repo in manifest["repositories"]:
        name = repo["name"]
        is_fork = repo["fork"]
        kind = "Fork" if is_fork else "Non-fork"
        archived = " · Archived on GitHub" if repo["archived"] else ""
        short = f' · {esc(repo["description"])}' if repo["description"] else ""
        targets = mapping.get(name.casefold(), [])
        route = (f'<br><span class="kind">Atlas maps to '
                 + " / ".join(link(FAMILIES[s][0], "../core-10/" if s == "core-10" else f"{ESTATE}/{s}") for s in targets)
                 + "</span>") if targets else ""
        entries.append(f'<li data-kind="{kind}">{link(name, f"{ESTATE}/{name}")}'
                       f' <span class="kind">· {kind}{archived}</span>{short}{route}</li>')
    num = len(entries)
    page("repositories", "Public repositories", "Search the GitHub collection by name, subject, or the project home Atlas assigns it.", f"""
<p class="meta">GitHub snapshot dated {esc(manifest['as_of'])}. A fork can carry useful changes or provide a reference. It is not necessarily an original project.</p>
<div id="search-options" class="search-options" hidden>
  <div><label for="repo-search">Find a repository</label><input id="repo-search" type="search" placeholder="Try Pico, chemistry, or robotics"></div>
  <div><label for="repo-type">Repository type</label><select id="repo-type"><option value="">All types</option><option>Non-fork</option><option>Fork</option></select></div>
</div>
<p id="repo-status" role="status">{num} public repositories.</p>
<ul id="repo-list">{''.join(entries)}</ul>
<p>{link('Read the legacy repository map', f'{ATLAS_MAIN}/LEGACY_REPOSITORY_MAP.md')} · review the historical context and migration decisions.</p>
""", source=f"https://github.com/{OWNER}?tab=repositories",
         extra='<script defer src="../assets/archive.js"></script>\n')

def public_document(path, exclude, toc=False):
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r'\A# [^\n]+\n+', '', raw)
    for heading in exclude:
        raw = re.sub(rf'^## {re.escape(heading)}[^\n]*\n.*?(?=^## |\Z)', '', raw, flags=re.M | re.S)
    opts = ["pandoc", "--from=gfm-raw_html", "--to=html5", "--wrap=none"]
    result = subprocess.run(opts, input=raw, text=True, capture_output=True, check=True).stdout
    result = re.sub(r"<colgroup>.*?</colgroup>", "", result, flags=re.S)
    if toc:
        items = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', result)
        jump = ''.join(f'<li><a href="#{slug}">{label}</a></li>' for slug, label in items)
        result = f'<details><summary>Jump to a section</summary><ol>{jump}</ol></details>\n' + result
    return result.replace("<table>", '<div class="table-scroll" role="region" aria-label="Project table" tabindex="0"><table>').replace("</table>", "</table></div>")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--atlas-source", type=Path, default=WEB.parent)
    ap.add_argument("--refresh-repos", action="store_true")
    ap.add_argument("--from-api-snapshot", type=Path, help="Use a retained GitHub public API response")
    ap.add_argument("--snapshot-date", help="ISO capture date for --from-api-snapshot")
    args = ap.parse_args()
    if args.from_api_snapshot:
        date = datetime.date.fromisoformat(args.snapshot_date).isoformat()
        manifest = filter_manifest(json.loads(args.from_api_snapshot.read_text()), date)
    elif args.refresh_repos:
        manifest = public_manifest()
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    home(len(manifest["repositories"]))
    core()
    repo_archive(manifest, args.atlas_source / "LEGACY_REPOSITORY_MAP.md")
    for name, title, summary, file, exclude in [
        ("ideas", "Idea index", "The durable ideas behind the work, from measurement and teaching to open instruments and publication.",
         "IDEA_INDEX.md", ["Protected idea estate"]),
        ("inventory", "Project inventory", "The Atlas record of public systems, their documented maturity, and where to find them.",
         "CANONICAL_INVENTORY.md", ["Protected system"]),
    ]:
        body = public_document(args.atlas_source / file, exclude, toc=True)
        page(name, title, summary, f'<article>{body}</article>', source=f"{ATLAS_MAIN}/{file}")
    print(f"Built five pages and indexed {len(manifest['repositories'])} public repositories.")

if __name__ == "__main__":
    main()

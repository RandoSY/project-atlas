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
CALCULUS = "/calculus/"
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
    destinations = (("Home", ""), ("Exhibits", "exhibits"), ("Ideas", "ideas"),
                    ("Projects", "inventory"), ("Repositories", "repositories"))
    exhibit_children = {"singing-rule", "sqm-plus", "instruments", "core-10", "pop-can-calorimeter"}
    nav = []
    for name, dest in destinations:
        attr = ' aria-current="page"' if dest == directory else ''
        if dest == "exhibits" and directory in exhibit_children:
            attr = ' class="atlas-nav-section" aria-current="location"'
        if not dest and directory == "start-here":
            attr = ' class="atlas-nav-section" aria-current="location"'
        url = (prefix or "./") + ((dest + "/") if dest else "")
        nav.append(f'<a href="{url}"{attr}>{name}</a>')
    footer_home = link("Project Atlas home", "../") + " · " if directory else ""
    full = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(description)}">
<title>{esc(title)} · Randall Young</title>
<link rel="stylesheet" href="{prefix}assets/calculus-theme.css">
<link rel="stylesheet" href="{prefix}assets/atlas.css">
<link rel="stylesheet" href="{prefix}assets/navigation.css">
{extra}</head>
<body><main>
<nav class="atlas-nav" aria-label="Project Atlas">{' '.join(nav)}</nav>
<p>RANDALL YOUNG · {esc(header)}</p>
<h1>{esc(title)}</h1>
<p>{esc(description)}</p>
{body}
<footer>
<p>{footer_home}{link('View the source on GitHub', source)}</p>
</footer>
</main></body>
</html>
"""
    target = OUT / directory / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(full, encoding="utf-8")

def cover(filename, alt):
    return f'<img src="{filename}" width="1600" height="800" alt="{esc(alt)}">'

def homes(prefix=""):
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
            url = f"{prefix}core-10/" if slug == "core-10" else f"{ESTATE}/{slug}"
            entries.append(f"<li>{link(title, url)} · {esc(summary)}</li>")
        output.append(f"<h3>{heading}</h3><ul>{''.join(entries)}</ul>")
    return "\n".join(output)

def home(n):
    page("", "Project Atlas", "Randall Young’s public working archive of experiments, instruments, and the ideas that connect them.", f"""
<section class="atlas-start" aria-labelledby="atlas-start-title">
<div>
<p class="atlas-kicker">New to Project Atlas?</p>
<h2 id="atlas-start-title"><a href="start-here/">Start Here</a></h2>
<p>Choose one thing to try, teach, or build. Then find your way to the evidence and source.</p>
</div>
<div class="atlas-start-actions">
<a class="atlas-start-primary" href="start-here/">Open the guide <span aria-hidden="true">→</span></a>
<a href="start-here/Project-Atlas-Start-Here.pdf" download>Download PDF</a>
</div>
</section>
<section class="atlas-feature" aria-labelledby="home-singing">
<div>
<p class="atlas-kicker">Flagship activity · Experience before equation</p>
<h2 id="home-singing"><a href="singing-rule/">The Singing Rule</a></h2>
<p>Pluck a ruler at the edge of a table. Follow the original bench experiment from a Bluetooth trace to a model you can test yourself.</p>
<p class="atlas-feature-links"><a href="singing-rule/#evidence">See the measured run</a><a href="singing-rule/#model">Pluck the model</a><a href="singing-rule/#classroom">Teach it</a></p>
</div>
<a href="singing-rule/"><img src="singing-rule/media/bench.webp" width="1440" height="1084" alt="A green ruler with a wireless motion sensor fastened near its free end"></a>
</section>
<div class="atlas-mini-grid" aria-label="More featured exhibits">
<a class="atlas-mini" href="sqm-plus/">
<img src="sqm-plus/media/hallway.svg" width="1280" height="610" alt="">
<div><b id="home-sqm">SQM+ Hallway Observatory</b><span>Eleven meters, a stopwatch, and a step detector under test.</span></div></a>
<a class="atlas-mini" href="instruments/">
<img src="instruments/screens/frequency-meter.webp" width="1240" height="945" alt="">
<div><b id="home-instruments">Virtual Instruments</b><span>Five wireless builds and the dashboards that make them usable.</span></div></a>
</div>
<p class="atlas-all"><a href="exhibits/">Browse all exhibits →</a></p>
<section class="atlas-directory" aria-labelledby="read">
<h2 id="read">Read the Atlas</h2>
<p><strong>How much? Enough?</strong> Measure what happened, then decide whether it was enough for the purpose.</p>
<ul>
<li><a href="ideas/">Ideas</a> · the principles and designs that recur across the work</li>
<li><a href="inventory/">Projects</a> · what was built, what is still under test, and where to find it</li>
<li><a href="repositories/">Repositories</a> · search all {n} public repositories, including earlier versions and upstream forks</li>
</ul>
</section>
""", header="HOW MUCH? ENOUGH?")


def start_here():
    data = json.loads((WEB / "start-here.json").read_text(encoding="utf-8"))
    routes = [
        f'<li><h3>{esc(row["title"])}</h3><p>{esc(row["text"])}</p>'
        f'<p class="sg-action">{link(row["label"], row["url"])}</p></li>'
        for row in data["routes"]
    ]
    places = [
        f'<div><dt>{link(row["title"], row["url"])}</dt><dd>{esc(row["text"])}</dd></div>'
        for row in data["navigation"]
    ]
    exhibits = [
        f'<li><p class="atlas-kicker">{esc(row["topic"])}</p>'
        f'<h3>{link(row["title"], row["url"])}</h3><p>{esc(row["text"])}</p>'
        f'<p class="sg-first"><strong>First move</strong> {esc(row["start"])}</p></li>'
        for row in data["exhibits"]
    ]
    workflow = [
        f'<li><strong>{esc(row["title"])}</strong><p>{esc(row["text"])}</p></li>'
        for row in data["workflow"]
    ]
    page("start-here", data["title"], data["subtitle"], f"""
<div class="sg-guide">
<p class="sg-intro">{esc(data['intro'])}</p>
<p><a class="sg-download" href="Project-Atlas-Start-Here.pdf" download>Download the two-page PDF</a></p>
<section aria-labelledby="sg-entry">
<h2 id="sg-entry">Choose your first stop</h2>
<ol class="sg-routes">{''.join(routes)}</ol>
</section>
<section aria-labelledby="sg-nav">
<h2 id="sg-nav">Find your way around Atlas</h2>
<dl class="sg-nav-list">{''.join(places)}</dl>
</section>
<section aria-labelledby="sg-exhibits">
<h2 id="sg-exhibits">Six places to begin</h2>
<p>Try the first move before reading everything.</p>
<ul class="sg-exhibits">{''.join(exhibits)}</ul>
</section>
<section class="sg-method" aria-labelledby="sg-workflow">
<h2 id="sg-workflow">Capture → Analyze → Publish</h2>
<ol>{''.join(workflow)}</ol>
</section>
<section class="sg-evidence" aria-labelledby="sg-evidence">
<h2 id="sg-evidence">Read the evidence</h2>
<p>{esc(data['evidence'])}</p>
</section>
</div>
""", extra='<link rel="stylesheet" href="../assets/start-here.css">\n',
         header="PROJECT ATLAS · GETTING STARTED")


def exhibits():
    cards = [
        ("Flagship activity", "../singing-rule/", "The Singing Rule",
         "Pluck a ruler and follow the motion from the original bench photo to live traces, measured ringdown, and a model you can try.",
         "../singing-rule/media/bench.webp", 1440, 1084),
        ("Premier CORE 10 activity", "../pop-can-calorimeter/", "Pop-Can Calorimeter",
         "Follow a tea light from grams of fuel to joules in the water, compare heating rates, and account for where the rest of the energy went.",
         "../pop-can-calorimeter/media/picoscale.webp", 1440, 847),
        ("Current experiment", "../sqm-plus/", "SQM+ Hallway Observatory",
         "Run a marked 11-meter leg and see why a stopwatch and a wearable answer two different questions.",
         "../sqm-plus/media/hallway.svg", 1280, 610),
        ("Instrument workshop", "../instruments/", "Virtual Instruments",
         "See original dashboards and build a wireless voltmeter, frequency meter, scale, ToF ruler, or thermometer.",
         "../instruments/screens/frequency-meter.webp", 1240, 945),
        ("Mathematics", CALCULUS, "Ten Problems That Teach Calculus",
         "Start with the cart that reverses direction. Learn why total distance and net change are not the same thing.",
         "/calculus/assets/calculus-tangent-cover.svg", 1600, 800),
        ("Curriculum", "../core-10/", "CORE 10",
         "Use an ordinary cup of water to distinguish the heat it gains from the electricity an appliance uses.",
         "../assets/core10-cover.svg", 1600, 800),
    ]
    blocks = []
    for label, url, title, description, image, width, height in cards:
        emphasis = " atlas-premier" if label.startswith("Premier") else ""
        blocks.append(f"""<article class="atlas-exhibit{emphasis}">
<a class="atlas-exhibit-visual" href="{esc(url)}" aria-label="Open {esc(title)}">
<img src="{esc(image)}" width="{width}" height="{height}" alt="" decoding="async"></a>
<div class="atlas-exhibit-body">
<p class="atlas-kicker">{esc(label)}</p>
<h2>{link(title, url)}</h2>
<p class="atlas-exhibit-summary">{esc(description)}</p>
</div></article>""")
    page("exhibits", "Exhibits", "Experiments you can try, instruments you can build, and models you can test.", f"""
<div class="atlas-exhibits">{''.join(blocks)}</div>
<p class="atlas-collection-note">Looking for work beyond this gallery? Browse the <a href="../inventory/">project inventory</a> or search the <a href="../repositories/">public repositories</a>.</p>
""", header="EXPERIENCE BEFORE EQUATION")


def core():
    page("core-10", "CORE 10", "A practical science and engineering curriculum that starts with something you can see, measure, and investigate.", f"""
{cover('../assets/core10-cover.svg', 'Electrical energy enters a heating system while a thermometer measures the heat gained by the water.')}
<section class="atlas-directory" aria-labelledby="core-signature">
<p class="atlas-kicker">Signature Kitchen Inquiry Lab</p>
<h2 id="core-signature"><a href="../pop-can-calorimeter/">Pop-Can Calorimeter</a></h2>
<p>One candle creates two records: the mass of fuel consumed and the heat gained by the water. This is where CORE 10 connects measurement, chemistry, watts, and evidence about where the energy went.</p>
</section>
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

def instruments():
    catalog = json.loads((WEB / "capture_catalog.json").read_text(encoding="utf-8"))
    source = (WEB / "instruments.html").read_text(encoding="utf-8")

    def figure(match):
        key = match.group(1)
        title, alt, caption, filename, width, height = catalog[key]
        asset = f"screens/{key}.webp"
        if not (OUT / "instruments" / asset).is_file():
            raise FileNotFoundError(asset)
        return (f'<figure><a href="{asset}" aria-label="Open full-size capture: {esc(title)}">'
                f'<img loading="lazy" decoding="async" src="{asset}" width="{width}" height="{height}" alt="{esc(alt)}"></a>'
                f'<figcaption><strong>{esc(title)}</strong><br>{esc(caption)}'
                f'<br><code>{esc(filename)}</code></figcaption></figure>')

    assert set(re.findall(r"@@([a-z0-9-]+)@@", source)) == catalog.keys()
    body = re.sub(r"@@([a-z0-9-]+)@@", figure, source)
    page("instruments", "Virtual Instruments",
         "Five bench instruments, real control-dashboard captures, and practical wireless builds.",
         body, header="SOFTWARE-DEFINED LABORATORY · EXPERIENCE BEFORE EQUATION",
         extra='<link rel="stylesheet" href="../assets/instruments.css">\n',
         source=f"{ATLAS}/tree/atlas-web-preview/web")


def singing_rule():
    catalog = json.loads((WEB / "singing-rule-media.json").read_text(encoding="utf-8"))
    source = (WEB / "singing-rule.html").read_text(encoding="utf-8")

    def figure(match):
        key = match.group(1)
        item = catalog[key]
        asset = f"media/{key}.webp"
        if not (OUT / "singing-rule" / asset).is_file():
            raise FileNotFoundError(asset)
        sized = f'width="{int(item["width"])}" height="{int(item["height"])}"'
        loading = 'fetchpriority="high"' if key == "bench" else 'loading="lazy" decoding="async"'
        return (f'<figure class="sr-figure"><a href="{asset}">'
                f'<img src="{asset}" {sized} {loading} alt="{esc(item["alt"])}"></a>'
                f'<figcaption>{esc(item["caption"])}</figcaption></figure>')

    assert set(re.findall(r"@@([a-z0-9-]+)@@", source)) == catalog.keys()
    body = re.sub(r"@@([a-z0-9-]+)@@", figure, source)
    page("singing-rule", "The Singing Rule",
         "A tabletop experiment that turns one pluck into a waveform, a frequency, and a model.",
         body, header="FLAGSHIP ACTIVITY · EXPERIENCE BEFORE EQUATION",
         extra='<link rel="stylesheet" href="../assets/singing-rule.css">\n<script src="../assets/singing-rule.js" defer></script>\n',
         source=f"{ESTATE}/measured-world-lab/tree/main/archive/singing-rule")


def sqm_plus():
    catalog = json.loads((WEB / "sqm-plus-media.json").read_text(encoding="utf-8"))
    source = (WEB / "sqm-plus.html").read_text(encoding="utf-8")

    def figure(match):
        key = match.group(1)
        item = catalog[key]
        asset = f"media/{key}.webp"
        if not (OUT / "sqm-plus" / asset).is_file():
            raise FileNotFoundError(asset)
        sized = f'width="{int(item["width"])}" height="{int(item["height"])}"'
        loading = 'fetchpriority="high"' if key == "one-walk" else 'loading="lazy" decoding="async"'
        return (f'<figure class="sq-figure"><a href="{asset}">'
                f'<img src="{asset}" {sized} {loading} alt="{esc(item["alt"])}"></a>'
                f'<figcaption>{esc(item["caption"])}</figcaption></figure>')

    assert set(re.findall(r"@@([a-z0-9-]+)@@", source)) == catalog.keys()
    body = re.sub(r"@@([a-z0-9-]+)@@", figure, source)
    page("sqm-plus", "SQM+ Hallway Observatory",
         "A known distance, an independent clock, and a wearable under test.",
         body, header="SOFTWARE-DEFINED WALKING LABORATORY · MEASUREMENT FIRST",
         extra='<link rel="stylesheet" href="../assets/sqm-plus.css">\n<script src="../assets/sqm-plus.js" defer></script>\n',
         source=f"{ESTATE}/measured-human-performance")


def pop_can_calorimeter():
    catalog = json.loads((WEB / "pop-can-media.json").read_text(encoding="utf-8"))
    source = (WEB / "pop-can-calorimeter.html").read_text(encoding="utf-8")

    def figure(match):
        key = match.group(1)
        item = catalog[key]
        asset = f"media/{key}.webp"
        if not (OUT / "pop-can-calorimeter" / asset).is_file():
            raise FileNotFoundError(asset)
        sized = f'width="{int(item["width"])}" height="{int(item["height"])}"'
        load = 'fetchpriority="high"' if key == "apparatus" else 'loading="lazy" decoding="async"'
        return (f'<figure class="pc-figure"><a href="{asset}">'
                f'<img src="{asset}" {sized} {load} alt="{esc(item["alt"])}"></a>'
                f'<figcaption>{esc(item["caption"])}</figcaption></figure>')

    assert set(re.findall(r"@@([a-z0-9-]+)@@", source)) == catalog.keys()
    body = re.sub(r"@@([a-z0-9-]+)@@", figure, source)
    page("pop-can-calorimeter", "Pop-Can Calorimeter",
         "A premier CORE 10 activity about fuel, heat, and where the energy goes.",
         body, header="CORE 10 · KITCHEN INQUIRY LAB",
         extra='<link rel="stylesheet" href="../assets/pop-can.css">\n<script src="../assets/pop-can.js" defer></script>\n',
         source=f"{CORE}/tree/main/kitchen-inquiry-lab")


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
    start_here()
    exhibits()
    core()
    instruments()
    singing_rule()
    sqm_plus()
    pop_can_calorimeter()
    repo_archive(manifest, args.atlas_source / "LEGACY_REPOSITORY_MAP.md")
    for name, title, summary, file, exclude in [
        ("ideas", "Idea index", "The durable ideas behind the work, from measurement and teaching to open instruments and publication.",
         "IDEA_INDEX.md", ["Protected idea estate"]),
        ("inventory", "Project inventory", "The Atlas record of public systems, their documented maturity, and where to find them.",
         "CANONICAL_INVENTORY.md", ["Protected system"]),
    ]:
        body = public_document(args.atlas_source / file, exclude, toc=True)
        families = (f'<section class="atlas-family-list" aria-labelledby="families">'
                    f'<h2 id="families">Project families</h2>{homes("../")}</section>') if name == "inventory" else ""
        page(name, title, summary, f'<article>{body}</article>{families}', source=f"{ATLAS_MAIN}/{file}")
    print(f"Built eleven pages and indexed {len(manifest['repositories'])} public repositories.")

if __name__ == "__main__":
    main()

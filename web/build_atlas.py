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
    exhibit_children = {"singing-rule", "sqm-plus", "instruments", "core-10", "pop-can-calorimeter", "water-clock", "teatime", "sphericity-meter", "fair-fitness-testing", "lazy-lidar", "cutebot-motion-evidence"}
    nav = []
    for name, dest in destinations:
        attr = ' aria-current="page"' if dest == directory else ''
        if dest == "exhibits" and directory in exhibit_children:
            attr = ' class="atlas-nav-section" aria-current="location"'
        if not dest and directory in {"start-here", "explore"}:
            attr = ' class="atlas-nav-section" aria-current="location"'
        url = (prefix or "./") + ((dest + "/") if dest else "")
        nav.append(f'<a href="{url}"{attr}>{name}</a>')
    footer_html = (
        f'<p>{link("Project Atlas home", "../")} · {link("View the source on GitHub", source)}</p>'
        if directory else
        '<p class="atlas-footer-meta"><strong>Randall S. Young, Ed.S.</strong> · Independent researcher and educator · <a href="https://orcid.org/0009-0003-1657-0243">ORCID 0009-0003-1657-0243</a></p>\n'
        '<p class="atlas-footer-links"><a href="https://github.com/RandoSY/project-atlas/tree/atlas-web-preview">View the source on GitHub</a> · <a href="start-here/">Start Here</a> · <a href="exhibits/">All exhibits</a> · <a href="repositories/">89 public repositories</a></p>'
    )
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
{footer_html}
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
    destinations = (("Home", ""), ("Exhibits", "exhibits"), ("Ideas", "ideas"),
                    ("Projects", "inventory"), ("Repositories", "repositories"))
    nav = []
    for name, dest in destinations:
        attr = ' aria-current="page"' if not dest else ''
        url = "./" + ((dest + "/") if dest else "")
        nav.append(f'<a href="{url}"{attr}>{name}</a>')
    full = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Randall Young’s public working archive of experiments, instruments, research papers, and the ideas that connect them.">
<title>Project Atlas · Randall Young</title>
<link rel="stylesheet" href="assets/calculus-theme.css">
<link rel="stylesheet" href="assets/atlas.css">
<link rel="stylesheet" href="assets/navigation.css">
</head>
<body><main class="atlas-home">
<nav class="atlas-nav" aria-label="Project Atlas">{' '.join(nav)}</nav>

<header class="atlas-home-header">
<div>
<p class="atlas-home-eyebrow">Randall Young · Public Working Archive</p>
<h1>Project Atlas</h1>
<p class="atlas-home-lead"><strong>How much? Enough?</strong> Measure what happened, then decide whether it was enough for the purpose—across teaching labs, instruments, movement, and research.</p>
</div>
<div class="atlas-guide-actions">
<a class="atlas-btn-primary" href="start-here/">Start Here <span aria-hidden="true">→</span></a>
<a href="start-here/Project-Atlas-Start-Here.pdf" download>PDF</a>
<a href="explore/">Explore</a>
</div>
</header>

<div class="atlas-tabs" role="tablist" aria-label="Filter work by territory">
<button type="button" class="atlas-tab" role="tab" id="tab-highlights" data-tab="highlights" aria-controls="panel-highlights" aria-selected="true">Highlights</button>
<button type="button" class="atlas-tab" role="tab" id="tab-experiments" data-tab="experiments" aria-controls="panel-experiments" aria-selected="false">Experiments &amp; Teaching</button>
<button type="button" class="atlas-tab" role="tab" id="tab-instruments" data-tab="instruments" aria-controls="panel-instruments" aria-selected="false">Instruments &amp; Robotics</button>
<button type="button" class="atlas-tab" role="tab" id="tab-movement" data-tab="movement" aria-controls="panel-movement" aria-selected="false">Movement &amp; Fitness</button>
<button type="button" class="atlas-tab" role="tab" id="tab-research" data-tab="research" aria-controls="panel-research" aria-selected="false">Circuits &amp; Genomes</button>
</div>

<section class="atlas-panel" id="panel-highlights" data-panel="highlights" role="tabpanel" aria-labelledby="tab-highlights">
<div class="atlas-pair">
<article class="atlas-card atlas-card-warm">
<a class="atlas-card-media" href="singing-rule/" aria-label="Open The Singing Rule"><img src="singing-rule/media/bench.webp" width="1440" height="1084" alt="A green ruler with a wireless motion sensor fastened near its free end"></a>
<div class="atlas-card-body">
<p class="atlas-kicker">Flagship bench activity · Experience before equation</p>
<h2 id="home-singing"><a href="singing-rule/">The Singing Rule</a></h2>
<p>Pluck a ruler at a table edge. Follow the bench run from a Bluetooth trace to a model you can test yourself.</p>
<div class="atlas-card-actions"><a class="atlas-btn-primary" href="singing-rule/">Open exhibit <span aria-hidden="true">→</span></a><a href="singing-rule/#evidence">Measured run</a><a href="singing-rule/#model">Model</a><a href="singing-rule/#classroom">Teach it</a></div>
</div>
</article>
<article class="atlas-card atlas-card-research">
<a class="atlas-card-media atlas-media-light" href="circuits-to-genomes/" aria-label="Open From Circuits to Genomes"><img src="circuits-to-genomes/media/reciprocal.svg" width="1200" height="430" alt="Diagram of the golden thread connecting the PDP-8, regulatory genome, and H100-inspired parallel computation"></a>
<div class="atlas-card-body">
<p class="atlas-kicker">Research &amp; scholarship · Three papers + open lab</p>
<h2 id="home-c2g"><a href="circuits-to-genomes/">From Circuits to Genomes</a></h2>
<p>Can function endure as implementation changes? Follow one question from the PDP-8 to peroxide-managing enzymes and AI-assisted inquiry.</p>
<div class="atlas-card-actions"><a class="atlas-btn-primary" href="circuits-to-genomes/">Open portal <span aria-hidden="true">→</span></a><a href="circuits-to-genomes/#architecture">Paper 1</a><a href="circuits-to-genomes/#peroxide">Paper 2</a><a href="catalase-fem/open-lab/">Open Lab</a></div>
</div>
</article>
</div>
<div class="atlas-strip-4" aria-label="Featured exhibits across territories">
<a class="atlas-tile" href="sqm-plus/">
<span class="atlas-tile-media atlas-media-contain"><img src="sqm-plus/media/hallway.svg" width="1280" height="610" alt=""></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Movement</p><b id="home-sqm">SQM+ Hallway</b><span>11 meters, a stopwatch, and a step detector under test.</span></div>
</a>
<a class="atlas-tile" href="instruments/">
<span class="atlas-tile-media"><img src="instruments/screens/frequency-meter.webp" width="1240" height="945" alt=""></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Instruments</p><b id="home-instruments">Virtual Instruments</b><span>Five wireless builds and live browser dashboards.</span></div>
</a>
<a class="atlas-tile" href="water-clock/">
<span class="atlas-tile-media atlas-media-light"><img src="water-clock/media/apparatus.webp" width="1350" height="1043" alt=""></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Bench lab</p><b id="home-water-clock">Galileo’s Water Clock</b><span>Weigh water, infer time, and test it on a ramp.</span></div>
</a>
<a class="atlas-tile" href="teatime/">
<span class="atlas-tile-media"><img src="teatime/media/optical-bench.svg" width="1040" height="650" alt=""></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Optics</p><b id="home-teatime">TeaTime</b><span>Use light to estimate an unknown tea dilution.</span></div>
</a>
</div>
</section>

<section class="atlas-panel" id="panel-experiments" data-panel="experiments" role="tabpanel" aria-labelledby="tab-experiments" hidden>
<div class="atlas-panel-bar">
<p><strong>Experience before equation:</strong> ordinary phenomena first so equations are earned through measurement.</p>
<div class="atlas-panel-links"><a href="core-10/">CORE 10 hub</a><a href="ideas/#2-experience-before-equation">Idea note</a><a href="explore/#teach">Curriculum map →</a></div>
</div>
<div class="atlas-strip-3">
<a class="atlas-tile" href="singing-rule/">
<span class="atlas-tile-media"><img src="singing-rule/media/bench.webp" width="1440" height="1084" alt="Green ruler with wireless motion sensor"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Flagship bench lab</p><b>The Singing Rule</b><span>Bluetooth ringdown trace to interactive vibration model.</span></div>
</a>
<a class="atlas-tile" href="pop-can-calorimeter/">
<span class="atlas-tile-media atlas-media-light"><img src="pop-can-calorimeter/media/picoscale.webp" width="1440" height="847" alt="Pop-can calorimeter apparatus with scale"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">CORE 10 · Energy</p><b>Pop-Can Calorimeter</b><span>Follow a candle from grams of fuel to joules in water.</span></div>
</a>
<a class="atlas-tile" href="water-clock/">
<span class="atlas-tile-media atlas-media-light"><img src="water-clock/media/apparatus.webp" width="1350" height="1043" alt="Water clock apparatus schematic"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Physical calculus</p><b>Galileo’s Water Clock</b><span>Weigh water, calibrate flow, and time a ramp.</span></div>
</a>
<a class="atlas-tile" href="teatime/">
<span class="atlas-tile-media"><img src="teatime/media/optical-bench.svg" width="1040" height="650" alt="TeaTime optical bench schematic"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Kitchen Inquiry</p><b>TeaTime · Beer–Lambert</b><span>Calibrate light transmission to identify an unknown.</span></div>
</a>
<a class="atlas-tile" href="sphericity-meter/">
<span class="atlas-tile-media"><img src="sphericity-meter/media/opening-rocks.webp" width="1450" height="551" alt="Selection of rocks for comparing sphericity"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Inquiry design</p><b>Invent a Sphericity Meter</b><span>Invent a repeatable rule for shape and test its limits.</span></div>
</a>
<a class="atlas-tile" href="catalase-fem/open-lab/">
<span class="atlas-tile-media atlas-media-dark"><img src="catalase-fem/media/open-lab-cover-v1.1.svg" width="1200" height="720" alt="Oxygen collection apparatus and balloon calibration"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Open Lab · Biology</p><b>Catalase Open Lab</b><span>Yeast, peroxide, gas collection, and teacher/student guides.</span></div>
</a>
</div>
</section>

<section class="atlas-panel" id="panel-instruments" data-panel="instruments" role="tabpanel" aria-labelledby="tab-instruments" hidden>
<div class="atlas-panel-bar">
<p><strong>Software-defined laboratory &amp; robotics:</strong> low-cost wireless builds, browser dashboards, and visible machines.</p>
<div class="atlas-panel-links"><a href="ideas/#4-the-software-defined-laboratory">SDL architecture</a><a href="ideas/#32-low-cost-is-an-engineering-constraint-not-an-apology">Low-cost rule</a><a href="explore/#build">Build pathway →</a></div>
</div>
<div class="atlas-strip-3">
<a class="atlas-tile" href="instruments/">
<span class="atlas-tile-media"><img src="instruments/screens/frequency-meter.webp" width="1240" height="945" alt="Wireless frequency meter browser dashboard"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Instrument workshop</p><b>Virtual Instruments</b><span>Five wireless builds—voltmeter, frequency meter, scale, ToF ruler, thermometer.</span></div>
</a>
<a class="atlas-tile" href="lazy-lidar/">
<span class="atlas-tile-media"><img src="lazy-lidar/media/cutebot-console.webp" width="1680" height="1142" alt="Lazy LiDAR browser console"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Bargain Bin Robotics</p><b>Lazy LiDAR</b><span>Build a room map from patient readings and inspect heading bias.</span></div>
</a>
<a class="atlas-tile" href="cutebot-motion-evidence/">
<span class="atlas-tile-media"><img src="cutebot-motion-evidence/media/cutebot-card.webp" width="900" height="500" alt="Cutebot robot for motion evidence lab"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">ROBOT_EDU preview</p><b>Cutebot Motion Evidence</b><span>Separate what a robot was told to do from what it actually did.</span></div>
</a>
</div>
</section>

<section class="atlas-panel" id="panel-movement" data-panel="movement" role="tabpanel" aria-labelledby="tab-movement" hidden>
<div class="atlas-panel-bar">
<p><strong>Measured human performance:</strong> interpretable gait trials, step validation, and fair physical workload testing.</p>
<div class="atlas-panel-links"><a href="ideas/#23-movement-quality--sqm">SQM+ idea</a><a href="ideas/#22-fair-fitness--dynametics">Fair Fitness idea</a><a href="explore/#movement">Movement path →</a></div>
</div>
<div class="atlas-pair">
<article class="atlas-card">
<a class="atlas-card-media atlas-media-contain" href="sqm-plus/" aria-label="Open SQM+ Hallway Observatory"><img src="sqm-plus/media/hallway.svg" width="1280" height="610" alt="Diagram of an 11-meter hallway observatory leg"></a>
<div class="atlas-card-body">
<p class="atlas-kicker">Gait metrology · Sensor validation</p>
<h3><a href="sqm-plus/">SQM+ Hallway Observatory</a></h3>
<p>Start with a marked 11-meter leg and an independent clock, then test what a wearable step detector actually catches.</p>
<div class="atlas-card-actions"><a class="atlas-btn-primary" href="sqm-plus/">Open exhibit <span aria-hidden="true">→</span></a></div>
</div>
</article>
<article class="atlas-card">
<a class="atlas-card-media atlas-media-dark" href="fair-fitness-testing/" aria-label="Open Fair Fitness Testing"><img src="fair-fitness-testing/media/three-checks.svg" width="1200" height="630" alt="Three jobs in Fair Fitness Testing: prescribe work, confirm motion, observe heart rate"></a>
<div class="atlas-card-body">
<p class="atlas-kicker">Release preview · Workload prescription</p>
<h3><a href="fair-fitness-testing/">Fair Fitness Testing</a></h3>
<p>Separate prescribing physical work, verifying motion evidence, and supervising heart-rate response in an Android prototype walkthrough.</p>
<div class="atlas-card-actions"><a class="atlas-btn-primary" href="fair-fitness-testing/">Open exhibit <span aria-hidden="true">→</span></a></div>
</div>
</article>
</div>
</section>

<section class="atlas-panel" id="panel-research" data-panel="research" role="tabpanel" aria-labelledby="tab-research" hidden>
<div class="atlas-panel-bar">
<p><strong>Circuits to Genomes:</strong> architectural economy, evolutionary peroxide management, and accountable AI-assisted inquiry.</p>
<div class="atlas-panel-links"><a href="circuits-to-genomes/#architecture">Paper 1</a><a href="circuits-to-genomes/#peroxide">Paper 2</a><a href="circuits-to-genomes/#investigator">Paper 3</a><a href="ideas/#11-fidelity-mirrors--one-phenomenon-many-realizations">Fidelity Mirrors</a></div>
</div>
<div class="atlas-strip-3">
<a class="atlas-tile" href="circuits-to-genomes/">
<span class="atlas-tile-media atlas-media-light"><img src="circuits-to-genomes/media/reciprocal.svg" width="1200" height="430" alt="Golden thread connecting PDP-8, regulatory genome, and parallel computation"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Research portal · v1.2</p><b>From Circuits to Genomes</b><span>Three scholarly tracks, computational evidence, and preserved companion archive.</span></div>
</a>
<a class="atlas-tile" href="catalase-fem/">
<span class="atlas-tile-media atlas-media-dark"><img src="catalase-fem/media/research-cover-v1.1.svg" width="1200" height="720" alt="Conceptual catalase molecular architecture"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Biochemical benchmark</p><b>Catalase &amp; Continuity</b><span>One reaction, diverse molecular architectures and complementary scavenging.</span></div>
</a>
<a class="atlas-tile" href="catalase-fem/open-lab/">
<span class="atlas-tile-media atlas-media-dark"><img src="catalase-fem/media/open-lab-cover-v1.1.svg" width="1200" height="720" alt="Catalase Open Lab apparatus illustration"></span>
<div class="atlas-tile-body"><p class="atlas-kicker">Open Lab · 21 pp. guides</p><b>Catalase Open Lab</b><span>Kitchen-table yeast &amp; peroxide entry point with guides, Python, and data templates.</span></div>
</a>
</div>
</section>

<section class="atlas-archive-band" aria-label="Connecting ideas and archive index">
<div class="atlas-idea-row">
<span class="atlas-idea-label">Recurring ideas:</span>
<a href="ideas/#1-how-much--enough">How Much? / Enough?</a>
<a href="ideas/#2-experience-before-equation">Experience Before Equation</a>
<a href="ideas/#4-the-software-defined-laboratory">Software-Defined Lab</a>
<a href="ideas/#12-executable-transparency">Executable Transparency</a>
<a href="ideas/#32-low-cost-is-an-engineering-constraint-not-an-apology">Low Cost Constraint</a>
</div>
<div class="atlas-index-row">
<a href="exhibits/">All exhibits →</a>
<a href="ideas/">33 ideas →</a>
<a href="inventory/">Project inventory →</a>
<a href="repositories/">Search {n} repositories →</a>
<a href="explore/">Explore pathways →</a>
</div>
</section>

<footer>
<p class="atlas-footer-line"><span><strong>Randall S. Young, Ed.S.</strong> · Independent researcher &amp; educator · <a href="https://orcid.org/0009-0003-1657-0243">ORCID</a></span><span><a href="https://github.com/RandoSY/project-atlas/tree/atlas-web-preview">View the source on GitHub</a></span></p>
</footer>
</main>
<script>
(()=>{{
  const tabs=[...document.querySelectorAll('[data-tab]')];
  const panels=[...document.querySelectorAll('[data-panel]')];
  if(!tabs.length||!panels.length)return;
  const byName=new Map(panels.map(p=>[p.dataset.panel,p]));
  function activate(name,updateHash){{
    const target=byName.has(name)?name:tabs[0].dataset.tab;
    tabs.forEach(t=>{{
      const on=t.dataset.tab===target;
      t.setAttribute('aria-selected',on?'true':'false');
      t.tabIndex=on?0:-1;
    }});
    panels.forEach(p=>{{p.hidden=p.dataset.panel!==target;}});
    if(updateHash){{
      const next=target==='highlights'?location.pathname+location.search:'#'+target;
      history.replaceState(null,'',next);
    }}
  }}
  tabs.forEach((t,i)=>{{
    t.addEventListener('click',()=>activate(t.dataset.tab,true));
    t.addEventListener('keydown',e=>{{
      if(e.key!=='ArrowRight'&&e.key!=='ArrowLeft'&&e.key!=='Home'&&e.key!=='End')return;
      e.preventDefault();
      const idx=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
      tabs[idx].focus();
      activate(tabs[idx].dataset.tab,true);
    }});
  }});
  function fromHash(){{
    const h=decodeURIComponent(location.hash.slice(1));
    activate(byName.has(h)?h:'highlights',false);
  }}
  window.addEventListener('hashchange',fromHash);
  fromHash();
}})();
</script>
</body>
</html>
"""
    (OUT / "index.html").write_text(full, encoding="utf-8")


def start_here():
    data = json.loads((WEB / "start-here.json").read_text(encoding="utf-8"))
    software = data["software_aside"]
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
<p><a class="sg-download" href="Project-Atlas-Start-Here.pdf" download>Download the two-page PDF</a> · <a href="../explore/">Explore the Work by interest</a></p>
<section aria-labelledby="sg-entry">
<h2 id="sg-entry">Choose your first stop</h2>
<ol class="sg-routes">{''.join(routes)}</ol>
</section>
<aside id="make-it-your-own" class="sg-aside" aria-labelledby="sg-aside-title">
<h2 id="sg-aside-title">{esc(software['title'])}</h2>
<p>{esc(software['status'])}</p>
<p>{esc(software['advice'])}</p>
<p>{esc(software['bench_check'])}</p>
<p class="sg-aside-link">{link(software['label'], software['url'])} ·
{link(software['example']['label'], software['example']['url'])}</p>
</aside>
<section aria-labelledby="sg-nav">
<h2 id="sg-nav">Find your way around Atlas</h2>
<dl class="sg-nav-list">{''.join(places)}</dl>
</section>
<section aria-labelledby="sg-exhibits">
<h2 id="sg-exhibits">Ten places to begin</h2>
<p>Try the first move before reading everything. For another no-hardware starting point, <a href="../lazy-lidar/">try mapping a room with Lazy LiDAR</a>.</p>
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
        ("Research and scholarship", "../circuits-to-genomes/", "From Circuits to Genomes",
         "Follow a question from the PDP-8 to genomic regulation and back to modern AI accelerators. Three research papers, 73 pages, plus experimental evidence." , "../circuits-to-genomes/media/pdp8.jpg", 4372, 2906),
        ("Flagship activity", "../singing-rule/", "The Singing Rule",
         "Pluck a ruler and follow the motion from the original bench photo to live traces, measured ringdown, and a model you can try.",
         "../singing-rule/media/bench.webp", 1440, 1084),
        ("New exhibit · Classroom inquiry design", "../sphericity-meter/", "Invent a Sphericity Meter",
         "Which rock is more nearly spherical? Invent a rule another team can repeat, then test what your rule misses.",
         "../sphericity-meter/media/opening-rocks.webp", 1450, 551),
        ("New exhibit · Release preview", "../fair-fitness-testing/", "Fair Fitness Testing",
         "Compare two workload prescriptions and follow a documented Android prototype walkthrough.",
         "../fair-fitness-testing/media/three-checks.svg", 1200, 630),
        ("Premier CORE 10 activity", "../pop-can-calorimeter/", "Pop-Can Calorimeter",
         "Follow a tea light from grams of fuel to joules in the water, compare heating rates, and account for where the rest of the energy went.",
         "../pop-can-calorimeter/media/picoscale.webp", 1440, 847),
        ("Physical calculus", "../water-clock/", "Galileo’s Water Clock",
         "Make time measurable with a cup and scale. Calibrate the flow, try the original interactive lab, and transfer the clock to an inclined plane.",
         "../water-clock/media/apparatus.webp", 1350, 1043),
        ("Kitchen Inquiry Lab", "../teatime/", "TeaTime · Beer–Lambert’s Law",
         "Make a dilution series, measure how much light gets through, and use the calibration to identify an unknown.",
         "../teatime/media/optical-bench.svg", 1040, 650),
        ("Current experiment", "../sqm-plus/", "SQM+ Hallway Observatory",
         "Run a marked 11-meter leg and see why a stopwatch and a wearable answer two different questions.",
         "../sqm-plus/media/hallway.svg", 1280, 610),
        ("Instrument workshop", "../instruments/", "Virtual Instruments",
         "See original dashboards and build a wireless voltmeter, frequency meter, scale, ToF ruler, or thermometer.",
         "../instruments/screens/frequency-meter.webp", 1240, 945),
        ("Robotics · Interactive simulation", "../lazy-lidar/", "Lazy LiDAR",
         "Make a map from ranges and bearings. Then change the heading and see what a repeatable measurement still gets wrong.",
         "../lazy-lidar/media/cutebot-console.webp", 1680, 1142),
        ("ROBOT_EDU · Classroom preview", "../cutebot-motion-evidence/", "Cutebot Motion Evidence Lab",
         "Repeat a short drive command and use a tape measure and a motion trace to decide whether the car did what you asked.",
         "../cutebot-motion-evidence/media/cutebot-card.webp", 900, 500),
        ("Mathematics", CALCULUS, "Ten Problems That Teach Calculus",
         "Start with the cart that reverses direction. Learn why total distance and net change are not the same thing.",
         "/calculus/assets/calculus-tangent-cover.svg", 1600, 800),
        ("Curriculum", "../core-10/", "CORE 10",
         "Use an ordinary cup of water to distinguish the heat it gains from the electricity an appliance uses.",
         "../assets/core10-cover.svg", 1600, 800),
    ]
    blocks = []
    for label, url, title, description, image, width, height in cards:
        if url == "../circuits-to-genomes/":
            description = description + " Photo: Todd Dailey, CC BY-SA 2.0 (see exhibit for attribution)."
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
<p>For a companion lesson in rate and accumulation, visit <a href="../water-clock/">Galileo’s Water Clock</a>. In this experiment the mass goes up, and its slope can tell time.</p>
<p><a href="../sphericity-meter/">Invent a Sphericity Meter</a> takes the same idea of learning through measurement outdoors. Start with a few rocks and ask what a repeatable rule for shape would have to notice.</p>
<p>For a companion lesson in calibration, visit <a href="../teatime/">TeaTime</a>. A cup of tea, a light source, and a detector turn an unknown dilution into a test of Beer–Lambert’s law.</p>
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


def water_clock():
    page("water-clock", "Galileo’s Water Clock",
         "A hands-on path from water mass to elapsed time, then from time to motion.",
         (WEB / "water-clock.html").read_text(encoding="utf-8"),
         header="EXPERIENCE BEFORE EQUATION · MEASUREMENT LADDER",
         extra='<link rel="stylesheet" href="../assets/water-clock.css">\n')


def teatime():
    page("teatime", "TeaTime · Beer–Lambert’s Law",
         "A cup of tea, a little light, and a calibration you can put to the test.",
         (WEB / "teatime.html").read_text(encoding="utf-8"),
         header="EXPERIENCE BEFORE EQUATION · SCIENCE OF TEA TIME",
         extra='<link rel="stylesheet" href="../assets/teatime.css">\n')


def next_edition_pages():
    specs = (
        ("explore", "Explore the Work",
         "Three ways into Randall Young’s work, from classroom inquiry to instruments and human movement.",
         "PROJECT ATLAS · CHOOSE A PATH"),
        ("sphericity-meter", "Invent a Sphericity Meter",
         "A CORE 10 investigation of shape, uniformity, and how to make a fair comparison.",
         "CORE 10 · MODEL-ELICITING ACTIVITY"),
        ("fair-fitness-testing", "Fair Fitness Testing",
         "A release preview about prescribing work, checking motion, and observing the heart-rate response.",
         "MEASURED HUMAN PERFORMANCE · RELEASE PREVIEW"),
        ("lazy-lidar", "Lazy LiDAR",
         "Give an inexpensive range sensor time and a known viewpoint. Can it draw a useful map?",
         "BARGAIN BIN ROBOTICS · PATIENT MAPPING"),
        ("cutebot-motion-evidence", "Cutebot Motion Evidence Lab",
         "A repeatable floor trial that separates what a robot is told to do from what it actually does.",
         "BARGAIN BIN ROBOTICS · ROBOT_EDU"),
    )
    additions = {"fair-fitness-testing": ("fft-captures",), "lazy-lidar": ("lazy-lidar",),
                 "cutebot-motion-evidence": ("cutebot-motion-evidence",)}
    for slug, title, description, header in specs:
        styles = ("work",) + additions.get(slug, ())
        extra = "".join(f'<link rel="stylesheet" href="../assets/{style}.css">\n' for style in styles)
        page(slug, title, description, (WEB / f"{slug}.html").read_text(encoding="utf-8"),
             header=header, extra=extra,
             source=(f"{ESTATE}/bargain-bin-robotics/tree/6b07a83aee4bec98f0cd295cc5d18aad4b3315c3/exemplars/cutebot-motion-evidence"
                     if slug == "cutebot-motion-evidence" else ATLAS))


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
    water_clock()
    teatime()
    next_edition_pages()
    repo_archive(manifest, args.atlas_source / "LEGACY_REPOSITORY_MAP.md")
    for name, title, summary, file, exclude in [
        ("ideas", "Idea index", "The durable ideas behind the work, from measurement and teaching to open instruments and publication.",
         "IDEA_INDEX.md", ["Protected idea estate"]),
        ("inventory", "Project inventory", "The Atlas record of public systems, their documented maturity, and where to find them.",
         "CANONICAL_INVENTORY.md", ["Protected system"]),
    ]:
        body = public_document(args.atlas_source / file, exclude, toc=True)
        if name == "ideas":
            heading = '<h2 id="22-fair-fitness--dynametics">22. Fair Fitness / DYNAMETICS</h2>'
            if heading in body:
                body = body.replace(heading, heading + '\n<p><a href="../fair-fitness-testing/">Open the Fair Fitness Testing exhibit and release preview</a>.</p>', 1)
            else:
                raise ValueError("The Fair Fitness idea anchor changed. Update its exhibit cross-link.")
            lidar_heading = '<h2 id="19-lazy--patient-lidar">19. Lazy / Patient LiDAR</h2>'
            if lidar_heading not in body:
                raise ValueError("The Lazy LiDAR idea anchor changed. Update its exhibit cross-link.")
            body = body.replace(lidar_heading, lidar_heading + '\n<p><a href="../lazy-lidar/">Open the Lazy LiDAR exhibit and virtual robot lab</a>.</p>', 1)
        if name == "inventory":
            cutebot_cell = '<td>Cutebot Motion Evidence Lab</td>'
            if body.count(cutebot_cell) != 1:
                raise ValueError("The Cutebot inventory row changed. Update its exhibit cross-link.")
            body = body.replace(cutebot_cell, '<td><a href="../cutebot-motion-evidence/">Cutebot Motion Evidence Lab</a></td>', 1)
        if name == "inventory":
            body += "<p><strong><a href=\"../circuits-to-genomes/\">From Circuits to Genomes (C2G)</a></strong> — active research portfolio; Paper 1 v11, Paper 2 v1.2, Paper 3 v0.5 (73 pages). <a href=\"https://github.com/RandoSY/circuits-to-genomes\">Canonical research repository</a>. Independent validation pending. Updated 26 November 2026.</p>"
        families = (f'<section class="atlas-family-list" aria-labelledby="families">'
                    f'<h2 id="families">Project families</h2>{homes("../")}</section>') if name == "inventory" else ""
        page(name, title, summary, f'<article>{body}</article>{families}', source=f"{ATLAS_MAIN}/{file}")
    print(f"Built Atlas pages and indexed {len(manifest['repositories'])} public repositories.")

if __name__ == "__main__":
    main()

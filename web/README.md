# Project Atlas on the web

The six static pages under `web/atlas/` are ready to serve at `/atlas/`. They reuse the live calculus page's stylesheet. The two illustrations use the same dark grid, teal, and gold visual language, with subjects drawn for Atlas and CORE 10.

The Idea Index and Project Inventory are rendered from the canonical Markdown at the root of this repository. Their off-GitHub sections are deliberately omitted from the rendered site. The full repository browser uses a snapshot of GitHub's public listing, distinguishes forks, and adds historical project homes from the legacy map. Only the generated `web/atlas/` directory belongs in the Nginx web root.

## Rebuild on a PC

Install Python 3 and Pandoc. From the repository root, run:

```sh
python3 web/build_atlas.py
```

To refresh the public repository snapshot as part of the rebuild:

```sh
python3 web/build_atlas.py --refresh-repos
```

Review the changes to the public snapshot and generated HTML before committing. The IONOS host does not need to run the generator, install any runtime, or hold GitHub credentials.

## Local check

```sh
python3 -m http.server 8000 --directory web
```

Open `http://127.0.0.1:8000/atlas/`. The CORE 10 and first-page downloads link to their existing original copies on GitHub rather than creating new copies. The calculus link stays on the current origin and expects the separate calculus site at `/calculus/`. The standalone preview serves Atlas only.

## First install on the existing IONOS VM

Use the same authenticated Linux shell and Nginx web root that serve `/calculus/`. The commands in the handoff download the reviewed commit as a GitHub archive and extract only `web/atlas/`. They verify the expected calculus file and the staging files before moving the new directory into place. The first-install command stops if `/atlas/` already exists on disk. No Nginx reload or configuration change is needed, and the calculus directory is not changed.

For later revisions, build in GitHub first, stage a new directory beside the current Atlas, and retain the previous directory outside the web root until the new version and its links are verified.


## Virtual Instruments

The home-page feature leads into five build guides and a gallery of real browser captures. The gallery captions and original source names are in `capture_catalog.json`. The public copies are WebP images, not the original device-control HTML. Most captures were freshly rendered from the original interfaces with no bench device attached. The archived UNO Q reference screenshot is identified separately.

The guide is authored in `instruments.html`; the generator inserts the capture catalog and writes `atlas/instruments/index.html`. Treat illustrative pin assignments as starting points, not tested builds or replacements for the board documentation.

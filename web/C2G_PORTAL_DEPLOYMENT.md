# C2G portal 1.0 — deployment and preservation
27 November 2026. Author-approved website refocus. Portal content commit 08c89ba55cb5ab78aa27c43e5d502de5c7757666; previous branch head 337a29d887d761407da17d733a53794e8a58d3bc retains the old site. No research manuscripts or prior figures changed. New current Paper 2 is peroxide-management v0.1 Markdown; Paper 3 v0.6 Markdown; Paper 1 v11 PDF. Primate FEM v1.2 and all other versions remain independently accessible; v1.3 is uninspected. No current total page count asserted. Open Lab v1.1 ZIP and original installer present under web/releases/catalase-open-lab/v1.1/; live downloads previously reported linked, not independently checked by assistant.

## Run on the Atlas Ubuntu server
```bash
work=$(mktemp -d)
git clone --depth 1 --single-branch --branch atlas-web-preview https://github.com/RandoSY/project-atlas.git "$work/repo" && python3 "$work/repo/web/deploy-c2g-portal.py"
```
Use sudo if not root. Default /var/www/html/atlas, override --site and --url if needed. No raw GitHub downloads, no binary transfer required. Preflight checks existing images and Open Lab downloads, checks tab IDs, selectively merges only three relevant gallery cards, preserves the old catalase research page and all unrelated pages, backs up four target files, checks public bytes and rolls back on failure. --local-only is for staging tests, not production. Existing historical image assets were generated or installed in previous deployments and not recreated here. If any missing, restore the named file before rerunning. Previous historical anchor links map to current panels. With JavaScript disabled all sections remain visible. Browser/production validation pending.

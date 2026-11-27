#!/usr/bin/env bash
# Deploy CAT-FEM without replacing other live gallery entries.
set -Eeuo pipefail
REV=cdbf36865cfaa106e4f7fffe8040b098dca0abac
SITE=${ATLAS_SITE:-/var/www/html/atlas}
BASE=${ATLAS_URL:-https://project-atlas-lab.duckdns.org/atlas}
RAW="https://raw.githubusercontent.com/RandoSY/project-atlas/$REV/web/atlas"
WORK=$(mktemp -d)
BACKUP=""
CHANGED=0
FILES=(catalase-fem/media/cover.svg catalase-fem/index.html exhibits/index.html)
cleanup(){
  code=$?
  if (( code != 0 && CHANGED == 1 )); then
    echo "Verification failed; restoring affected files from $BACKUP" >&2
    for f in "${FILES[@]}"; do
      if [[ -f "$BACKUP/$f" ]]; then install -D -m 644 "$BACKUP/$f" "$SITE/$f" || true
      else rm -f "$SITE/$f" || true; fi
    done
  fi
  rm -rf "$WORK"
  exit "$code"
}
trap cleanup EXIT
for cmd in curl python3 install cmp mktemp; do command -v "$cmd" >/dev/null; done
test -f "$SITE/exhibits/index.html"
test -w "$SITE/exhibits"
fetch(){ curl --retry 3 --connect-timeout 15 --max-time 90 -fsSL "$1" -o "$2"; test -s "$2"; }
mkdir -p "$WORK/stage/catalase-fem/media" "$WORK/stage/exhibits"
for f in "${FILES[@]:0:2}"; do fetch "$RAW/$f" "$WORK/stage/$f"; done
fetch "$RAW/exhibits/index.html" "$WORK/gallery-source.html"
python3 - "$WORK/gallery-source.html" "$SITE/exhibits/index.html" "$WORK/stage/exhibits/index.html" <<'PY'
import re, sys
from pathlib import Path
src, live, dest = map(Path, sys.argv[1:])
s = src.read_text(encoding="utf-8")
current = live.read_text(encoding="utf-8")
pattern = r"<!-- CAT-FEM exhibit start -->.*?<!-- CAT-FEM exhibit end -->"
cards = re.findall(pattern, s, re.S)
if len(cards) != 1:
    raise SystemExit("Expected one pinned CAT-FEM card")
if len(re.findall(pattern, current, re.S)) > 1:
    raise SystemExit("Duplicate CAT-FEM cards; inspect gallery")
if re.search(pattern, current, re.S):
    result = re.sub(pattern, lambda _: cards[0], current, count=1, flags=re.S)
else:
    marker = '<div class="atlas-exhibits">'
    if current.count(marker) != 1 or "../catalase-fem/" in current:
        raise SystemExit("Unexpected live gallery structure; no changes made")
    result = current.replace(marker, marker + cards[0], 1)
dest.write_text(result, encoding="utf-8")
PY
for f in "${FILES[@]}"; do test -s "$WORK/stage/$f"; done
for f in calculus-theme.css atlas.css navigation.css work.css; do test -s "$SITE/assets/$f"; done
BACKUP=$(mktemp -d "${HOME:-/root}/atlas-cat-fem-backup-XXXXXXXX")
for f in "${FILES[@]}"; do
  if [[ -f "$SITE/$f" ]]; then install -D -m 644 "$SITE/$f" "$BACKUP/$f"; fi
done
echo "Backup: $BACKUP"
CHANGED=1
for f in "${FILES[@]}"; do
  mkdir -p "$(dirname "$SITE/$f")"
  tmp=$(mktemp "$SITE/$f.tmp.XXXXXXXX")
  install -m 644 "$WORK/stage/$f" "$tmp"
  mv -f "$tmp" "$SITE/$f"
done
for f in "${FILES[@]}"; do
  fetch "${BASE%/}/$f?rev=$REV" "$WORK/live"
  cmp "$WORK/live" "$WORK/stage/$f"
  echo "VERIFIED: $f"
done
CHANGED=0
echo "CAT-FEM EXHIBIT DEPLOYED"
echo "${BASE%/}/catalase-fem/"
echo "${BASE%/}/exhibits/"
echo "Backup: $BACKUP"

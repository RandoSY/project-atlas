#!/usr/bin/env bash
# Install verified Catalase Open Lab v1.1. No edits until archive is verified.
set -Eeuo pipefail
REV=7cd09de4015a53a144880272399f676689c01fa7
SITE=${ATLAS_SITE:-/var/www/html/atlas}
BASE=${ATLAS_URL:-https://project-atlas-lab.duckdns.org/atlas}
RAW="https://raw.githubusercontent.com/RandoSY/project-atlas/$REV/web/atlas"
ZIPURL="https://raw.githubusercontent.com/RandoSY/project-atlas/atlas-web-preview/web/atlas/catalase-fem/downloads/v1.1/Catalase_Open_Lab_v1.1.zip"
WORK=$(mktemp -d)
STAGE="$WORK/stage"
EX=catalase-fem
D="$EX/downloads/v1.1"
FILES=("$EX/media/cover.svg" "$EX/media/open-lab-apparatus.svg" "$EX/media/open-lab-balloon.svg" "$D/SHA256SUMS.txt" "$D/Catalase_Open_Lab_v1.1.zip" "$D/01_Teacher_Guide.pdf" "$D/02_Student_Guide.pdf" "$D/03_Theory_and_Research.pdf" "$D/START_HERE.txt" "$D/analyze.py" "$D/measurements_template.csv" "$D/balloon_template.csv" "$EX/index.html" exhibits/index.html)
BACKUP=""
CHANGED=0
cleanup(){
  rc=$?
  if (( rc != 0 && CHANGED == 1 )); then
    echo "Verification failed; restoring $BACKUP" >&2
    for f in "${FILES[@]}"; do
      if [[ -f "$BACKUP/$f" ]]; then install -D -m 644 "$BACKUP/$f" "$SITE/$f" || true
      else rm -f "$SITE/$f" || true; fi
    done
  fi
  rm -rf "$WORK"
  exit "$rc"
}
trap cleanup EXIT
for cmd in curl python3 sha256sum install cmp mktemp; do command -v "$cmd" >/dev/null; done
test -f "$SITE/exhibits/index.html"
test -w "$SITE/exhibits"
fetch(){ mkdir -p "$(dirname "$2")"; curl --retry 2 --connect-timeout 15 --max-time 120 -fsSL "$1" -o "$2"; test -s "$2"; }
for f in "$EX/media/cover.svg" "$EX/media/open-lab-apparatus.svg" "$EX/media/open-lab-balloon.svg" "$D/SHA256SUMS.txt" "$EX/index.html"; do fetch "$RAW/$f" "$STAGE/$f"; done
if [[ $# -eq 1 ]]; then cp -- "$1" "$STAGE/$D/Catalase_Open_Lab_v1.1.zip"
elif [[ $# -eq 0 ]]; then fetch "$ZIPURL" "$STAGE/$D/Catalase_Open_Lab_v1.1.zip"
else echo "Usage: $0 [local original ZIP]" >&2; exit 2; fi
(cd "$STAGE/$D" && grep '  Catalase_Open_Lab_v1.1.zip$' SHA256SUMS.txt | sha256sum -c -)
python3 - "$STAGE/$D" <<'PY'
from pathlib import Path
from zipfile import ZipFile
import sys
d=Path(sys.argv[1])
names=['01_Teacher_Guide.pdf','02_Student_Guide.pdf','03_Theory_and_Research.pdf','START_HERE.txt','analyze.py','measurements_template.csv','balloon_template.csv']
with ZipFile(d/'Catalase_Open_Lab_v1.1.zip') as z:
    if z.testzip() is not None: raise SystemExit('Corrupt ZIP')
    for n in names:
        data=z.read('catalase_open_lab/'+n)
        if len(data)>10_000_000: raise SystemExit('Unexpected member size')
        (d/n).write_bytes(data)
PY
(cd "$STAGE/$D" && sha256sum -c SHA256SUMS.txt)
fetch "$RAW/exhibits/index.html" "$WORK/gallery-source.html"
mkdir -p "$STAGE/exhibits"
python3 - "$STAGE/$EX/index.html" "$WORK/gallery-source.html" "$SITE/exhibits/index.html" "$STAGE/exhibits/index.html" <<'PY'
import re,sys
from pathlib import Path
page,source,live,dest=map(Path,sys.argv[1:])
s=page.read_text(encoding='utf-8')
for n,label in [('01_Teacher_Guide.pdf','Download teacher guide (PDF)'),('02_Student_Guide.pdf','Download student guide (PDF)'),('03_Theory_and_Research.pdf','Download theory and research (PDF)'),('Catalase_Open_Lab_v1.1.zip','Download complete laboratory ZIP')]:
    pattern=r'(<p[^>]*data-lab-download="'+re.escape(n)+r'"[^>]*>).*?(</p>)'
    s,count=re.subn(pattern,lambda m:m[1]+'<a href="downloads/v1.1/'+n+'">'+label+'</a>'+m[2],s,flags=re.S)
    if count!=1: raise SystemExit('Expected one placeholder for '+n)
page.write_text(s,encoding='utf-8')
pattern=r'<!-- CAT-FEM exhibit start -->.*?<!-- CAT-FEM exhibit end -->'
cards=re.findall(pattern,source.read_text(encoding='utf-8'),re.S)
if len(cards)!=1: raise SystemExit('Expected one source card')
card=cards[0].replace('Follow a 2024 kitchen experiment design into a study of evolutionary functional continuity. Compare published enzyme measurements, inspect the Python analysis, and explore the next research question.','Try the illustrated Open Lab with teacher and student guides, oxygen measurements, balloon calibration, and the scientific bridge to Circuits to Genomes.')
s=live.read_text(encoding='utf-8')
matches=re.findall(pattern,s,re.S)
if len(matches)>1: raise SystemExit('Duplicate gallery entry')
if matches: s=re.sub(pattern,lambda _:card,s,count=1,flags=re.S)
else:
    marker='<div class="atlas-exhibits">'
    if s.count(marker)!=1 or '../catalase-fem/' in s: raise SystemExit('Unexpected gallery structure')
    s=s.replace(marker,marker+card,1)
dest.write_text(s,encoding='utf-8')
PY
for f in "${FILES[@]}"; do test -s "$STAGE/$f"; done
for f in calculus-theme.css atlas.css navigation.css work.css; do test -s "$SITE/assets/$f"; done
BACKUP=$(mktemp -d "${HOME:-/root}/atlas-open-lab-backup-XXXXXXXX")
for f in "${FILES[@]}"; do
  if [[ -f "$SITE/$f" ]]; then install -D -m 644 "$SITE/$f" "$BACKUP/$f"; fi
done
CHANGED=1
for f in "${FILES[@]}"; do
  mkdir -p "$(dirname "$SITE/$f")"
  tmp=$(mktemp "$SITE/$f.tmp.XXXXXXXX")
  install -m 644 "$STAGE/$f" "$tmp"
  mv -f "$tmp" "$SITE/$f"
done
for f in "${FILES[@]}"; do
  fetch "${BASE%/}/$f?rev=$REV" "$WORK/live"
  cmp "$WORK/live" "$STAGE/$f"
  echo "VERIFIED: $f"
done
CHANGED=0
echo "CATALASE OPEN LAB v1.1 DEPLOYED"
echo "${BASE%/}/catalase-fem/"
echo "Backup: $BACKUP"

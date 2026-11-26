#!/usr/bin/env bash
# Deploy only the illustrated C2G exhibit. Run on the Atlas Linux server.
set -Eeuo pipefail
ATLAS_REV=a7eb7a754903eaac371617fa8393639c39b0436c
C2G_REV=d400c6b2d944f8d4d78c0687e53273a03af560f0
SITE=${ATLAS_SITE:-/var/www/html/atlas}
BASE_URL=${ATLAS_URL:-https://project-atlas-lab.duckdns.org/atlas}
WORK=$(mktemp -d)
STAGE="$WORK/stage"
BACKUP=""
INSTALLED=0
FILES=(index.html media/c2g-cover.svg media/continuity.png media/networks.png media/equivalence.png media/precision.png media/framework.png)
cleanup(){
  code=$?
  if [ "$code" -ne 0 ] && [ "$INSTALLED" -eq 1 ]; then
    echo "Deployment failed; restoring previously installed files." >&2
    for f in "${FILES[@]}"; do
      if [ -f "$BACKUP/$f" ]; then
        install -D -m 644 "$BACKUP/$f" "$SITE/circuits-to-genomes/$f" || true
      else
        rm -f "$SITE/circuits-to-genomes/$f" || true
      fi
    done
    echo "Backup: $BACKUP" >&2
  fi
  rm -rf "$WORK"
  exit "$code"
}
trap cleanup EXIT
test -f "$SITE/index.html" || { echo "Atlas site not found: $SITE" >&2; exit 1; }
test -w "$SITE" || { echo "Run with sudo or as root." >&2; exit 1; }
for cmd in curl sha256sum install cmp; do command -v "$cmd" >/dev/null; done
if ! command -v pdftoppm >/dev/null; then
  echo "Installing Poppler PDF tools..."
  apt-get update
  apt-get install -y poppler-utils
fi
mkdir -p "$STAGE/media"
ATLAS="https://raw.githubusercontent.com/RandoSY/project-atlas/$ATLAS_REV/web/atlas/circuits-to-genomes"
PAPERS="https://raw.githubusercontent.com/RandoSY/circuits-to-genomes/$C2G_REV/papers"
fetch(){ curl --retry 3 --connect-timeout 15 --max-time 180 -fsSL "$1" -o "$2"; test -s "$2"; }
echo "Fetching pinned exhibit and manuscripts..."
fetch "$ATLAS/index.html" "$STAGE/index.html"
fetch "$ATLAS/media/c2g-cover.svg" "$STAGE/media/c2g-cover.svg"
fetch "$PAPERS/01-architectural-economy/Architectural_Economy_v8.pdf" "$WORK/ae.pdf"
fetch "$PAPERS/02-primate-enhancer-fem/Primate_Enhancer_FEM_v1.pdf" "$WORK/fem.pdf"
fetch "$PAPERS/03-augmented-investigator/The_Augmented_Investigator_v0.2.pdf" "$WORK/ai.pdf"
(cd "$WORK" && sha256sum -c <<'SUMS'
f5fa8e89968d5b75118692c628d979c598c490b5d3d8664c6ddd6451166c727f  ae.pdf
0eaa5ca09eff97e341642cb77b80f10e65d5fa9596ec4fa882994255a776c901  fem.pdf
ad6726deb9433ca98d8ddf47d77b136dd837a1927aaa77fb3c6c0ed81dba96c2  ai.pdf
SUMS
)
echo "Rendering manuscript crops..."
crop(){
  local pdf=$1 page=$2 x=$3 y=$4 w=$5 h=$6 name=$7
  pdftoppm -r 144 -f "$page" -l "$page" -singlefile -png -x "$x" -y "$y" -W "$w" -H "$h" "$WORK/$pdf.pdf" "$STAGE/media/$name"
}
crop ae 17 120 470 984 482 continuity
crop ae 5 120 120 984 336 networks
crop fem 8 116 120 992 352 equivalence
crop fem 9 116 215 992 350 precision
crop ai 6 118 234 992 442 framework
for f in "${FILES[@]}"; do test -s "$STAGE/$f"; done
BACKUP=$(mktemp -d "${HOME:-/root}/atlas-c2g-backup-XXXXXXXX")
echo "Backing up exhibit to $BACKUP"
for f in "${FILES[@]}"; do
  if [ -f "$SITE/circuits-to-genomes/$f" ]; then
    install -D -m 644 "$SITE/circuits-to-genomes/$f" "$BACKUP/$f"
  fi
done
INSTALLED=1
# Publish assets first, HTML last.
for f in "${FILES[@]:1}"; do install -D -m 644 "$STAGE/$f" "$SITE/circuits-to-genomes/$f"; done
install -D -m 644 "$STAGE/index.html" "$SITE/circuits-to-genomes/index.html"
echo "Checking live content..."
for f in "${FILES[@]}"; do
  fetch "${BASE_URL%/}/circuits-to-genomes/$f?rev=$ATLAS_REV" "$WORK/live"
  cmp "$WORK/live" "$STAGE/$f"
  echo "VERIFIED: $f"
done
INSTALLED=0
for f in index.html exhibits/index.html; do
  if ! grep -q 'circuits-to-genomes/' "$SITE/$f"; then
    echo "NOTE: $f does not yet link to C2G; existing navigation was not overwritten."
  fi
done
echo "C2G ILLUSTRATED EDITION DEPLOYED"
echo "Backup: $BACKUP"
echo "${BASE_URL%/}/circuits-to-genomes/"

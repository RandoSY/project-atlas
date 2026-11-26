#!/usr/bin/env bash
# Deploy the 26 Nov 2026 C2G research exhibit only, preserving other Atlas pages.
set -Eeuo pipefail
ATLAS_REV=2439de4e8e271d111ccb1f0bcda4c3be0929dccd
C2G_REV=d400c6b2d944f8d4d78c0687e53273a03af560f0
SITE=${ATLAS_SITE:-/var/www/html/atlas}
BASE_URL=${ATLAS_URL:-https://project-atlas-lab.duckdns.org/atlas}
WORK=$(mktemp -d)
STAGE="$WORK/stage"
BACKUP=""
INSTALLED=0
EXHIBIT=circuits-to-genomes
FILES=(index.html exhibits/index.html inventory/index.html "$EXHIBIT/index.html" "$EXHIBIT/media/c2g-cover.svg" "$EXHIBIT/media/research.css" "$EXHIBIT/media/reciprocal.svg" "$EXHIBIT/media/dependencies.svg" "$EXHIBIT/media/PHOTO_CREDIT.md" "$EXHIBIT/media/pdp8.jpg" "$EXHIBIT/media/continuity.png" "$EXHIBIT/media/networks.png" "$EXHIBIT/media/equivalence.png" "$EXHIBIT/media/precision.png" "$EXHIBIT/media/framework.png")
cleanup(){
  code=$?
  if [ "$code" -ne 0 ] && [ "$INSTALLED" -eq 1 ]; then
    echo "Verification failed; restoring prior Atlas files." >&2
    for f in "${FILES[@]}"; do
      if [ -f "$BACKUP/$f" ]; then install -D -m 644 "$BACKUP/$f" "$SITE/$f" || true
      else rm -f "$SITE/$f" || true; fi
    done
    echo "Backup: $BACKUP" >&2
  fi
  rm -rf "$WORK"
  exit "$code"
}
trap cleanup EXIT
test -f "$SITE/index.html" || { echo "Atlas site not found: $SITE" >&2; exit 1; }
test -w "$SITE" || { echo "Run with sudo or as root." >&2; exit 1; }
for cmd in curl sha256sum sha1sum install cmp pdftoppm; do
  command -v "$cmd" >/dev/null || { echo "Missing $cmd. Install poppler-utils if pdftoppm is absent." >&2; exit 1; }
done
mkdir -p "$STAGE/$EXHIBIT/media"
ATLAS="https://raw.githubusercontent.com/RandoSY/project-atlas/$ATLAS_REV/web/atlas"
PAPERS="https://raw.githubusercontent.com/RandoSY/circuits-to-genomes/$C2G_REV/papers"
fetch(){ mkdir -p "$(dirname "$2")"; curl --retry 3 --connect-timeout 15 --max-time 180 -fsSL "$1" -o "$2"; test -s "$2"; }
echo "Staging current exhibit, navigation and illustrations..."
for f in "${FILES[@]:0:9}"; do fetch "$ATLAS/$f" "$STAGE/$f"; done
# The original source photo is pinned by its Wikimedia Commons SHA-1.
fetch "https://upload.wikimedia.org/wikipedia/commons/1/16/PDP-8_at_the_Computer_History_Museum.jpg" "$STAGE/$EXHIBIT/media/pdp8.jpg"
printf '%s  %s\n' '92b33981b19ad1082ee2fe3738db65f379ec8c93' "$STAGE/$EXHIBIT/media/pdp8.jpg" | sha1sum -c -
# Older manuscript figures remain explicitly labeled with their actual source.
fetch "$PAPERS/01-architectural-economy/Architectural_Economy_v8.pdf" "$WORK/ae.pdf"
fetch "$PAPERS/02-primate-enhancer-fem/Primate_Enhancer_FEM_v1.pdf" "$WORK/fem.pdf"
fetch "$PAPERS/03-augmented-investigator/The_Augmented_Investigator_v0.2.pdf" "$WORK/ai.pdf"
(cd "$WORK" && sha256sum -c <<'SUMS'
f5fa8e89968d5b75118692c628d979c598c490b5d3d8664c6ddd6451166c727f  ae.pdf
0eaa5ca09eff97e341642cb77b80f10e65d5fa9596ec4fa882994255a776c901  fem.pdf
ad6726deb9433ca98d8ddf47d77b136dd837a1927aaa77fb3c6c0ed81dba96c2  ai.pdf
SUMS
)
crop(){
  local pdf=$1 page=$2 x=$3 y=$4 w=$5 h=$6 name=$7
  pdftoppm -r 144 -f "$page" -l "$page" -singlefile -png -x "$x" -y "$y" -W "$w" -H "$h" "$WORK/$pdf.pdf" "$STAGE/$EXHIBIT/media/$name"
}
crop ae 17 120 470 984 482 continuity
crop ae 5 120 120 984 336 networks
crop fem 8 116 120 992 352 equivalence
crop fem 9 116 215 992 350 precision
crop ai 6 118 234 992 442 framework
for f in "${FILES[@]}"; do test -s "$STAGE/$f"; done
for f in Architectural_Economy_v11.pdf Primate_Enhancer_FEM_v1.2.pdf The_Augmented_Investigator_v0.5.pdf; do grep -Fq "$f" "$STAGE/$EXHIBIT/index.html"; done
# Refuse to deploy if the three latest public PDFs cannot be downloaded and verified.
LATEST="https://raw.githubusercontent.com/RandoSY/circuits-to-genomes/b418b4c8ed95fb63163c11636d6dec11e0c85ffc/papers"
fetch "$LATEST/01-architectural-economy/Architectural_Economy_v11.pdf" "$WORK/latest1.pdf"
fetch "$LATEST/02-primate-enhancer-fem/Primate_Enhancer_FEM_v1.2.pdf" "$WORK/latest2.pdf"
fetch "$LATEST/03-augmented-investigator/The_Augmented_Investigator_v0.5.pdf" "$WORK/latest3.pdf"
(cd "$WORK" && sha256sum -c <<'SUMS'
bd019c078f7af0fcb93ed3528b4d6ef01dd2d19f3e6cec65170669add3146578  latest1.pdf
0a64ee48d98c5b1c219825bd2421bf94c0c0f66b249fe149a6c1f837c8286539  latest2.pdf
fa6e70ae37d71c46e44f6f6e8ab0eef533aafa6b83a4bc80e7d7f138b3680faf  latest3.pdf
SUMS
)
BACKUP=$(mktemp -d "${HOME:-/root}/atlas-c2g-backup-XXXXXXXX")
for f in "${FILES[@]}"; do
  if [ -f "$SITE/$f" ]; then install -D -m 644 "$SITE/$f" "$BACKUP/$f"; fi
done
echo "Backup: $BACKUP"
INSTALLED=1
for f in "${FILES[@]}"; do [[ "$f" == *.html ]] || install -D -m 644 "$STAGE/$f" "$SITE/$f"; done
for f in "${FILES[@]}"; do [[ "$f" != *.html ]] || install -D -m 644 "$STAGE/$f" "$SITE/$f"; done
for f in "${FILES[@]}"; do
  # Attribution Markdown is served statically on the same site.
  fetch "${BASE_URL%/}/$f?rev=$ATLAS_REV" "$WORK/live"
  cmp "$WORK/live" "$STAGE/$f"
  echo "VERIFIED: $f"
done
INSTALLED=0
echo "C2G RESEARCH EXHIBIT DEPLOYED — v11 / v1.2 / v0.5 — 73 pages"
echo "${BASE_URL%/}/circuits-to-genomes/"
echo "${BASE_URL%/}/exhibits/"
echo "Backup: $BACKUP"

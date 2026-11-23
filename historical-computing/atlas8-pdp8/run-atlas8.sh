#!/usr/bin/env bash
# ATLAS-8: one-command desktop and Pico launch.
# Invocation: bash run-atlas8.sh [pc|os8 IMAGE|pico PORT]
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3 not found. Set PYTHON=/path/to/python3 or install python3." >&2
  exit 127
fi

usage() {
  cat <<'EOF'
ATLAS-8 launch modes

  bash run-atlas8.sh                 Run working desktop PDP-8 in Chrome
  bash run-atlas8.sh pc              Same, using 8 memory fields (32K)
  bash run-atlas8.sh os8 IMAGE.rk05  Attach RK05 disk to PC emulator (OS/8 boot NOT YET verified)
  bash run-atlas8.sh pico PORT       Connect Chrome to existing MicroPython Pico
  bash run-atlas8.sh help            Show this help

IMAGE must already exist as a valid RK05/SIMH disk image. The OS/8
experiment defaults to READ-ONLY and does not download disk images.
Use a working copy for any future write-enabled OS/8 exercises.

The Pico mode presently runs the existing instruction-level educational
emulator; full OS/8 disk/pascal support on physical Pico is future work.
EOF
}
case "${1:-pc}" in
  pc)
    exec "$PYTHON" pc_dashboard_server.py --mode sim --fields 8 --open
    ;;
  os8)
    if [[ $# -ne 2 || ! -f "${2:-}" ]]; then
      echo "OS/8 development mode requires an existing RK05 image path." >&2
      usage >&2
      exit 2
    fi
    exec "$PYTHON" pc_dashboard_server.py --mode sim --fields 8 --rk05 "$2" --open
    ;;
  pico)
    if [[ $# -ne 2 ]]; then
      echo "Pico mode requires a USB serial port, e.g. COM7 or /dev/ttyACM0." >&2
      usage >&2
      exit 2
    fi
    exec "$PYTHON" pc_dashboard_server.py --mode serial --port "$2" --open
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "Unknown mode: $1" >&2
    usage >&2
    exit 2
    ;;
esac

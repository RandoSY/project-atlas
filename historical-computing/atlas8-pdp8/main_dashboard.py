"""Rename to main.py ON PICO to start the Atlas dashboard USB protocol."""
from dashboard_bridge import serve
serve(fields=1)  # Set fields=8 to enable 32K words (PDP-8/E memory extension).

"""Pico boot entrypoint. Set fields=8 for 32K-word PDP-8 memory."""
from monitor import main
main(fields=1)

# ATLAS-8 v0.5 — GitHub staging status

**Checkpoint:** 2026-11-22

This directory is a dedicated home for the ATLAS-8 PDP-8 MicroPython project.

## Available now
- Branded README and SVG logo
- `pdp8.py`: authentic 12-bit PDP-8 style CPU emulator core
- `programs.py`: real PDP-8 machine-word calculator / Teletype exercises
- `examples/quickstart.py`: standalone arithmetic demonstration
- Windows launcher and start-here notes

Run from the repository directory (Python 3): `python examples/quickstart.py`.
On the Pico, `pdp8.py`, `programs.py` and this example must be copied to the MicroPython filesystem.

## Not yet in this GitHub directory

The **full** v0.5 dashboard release bundle, PC bridge, host server, test suite, operator's manual PDF, and additional modules have been produced as ChatGPT downloadable artifacts, but have not all been transferred to GitHub. Do not expect the Windows launcher to work with this partial directory checkout.

## Validation boundaries

- 26 desktop CPU/host automated tests passed on the complete local package.
- Browser smoke testing of the complete local dashboard covered arithmetic, Teletype and a desktop no-scroll layout.
- The GitHub directory itself has not been independently smoke-tested as an installable release.
- Physical RP2040 hardware and unmodified native OS/8 or FOCAL binaries remain unverified.

**Next publication milestone:** transfer the remaining original release source files and PDF, verify checksums against the local v0.5 bundle, and run a clean-clone dashboard smoke test.

#!/usr/bin/env python3
"""Repository convenience entry point; the installed skill also contains the CLI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "skills/rstack/scripts"))
from rstacklib.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

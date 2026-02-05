#!/usr/bin/env python3
"""
Extract release notes for a given version from CHANGELOG.md.

Usage:
  python scripts/release_notes.py v0.1.0
  python scripts/release_notes.py 0.1.0   # will normalize to v0.1.0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def normalize_version(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("Empty version.")
    if not v.startswith("v"):
        v = "v" + v
    return v


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/release_notes.py vX.Y.Z", file=sys.stderr)
        return 2

    version = normalize_version(sys.argv[1])

    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("ERROR: CHANGELOG.md not found at repo root.", file=sys.stderr)
        return 2

    text = changelog_path.read_text(encoding="utf-8", errors="replace")

    heading_re = re.compile(
        rf"^##\s*(?:\[\s*)?({re.escape(version)})(?:\s*\])?.*$",
        re.MULTILINE,
    )

    m = heading_re.search(text)
    if not m:
        print(f"ERROR: Version section '{version}' not found in CHANGELOG.md.", file=sys.stderr)
        return 2

    start = m.end()
    next_m = re.search(r"^##\s+", text[start:], flags=re.MULTILINE)
    end = start + next_m.start() if next_m else len(text)

    notes = text[start:end].strip()
    notes = re.sub(r"^\s+", "", notes)

    if not notes:
        print(f"ERROR: Version section '{version}' is empty.", file=sys.stderr)
        return 2

    print(notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

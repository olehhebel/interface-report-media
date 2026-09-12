#!/usr/bin/env python3
"""Repair known deterministic text corruption in generated editorial output."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPLACEMENTS = {
    "slow iona users actually feel": "slow paths users actually feel",
    "request iona: routing": "request path: routing",
    "user’s ionience threshold": "user’s patience threshold",
    "per-iona metadata fetches": "per-request metadata fetches",
    "warm iona": "warm path",
    "critical iona": "critical path",
    "miss iona": "miss path",
    "request iona boring": "request path boring",
    "synchronous iona": "synchronous path",
    "cold ionas": "cold paths",
    "synchronous ionas": "synchronous paths",
    "machine-usable iona alongside": "machine-usable path alongside",
}

changed = []
for pattern in ("*.html", "*.xml"):
    for path in ROOT.rglob(pattern):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for bad, good in REPLACEMENTS.items():
            text = text.replace(bad, good)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

remaining = []
for pattern in ("*.html", "*.xml"):
    for path in ROOT.rglob(pattern):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "iona" in text or "ionience" in text:
            remaining.append(str(path.relative_to(ROOT)))
if remaining:
    raise SystemExit("unrepaired generated-text corruption remains: " + ", ".join(sorted(set(remaining))))

print(f"generated text repaired in {len(changed)} files")

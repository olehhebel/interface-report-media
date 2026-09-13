#!/usr/bin/env python3
"""Merge sitemap URL entries from a pre-generation snapshot without overwriting generated entries."""
from __future__ import annotations

import argparse
import pathlib
import xml.etree.ElementTree as ET

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"
ET.register_namespace("", NS)
ET.register_namespace("image", IMAGE_NS)


def loc_of(node: ET.Element) -> str:
    loc = node.find(f"{{{NS}}}loc")
    return (loc.text or "").strip() if loc is not None else ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=pathlib.Path)
    parser.add_argument("--target", type=pathlib.Path, default=pathlib.Path("sitemap.xml"))
    args = parser.parse_args()

    if not args.snapshot.exists():
        raise SystemExit(f"missing sitemap snapshot: {args.snapshot}")
    if not args.target.exists():
        raise SystemExit(f"missing generated sitemap: {args.target}")

    old_tree = ET.parse(args.snapshot)
    new_tree = ET.parse(args.target)
    old_root = old_tree.getroot()
    new_root = new_tree.getroot()

    existing = {loc_of(node) for node in new_root.findall(f"{{{NS}}}url")}
    restored = 0
    for node in old_root.findall(f"{{{NS}}}url"):
        loc = loc_of(node)
        if not loc or loc in existing:
            continue
        new_root.append(node)
        existing.add(loc)
        restored += 1

    ET.indent(new_tree, space="  ")
    new_tree.write(args.target, encoding="utf-8", xml_declaration=True)
    print(f"restored {restored} sitemap entries from pre-generation snapshot")


if __name__ == "__main__":
    main()

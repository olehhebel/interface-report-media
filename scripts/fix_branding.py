#!/usr/bin/env python3
"""Normalize Interface Report branding and organization schema across static HTML."""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGO_URL = "https://interfacereport.com/assets/interface-report-logo.png"
HEADER_OLD = '<a class="brand" href="/"><span class="brand-dot"></span>Interface Report</a>'
HEADER_NEW = '<a class="brand" href="/" aria-label="Interface Report home"><img src="/assets/interface-report-logo.png" width="1536" height="768" alt="Interface Report" decoding="async" style="display:block;height:32px;width:auto"/></a>'
FOOTER_OLD = '<div class="footer-brand">Interface<br/>Report.</div>'
FOOTER_NEW = '<a href="/" aria-label="Interface Report home"><img src="/assets/interface-report-logo.png" width="1536" height="768" alt="Interface Report" loading="lazy" decoding="async" style="display:block;width:180px;height:auto"/></a>'
SCRIPT_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def repair_jsonld(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw

    changed = False

    def walk(node):
        nonlocal changed
        if isinstance(node, dict):
            kinds = node.get("@type")
            if isinstance(kinds, str):
                kinds = [kinds]
            if isinstance(kinds, list) and any(k in {"Organization", "NewsMediaOrganization"} for k in kinds):
                logo = {
                    "@type": "ImageObject",
                    "@id": "https://interfacereport.com/#logo",
                    "url": LOGO_URL,
                    "contentUrl": LOGO_URL,
                    "width": 1536,
                    "height": 768,
                    "caption": "Interface Report",
                }
                if node.get("logo") != logo:
                    node["logo"] = logo
                    changed = True
                image = {"@id": "https://interfacereport.com/#logo"}
                if node.get("image") != image:
                    node["image"] = image
                    changed = True
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")) if changed else raw


changed_files = []
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    original = text
    text = text.replace(HEADER_OLD, HEADER_NEW).replace(FOOTER_OLD, FOOTER_NEW)
    text = SCRIPT_RE.sub(lambda m: f'<script type="application/ld+json">{repair_jsonld(m.group(1))}</script>', text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        changed_files.append(str(path.relative_to(ROOT)))

# Fail closed if legacy text branding remains in static HTML.
legacy = []
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    if HEADER_OLD in text or FOOTER_OLD in text:
        legacy.append(str(path.relative_to(ROOT)))
    if 'NewsMediaOrganization' in text and LOGO_URL not in text:
        legacy.append(f"{path.relative_to(ROOT)}:missing-org-logo")
if legacy:
    raise SystemExit("branding normalization incomplete: " + ", ".join(sorted(set(legacy))))

print(f"canonical branding normalized in {len(changed_files)} files")

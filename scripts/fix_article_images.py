#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://interfacereport.com/assets/"

IMAGES = {
    "data-agent-kills-dashboard-first-analytics": ("agent-control-surface.png", "AI analytics agent control surface"),
    "gpt-6-astra-model-is-not-the-product": ("agent-control-surface.png", "AI product capability control surface"),
    "agents-api-build-vs-orchestrate": ("patterns.png", "AI agent orchestration patterns"),
    "agent-harness-portability-infrastructure": ("patterns.png", "Portable AI agent harness patterns"),
    "permission-ux-is-ai-safety-interface": ("trust.png", "AI permission and trust interface"),
    "evidence-loop-ai-analytics-trust": ("trust.png", "AI analytics evidence and trust loop"),
    "full-duplex-voice-ui-design-rules": ("agent-control-surface.png", "Full-duplex AI voice control surface"),
    "stop-making-every-ai-feature-chat": ("patterns.png", "Alternative AI interaction patterns"),
    "production-agent-sandbox-checklist": ("trust.png", "Production AI agent safety controls"),
    "tail-latency-ai-product-engineering": ("patterns.png", "AI product latency and reliability patterns"),
    "ai-pricing-is-a-product-system": ("patterns.png", "AI product pricing system patterns"),
    "agent-ready-saas-nonhuman-buyer": ("agent-control-surface.png", "Agent-ready SaaS control surface"),
}

for slug, (filename, alt) in IMAGES.items():
    path = ROOT / "analysis" / slug / "index.html"
    text = path.read_text(encoding="utf-8")
    text = text.replace(f"{BASE}og-default.png", f"{BASE}{filename}")
    text = text.replace('src="/assets/og-default.png"', f'src="/assets/{filename}"')
    text = text.replace('alt="Interface Report editorial analysis"', f'alt="{alt}"')
    text = text.replace('content="Interface Report editorial analysis"', f'content="{alt}"')
    path.write_text(text, encoding="utf-8")

sitemap = ROOT / "sitemap.xml"
text = sitemap.read_text(encoding="utf-8")
for slug, (filename, _) in IMAGES.items():
    pattern = rf'(<url><loc>https://interfacereport\.com/analysis/{re.escape(slug)}/</loc><lastmod>[^<]+</lastmod><image:image><image:loc>)https://interfacereport\.com/assets/og-default\.png(</image:loc></image:image></url>)'
    text, n = re.subn(pattern, rf'\1{BASE}{filename}\2', text)
    if n != 1:
        raise SystemExit(f"sitemap image replacement failed for {slug}: {n}")
sitemap.write_text(text, encoding="utf-8")

for slug, (filename, _) in IMAGES.items():
    page = (ROOT / "analysis" / slug / "index.html").read_text(encoding="utf-8")
    expected = f"{BASE}{filename}"
    if expected not in page or "assets/og-default.png" in page:
        raise SystemExit(f"article image QA failed for {slug}")

print(f"updated {len(IMAGES)} article images and sitemap image entries")

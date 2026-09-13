#!/usr/bin/env python3
"""Ensure every Interface Report analysis article has canonical BreadcrumbList JSON-LD."""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = "https://interfacereport.com"
SCRIPT_RE = re.compile(
    r'(<script\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)',
    re.S | re.I,
)

TOPICS = {
    "AI Products": ("AI Products", "/topics/ai-products/"),
    "AI Product": ("AI Products", "/topics/ai-products/"),
    "AI Agents": ("AI Agents", "/topics/ai-agents/"),
    "Agents": ("AI Agents", "/topics/ai-agents/"),
    "Human–AI": ("Human–AI", "/topics/human-ai/"),
    "Human-AI": ("Human–AI", "/topics/human-ai/"),
    "Design & UX": ("Design & UX", "/topics/design-ux/"),
    "Design &amp; UX": ("Design & UX", "/topics/design-ux/"),
    "Engineering": ("Engineering", "/topics/engineering/"),
    "Startups & SaaS": ("Startups & SaaS", "/topics/startups-saas/"),
    "Startups &amp; SaaS": ("Startups & SaaS", "/topics/startups-saas/"),
}


def absolute(url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"{SITE}{url if url.startswith('/') else '/' + url}"


def repair(path: pathlib.Path) -> bool:
    text = path.read_text(encoding="utf-8")
    match = SCRIPT_RE.search(text)
    if not match:
        raise SystemExit(f"missing JSON-LD script in {path.relative_to(ROOT)}")

    try:
        data = json.loads(match.group(2))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON-LD in {path.relative_to(ROOT)}: {exc}") from exc

    graph = data.get("@graph") if isinstance(data, dict) else None
    if not isinstance(graph, list):
        raise SystemExit(f"missing @graph in {path.relative_to(ROOT)}")

    if any(isinstance(node, dict) and node.get("@type") == "BreadcrumbList" for node in graph):
        return False

    article = next((node for node in graph if isinstance(node, dict) and node.get("@type") in {"Article", "NewsArticle"}), None)
    webpage = next((node for node in graph if isinstance(node, dict) and node.get("@type") == "WebPage"), None)
    if not article or not webpage:
        raise SystemExit(f"article/webpage schema missing in {path.relative_to(ROOT)}")

    canonical = absolute(str(webpage.get("url") or ""))
    headline = str(article.get("headline") or webpage.get("name") or path.parent.name).strip()
    section = str(article.get("articleSection") or "").strip()

    items = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Interface Report",
            "item": f"{SITE}/",
        }
    ]

    topic = TOPICS.get(section)
    if topic:
        topic_name, topic_path = topic
        items.append(
            {
                "@type": "ListItem",
                "position": 2,
                "name": topic_name,
                "item": absolute(topic_path),
            }
        )

    items.append(
        {
            "@type": "ListItem",
            "position": len(items) + 1,
            "name": headline,
            "item": canonical,
        }
    )

    graph.append(
        {
            "@type": "BreadcrumbList",
            "@id": f"{canonical}#breadcrumb",
            "itemListElement": items,
        }
    )

    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    updated = text[: match.start(2)] + encoded + text[match.end(2) :]
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    article_paths = sorted(ROOT.glob("analysis/*/index.html"))
    if not article_paths:
        raise SystemExit("no analysis article pages found")

    changed = 0
    for article_path in article_paths:
        changed += int(repair(article_path))

    print(f"breadcrumb schema checked on {len(article_paths)} article pages; repaired {changed}")


if __name__ == "__main__":
    main()

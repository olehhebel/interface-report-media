#!/usr/bin/env python3
"""Build a six-story Interface Report newsletter from the live RSS feed.

Preview: python3 scripts/build_newsletter.py --output newsletter-draft.html
After a confirmed beehiiv send: python3 scripts/build_newsletter.py --mark-sent
Commit the resulting newsletter-history.json only after the send is confirmed.
Never send from this script; beehiiv owns consent, suppression and unsubscribe.
"""

import argparse
import html
import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen
from xml.etree import ElementTree

FEED = "https://interfacereport.com/feed.xml"
SITE = "https://interfacereport.com"
DEFAULT_HISTORY = Path("newsletter-history.json")
DEFAULT_MANIFEST = Path("newsletter-manifest.json")


def load_history(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
        raise ValueError("History must be a JSON list of sent issues")
    return data


def stories(feed):
    root = ElementTree.fromstring(feed)
    result = []
    seen = set()
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        date = (item.findtext("pubDate") or "").strip()
        parsed = urlparse(url)
        if not title or not date or parsed.scheme != "https" or parsed.netloc != "interfacereport.com" or not parsed.path.startswith("/analysis/"):
            continue
        if url in seen:
            continue
        seen.add(url)
        result.append({"title": title, "url": url, "description": desc, "date": date,
                       "timestamp": parsedate_to_datetime(date).timestamp()})
    return sorted(result, key=lambda row: (-row["timestamp"], row["url"]))


def select_six(pool, history):
    sent = {url for issue in history for url in issue.get("urls", [])}
    fresh = [story for story in pool if story["url"] not in sent]
    if len(fresh) < 6:
        raise ValueError(f"Only {len(fresh)} unseen articles remain; publish more or explicitly plan a repeat before sending.")
    return fresh[:6]


def render(selected, issue):
    esc = lambda value: html.escape(str(value), quote=True)
    rows = []
    for index in range(6):
        cells = []
        for item in selected[index:index + 1]:
            date = parsedate_to_datetime(item["date"]).strftime("%b %-d, %Y")
            link = esc(item["url"] + f"?utm_source=newsletter&amp;utm_medium=email&amp;utm_campaign=issue_{issue:03d}")
            # Avoid double-escaping the HTML query-parameter separators.
            link = link.replace("&amp;amp;", "&amp;")
            cells.append(f'''<td width="100%" valign="top" style="padding:6px;"><a href="{link}" style="display:block;border:1px solid #dce5f3;border-radius:12px;padding:18px;color:#0b214b;text-decoration:none;"><span style="font:12px Arial;color:#617695;">{esc(date)}</span><strong style="display:block;margin:12px 0 10px;font:700 21px/1.22 Arial;">{esc(item["title"])}</strong><span style="display:block;font:14px/1.4 Arial;color:#46546c;">{esc(item["description"])}</span><span style="display:block;margin-top:14px;color:#1164ee;font:22px Arial;">↗</span></a></td>''')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Interface Report · Brief {issue:03d}</title></head>
<body style="margin:0;background:#f4f7fc;color:#162b4c;font-family:Arial,Helvetica,sans-serif;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7fc;"><tr><td align="center" style="padding:22px 10px;"><table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border:1px solid #e5eaf4;"><tr><td style="padding:30px 32px 12px;"><a href="{SITE}/" style="text-decoration:none;color:#0b214b;"><img src="{SITE}/assets/interface-report-mark.jpg" width="48" alt="" style="vertical-align:middle;border:0;margin-right:12px;"><strong style="font:700 22px Arial;vertical-align:middle;">Interface Report</strong></a></td></tr><tr><td style="padding:20px 32px 10px;"><span style="color:#1164ee;font:700 11px Arial;letter-spacing:2px;">SIGNAL OVER NOISE · ISSUE {issue:03d}</span><h1 style="margin:12px 0;color:#0b214b;font:700 34px/1.12 Arial;">Six useful signals for what comes next.</h1><p style="font:16px/1.55 Arial;color:#46546c;">A concise selection from Interface Report: AI products, agents and design decisions worth examining. Older stories are included when they remain useful; dates appear on every card.</p></td></tr><tr><td style="padding:2px 20px 28px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed;">{''.join(rows)}</table></td></tr><tr><td style="padding:24px 32px 30px;background:#f5f8ff;border-top:1px solid #dce5f3;"><span style="font:700 11px Arial;color:#1164ee;letter-spacing:2px;">PARTNER NOTE</span><h2 style="font:700 25px/1.2 Arial;color:#0b214b;">Building something worth understanding?</h2><p style="font:15px/1.55 Arial;color:#46546c;">If you are launching an AI product or rethinking an interface, tell us what changed and why it matters. Interface Report reviews proposals for clearly labeled sponsored stories and founder features. Payment does not guarantee publication or a positive conclusion.</p><a href="{SITE}/commercial-deck/?utm_source=newsletter&amp;utm_medium=email&amp;utm_campaign=issue_{issue:03d}" style="display:inline-block;background:#1065f6;color:#fff;padding:16px 24px;border-radius:10px;text-decoration:none;font:700 16px Arial;">Explore the Commercial Deck ↗</a></td></tr><tr><td style="padding:20px 32px;color:#64748b;font:12px/1.5 Arial;">Oleh Hebel · Interface Report<br><a href="{SITE}/" style="color:#1164ee;">interfacereport.com</a> · <a href="https://www.linkedin.com/in/olehhebel/" style="color:#1164ee;">LinkedIn</a><br>Sent only to confirmed subscribers. The sending platform adds its required unsubscribe link and mailing footer.</td></tr></table></td></tr></table></body></html>'''


def render_editor_copy(selected, issue):
    """Editable content for beehiiv Launch, whose newsletter editor excludes custom HTML."""
    lines = [f"Interface Report · Issue {issue:03d}", "", "Six useful signals for what comes next.", "",
             "A concise selection from Interface Report: AI products, agents and design decisions worth examining. Older stories are included when they remain useful; dates appear on every card.", ""]
    for item in selected:
        date = parsedate_to_datetime(item["date"]).strftime("%b %-d, %Y")
        link = item["url"] + f"?utm_source=newsletter&utm_medium=email&utm_campaign=issue_{issue:03d}"
        lines.extend([item["title"], date, item["description"], "Read the story ↗ " + link, ""])
    lines.extend(["PARTNER NOTE", "Building something worth understanding?", "If you are launching an AI product or rethinking an interface, tell us what changed and why it matters. Interface Report reviews proposals for clearly labeled sponsored stories and founder features. Payment does not guarantee publication or a positive conclusion.", "Explore the Commercial Deck ↗ " + SITE + f"/commercial-deck/?utm_source=newsletter&utm_medium=email&utm_campaign=issue_{issue:03d}", "", "Oleh Hebel · Interface Report", SITE + "/", "https://www.linkedin.com/in/olehhebel/", "", "Add the platform's required unsubscribe link and mailing footer before sending."])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feed", default=FEED, help="RSS URL or local fixture")
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=Path("newsletter-draft.html"))
    parser.add_argument("--editor-copy", type=Path, default=Path("newsletter-editor-copy.txt"), help="Editable text for the free beehiiv editor")
    parser.add_argument("--mark-sent", action="store_true", help="Record a manifest only after confirmed delivery")
    args = parser.parse_args()
    history = load_history(args.history)
    if args.mark_sent:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if any(row.get("issue") == manifest.get("issue") for row in history):
            raise ValueError("This issue is already marked as sent")
        if len(manifest.get("urls", [])) != 6:
            raise ValueError("Manifest must contain exactly six story URLs")
        history.append({"issue": manifest["issue"], "urls": manifest["urls"],
                        "sent_at": datetime.now(timezone.utc).isoformat()})
        args.history.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return
    source = Path(args.feed).read_bytes() if Path(args.feed).exists() else urlopen(args.feed, timeout=15).read()
    chosen = select_six(stories(source), history)
    issue = max([int(row.get("issue", 0)) for row in history], default=0) + 1
    args.output.write_text(render(chosen, issue), encoding="utf-8")
    args.editor_copy.write_text(render_editor_copy(chosen, issue), encoding="utf-8")
    args.manifest.write_text(json.dumps({"issue": issue, "urls": [row["url"] for row in chosen]}, indent=2) + "\n", encoding="utf-8")
    print(f"Draft issue {issue:03d}: {len(chosen)} distinct articles. Preview {args.output}. Mark sent only after beehiiv confirms the send.")


if __name__ == "__main__":
    main()

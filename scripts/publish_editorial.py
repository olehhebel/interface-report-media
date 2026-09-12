#!/usr/bin/env python3
"""Generate the reviewed September 12, 2026 Interface Report editorial package."""
from __future__ import annotations
import base64
import hashlib
import io
import pathlib
import tarfile

SHA256 = "371b724136bc81e0fd31cf0c4b94b4d3e039151f376e063a857b53d6e58fda6b"
repo = pathlib.Path(__file__).resolve().parents[1]
parts = [
    "editorial_payload_01.txt",
    "editorial_payload_02.txt",
    "editorial_payload_03.txt",
    "editorial_payload_04a.txt",
    "editorial_payload_04b.txt",
    "editorial_payload_05.txt",
]
payload = "".join((repo / "scripts" / name).read_text(encoding="utf-8").strip() for name in parts)
raw = base64.b64decode(payload)
actual = hashlib.sha256(raw).hexdigest()
if actual != SHA256:
    raise SystemExit(f"archive checksum mismatch: {actual}")

allowed_roots = {"analysis", "authors", "latest", "topics"}
allowed_files = {"sitemap.xml", "news-sitemap.xml", "feed.xml", "robots.txt"}
with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
    for member in tf.getmembers():
        if not member.isfile():
            continue
        path = pathlib.PurePosixPath(member.name)
        if path.is_absolute() or ".." in path.parts:
            raise SystemExit(f"unsafe archive path: {member.name}")
        if path.parts[0] not in allowed_roots and member.name not in allowed_files:
            raise SystemExit(f"unexpected output path: {member.name}")
        source = tf.extractfile(member)
        if source is None:
            continue
        target = repo.joinpath(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read())
        print(f"wrote {member.name}")

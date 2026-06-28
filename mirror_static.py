#!/usr/bin/env python3
"""Mirror a static page and its relative assets into a local folder."""

import os
import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

DOWNLOADED = set()
QUEUE = set()


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
        return resp.read(), resp.headers.get_content_type()


def resolve(base_url, ref):
    ref = ref.strip().split("#")[0].split("?")[0]
    if not ref or ref.startswith("data:") or ref.startswith("javascript:"):
        return None
    if ref.startswith("//"):
        return "https:" + ref
    if ref.startswith("http"):
        parsed = urllib.parse.urlparse(ref)
        base = urllib.parse.urlparse(base_url)
        if parsed.netloc and parsed.netloc != base.netloc:
            return None
        return ref
    return urllib.parse.urljoin(base_url, ref)


def page_dir(base_url):
    """Directory containing the mirrored page (URL path without filename)."""
    path = urllib.parse.urlparse(base_url).path
    if path.endswith("/"):
        return path
    return path.rsplit("/", 1)[0] + "/"


def local_for(base_url, root, url):
    parsed_base = urllib.parse.urlparse(base_url)
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc and parsed.netloc != parsed_base.netloc:
        return None
    base_dir = page_dir(base_url)
    rel = urllib.parse.urljoin(base_dir, parsed.path)
    if rel.startswith(base_dir):
        rel = rel[len(base_dir) :]
    if rel.endswith("/"):
        rel += "index.html"
    return root / rel.lstrip("/")


def extract_refs(text, base_url):
    refs = set()
    for m in re.findall(r'(?:href|src|action)=["\']([^"\']+)["\']', text, re.I):
        u = resolve(base_url, m)
        if u:
            refs.add(u)
    for m in re.findall(r'url\(["\']?([^"\')\s]+)["\']?\)', text, re.I):
        u = resolve(base_url, m)
        if u:
            refs.add(u)
    for m in re.findall(r'<source[^>]+src=["\']([^"\']+)["\']', text, re.I):
        u = resolve(base_url, m)
        if u:
            refs.add(u)
    return refs


def download(url, base_url, root):
    if url in DOWNLOADED:
        return
    local = local_for(base_url, root, url)
    if not local:
        return
    try:
        data, _ = fetch(url)
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(data)
        DOWNLOADED.add(url)
        print(f"  {local.relative_to(root)}")
        ct = local.suffix.lower()
        if ct in (".css", ".js", ".html"):
            text = data.decode("utf-8", errors="ignore")
            for ref in extract_refs(text, url):
                if ref not in DOWNLOADED:
                    QUEUE.add(ref)
    except Exception as e:
        print(f"  skip {url}: {e}")


def mirror(page_url, out_dir):
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    print(f"Mirroring {page_url} -> {root}")
    data, _ = fetch(page_url)
    html = data.decode("utf-8", errors="ignore")
    for ref in extract_refs(html, page_url):
        QUEUE.add(ref)
    while QUEUE:
        download(QUEUE.pop(), page_url, root)
    out = local_for(page_url, root, page_url)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  wrote {out.relative_to(root)} ({len(html)} bytes)")
    print(f"Done: {len(DOWNLOADED)} assets")


if __name__ == "__main__":
    import sys

    mirror(sys.argv[1], sys.argv[2])

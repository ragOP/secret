#!/usr/bin/env python3
"""Mirror patnjali.online into this folder as static HTML."""

import json
import os
import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://patnjali.online"
ROOT = Path(__file__).resolve().parent
PAGES = ["/", "/home1"]
PAGE_URLS = {BASE + "/", BASE + "/home1", BASE}
DOWNLOADED = set()
QUEUE = set()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return resp.read(), resp.headers.get_content_type()


def local_path(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc and parsed.netloc not in ("patnjali.online", "www.patnjali.online"):
        return None
    path = parsed.path or "/"
    if path.endswith("/"):
        path += "index.html"
    elif not Path(path).suffix and "/wp-" not in path and path not in ("/home1",):
        path = path.rstrip("/") + "/index.html"
    # home1 -> home1.html for simple local serving
    if path == "/index.html":
        return ROOT / "index.html"
    if path == "/home1/index.html" or path == "/home1":
        return ROOT / "home1.html"
    local = ROOT / path.lstrip("/")
    return local


def url_to_local_ref(url):
    lp = local_path(url)
    if not lp:
        return url
    rel = os.path.relpath(lp, ROOT)
    return rel.replace("\\", "/")


def extract_urls(text):
    urls = set()
    for m in re.findall(r'https:\\/\\/patnjali\.online[^"\\]+', text):
        urls.add(m.replace("\\/", "/").split("#")[0])
    for m in re.findall(r'https://patnjali\.online[^"\')\s>\\]+', text):
        urls.add(m.split("#")[0])
    for m in re.findall(r'"(/[^"\s#?]+(?:\?[^"\s#]*)?)"', text):
        if m.startswith("/wp-") or m.startswith("/home"):
            urls.add(BASE + m.split("#")[0])
    for attr in [
        "href", "src", "content", "bv-data-src", "bv-data-srcset",
        "bv-data-mobile-src", "bv-data-desktop-src", "bv-data-ipad-src",
        "bv-data-large-src", "data-src", "data-srcset",
    ]:
        for m in re.findall(rf'{attr}="([^"]+)"', text):
            if m.startswith("data:"):
                continue
            if m.startswith("//"):
                urls.add("https:" + m.split("#")[0])
            elif m.startswith("/"):
                urls.add(BASE + m.split("#")[0])
            elif m.startswith("http"):
                urls.add(m.split("#")[0])
    for m in re.findall(r'url\(["\']?([^"\')\s]+)["\']?\)', text):
        if m.startswith("data:"):
            continue
        if m.startswith("/"):
            urls.add(BASE + m.split("#")[0])
        elif m.startswith("http"):
            urls.add(m.split("#")[0])
    return urls


def download_asset(url):
    if url in DOWNLOADED or url in PAGE_URLS:
        return
    lp = local_path(url)
    if not lp:
        return
    if lp.name in ("index.html", "home1.html"):
        return
    if lp.suffix in (".html",):
        return
    try:
        data, _ = fetch(url)
        lp.parent.mkdir(parents=True, exist_ok=True)
        lp.write_bytes(data)
        DOWNLOADED.add(url)
        print(f"  asset: {lp.relative_to(ROOT)}")
        if lp.suffix in (".css", ".js"):
            text = data.decode("utf-8", errors="ignore")
            for u in extract_urls(text):
                if u not in DOWNLOADED:
                    QUEUE.add(u)
    except Exception as e:
        print(f"  skip {url}: {e}")


def rewrite_html(html, page_path):
    html = html.replace("https:\\/\\/patnjali.online", "__LOCAL__")
    html = re.sub(r"https://patnjali\.online", "__LOCAL__", html)

    def repl(m):
        url = m.group(0).replace("__LOCAL__", "https://patnjali.online")
        if url.startswith("https://patnjali.online"):
            lp = local_path(url)
            if lp and lp.exists():
                rel = os.path.relpath(lp, page_path.parent)
                return rel.replace("\\", "/")
            rel = url_to_local_ref(url)
            if rel != url:
                return rel
        return m.group(0)

    html = html.replace("__LOCAL__", "https://patnjali.online")
    html = re.sub(r'https://patnjali\.online[^"\')\s>\\]*', repl, html)
    html = html.replace('href="/home1"', 'href="home1.html"')
    html = html.replace("href='/home1'", "href='home1.html'")
    html = html.replace('href="/"', 'href="index.html"')
    return html


def simplify_for_offline(html):
    """Strip BV delay loaders so CSS/JS work offline immediately."""
    html = re.sub(r'<script id="bv-web-worker-handler"[^>]*>.*?</script>', '', html, flags=re.S)
    html = re.sub(r'<script id="bv-web-worker"[^>]*>.*?</script>', '', html, flags=re.S)
    html = re.sub(r'<script id="bv-dl-scripts-list"[^>]*>.*?</script>', '', html, flags=re.S)
    html = re.sub(r'<script id="bv-dl-styles-list"[^>]*>.*?</script>', '', html, flags=re.S)
    # Inject CSS from linkStyleAttrs inline if present
    m = re.search(r'var linkStyleAttrs = (\[.*?\]);', html, re.S)
    if m:
        try:
            links = json.loads(m.group(1))
            inject = []
            for item in links:
                href = item.get("attrs", {}).get("href", "")
                lp = local_path(href)
                if lp and lp.exists():
                    rel = os.path.relpath(lp, ROOT).replace("\\", "/")
                    inject.append(f'<link rel="stylesheet" href="{rel}">')
            if inject:
                html = html.replace("</head>", "\n".join(inject) + "\n</head>")
        except json.JSONDecodeError:
            pass
    # Swap lazy images: bv-data-src -> src
    def swap_img(m):
        tag = m.group(0)
        for attr in re.findall(r'bv-data-(?:mobile-|desktop-|ipad-|large-)?src="([^"]+)"', tag):
            if not attr.startswith("data:"):
                tag = re.sub(r'\ssrc="[^"]*"', f' src="{attr}"', tag, count=1)
                break
        return tag

    html = re.sub(r'<img[^>]+>', swap_img, html)
    return html


def mirror_page(path):
    url = BASE + (path if path != "/" else "/")
    print(f"Page: {url}")
    data, _ = fetch(url)
    html = data.decode("utf-8", errors="ignore")
    for u in extract_urls(html):
        QUEUE.add(u)

    while QUEUE:
        u = QUEUE.pop()
        download_asset(u)

    out = ROOT / ("index.html" if path == "/" else "home1.html")
    html = simplify_for_offline(html)
    html = rewrite_html(html, out)
    out.write_text(html, encoding="utf-8")
    print(f"  wrote {out.name} ({len(html)} bytes)")


def main():
    for p in PAGES:
        mirror_page(p)
    print(f"\nDone. {len(DOWNLOADED)} assets downloaded.")
    print(f"Open: file://{ROOT / 'index.html'}")


if __name__ == "__main__":
    main()

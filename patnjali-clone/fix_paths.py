#!/usr/bin/env python3
"""Post-process cloned HTML to fix local asset paths."""

import os
import re
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent
BASE = "https://patnjali.online"

CSS_FILES = [
    "wp-content/uploads/al_opt_content/CSS/431909ef7202ab2e448f1c809fbc6df4.css",
    "wp-content/uploads/al_opt_content/CSS/72bbd63606a42973dec6dad19a3b5fd0.css",
    "wp-content/uploads/al_opt_content/CSS/4fb5f7fc5e41f736ec0527b162519d52.css",
    "wp-content/uploads/al_opt_content/CSS/739945fff2c08dae5b19fd04eb980fb9.css",
    "wp-content/uploads/al_opt_content/CSS/12045858d487a8ae56337b554a5ee03c.css",
    "wp-content/uploads/al_opt_content/CSS/c3be9e612baf8fc4af612de8af4c0864.css",
    "wp-content/uploads/al_opt_content/CSS/82ed9c21c04cae90e59378da9fa03711.css",
    "wp-content/uploads/al_opt_content/CSS/34b4af0c503f58874030de4f1bcc8df2.css",
    "wp-content/uploads/al_opt_content/CSS/c54f873e89895823f30d63516df8166e.css",
    "wp-content/uploads/al_opt_content/CSS/ddd61411bcffe00288eace4c917d8fbd.css",
]


def fetch(url):
    import ssl
    import urllib.request
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return resp.read()


def ensure_css():
    for rel in CSS_FILES:
        path = ROOT / rel
        if path.exists():
            continue
        url = f"{BASE}/{rel}"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(fetch(url))
            print(f"  css: {rel}")
        except Exception as e:
            print(f"  skip css {rel}: {e}")


def to_local(url, page_dir):
    url = unquote(url.split("#")[0].split(" ")[0].strip())
    if not url.startswith(BASE):
        return url
    rel_path = url[len(BASE):].split("?")[0]
    if rel_path.startswith("/"):
        rel_path = rel_path[1:]
    if not rel_path:
        rel_path = "index.html"
    local = ROOT / rel_path
    if local.is_dir():
        local = local / "index.html"
    if local.exists():
        return os.path.relpath(local, page_dir).replace("\\", "/")
    return rel_path


def fix_file(path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    page_dir = path.parent

    def repl(m):
        return to_local(m.group(0), page_dir)

    html = re.sub(r"https://patnjali\.online[^\s\"'<>\\]+", repl, html)
    html = html.replace('href="/home1"', 'href="home1.html"')
    html = html.replace("href='/home1'", "href='home1.html'")

    # inject stylesheets if missing
    if "<link rel=\"stylesheet\"" not in html:
        links = []
        for rel in CSS_FILES:
            if (ROOT / rel).exists():
                href = os.path.relpath(ROOT / rel, page_dir).replace("\\", "/")
                links.append(f'<link rel="stylesheet" href="{href}">')
        if links:
            html = html.replace("</head>", "\n".join(links) + "\n</head>")

    path.write_text(html, encoding="utf-8")
    print(f"fixed {path.name}")


def main():
    print("Downloading missing CSS...")
    ensure_css()
    for f in ["index.html", "home1.html"]:
        fix_file(ROOT / f)
    print("Done.")


if __name__ == "__main__":
    main()

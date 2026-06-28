#!/usr/bin/env python3
"""Post-process cloned HTML for offline viewing."""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML_FILES = ["index.html", "home1.html"]


def fix_lazy_images(html: str) -> str:
    def fix_tag(match):
        tag = match.group(0)
        if 'src="data:' not in tag and "src='data:" not in tag:
            return tag
        for attr in (
            "bv-data-src",
            "bv-data-mobile-src",
            "bv-data-desktop-src",
            "bv-data-ipad-src",
            "bv-data-large-src",
        ):
            m = re.search(rf'{attr}="([^"]+)"', tag)
            if m and not m.group(1).startswith("data:"):
                tag = re.sub(r'\ssrc="[^"]*"', f' src="{m.group(1)}"', tag, count=1)
                break
        return tag

    return re.sub(r"<img[^>]+>", fix_tag, html)


def fix_links(html: str) -> str:
    html = html.replace('href="/home1"', 'href="home1.html"')
    html = html.replace("href='/home1'", "href='home1.html'")
    html = html.replace('href="/home1/"', 'href="home1.html"')
    html = html.replace('href="/"', 'href="index.html"')
    return html


def ensure_stylesheets(html, page_dir):
    links = [
        "wp-content/themes/astra/assets/css/minified/main.min.css",
        "wp-content/plugins/elementor/assets/css/frontend.min.css",
        "wp-content/uploads/elementor/css/post-6.css",
        "wp-content/uploads/elementor/css/post-35.css",
        "wp-content/plugins/elementor/assets/css/widget-image.min.css",
        "wp-content/plugins/pro-elements/assets/css/widget-countdown.min.css",
        "wp-content/plugins/pro-elements/assets/css/modules/sticky.min.css",
        "wp-content/uploads/al_opt_content/CSS/c54f873e89895823f30d63516df8166e.css",
        "wp-content/uploads/al_opt_content/CSS/ddd61411bcffe00288eace4c917d8fbd.css",
        "offline-fix.css",
    ]
    inject = []
    for rel in links:
        if (ROOT / rel).exists() and rel not in html:
            href = os.path.relpath(ROOT / rel, page_dir).replace("\\", "/")
            inject.append(f'<link rel="stylesheet" href="{href}">')
    if inject and 'href="offline-fix.css"' not in html:
        html = html.replace("</head>", "\n".join(inject) + "\n</head>")
    return html


def remove_form(html: str) -> str:
    html = re.sub(
        r'<div class="elementor-element elementor-element-45a5eeaa[^>]*>.*?</div>\s*'
        r'<div class="elementor-element elementor-element-40966475[^>]*>.*?</div>\s*',
        "",
        html,
        flags=re.S,
    )
    html = html.replace('href="#contact"', 'href="#"')
    return html


def process(path: Path) -> None:
    html = path.read_text(encoding="utf-8", errors="ignore")
    html = fix_lazy_images(html)
    html = fix_links(html)
    if path.name == "home1.html":
        html = remove_form(html)
        html = ensure_stylesheets(html, path.parent)
    path.write_text(html, encoding="utf-8")
    print(f"finalized {path.name}")


def main() -> None:
    for name in HTML_FILES:
        path = ROOT / name
        if path.exists():
            process(path)
    print("Done.")


if __name__ == "__main__":
    main()

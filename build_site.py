# -*- coding: utf-8 -*-
"""生成 GitHub Pages 静态阅读站点（输出到 docs/）。

用法：python build_site.py
会生成 docs/ 目录（index.html + chapters.json + chapters/ + epub）。
"""

import json
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
CH_DIR = ROOT / "chapters"
SITE = ROOT / "docs"


def articleize(text, title):
    """把章节源文件转成夸克阅读模式可识别的静态文章页。"""
    meta = (
        '<meta name="description" content="%s - 青崖雪"/>\n'
        '  <meta name="applicable-device" content="mobile"/>'
    ) % title
    text = text.replace(
        '<meta charset="utf-8"/>',
        '<meta charset="utf-8"/>\n  ' + meta,
        1,
    )
    text = re.sub(
        r"(<body>)([\s\S]*?)(</body>)",
        r"\1<article>\2</article>\3",
        text,
        flags=re.S,
    )
    return text


def main():
    chapters = []
    SITE.mkdir(exist_ok=True)
    (SITE / "chapters").mkdir(exist_ok=True)

    for p in sorted(CH_DIR.glob("ch*.html")):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"<h1>(.*?)</h1>", text, re.S)
        title = m.group(1).strip() if m else p.stem
        body = re.sub(r"<[^>]+>", "", text)
        chars = len(re.sub(r"\s", "", body))
        chapters.append({"file": p.name, "title": title, "chars": chars})
        out = SITE / "chapters" / p.name
        out.write_text(articleize(text, title), encoding="utf-8")

    (SITE / "chapters.json").write_text(
        json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copyfile(ROOT / "styles.css", SITE / "styles.css")
    shutil.copyfile(ROOT / "static_index.html", SITE / "index.html")
    epub = ROOT / "青崖雪.epub"
    if epub.exists():
        shutil.copyfile(epub, SITE / "青崖雪.epub")

    total = sum(c["chars"] for c in chapters)
    print(f"站点生成完成：{len(chapters)} 章，约 {total} 字")
    print(f"目录：{SITE}")


if __name__ == "__main__":
    main()

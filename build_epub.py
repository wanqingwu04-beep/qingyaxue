# -*- coding: utf-8 -*-
"""青崖雪：把 chapters/ 下的章节打包成 EPUB 电子书。

用法：python build_epub.py
每次新增章节后运行一次，会重新生成青崖雪.epub。
"""

import pathlib
import re
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
CH_DIR = ROOT / "chapters"
OUT = ROOT / "青崖雪.epub"

BOOK_TITLE = "青崖雪"
BOOK_AUTHOR = "Codex"
BOOK_ID = "urn:uuid:9f1b2a5e-1111-4c2e-9a3d-202608190001"


def read_chapters():
    items = []
    for p in sorted(CH_DIR.glob("ch*.html")):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"<h1>(.*?)</h1>", text, re.S)
        title = m.group(1).strip() if m else p.stem
        items.append((p.name, title, text))
    return items


def build():
    chapters = read_chapters()
    if not chapters:
        raise SystemExit("chapters 目录下没有章节文件")

    manifest = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="css" href="styles.css" media-type="text/css"/>',
    ]
    spine = []
    toc_items = ""
    for i, (fname, title, _text) in enumerate(chapters, 1):
        cid = f"ch{i:02d}"
        manifest.append(
            f'    <item id="{cid}" href="chapters/{fname}" '
            f'media-type="application/xhtml+xml"/>'
        )
        spine.append(f'    <itemref idref="{cid}"/>')
        toc_items += f'<li><a href="chapters/{fname}">{title}</a></li>'

    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0"
         unique-identifier="bookid" xml:lang="zh-CN">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{BOOK_ID}</dc:identifier>
    <dc:title>{BOOK_TITLE}</dc:title>
    <dc:language>zh-CN</dc:language>
    <dc:creator>{BOOK_AUTHOR}</dc:creator>
  </metadata>
  <manifest>
{chr(10).join(manifest)}
  </manifest>
  <spine>
{chr(10).join(spine)}
  </spine>
</package>
"""

    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head><title>目录</title></head>
  <body>
    <nav epub:type="toc" id="toc">
      <h1>目录</h1>
      <ol>{toc_items}</ol>
    </nav>
  </body>
</html>
"""

    css = (ROOT / "styles.css").read_text(encoding="utf-8")

    with zipfile.ZipFile(OUT, "w") as z:
        z.writestr("mimetype", "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container,
                   compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf,
                   compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav,
                   compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/styles.css", css,
                   compress_type=zipfile.ZIP_DEFLATED)
        for fname, _title, text in chapters:
            z.writestr(f"OEBPS/chapters/{fname}", text,
                       compress_type=zipfile.ZIP_DEFLATED)

    total_chars = sum(len(t) for _f, _t, t in chapters)
    print(f"打包完成：{len(chapters)} 章，共约 {total_chars} 字")
    print(f"输出：{OUT}")


if __name__ == "__main__":
    build()

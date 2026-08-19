# 青崖雪

一本仙侠小说，Codex 与用户共同创作。

## 目录结构

- `chapters/` — 章节源文件（HTML）
- `build_epub.py` — 打包 EPUB
- `build_site.py` — 生成 GitHub Pages 静态阅读站点（输出到 docs/）
- `docs/` — 静态站点（发布用）
- `reader/` — 局域网手机阅读服务（可选，不需要电脑常开时用 GitHub Pages 代替）

## 发布到 GitHub Pages

首次需要授权 GitHub，然后运行：

```powershell
.\publish.ps1
```

手机访问 `https://wanqingwu04-beep.github.io/qingyaxue/` 即可阅读。

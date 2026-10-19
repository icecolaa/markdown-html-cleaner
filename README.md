# markdown-html-cleaner

把语雀 / Notion / 网页导出的 Markdown 中的 HTML 表现层标签，清洗成标准 Markdown 语法。

导出文档常把 `<font style="color:rgb(...)">`、`</font>`、`<span style="background-color:...">`
塞进每一个文字片段，图片也保持 `<img src="..." class="ne-image">` 原样，
导致正文在任何 Markdown 阅读器里都显示为源码而非渲染结果。本工具做同义转换，
保留原有标题层级、粗体、表格、列表与代码块内容。

## 用法

```bash
# 扫描：代码块外还剩多少 HTML 标签（退出码 2 表示有残留）
python scripts/clean_md.py <目录或文件> --scan

# 预演：只统计 + 打印改动样例，不写盘
python scripts/clean_md.py <目录或文件> --dry-run --diff

# 执行
python scripts/clean_md.py <目录或文件>
```

省略路径时处理当前目录下的 `.md` 文件。仅需 Python 标准库。

## 转换对照

| 原文 | 结果 |
| --- | --- |
| `<font style="...">文本</font>` | `文本` |
| `<span style="background-color:...">文本</span>` | `文本` |
| `<img src="X" ...>` | `![插图](X)` |
| `<a href="U">文本</a>` | `[文本](U)` |
| `<br>` | 行尾两空格硬换行 |
| `<b>/<strong>`、`<i>/<em>`、`<s>/<del>` | `**`、`*`、`~~` |
| `&nbsp;` `&amp;` `&lt;` `&gt;` `&quot;` | 空格 `&` `<` `>` `"` |
| `\_` `\*` `\#` | `_` `*` `#` |
| `****`（空强调）、3+ 连续空行 | 清理 / 压缩 |

## 关键约束

- **只处理代码块围栏之外**：``` 内的 `<class 'int'>`、`if a < b` 等原样保留
- **保留行尾两空格的 Markdown 硬换行**
- **只做同义转换**，不改写措辞、不删减内容
- 写盘前先 `--dry-run --diff`；未被 git 跟踪的文件先备份

## 实测

在 PythonAI 教程仓库（语雀导出的 9 章 Python 教程 + 入门讲义）上：

- 清洗 `<font>` × 330、`<span>` × 26、`<img>` × 5
- 清洗后代码块外残留标签 0，其中 1 个文件零改动（无误伤）
- git diff 仅涉及含标签的行，无整文件重写

## License

MIT

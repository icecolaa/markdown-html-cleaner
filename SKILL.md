---
name: markdown-html-cleaner
slug: markdown-html-cleaner
version: 1.0.0
displayName: Markdown HTML 标签清洗
summary: 把语雀/Notion/网页导出的 Markdown 中的 HTML 标签清洗为纯 Markdown 可读形式
description: 清洗 Markdown 文件里从语雀、Notion、Confluence、网页复制等来源混入的 HTML 表现层标签（font/span 样式标签、img 图片标签、a 链接标签、HTML 实体、反斜杠转义等），转换为标准 Markdown 语法并保持代码块内容不变。当文档出现 HTML 标签导致正文在 Markdown 阅读器里显示为源码、无法渲染，或需要批量整理导出文档时使用本技能。
tags:
  - markdown
  - html
  - 文档清洗
  - 语雀
  - 格式化
license: MIT
agent_created: true
---

# Markdown HTML 标签清洗

## 用途

将导出型 Markdown（语雀 / Notion / Confluence / 网页复制）中残留的 HTML 表现层标签，
转换为标准 Markdown 语法，使文档在任意 Markdown 阅读器中正常渲染，同时保持结构与内容零丢失。

## 触发场景

- 文档正文出现 `<font style="color:...">`、`</font>`、`<span style="background-color:...">` 等噪声标签
- 图片仍是原始 `<img src="..." width=... class=...>` 而非 `![](...)`
- 出现 `&quot;` `&nbsp;` `&amp;` 等 HTML 实体，或 `state\_dict` 这类多余转义
- 需要批量整理一整个目录的导出文档

## 核心工作流

### 第 1 步：扫描确认

对目标目录运行扫描，拿到"哪些文件、多少标签"的清单，避免盲改：

```bash
python scripts/clean_md.py <目录或文件> --scan
```

退出码为 2 表示仍有残留标签。

### 第 2 步：预演（必做）

先看改动统计与样例，确认没有误伤：

```bash
python scripts/clean_md.py <目录或文件> --dry-run --diff
```

`--diff` 会打印每个文件的前若干处改动，重点检查：
代码块内的内容是否被动过（不应出现）、列表/表格结构是否被破坏。

### 第 3 步：执行清洗

确认无误后落盘：

```bash
python scripts/clean_md.py <目录或文件>
```

### 第 4 步：复核

再次 `--scan` 确认残留为 0，并用 `git diff --stat` 抽查改动量级是否合理
（应只涉及含标签的行，不应出现整文件重写；整文件重写通常意味着换行符被改动）。

## 不可违反的约束

1. **代码块围栏外才处理**：``` / ~~~ 围栏内的内容必须原样保留。
   Python 教程正文里常有 `<class 'int'>`、`if a < b` 这类输出与表达式，
   在围栏内清洗会直接破坏代码示例。脚本通过围栏状态机保证这一点。
2. **保留行尾两空格硬换行**：Markdown 中行尾两个空格表示 `<br>`，
   清洗时只清理多余空白，不得抹掉这个语义。
3. **不得删减正文**：只做标签→Markdown 的同义转换，不改写措辞、不删除段落。
4. **先备份再写盘**：目标文件若未被 git 跟踪，先复制一份再清洗；
   已跟踪的先确认工作区干净，保证 `git checkout -- <file>` 可回滚。

## 转换规则

| 原文 | 转换结果 |
| --- | --- |
| `<font style="...">文本</font>` | `文本` |
| `<span style="background-color:...">文本</span>` | `文本` |
| `<img src="X" width=... class=...>` | `![插图](X)`（alt 为空时取 title，否则用"插图"） |
| `<a href="U">文本</a>` | `[文本](U)` |
| `<br>` / `<br/>` | 行尾两空格硬换行 |
| `<b>` / `<strong>` | `**` |
| `<i>` / `<em>` | `*` |
| `<s>` / `<del>` | `~~` |
| `<div>` `<p>` `<section>` | 去标签，保留文本 |
| `&nbsp;` `&amp;` `&lt;` `&gt;` `&quot;` | 空格 `&` `<` `>` `"` |
| `\_` `\*` `\#` | `_` `*` `#` |
| `****`（空强调） | 删除 |
| 连续 3 个以上空行 | 压缩为 1 个空行 |

## 脚本参数

```
python scripts/clean_md.py [路径...] [--dry-run] [--diff] [--scan]
```

- 省略路径时处理当前目录
- `--dry-run` 只统计不写盘；`--diff` 打印改动样例；`--scan` 只做残留检查
- 路径可以是文件也可以是目录（只取 `.md`）

## 常见来源与特征

| 来源 | 典型残留 | 备注 |
| --- | --- | --- |
| 语雀导出 | `<font style="color:rgb(...)">` 密集包裹每个文字片段 | 常与 `**粗体**` 嵌套，去标签后 `**粗体**` 自动复原 |
| 语雀导出 | `<img ... class="ne-image">` 独占一行 | 转为 `![]()` 后需确认图片路径是否存在 |
| Notion 导出 | `<div>`、`<span>`、内联样式 | 表格内也常带标签 |
| 网页复制 | `&nbsp;`、`<br>`、`<a href>` | 实体较多 |

## 已知陷阱

- **图片路径失效**：相对路径图片（如 `./images/31.jpg`）导出时往往不带图片目录，
  转成 `![]()` 后仍是坏链。清洗后应提示用户补图，而非删除引用。
- **表格内的标签**：语雀导出的表格每个单元格都带 `<font>`，去标签后表头
  `| **时间** |` 的粗体需保持，不要顺手改成 `| 时间 |`。
- **换行符**：Python 以文本模式读取会把 CRLF 归一为 LF，写回时用 `newline='\n'`
  保证与仓库一致，避免整文件 diff。
- **嵌套标记**：`<Mark bold>` 类的组件标记不在本技能范围内（那是 WorkBuddy 资料库的
  文档组件格式），本脚本只处理标准 HTML 标签。

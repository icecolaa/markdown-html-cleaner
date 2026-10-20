---
name: markdown-html-cleaner
slug: markdown-html-cleaner
version: 1.1.0
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

把导出型 Markdown 里的 HTML 表现层标签**同义转回**标准 Markdown；
代码块围栏（``` 与 `~~~`）内的内容一个字符都不动。
零第三方依赖，只用 Python 标准库。

---

## When to Use（什么时候用）

- 正文出现 `<font style="color:...">`、`</font>`、`<span style="background-color:...">` 等噪声标签
- 图片仍是 `<img src="..." width=... class=...>` 而非 `![](...)`
- 出现 `&quot;` `&nbsp;` `&amp;` 等 HTML 实体，或 `state\_dict` 这类多余转义
- 需要批量整理一整个目录（可递归）的导出文档

不适用 / 不该用的情况见下一节。

## When NOT to Use（什么时候不该用、不适用）

- 文档本身就是 HTML / MDX，标签是**有意保留**的结构，不是导出噪声
- 需要排版美化、措辞改写 —— 本技能只做同义转换，**不改措辞、不删段落**
- 需要重排表格、翻译、摘要 —— 超出范围
- 含 `<Mark bold>` 这类资料库组件标记 —— 那不是 HTML，本技能不处理
- 目标文件未被 git 跟踪且**没有备份** —— 先备份再清洗（脚本无回滚能力）

超出范围时的替代方案：先人工确认文档确实来自「导出 / 复制」，再决定是否清洗；
只想去掉个别标签时，直接用编辑器替换更快。

## Prerequisites（前置条件）

- Python 3.6+（仅标准库，无需 pip 安装）
- 目标文件为 UTF-8 编码的 `.md`

## Quick Start（30 秒上手）

```bash
python scripts/clean_md.py <目录或文件> --scan            # 1. 看有多少残留（退出码 2 = 有残留）
python scripts/clean_md.py <目录或文件> --dry-run --diff   # 2. 预演，确认没有误伤
python scripts/clean_md.py <目录或文件>                    # 3. 落盘
```

## Usage（用法与参数）

```
python scripts/clean_md.py [路径...] [--recursive] [--dry-run] [--diff] [--scan]
```

| 参数 | 作用 |
| --- | --- |
| 路径 | 文件或目录（只取 `.md`）；省略 = 当前目录 |
| `--recursive` | 连同子目录一起处理（默认只取顶层） |
| `--dry-run` | 只统计，不写盘 |
| `--diff` | 打印每个文件的前若干处改动样例 |
| `--scan` | 只统计「清洗前」的残留；有残留时退出码为 **2** |

## 工作流

### Step 1 · 扫描确认

```bash
python scripts/clean_md.py <目录或文件> --scan
```

拿到「哪些文件、多少标签」的清单，避免盲改。退出码 2 = 还有残留需要清洗。

### Step 2 · 预演（必做）

```bash
python scripts/clean_md.py <目录或文件> --dry-run --diff
```

`--diff` 会打印每处改动，重点检查三件事：代码块内容是否被动过（不应出现）、
列表缩进是否被破坏、表格结构是否变形。

### Step 3 · 执行清洗

```bash
python scripts/clean_md.py <目录或文件>
```

多章子目录加 `--recursive`。

### Step 4 · 复核残留

再跑一次 `--scan`：残留应为 0、退出码应为 0。

### Step 5 · 核对改动量级

```bash
git diff --stat
```

应只涉及含标签的行。**出现整文件重写 = 换行符被改动**，立即回滚排查。

## Rules（不可违反的约束）

1. **围栏内外有别**：``` 与 `~~~` 围栏内的内容必须原样保留。教程正文里的
   `<class 'int'>`、`if a < b` 一旦被清洗，代码示例就毁了。
2. **保留行尾两空格硬换行**：Markdown 中行尾两空格表示 `<br>`，清洗只清多余空白，不抹掉这个语义。
3. **不得删减正文**：只做标签→Markdown 的同义转换，不改写措辞、不删除段落。
4. **表格去标签后保留加粗**：`| **时间** |` 不能顺手改成 `| 时间 |`。
5. **先备份再写盘**：未跟踪文件先复制一份；已跟踪的先确认工作区干净，保证可回滚。

## Gotchas（已知陷阱）

- **图片路径可能失效**：相对路径图片导出时往往不带图片目录，转成 `![]()` 后仍是坏链
  → 提示用户补图，不要删引用
- **表格单元格普遍带 `<font>`**：去标签后表头加粗需保持
- **换行符是整文件 diff 的头号元凶**：写盘固定 `newline='\n'`
- **目录默认不递归**：多章子目录要加 `--recursive`，否则只处理顶层
- **`~~~` 围栏同样受保护**：不要误以为只有 ``` 才保护
- **无 `src` 的 `<img>`**：保留 alt/title 文本，不会整枚消失
- **嵌套标记不算 HTML**：`<Mark bold>` 类组件标记不在范围内
- **统计口径**：`font / img / 其他` 均只统计围栏之外的标签

## 自检清单（验证）

执行完逐条确认，任何一条不过都不要交付：

1. `--scan` 退出码为 0（清洗前残留 = 0）
2. `git diff --stat` 只涉及含标签的行，没有整文件重写
3. 围栏内的 `<class 'int'>`、`if a < b` 原样未动
4. 表格表头 `| **时间** |` 的加粗仍在
5. 图片引用数量与清洗前一致（不多不少）

## 安全声明

- **不联网、不上传、不收集、不存储**任何文件内容或用户信息
- 仅对本地文件做读写；`--dry-run` / `--scan` 完全不写盘
- 无密钥、无 token、无环境变量依赖

## 进阶参考（按需加载）

不需要一次读完，遇到具体问题时再**加载** `references/` 下的文件：

| 文件 | 什么时候读 |
| --- | --- |
| `references/rules/conversion-rules.md` | 需要完整转换规则对照表、想确认某类标签怎么处理 |
| `references/sources/yuque.md` | 处理语雀导出、遇到 `<font>` 密集嵌套 |
| `references/sources/notion-web.md` | 处理 Notion / 网页复制、遇到 `<div>` `<span>` 内联样式 |

样例见 `examples/`：每个 `*.md` 都配一份 `*.cleaned.md` 期望输出，
可用 `--dry-run --diff` 对照验证。

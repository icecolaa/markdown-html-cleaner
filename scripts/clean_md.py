# -*- coding: utf-8 -*-
"""
把语雀 / Notion / 网页导出的 Markdown 中的 HTML 标签清洗为纯 Markdown 可读形式。

处理范围（仅限代码块之外，``` 与 ~~~ 围栏内的内容原样保留）：
  1. <font style="...">文本</font>        -> 文本
  2. <img src="X" ...>                   -> ![插图](X)
  3. <br> / <br/>                        -> 换行
  4. <b>/<strong>、<i>/<em>、<u>、<s>    -> ** / * / ~~
  5. <span>/<div>/<p>/<a> 等残留行内标签  -> 去除标签保留文本（<a> 保留 href 为 Markdown 链接）
  6. &nbsp; &amp; &lt; &gt; &quot;       -> 对应字符
  7. \\_  \\*  \\#  等转义                -> 还原
  8. 收尾整理：空强调 ****、行尾空格、连续空行（保留行尾两空格的硬换行）

用法：
  python scripts/clean_md.py                       # 处理当前目录
  python scripts/clean_md.py <文件或目录> [...]     # 处理指定路径
  python scripts/clean_md.py --recursive           # 连同子目录一起处理
  python scripts/clean_md.py --dry-run             # 只预览改动统计，不写盘
  python scripts/clean_md.py --diff                # 打印前 N 处改动样例
  python scripts/clean_md.py --scan                # 只统计「清洗前」残留的 HTML 标签数

退出码：0 正常；2 表示 --scan 发现原文仍有残留标签（即还有文件需要清洗）。
"""
import io
import os
import re
import sys

FONT_RE = re.compile(r'</?font\b[^>]*>', re.I)
IMG_RE = re.compile(r'<img\b[^>]*>', re.I)
BR_RE = re.compile(r'<br\s*/?>', re.I)
BOLD_RE = re.compile(r'</?(?:b|strong)\b[^>]*>', re.I)
ITAL_RE = re.compile(r'</?(?:i|em)\b[^>]*>', re.I)
U_RE = re.compile(r'</?u\b[^>]*>', re.I)
DEL_RE = re.compile(r'</?(?:s|del|strike)\b[^>]*>', re.I)
ANCHOR_RE = re.compile(r'<a\b[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.I | re.S)
STRIP_RE = re.compile(
    r'</?(?:span|div|p|section|article|font|small|big|code|pre|mark)\b[^>]*>', re.I)
ANY_TAG_RE = re.compile(r'<[/]?[a-zA-Z][a-zA-Z0-9]*')
ATTR_SRC = re.compile(r'\bsrc="([^"]*)"', re.I)
ATTR_ALT = re.compile(r'\balt="([^"]*)"', re.I)
ATTR_TITLE = re.compile(r'\btitle="([^"]*)"', re.I)

ENTITIES = [
    ('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
    ('&quot;', '"'), ('&apos;', "'"), ('&#39;', "'"),
]


FENCE_MARKS = ('```', '~~~')


def iter_markdown_lines(text):
    """逐行产出 (line, in_code_fence)。围栏行本身也产出，便于原样保留。

    同时支持 ``` 与 ~~~ 两种围栏（SKILL.md 承诺两者都保护），
    并记录开启时的围栏字符，避免 ``` 被 ~~~ 提前关闭或反之。
    """
    in_fence = False
    fence_char = ''
    for line in text.split('\n'):
        stripped = line.lstrip()
        if in_fence:
            yield line, True
            if stripped.startswith(fence_char):
                in_fence = False
                fence_char = ''
            continue
        if stripped.startswith(FENCE_MARKS):
            fence_char = stripped[:3]
            in_fence = True
            yield line, True
            continue
        yield line, False


def clean_line(line):
    """清洗一行（调用方保证这行不在代码块内）。"""
    def img_repl(m):
        tag = m.group(0)
        alt = ATTR_ALT.search(tag)
        title = ATTR_TITLE.search(tag)
        alt_text = (alt.group(1).strip() if alt and alt.group(1).strip()
                    else (title.group(1).strip()
                          if title and title.group(1).strip() not in ('', 'null')
                          else ''))
        src = ATTR_SRC.search(tag)
        if not src:
            # 无 src 的占位图：保留可读文本，不让内容凭空消失
            return alt_text
        return '![%s](%s)' % (alt_text or '插图', src.group(1))
    line = IMG_RE.sub(img_repl, line)

    def a_repl(m):
        return '[%s](%s)' % (re.sub(r'<[^>]+>', '', m.group(2)).strip(), m.group(1))
    line = ANCHOR_RE.sub(a_repl, line)

    line = BR_RE.sub('  \n', line)
    line = BOLD_RE.sub('**', line)
    line = ITAL_RE.sub('*', line)
    line = U_RE.sub('', line)
    line = DEL_RE.sub('~~', line)
    line = FONT_RE.sub('', line)
    line = STRIP_RE.sub('', line)

    for ent, ch in ENTITIES:
        line = line.replace(ent, ch)

    line = line.replace('\\_', '_').replace('\\*', '*').replace('\\#', '#')

    line = line.replace('****', '').replace('** **', ' ').replace('* *', ' ')
    line = re.sub(r'\*\*\s*\*\*', '', line)
    if not line.strip():
        return ''
    hard_break = re.search(r'[ \t]{2,}$', line) is not None
    return re.sub(r'[ \t]+$', '', line) + ('  ' if hard_break else '')


def clean_text(text):
    out = []
    for line, in_fence in iter_markdown_lines(text):
        out.append(line if in_fence else clean_line(line))
    result = '\n'.join(out)
    return re.sub(r'\n{3,}', '\n\n', result).rstrip() + '\n'


def count_tags(text, regex=ANY_TAG_RE):
    """统计代码块之外的标签数量。默认统计任意 HTML 标签，可传入指定正则。"""
    total = 0
    for line, in_fence in iter_markdown_lines(text):
        if in_fence:
            continue
        total += len(regex.findall(line))
    return total


def collect_files(targets, recursive=False):
    files = []
    for t in targets:
        if os.path.isdir(t):
            if recursive:
                for root, dirs, names in os.walk(t):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for name in sorted(names):
                        if name.lower().endswith('.md'):
                            files.append(os.path.join(root, name))
            else:
                for name in sorted(os.listdir(t)):
                    if name.lower().endswith('.md'):
                        files.append(os.path.join(t, name))
        elif os.path.isfile(t):
            files.append(t)
        else:
            print('跳过（不存在）: %s' % t, file=sys.stderr)
    return files


def main():
    argv = sys.argv[1:]
    dry_run = '--dry-run' in argv
    show_diff = '--diff' in argv
    scan_only = '--scan' in argv
    recursive = '--recursive' in argv
    flags = ('--dry-run', '--diff', '--scan', '--recursive')
    argv = [a for a in argv if a not in flags]
    targets = argv or [os.getcwd()]

    files = collect_files(targets, recursive)
    if not files:
        print('没有找到 .md 文件', file=sys.stderr)
        return 1

    changed_count = 0
    leftover = 0
    for path in files:
        with io.open(path, 'r', encoding='utf-8') as f:
            before = f.read()
        after = clean_text(before)
        changed = before != after
        # 围栏感知：围栏内的标签不算，统计口径才与实际改动一致
        n_font = count_tags(before, FONT_RE)
        n_img = count_tags(before, IMG_RE)
        # FONT_RE 已同时匹配开闭标签，这里只减一次
        n_other = count_tags(before) - n_font - n_img
        # --scan 关心「原文还剩多少」（决定退出码 2）；
        # 其余模式关心「清洗后还剩多少」（衡量规则覆盖度）
        leftover += count_tags(before) if scan_only else count_tags(after)
        if changed and not dry_run and not scan_only:
            with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(after)
        if changed:
            changed_count += 1
        verb = '需清洗' if scan_only else ('将改写' if dry_run else '已改写')
        shown_path = path if recursive else os.path.basename(path)
        print('%-46s %-8s font:%-4d img:%-3d 其他:%-3d'
              % (shown_path[-46:], verb if changed else '无需改动',
                 n_font, n_img, max(n_other, 0)))
        if show_diff and changed:
            import difflib
            shown = 0
            for d in difflib.unified_diff(before.split('\n'), after.split('\n'),
                                          lineterm='', n=0):
                if d.startswith(('-', '+')) and not d.startswith(('---', '+++')):
                    print('    %s' % d[:160])
                    shown += 1
                    if shown >= 6:
                        print('    ...')
                        break

    print('\n共 %d 个文件，%s %d 个；%s：%d。%s'
          % (len(files),
             '需清洗' if scan_only else ('将改写' if dry_run else '已改写'),
             changed_count,
             '清洗前代码块外残留标签' if scan_only else '清洗后代码块外残留标签',
             leftover,
             '（dry-run，未写盘）' if dry_run else ''))
    return 2 if (scan_only and leftover) else 0


if __name__ == '__main__':
    sys.exit(main())

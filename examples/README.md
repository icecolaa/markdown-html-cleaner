# 样例与回归对照

每个 `*.md` 都配一份 `*.cleaned.md`，后者是**脚本跑出来的期望输出**，不是手写稿。

| 原始 | 期望输出 | 覆盖点 |
| --- | --- | --- |
| `yuque-sample.md` | `yuque-sample.cleaned.md` | `<font>` 密集嵌套、`**粗体**` 复原、表格单元格、图片、无 src 的 img、\`\`\` 围栏、反斜杠转义、HTML 实体 |
| `notion-web-sample.md` | `notion-web-sample.cleaned.md` | `<div>`/`<span>`、`<br>`、`<b>/<i>/<u>`、`&amp;`/`&quot;`、\`\`\` 之外的 `~~~` 围栏 |

## 怎么验证脚本没跑偏

把原始样例复制到临时目录，跑一遍，跟期望输出比对：

```bash
cp examples/yuque-sample.md /tmp/t.md
python ../scripts/clean_md.py /tmp/t.md
diff /tmp/t.md examples/yuque-sample.cleaned.md && echo "一致"
```

`diff` 无输出即通过。改动脚本后请务必跑一遍这两个样例。

## 三条不可回归的基线

1. 围栏内的内容原样不动（两个样例都有围栏内容）
2. 表格表头的 `**加粗**` 保留
3. 图片引用数量与清洗前一致

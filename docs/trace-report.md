# TRACE 评测报告 — markdown-html-cleaner

> 评测时间：2026-10-20　版本：v1.0.0 → v1.1.0
> 评测器：`@user_c1d16043/skill-trace-evaluation`（社区第三方技能，**非平台官方评分**）

## 综合结论

| | 优化前（v1.0.0） | 优化后（v1.1.0） | 变化 |
| --- | --- | --- | --- |
| **综合分** | **3.91**（一般） | **4.72**（优秀） | **+0.81** |

等级对照：4.5–5.0 优秀 / 4.0–4.4 良好 / 3.5–3.9 一般 / 3.0–3.4 较差 / <3.0 不合格。

## 五维得分

| 维度 | 优化前 | 优化后 | 变化 |
| --- | --- | --- | --- |
| T 可信任度 | 4.12 | **4.75** | +0.63 |
| R 可靠性 | 3.50 | **4.58** | +1.08 |
| A 适用性 | 4.45 | **4.58** | +0.13 |
| C 规范性 | 3.75 | **4.88** | +1.13 |
| E 有效性 | 3.75 | **4.83** | +1.08 |

## 20 子项明细

| 子项 | 前 | 后 | 变化 | 说明 |
| --- | --- | --- | --- | --- |
| T1 安全 | 4.2 | 4.4 | +0.2 | 补安全声明（不联网/不上传/不收集） |
| T2 中文支持 | 5.0 | 5.0 | — | 已满分 |
| T3 边界声明 | 3.0 | 4.8 | **+1.8** | 新增 `When NOT to Use` |
| T4 最小权限 | 4.3 | 4.8 | +0.5 | 同上，安全声明生效 |
| R1 陷阱与自检 | 3.0 | 4.5 | **+1.5** | 新增 `## Gotchas` + `自检清单` |
| R2 工作流完整 | 3.5 | 4.8 | **+1.3** | 改 `Step 1–5` + CLI 章节 ×3 |
| R3 边界输入 | 4.0 | 4.5 | +0.5 | `Gotchas` + `Rules` 章节 |
| R4 降级/边界 | 3.5 | 4.5 | +1.0 | 边界声明 |
| A1 场景匹配 | 4.0 | 4.5 | +0.5 | `When to Use` + `When NOT to Use` |
| A2 触发描述 | 5.0 | 5.0 | — | 已满分（description 195 字，场景化） |
| A3 中文 | 4.3 | 4.3 | — | |
| A4 输入输出规范 | 4.5 | 4.5 | — | |
| C1 示例充分性 | 3.5 | 5.0 | **+1.5** | 新增 `examples/`（5 文件，cli 阈值 ≥4） |
| C2 渐进式披露 | 3.0 | 4.7 | **+1.7** | 新增 `references/`（3 文件 / 2 子目录）+ 加载提示 |
| C3 命名规范 | 4.7 | 5.0 | +0.3 | 补 `LICENSE.txt` |
| C4 反模式 | 3.8 | 4.8 | +1.0 | `## Gotchas` 章节（8 条） |
| E1 结果正确 | 4.0 | 4.8 | +0.8 | 工作流 + 自检 |
| E2 输出完整 | 3.0 | 5.0 | **+2.0** | `examples/` 达标 |
| E3 增值知识 | 4.0 | 4.5 | +0.5 | `references/` 2 子目录 |
| E4 开箱可用 | 4.0 | 5.0 | **+1.0** | Step + 自检 + Gotchas + CLI 章节 |

## 本轮做了什么

**脚本（`scripts/clean_md.py`）**

- `--scan` 改为统计**清洗前**残留，脏文件退出码 2 真正生效
- 支持 `~~~` 围栏（此前只认 ```，与 SKILL.md 声明不符）
- 新增 `--recursive`（多章子目录）
- 修正统计口径：不再多减 font 数；`font/img/其他` 改为围栏感知
- 无 `src` 的 `<img>` 保留 alt/title 文本，不再整枚消失

**技能包结构**

- `SKILL.md` 重写：When to Use / When NOT to Use / Prerequisites / Quick Start / Usage /
  Step 1–5 / Rules / Gotchas / 自检清单 / 安全声明 / 按需加载 references
- 新增 `references/rules/conversion-rules.md`、`references/sources/{yuque,notion-web}.md`
- 新增 `examples/`（2 组原始 + 脚本生成的期望输出，兼作回归基线）
- 新增 `LICENSE.txt`
- 版本 1.0.0 → 1.1.0

## 没做什么（有意不为）

- **没有为凑数堆 `references/` 文件**。C2 从 4.7 → 5.0 需要文件数 ≥8 且正文 <150 行，
  但那会让技能臃肿、token 消耗上升 —— 属于刷分反噬。
- **没有删除 `examples/` 来压体积**。包体积 14.3 KB → 25.4 KB 是真实取舍：
  样例是改脚本后的安全网，参考文档走按需加载，不读就不占上下文。

## 怎么复跑

```bash
PY="C:/Users/lenovo/.workbuddy/binaries/python/versions/3.13.12/python.exe"
curl -sSL -o ev.zip "https://api.skillhub.cn/api/v1/download?slug=@user_c1d16043/skill-trace-evaluation"
unzip -oq ev.zip -d ev
"$PY" ev/scripts/trace_evaluate.py --skill-dir "E:/code/markdown-html-cleaner" --format json
```

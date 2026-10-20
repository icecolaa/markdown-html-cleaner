# HANDOFF.md — markdown-html-cleaner 交接文档

> **给新窗口的话**：只读这一个文件就够接续。所有命令、状态、坑、待办都在下面。
> 最后更新：2026-10-20（冒烟验证 + 双远端自动同步改造 + 建立本文档 + 修正 `f8523da` 被并发会话 reset 造成的失实叙述）

---

## 0. 30 秒速览

| 项 | 值 |
| --- | --- |
| 项目定位 | 单个 Python 脚本构成的 **Skill**：把语雀 / Notion / 网页导出的 Markdown 里的 HTML 表现层标签，同义转回标准 Markdown |
| 核心产物 | `scripts/clean_md.py`（约 200 行，仅用标准库） |
| 配套文档 | `SKILL.md`（技能说明，含 frontmatter，供 Skill 运行时读取）、`README.md`（用法与实测）、`references/`（规则细则 + 来源特征）、`examples/`（回归样例） |
| TRACE 评测 | 综合 **4.72 / 5**（优秀），优化前 3.91（一般）—— 见 §13 |
| 分支 / HEAD | `main`；三端一致于 2026-10-20 在 `6702454` 验证过（当前 HEAD 以 `git log -1` 为准，详见 §4） |
| 远端 | fetch 走 GitHub；push 同时走 **Gitee + GitHub**（双远端） |
| 自动同步 | `.githooks/post-commit` 在每次 commit 后逐远端推送，需 `core.hooksPath=.githooks`（已设好） |
| 运行时 | `C:/Users/lenovo/.workbuddy/binaries/python/versions/3.13.12/python.exe`，**零第三方依赖** |
| 当前可交付状态 | §8 的缺陷（A–F）**已全部修复**；v1.1.0 已于 2026-10-20 发布（skillId=286918，**审核中**，详情页审核通过后才切到新版本） |

---

## 1. 任务是什么

**原始需求**：把导出型 Markdown 里残留的 HTML 表现层标签清洗成标准 Markdown，让文档在任何 Markdown 阅读器里正常渲染，且**结构、内容零丢失**。

**背景痛点**：语雀 / Notion / 网页导出时，会把 `<font style="color:rgb(...)">`、`</font>`、`<span style="background-color:...">` 塞进**每一个文字片段**，图片保持 `<img src="..." class="ne-image">` 原样。结果正文在任何阅读器里都显示成源码。

**验收标准**（这三条是硬约束，任何时候都不能破）：
1. 代码块围栏内的内容**一个字符都不能动**（Python 教程正文里有 `<class 'int'>`、`if a < b`）；
2. 只做**同义转换**，不改写措辞、不删减段落；
3. 改动必须是**局部行级 diff**，不能出现整文件重写。

---

## 2. 完整过程

### 2.1 时间线

| 时间 | 提交 | 内容 |
| --- | --- | --- |
| 2026-10-20 00:32 | `ba44f8a` | `feat: 新增 markdown-html-cleaner 技能` —— 一次性落地 `scripts/clean_md.py` + `SKILL.md` + `README.md`，共 368 行新增 |
| 2026-10-20 00:59 | ~~`f8523da`~~ | `test: 验证 post-commit 自动推送`（空提交）。**该提交已在 01:00:20 被 `git reset HEAD~1` 撤销，现已不在历史中，仅作为悬空对象残留**（详见 §7.4） |
| 2026-10-20 01:05 | `6702454` | `docs: 新增 HANDOFF.md 交接文档与双远端自动推送钩子` —— 冒烟测试、发现缺陷（记入 §8）、钩子版本化改造、编写本文档 |
| 2026-10-20 10:20 | `dd5f0dd` | **按 SkillHub TRACE 评测报告做一轮优化**：修完 §8 全部缺陷（含新发现的 F）+ 重写 SKILL.md 结构 + 新增 `references/`、`examples/`、`LICENSE.txt`，综合分 3.91 → 4.72（详见 §13） |

> 上表只列**实质性**提交。此后若仅是文档润色（如 `9fc476a` 补 `.gitignore` 与 SHA 说明）不再逐条追加，完整历史以 `git log --oneline` 为准。

> ⚠️ **诚实说明**：`f8523da` 之前的设计讨论过程在历史会话中已检索不到（`conversation_search` 无结果）。上表中 00:32 / 00:59 两笔是**从 git 历史与提交信息还原**的；本次会话的内容是**当场实测**的。凡标"实测/已验证"的都跑过命令，凡标"待确认"的都未验证。

### 2.2 本次会话实际做了什么

1. **盘点**：确认仓库结构、git 状态、远端配置、`post-commit` 钩子内容。
2. **冒烟测试**（临时目录 `a.md`，覆盖 font / img / 表格 / 代码围栏 / HTML 实体）：
   - 四种来源标签全部按预期转换；
   - 代码块两行内容原样保留；
   - 清洗后代码块外残留标签 = 0。
   - 同时**发现 2 个真实缺陷**（`--scan` 退出码语义、统计口径算错），见 §8 缺陷 A / B。
3. **重构自动推送**：原钩子在 `.git/hooks/post-commit`（不版本化、且 `git push -u origin` 一处失败会连累另一处）。改造为 `.githooks/post-commit` + `core.hooksPath=.githooks`，逐 pushurl 推送。
4. **核对远端连通性**：Gitee / GitHub 两端 `ls-remote` 均可达，都停在 `ba44f8a`。
5. **收尾**：加 `.gitignore` 忽略 `.workbuddy/`（本地记忆数据不进技能仓库），写本文档。
6. **（收笔时才发现）HEAD 被并发会话动过**：整理最终 `git log` 时发现 `f8523da` 不见了，`git reflog` 显示 `01:00:20 reset: moving to HEAD~1`。
   真相是——**上一个会话在本会话开工的同时仍在做收尾**：它此前把 `remote.origin.pushurl` 临时指向
   `C:/Users/lenovo/AppData/Local/Temp/bare-test.git` 来验证钩子，收尾时还原了真实 pushurl 并 reset 掉测试提交。
   所以本文开头看到的"临时 pushurl"和"本地领先 1 个提交"都是**上一会话的中间状态**，不是稳定事实。
   → 已据此修正本文档，并把教训写进 §7.4。

> 📌 **关于 SHA**：下文出现的 `6702454` 是"三端同步已验证"这一事实的时间戳，历史不会变。
> 但**当前 HEAD 请始终以 `git log -1 --oneline` 为准**——后续每次提交都会让 HEAD 前进，
> 本文档不会跟着改 SHA。判断是否同步一律用 §10.3 的命令（它不依赖任何硬编码 SHA）。

---

## 3. 关键结论（设计决策与理由）

这些是"为什么这么写"，改代码前必读：

1. **逐行状态机，不是全文正则**。
   清洗单位是"行"，`iter_markdown_lines()` 维护 `in_fence` 布尔状态，围栏行原样吐出。**理由**：全文正则无法区分 `<class 'int'>` 是代码输出还是待清洗标签，一旦误伤就破坏代码示例——这是本项目最高风险的失败模式。

2. **只做同义转换，不"顺手美化"**。
   典型对照：表格单元格去标签后，`| **时间** |` 必须保持加粗，不能改成 `| 时间 |`。清洗器不做审美判断。

3. **零依赖，只用标准库**。
   定位是随取随用的 Skill，不能要求用户 `pip install`。

4. **写盘固定 `newline='\n'`**。
   Windows 下 Python 文本模式会把 LF 写成 CRLF，导致 `git diff` 显示整文件重写，直接违反验收标准 3。

5. **三段式操作节奏：`--scan` → `--dry-run --diff` → 执行**。
   不可跳过。`--diff` 的作用是肉眼确认"代码块没被动过、列表/表格没被破坏"。

6. **自动推送用"逐 pushurl 推送"而非 `git push origin`**。
   `git push origin <branch>` 会遍历该 remote 的所有 pushurl，但**第一个失败即中止**。Gitee 抽风会连累 GitHub 永远收不到代码。逐条推送可让两端互不影响。

7. **钩子放进仓库 `.githooks/`，不放 `.git/hooks/`**。
   `.git/hooks` 不被版本控制，新克隆即失效，自动同步会静默消失。

8. **钩子永远 `exit 0`**。
   提交本身已经成功，非零退出会让 IDE 把整个 commit 报成失败。失败只打印 `FAIL <url>` + 补推命令。

---

## 4. 当前仓库状态（2026-10-20 实测快照）

```text
# 2026-10-20 验证时快照（HEAD 会随后续提交前进，以 git log -1 为准）
分支: main           HEAD: 6702454 "docs: 新增 HANDOFF.md 交接文档与双远端自动推送钩子"
工作区: 干净          本地 / Gitee / GitHub 三端 main 均为 6702454 ✅ 已同步

remote.origin.url        = https://github.com/icecolaa/markdown-html-cleaner.git   (fetch)
remote.origin.pushurl[0] = https://gitee.com/ice-colaa/markdown-html-cleaner.git    (push)
remote.origin.pushurl[1] = https://github.com/icecolaa/markdown-html-cleaner.git    (push)

core.hooksPath = .githooks      →  生效钩子: .githooks/post-commit
core.autocrlf  = true（全局，本机未单独覆盖）
```

已验证：Gitee `ba44f8a..6702454`、GitHub `ba44f8a..6702454`，两端 `OK`。

> ⚠️ **别误读**：这里的 `ba44f8a..6702454` 是因为 `f8523da` 已被上一会话 reset（§2.2 第 6 条、§7.4），
> 并不是"把漏推的 `f8523da` 补上了"。**改造钩子的真实动因是健壮性**（一处失败连累另一处、钩子不版本化），
> 而不是"钩子当时推失败了"——那次钩子大概率是成功的，只是推的目标是临时 bare 仓库。

---

## 5. 怎么用（命令速查）

```bash
PY="C:/Users/lenovo/.workbuddy/binaries/python/versions/3.13.12/python.exe"

# 1) 扫描（退出码 2 = 有残留；注意缺陷 A，见 §8）
"$PY" scripts/clean_md.py <目录或文件> --scan

# 2) 预演：只统计 + 打印改动样例，不写盘
"$PY" scripts/clean_md.py <目录或文件> --dry-run --diff

# 3) 执行
"$PY" scripts/clean_md.py <目录或文件>

# 4) 复核
"$PY" scripts/clean_md.py <目录或文件> --scan
git diff --stat          # 应只涉及含标签的行，不应整文件重写
```

- 省略路径 = 当前目录；目录只取**顶层** `.md`（不递归，见缺陷 D）。
- 参数可叠加：`--dry-run --diff`。

---

## 6. 已验证的事实（2026-10-20 当场实测）

临时目录 `a.md`，统计行 `font:4 img:1 其他:0`，清洗后残留 `0`：

| 输入 | 输出 | 结论 |
| --- | --- | --- |
| `<font style="color:rgb(51,51,51)">普通文本</font>与**粗体**混合` | `普通文本与**粗体**混合` | ✅ 去标签，嵌套加粗自动复原 |
| `<img src="./images/31.jpg" width="800" class="ne-image">` | `![插图](./images/31.jpg)` | ✅ 无 alt/title 时回落"插图" |
| `\| <font style="color:rgb(0,0,0)">2026</font> \| 事项 \|` | `\| 2026 \| 事项 \|` | ✅ 表格单元格正常 |
| 表头 `\| **时间** \|` | 保持不变 | ✅ 未误改加粗（符合 §3.2） |
| 围栏内 `print(type(1))` / `if a < b: pass` | 原样 | ✅ 代码块保护有效 |
| `行尾 &nbsp;&<> 结束` | `行尾  &<> 结束` | ✅ 实体还原 |

**更早的实测数据**（来自 README，本次未重跑，供参考）：在 PythonAI 教程仓库（语雀导出的 9 章 Python 教程 + 入门讲义）上清洗 `<font>` × 330、`<span>` × 26、`<img>` × 5；清洗后代码块外残留 0；其中 1 个文件零改动（说明无误伤）；git diff 仅涉及含标签的行。

---

## 7. 踩坑点（血泪清单）

### 7.1 脚本逻辑类
1. **围栏只认 ```` ``` ````，不认 `~~~`** —— `SKILL.md` 白纸黑字写了"` ``` `/`~~~` 围栏内必须原样保留"，实现却只判断 `startswith('```')`。**文档与实现不一致**，遇到 `~~~` 围栏的文件会静默误伤代码。→ 缺陷 C
2. **`--scan` 统计的是"清洗后残留"而非"原文残留"** —— 于是脏文件也退出 0，README 承诺的"退出码 2 表示有残留"形同虚设。→ 缺陷 A
3. **统计口径多减了一次 font** —— `FONT_RE` 已经同时匹配开闭标签，代码里又乘 2，"其他"一栏常年被钳到 0，看不出真实残留构成。→ 缺陷 B
4. **目录不递归** —— 多章子目录的仓库要一个个传路径，容易漏。→ 缺陷 D
5. **无 `src` 的 `<img>` 会被整枚删除**（`img_repl` 返回空串）。占位图/图标会凭空消失；同行文字不受影响。→ 缺陷 E（低）
6. **`line.replace('****', '')` 是字符串级粗暴替换** —— 正文里真出现四个连续星号会被吃掉。目前未见真实案例，属理论风险。

### 7.2 Git / 环境类
7. **`.git/hooks` 不版本化** —— 新克隆后自动推送静默失效，很容易以为是"忘了 push"。→ 已改用 `.githooks/` + `core.hooksPath`，**新克隆后必须手动执行一次** `git config core.hooksPath .githooks`（这是该方案唯一的残留成本）。
8. **`git push -u origin <branch>` 一处失败即中止** —— 多 pushurl 场景下 Gitee 挂了 GitHub 也收不到。→ 已改为逐 pushurl 推送。
9. **Windows + Git Bash 下钩子输出中文会乱码** —— 所以 `.githooks/post-commit` 的输出**全部用英文**，中文说明只写在本文档里。**改钩子时请保持这个约定。**
10. **换行符是整文件 diff 的头号元凶** —— 任何写盘路径都必须带 `newline='\n'`。
    本机 `core.autocrlf=true`（全局），工作副本里的 `.md`/`.sh` 会被签出成 CRLF，而脚本写回时固定写 LF；因为 git 提交时会把 CRLF 归一成 LF，所以 **diff 依然是干净的，不会出现整文件重写**。
    因此提交时看到的 `warning: LF will be replaced by CRLF` 是**预期噪音，可忽略**——不要为了消掉它去改 autocrlf，那样反而会触发整仓库重写。
11. **未跟踪文件无法回滚** —— 脚本没有备份功能。对未被 git 跟踪的目标文件，清洗前先复制一份。

### 7.3 内容风险类
12. **图片路径可能是坏链** —— 导出时往往不带图片目录，`./images/31.jpg` 转成 `![]()` 后依然是死链。**正确做法是提示用户补图，而不是删掉引用。**
13. **表格里的加粗别顺手改** —— 见 §3.2，这是最容易"好心办坏事"的地方。
14. **`<Mark bold>` 不是 HTML** —— 那是 WorkBuddy 资料库的文档组件格式，本脚本**不应**处理，遇到了不要扩大正则范围。

### 7.4 协作 / 并发类

15. **另一个窗口可能正在改同一个仓库** —— 本次开工时读到的 HEAD（`f8523da`）在 22 秒后被上一会话 `git reset HEAD~1` 抹掉，同时读到的临时 `pushurl` 也被还原。
    **教训**：开工快照 ≠ 稳定状态。动手写文件前、提交前各核一次 HEAD；发现 HEAD 跳变先看 `git reflog --date=iso`。
16. **验证钩子不要改 `remote.origin.pushurl`** —— 上一会话为了测钩子把 pushurl 指向 `C:/Users/lenovo/AppData/Local/Temp/bare-test.git`，收尾时才还原。一旦中途被打断，仓库就会留下一条指向临时路径的 pushurl，自动推送会**静默推到空气里**。
    **更安全的做法**：测钩子直接 `git push <具体 url> <branch>`，或临时加独立 remote
    （`git remote add baretest <path>`，测完 `git remote remove baretest`），**永远别动 origin**。
17. **悬空提交不是丢代码** —— `f8523da` 被 reset 后仍可 `git show f8523da` 查看，只是不在任何分支上，最终会被 gc 回收。真要恢复：`git reflog` 定位后 `git cherry-pick f8523da`。

---

## 8. 已知缺陷 —— **已全部修复**（2026-10-20）

按 SkillHub TRACE 评测报告做优化时一并修完。记录保留备查，含"为什么这么修"和验证方式。

| # | 级别 | 问题 | 修复方式与验证 |
| --- | --- | --- | --- |
| **A** | 中 | `--scan` 统计清洗**后**残留，脏文件退出码仍为 0，与文档承诺不符 | scan 模式改统计 `count_tags(before)`，>0 时 `return 2` ✅ 脏文件 exit=2、清洗后 exit=0 |
| **C** | 中 | 只识别 ```` ``` ```` 围栏，`~~~` 内会被误清洗，与 SKILL.md 声明冲突 | `iter_markdown_lines()` 引入 `FENCE_MARKS = ('```', '~~~')` 并记录开启字符 ✅ `~~~` 内 `<font>` 原样保留 |
| **B** | 低 | `n_other` 多减一次 font 数，统计面板失真 | 去掉 `* 2` ✅ 4 个 `<b>/<span>` 如实显示为"其他:4"（此前被钳到 0） |
| **D** | 低 | 目录不递归，只取顶层 `.md` | 新增 `--recursive`（`os.walk`，跳过隐藏目录），默认行为不变 ✅ 递归能读到 `sub/b.md`，默认读不到 |
| **E** | 低 | 无 `src` 的 `<img>` 整枚删除 | 保留 alt/title 文本 ✅ `<img alt="占位图">` → `占位图` |
| **F**（本轮新发现） | 低 | `font/img` 统计把围栏内的标签也算进去，与实际改动不一致 | `count_tags(text, regex)` 改为围栏感知 ✅ 围栏内的 2 个 `<font>` 不再计入 |

**顺带**：`--recursive` 模式下输出完整相对路径（避免子目录同名文件看不出是哪个）；
`--scan` / `--dry-run` / 执行三种模式的措辞也区分开了（`需清洗` / `将改写` / `已改写`）。

---

## 9. 下一步计划

### ✅ 已完成（2026-10-20）

- 缺陷 A / C / B / D / E / F 全部修复（§8）
- 回归样例 `examples/`（原始 + 脚本生成的期望输出）
- 参考文档 `references/`（转换规则细则 + 各来源特征）
- `LICENSE.txt`（补上 MIT 正文，此前只在 frontmatter 里声明）
- `SKILL.md` 结构重写：When to Use / When NOT to Use / Rules / Gotchas / 自检清单 / 安全声明 / Step 1–5

### P0 — 发布 v1.1.0（✅ 已于 2026-10-20 提交，审核中）

1. **从暂存目录发布，不要从仓库根目录发布**（§13.3）。发布前必跑 `--dry-run`。
2. **审核通过后**回详情页核对三件事：版本号变为 1.1.0、`examples/` 与 `references/` 可见、
   token 预估消耗（会因新增样例/参考文档上升，见 §13.5 的取舍说明）。
   CLI 返回 `status=None` 不等于失败 —— 详情页仍显示旧版本是审核未完成，别重复发布。

### P1 — 回归自动化

3. `examples/` 目前靠手工 `diff`。下一步加 `scripts/run_examples.py`（纯标准库）：
   自动对每个 `*.md` 跑清洗并与 `*.cleaned.md` 比对，一条命令出结果。
   **理由**：本项目是"改正则"型脚本，动一条规则可能连锁误伤；样例已经有了，就该让它们自动跑起来。

### P2 — 到大仓库真刀真枪跑一轮

4. 拿 PythonAI 教程仓库（9 章 + 入门讲义）用 `--recursive` 做全量回归，
   核对"1 个文件零改动"的基线是否仍成立，更新 README 实测数据。

### P3 — 继续提分（可选，慎行）

5. 想再冲 TRACE：C2 从 4.7 → 5.0 需 `references/` 文件数 ≥8 且 SKILL.md 正文 <150 行（当前 3 个 / 143 行）。
   **但不建议**：为凑数堆 reference 会让技能臃肿、token 消耗上升，属于典型"刷分反噬"。

---

## 10. 双远端自动同步机制

### 10.1 它长什么样

```
commit  →  .githooks/post-commit 触发
              ├─ git push https://gitee.com/ice-colaa/markdown-html-cleaner.git   main
              └─ git push https://github.com/icecolaa/markdown-html-cleaner.git   main
        →  两端互相独立：一端失败，另一端照推
        →  钩子恒 exit 0，失败只打印 FAIL + 补推命令
```

- fetch 源是 GitHub（`remote.origin.url`），双推靠两条 `pushurl`。
- 提交信息规范（用户约定）：`type: 中文描述`，如 `feat:` / `fix:` / `docs:` / `refactor:` / `test:`。

### 10.2 新克隆后如何复现（唯一需要手工的一步）

```bash
git clone https://github.com/icecolaa/markdown-html-cleaner.git
cd markdown-html-cleaner
git config core.hooksPath .githooks      # 必须！否则自动推送不生效
```

### 10.3 验证两端是否一致

```bash
git ls-remote --heads https://gitee.com/ice-colaa/markdown-html-cleaner.git  main
git ls-remote --heads https://github.com/icecolaa/markdown-html-cleaner.git main
git rev-parse main
# 三个 SHA 应当完全相同
```

### 10.4 排查

| 现象 | 处理 |
| --- | --- |
| commit 后没看到 `[post-commit]` 输出 | `git config --get core.hooksPath`（应为 `.githooks`）；为空则执行 §10.2 那条命令 |
| 提示 `FAIL <url>` | 提交已安全保存在本地。按提示补推：`git push <url> main`；凭据失效时重新走 credential manager |
| 只有一端有代码 | 说明另一端推送失败过，手工补推另一端即可 |
| 两端都落后很多 | 大概率是长期在别的克隆里工作，或钩子曾失效；先 `git fetch origin` 看真实差距 |

---

## 11. 续作 Checklist（新窗口开工前照着做）

1. `cd /e/code/markdown-html-cleaner && git log --oneline -3 && git status --short` —— 看 HEAD 与工作区。
   **若 HEAD 与本文档记录对不上，先 `git reflog --date=iso`** —— 很可能被另一个并发窗口动过（§7.4 第 15 条），这是本项目真实发生过一次的事，别急着怀疑自己。
2. 跑 §10.3，确认双远端一致（不一致先补推）。
3. **改脚本前**：先读 §3（设计决策）和 §7（踩坑点），别绕过围栏保护和同义转换两条铁律。
4. **改脚本后**：`--scan` → `--dry-run --diff` → 执行 → 再 `--scan` → `git diff --stat`（警惕整文件重写）。
5. **提交**：`git add -A && git commit -m "fix: 中文描述"` —— 钩子自动双推。
6. 提交后再跑一次 §10.3 复核两端 SHA。
7. **更新本文档**：改"最后更新"时间，把修掉的缺陷从 §8 移到过程记录，把新发现的坑补进 §7。
8. 有重大进展时，同步更新 `README.md` 的"实测"数据与 `SKILL.md` 的"已知陷阱"。

---

## 12. 文件清单

| 文件 | 作用 |
| --- | --- |
| `scripts/clean_md.py` | 清洗工具本体，187 行，仅标准库 |
| `SKILL.md` | 技能说明（frontmatter + 工作流 + 约束 + 转换规则 + 已知陷阱），供 Skill 运行时读取 |
| `README.md` | 对外说明：用法、转换对照、关键约束、实测数据 |
| `.githooks/post-commit` | 双远端自动推送钩子（版本化，输出保持英文） |
| `.gitignore` | 忽略 `.workbuddy/`（本地记忆数据）与 Python 缓存 |
| `references/rules/conversion-rules.md` | 完整转换规则对照表（按需加载） |
| `references/sources/*.md` | 语雀 / Notion·网页 的来源特征与处理要点 |
| `examples/*.md` | 回归样例：原始 + 脚本生成的 `*.cleaned.md` 期望输出 |
| `LICENSE.txt` | MIT 正文 |
| `HANDOFF.md` | 本文档（**开发文档，不随技能发布**，见 §13.3） |

---

## 13. TRACE 评测与发布

### 13.1 TRACE 是什么

SkillHub 的技能质量评测体系：**T** 可信任度 / **R** 可靠性 / **A** 适用性 / **C** 规范性 / **E** 有效性，
五维共 20 个子项，0–5 分。等级：4.5–5.0 优秀 / 4.0–4.4 良好 / 3.5–3.9 一般 / 3.0–3.4 较差 / <3.0 不合格。

> ⚠️ **两点必须说清楚，别搞错**：
> 1. `https://skillhub.cn/tutorials#trace-evaluation` **没有这个锚点** —— 该页只有 CLI 发布指南，
>    上面不存在任何评测报告。别再去那个 URL 找分数。
> 2. 本轮用的评测器是**社区技能** `@user_c1d16043/skill-trace-evaluation`（含 `scripts/trace_evaluate.py`），
>    输出"确定性基分 + 证据包"，最终分还需 AI 阅读正文做 ±0.3 校准。
>    **它是第三方工具，不等于平台官方详情页上的评分。**

### 13.2 怎么复跑评测

```bash
PY="C:/Users/lenovo/.workbuddy/binaries/python/versions/3.13.12/python.exe"
# 取评测器
curl -sSL -o ev.zip "https://api.skillhub.cn/api/v1/download?slug=@user_c1d16043/skill-trace-evaluation"
unzip -oq ev.zip -d ev
# 跑
"$PY" ev/scripts/trace_evaluate.py --skill-dir "E:/code/markdown-html-cleaner" --format json
```

### 13.3 发布：必须从暂存目录发（重要）

`skillhub publish` 会打包目录里**除了** `.git/.idea/.vscode/node_modules/__pycache__`
和 `.pyc/.DS_Store/Thumbs.db` 之外的**全部文件**。

**从仓库根目录发布会把 `HANDOFF.md`（20 KB）、`.githooks/`、`.workbuddy/` 一起发出去**，
包从 25 KB 膨胀到 51 KB，token 预估消耗直接翻倍。所以：

```bash
STAGE="C:/Users/lenovo/AppData/Local/Temp/skillhub-publish/markdown-html-cleaner"
rm -rf "$STAGE" && mkdir -p "$STAGE"
cd /e/code/markdown-html-cleaner
cp SKILL.md README.md LICENSE.txt "$STAGE"/
cp -r scripts references examples "$STAGE"/

"$HOME/.local/bin/skillhub" publish "$STAGE" --dry-run                    # 预检
"$HOME/.local/bin/skillhub" publish "$STAGE" --changelog "修复 xxx，新增 yyy"  # 正式发布
```

（CLI **不在 PATH**，真实路径 `~/.local/bin/skillhub`；已登录账号 `user_5dea5c46`。）

### 13.4 本轮得分变化（2026-10-20）

| 维度 | 优化前 | 优化后 | 变化 |
| --- | --- | --- | --- |
| T 可信任度 | 4.12 | **4.75** | +0.63 |
| R 可靠性 | 3.50 | **4.58** | +1.08 |
| A 适用性 | 4.45 | **4.58** | +0.13 |
| C 规范性 | 3.75 | **4.88** | +1.13 |
| E 有效性 | 3.75 | **4.83** | +1.08 |
| **综合** | **3.91**（一般） | **4.72**（优秀） | **+0.81** |

拉低分数的关键子项，本轮全部补上：

| 子项 | 前 → 后 | 补了什么 |
| --- | --- | --- |
| T3 边界声明 | 3.0 → 4.8 | 新增 `When NOT to Use`（什么时候不该用 / 不适用） |
| R1 陷阱与自检 | 3.0 → 4.5 | 新增 `## Gotchas` 章节 + `自检清单（验证）` |
| R2 工作流 | 3.5 → 4.8 | 改为 `Step 1–5`，并补 `Quick Start / Usage / Prerequisites` |
| C1 示例充分性 | 3.5 → 5.0 | 新增 `examples/`（5 个文件，cli 类阈值 ≥4） |
| C2 渐进式披露 | 3.0 → 4.7 | 新增 `references/`（3 文件 / 2 子目录）+ 按需加载提示 |
| E2 输出完整性 | 3.0 → 5.0 | 同上，`examples/` 达标 |

> **一句实话**：这些改动本身都是真实改进（边界声明、自检清单、样例、LICENSE 都是该有的），
> 顺带把评测脚本的关键词检测全部点亮。但 §9 P3 那条"为凑数堆文件"的反模式，别碰。

### 13.5 一个必须承认的取舍：分数 ↑，体积也 ↑

| | v1.0.0 | v1.1.0 |
| --- | --- | --- |
| 包体积 | 14.3 KB | **25.4 KB** |
| 详情页 token 预估消耗 | 14.1K | **预计上升**（审核通过后可见实际值） |

新增的 `examples/`（2.9 KB）+ `references/`（4.3 KB）是 C/E 两个维度拿分的关键，
但它们也确实让包变大了。**这是有意为之的取舍，不是失误**：

- 样例是可执行的回归基线（改脚本后能立刻发现误伤），不是装饰
- 参考文档走"按需加载"，Agent 不读就不会占用上下文

如果后续发现 token 消耗成为用户抱怨点，优先瘦身 `references/`（合并成 1 个文件），
**不要**删 `examples/` —— 那是回归保护，删了就没有安全网了。

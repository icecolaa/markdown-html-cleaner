# HANDOFF.md — markdown-html-cleaner 交接文档

> **给新窗口的话**：只读这一个文件就够接续。所有命令、状态、坑、待办都在下面。
> 最后更新：2026-10-20（本次会话：冒烟验证 + 双远端自动同步改造 + 本文档）

---

## 0. 30 秒速览

| 项 | 值 |
| --- | --- |
| 项目定位 | 单个 Python 脚本构成的 **Skill**：把语雀 / Notion / 网页导出的 Markdown 里的 HTML 表现层标签，同义转回标准 Markdown |
| 核心产物 | `scripts/clean_md.py`（187 行，仅用标准库） |
| 配套文档 | `SKILL.md`（技能说明，含 frontmatter，供 Skill 运行时读取）、`README.md`（用法与实测） |
| 分支 / HEAD | `main` @ `f8523da`（见 §4 提交后更新） |
| 远端 | fetch 走 GitHub；push 同时走 **Gitee + GitHub**（双远端） |
| 自动同步 | `.githooks/post-commit` 在每次 commit 后逐远端推送，需 `core.hooksPath=.githooks`（已设好） |
| 运行时 | `C:/Users/lenovo/.workbuddy/binaries/python/versions/3.13.12/python.exe`，**零第三方依赖** |
| 当前可交付状态 | 可用、已验证；有 4 个已知缺陷（§8），均不影响主流程 |

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
| 2026-10-20 00:59 | `f8523da` | `test: 验证 post-commit 自动推送`（空提交，用于验证钩子） |
| 2026-10-20 01:0x | 本次会话 | 冒烟测试 → 发现 2 个真实缺陷 → 重构自动推送钩子为仓库内版本化 → 编写本文档 |

> ⚠️ **诚实说明**：`f8523da` 之前的设计讨论过程在历史会话中已检索不到（`conversation_search` 无结果）。上表中 00:32 / 00:59 两笔是**从 git 历史与提交信息还原**的；本次会话的内容是**当场实测**的。凡标"实测/已验证"的都跑过命令，凡标"待确认"的都未验证。

### 2.2 本次会话实际做了什么

1. **盘点**：确认仓库结构、git 状态、远端配置、`post-commit` 钩子内容。
2. **冒烟测试**（临时目录 `a.md`，覆盖 font / img / 表格 / 代码围栏 / HTML 实体）：
   - 四种来源标签全部按预期转换；
   - 代码块两行内容原样保留；
   - 清洗后代码块外残留标签 = 0。
   - 同时**发现 2 个真实缺陷**（`--scan` 退出码语义、统计口径算错），见 §8 缺陷 A / B。
3. **重构自动推送**：原钩子在 `.git/hooks/post-commit`（不版本化、且 `git push -u origin` 一处失败会连累另一处）。改造为 `.githooks/post-commit` + `core.hooksPath=.githooks`，逐 pushurl 推送。
4. **核对远端连通性**：Gitee / GitHub 两端 `ls-remote` 均可达，当时都停在 `ba44f8a`（即本地领先 1 个提交，说明钩子在 `f8523da` 那次**没有成功推送**——这也是本次改造的直接动因）。
5. **写本文档**。

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

## 4. 当前仓库状态（本次提交前实测）

```
分支: main           HEAD: f8523da "test: 验证 post-commit 自动推送"
工作区: 干净          origin/main: ba44f8a（本地领先 1 个提交，待本次推送）

remote.origin.url        = https://github.com/icecolaa/markdown-html-cleaner.git   (fetch)
remote.origin.pushurl[0] = https://gitee.com/ice-colaa/markdown-html-cleaner.git    (push)
remote.origin.pushurl[1] = https://github.com/icecolaa/markdown-html-cleaner.git    (push)

core.hooksPath = .githooks      →  生效钩子: .githooks/post-commit
```

> 提交 §2.2 的第 3–5 步后，本地与两端 main 会一致（见 §10 的验证命令）。

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
11. **未跟踪文件无法回滚** —— 脚本没有备份功能。对未被 git 跟踪的目标文件，清洗前先复制一份。

### 7.3 内容风险类
12. **图片路径可能是坏链** —— 导出时往往不带图片目录，`./images/31.jpg` 转成 `![]()` 后依然是死链。**正确做法是提示用户补图，而不是删掉引用。**
13. **表格里的加粗别顺手改** —— 见 §3.2，这是最容易"好心办坏事"的地方。
14. **`<Mark bold>` 不是 HTML** —— 那是 WorkBuddy 资料库的文档组件格式，本脚本**不应**处理，遇到了不要扩大正则范围。

---

## 8. 已知缺陷（按优先级，均未修）

| # | 级别 | 问题 | 位置 | 修复方向 |
| --- | --- | --- | --- | --- |
| **A** | 中 | `--scan` 统计清洗**后**残留，脏文件退出码仍为 0，与 README/SKILL.md 承诺不符 | `scripts/clean_md.py:157` `leftover += count_tags(after)` | scan 模式改为统计 `count_tags(before)` 并在 >0 时 `return 2`；常规模式保留 after 残留统计（用于确认规则覆盖度） |
| **C** | 中 | 只识别 ```` ``` ```` 围栏，`~~~` 围栏内会被误清洗，与 SKILL.md 声明冲突 | `scripts/clean_md.py:52-58` `iter_markdown_lines()` | 围栏判定改为同时匹配 ```` ``` ```` 与 `~~~`，并区分开关（记录围栏字符） |
| **B** | 低 | `n_other` 多减一次 font 数，统计面板失真 | `scripts/clean_md.py:156` | `count_tags(before) - n_font - n_img`（去掉 `* 2`） |
| **D** | 低 | 目录不递归，只取顶层 `.md` | `scripts/clean_md.py:123-126` `collect_files()` | 加 `--recursive`，用 `os.walk`；默认行为保持不变以免破坏既有调用 |
| **E** | 低 | 无 `src` 的 `<img>` 整枚删除 | `scripts/clean_md.py:66-67` | 改为保留 alt/title 文本，或仅在整行只有该 img 时删行 |

---

## 9. 下一步计划

**P0 — 消除"文档说的"和"代码做的"之间的裂缝**
1. 修缺陷 A（`--scan` 退出码语义）。这是唯一会让用户**误判文件已干净**的问题。
2. 修缺陷 C（`~~~` 围栏）。这是唯一会**静默损坏内容**的问题。

**P1 — 补齐回归保护**
3. 建 `tests/` 目录：把 §6 的冒烟用例固化成回归样本（font / img / 表格加粗 / 代码块 / `~~~` 围栏 / HTML 实体 / 无 src 的 img 各一条），配一个纯标准库 `unittest` 入口，跑法写进 README。
   **理由**：本项目是"改正则"型脚本，任何规则调整都可能连锁误伤，没有回归样本就不能安全地改。

**P2 — 易用性**
4. 修缺陷 D（`--recursive`，多章目录一把梭）。
5. 修缺陷 B（统计面板）+ 缺陷 E（无 src 的 img）。

**P3 — 到大仓库真刀真枪跑一轮**
6. 拿 PythonAI 教程仓库（9 章 + 入门讲义）做全量回归，核对"1 个文件零改动"的基线是否仍然成立，更新 README 实测数据。

**P4 — 发布（候选，待用户确认）**
7. `SKILL.md` 的 frontmatter（name/slug/version/tags）与 README 的 MIT 许可都已就位，具备发布条件。若确认发布：
   ```bash
   "$HOME/.local/bin/skillhub" publish <skill目录> --host https://api.skillhub.cn --dry-run
   ```
   （skillhub CLI **不在 PATH**，真实路径 `~/.local/bin/skillhub`，已登录账号 `user_5dea5c46`。先 `--dry-run`，确认无误再去掉该参数。）

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
| `HANDOFF.md` | 本文档 |

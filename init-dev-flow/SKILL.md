---
name: init-dev-flow
description: 初始化仓库的开发流程配置。由 agent 自动探测 tracker 类型（GitHub / 本地 .scratch），生成声明文件，让新开发者和 agent 进入仓库即可知道 issue 在哪。每个仓库运行一次。
---

# Init Dev Flow

初始化仓库的 issue tracker 配置与声明，让任何 agent 进入仓库后能立刻判断 issue 在哪。

## 触发信号

- 新仓库首次使用 dev-flow-skills
- 仓库缺少 `docs/agents/issue-tracker.md`
- 用户说"初始化流程"、"初始化这个仓库"

## 核心 Discipline

1. **探测而非询问** — agent 自动判断 tracker 类型，不把选择题抛给用户
2. **单一事实源** — tracker 类型只在一个文件声明，其他文件放指针，避免不一致
3. **新开发者可见** — 声明必须放在 agent 进入陌生仓库也会看到的位置
4. **避免双写** — 一个仓库只用一个 tracker，GitHub 和 .scratch 不同时作为主存

## 操作步骤

### Step 1: 探测现状

依次检查，**不要假设**：

```
- docs/agents/issue-tracker.md 存在？
  → 读取现有配置。若 execution-mode 为 subagent 但缺少基础模型，仅进入 Step 3e 补齐模型引导，保留 tracker、提交策略和已确认的执行模式；否则报告"已初始化：<模式>"，结束
- git remote -v 的输出：指向 GitHub / GitLab / 无 remote？
- gh CLI 可用且已登录（gh auth status）？
- .scratch/ 目录已存在？（可能之前手动建过）
- 根目录有 CLAUDE.md 还是 AGENTS.md，还是都没有？
```

### Step 2: 判定 tracker 模式

按探测结果自动判定，**优先级从上到下**：

| 条件 | 模式 | 说明 |
|------|------|------|
| `.scratch/` 已存在且有内容 | **本地模式** | 仓库已在用本地 tracker，直接补全声明 |
| git remote 指向 GitHub 且 `gh` 可用且已登录 | **GitHub 模式** | 用 GitHub issues，不建 .scratch |
| git remote 指向 GitLab 且 `glab` 可用且已登录 | **GitLab 模式** | 用 GitLab issues，不建 .scratch |
| 无 remote / CLI 不可用 | **本地模式** | 初始化 .scratch |

**探测边界情况处理：**

- **`.scratch/` 存在但为空** → 视为"未初始化本地 tracker"，按本地模式处理：补 `.scratch/README.md` + `docs/agents/issue-tracker.md`，不重复创建已有目录
- **git remote 指向 GitHub/GitLab，但 CLI 未登录**（`gh auth status` / `glab auth status` 失败）→ **不静默降级**。提示用户："检测到 remote 是 GitHub，但 gh 未登录。请先 `gh auth login`，或确认改用本地模式。" 由用户选择，不替用户决定
- **`gh`/`glab` 未安装** → 该 remote 模式的"CLI 可用"条件不满足，降级到本地模式，但报告中注明"remote 是 GitHub 但无 gh CLI，故用本地模式"

判定后向用户报告：

```
探测结果：
- git remote: github.com:edy/zss-server.git
- gh CLI: 已登录
- .scratch/: 已存在（含 diamond-mall, app-event-log）

判定：本地模式（.scratch 已在用，优先于 remote 探测）
```

如用户对判定有异议，允许其覆盖。

### Step 3: 生成声明文件

#### 3a. 写 `docs/agents/issue-tracker.md`（单一事实源）

读取 [共享执行约定](../_agents/workflow-contract.md)。下列本地/GitHub/GitLab 模板均补入同一段状态与字段声明，以及该模式适用的归属与列表约定：

```markdown
## Ticket conventions

- Status values: ready / claimed / code-complete / resolved / parked
- ready = 待执行；claimed = 执行中或必要自动检查未通过
- code-complete = 代码与必要自动检查通过，仍待最终验收/收尾 checkpoint；可解除 ticket 依赖，外部验证条件另验
- resolved = 所有必需验收通过且收尾 checkpoint 已处理；parked = 搁置，不解除依赖
- 每票使用 Status:、Parent:、Spec:、Plan:、Blocked by:；直接归属、spec 版本、plan 包和执行依赖分别记录
- 小改动省略 spec/plan 时写 none (原因)，必要决策和测试边界记录在 ticket 中
- Git 提交与验收状态分别记录；未获用户明确授权不得提交/推送
```

已有 tracker 保留其声明的值域与完成语义；需要采用中间态时先补齐 `code-complete` 的定义，不自动改写历史票的状态。

**本地模式：**

```markdown
# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.scratch/`.

**`.scratch/` is committed to the repo and shared with the whole team.** Tickets and specs go through the same pull/review flow as code. Pull before creating new ticket files to avoid numbering collisions; if two branches both take `NN`, the later one renumbers on merge.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- The implementation plan (when produced) is `.scratch/<feature-slug>/plan.md`
- `.scratch/<feature-slug>/INDEX.md` is the feature navigation entry: current Spec, Plan, linked ticket hierarchy, and version history; create it when the first Spec or ticket is saved
- Keep `.scratch/README.md` linked to each feature INDEX; preserve existing explanations and history
- Use Parent: for direct ownership (Spec → Plan → Tickets; existing Epic optional); file references in metadata are relative to the feature directory
- INDEX links point to real files and do not duplicate ticket statuses or approval state; `/find` reads those from the source files
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Every ticket follows the fields and states declared in Ticket conventions below
- API contracts produced by `/to-api-contract` live at `.scratch/<feature-slug>/contracts/<ticket-slug>.md`
- Small changes that skip spec/plan/ticket leave a record in `.scratch/<feature-slug>/changelog.md` (or an in-place edit to an existing spec/plan/ticket)
- The project architecture diagram (when generated) is `.scratch/architecture.md`
- Triage state is recorded as a `Status:` line near the top of each issue file
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.
```

**GitHub 模式：**

```markdown
# Issue tracker: GitHub

Issues and specs for this repo live in GitHub Issues on the connected remote. Use the `gh` CLI.

## Artifact conventions

- Spec、Plan、Ticket 分别使用独立 issue；Plan issue 正文是现行技术方案，评论只记录讨论、批准依据和变更原因
- Spec 正文用 Plan: 引用 Plan issue；Plan 正文用 Spec: 指向当前执行版 Spec，列出关联 tickets
- Parent: 记录直接归属，并同步原生 Spec → Plan → Tickets；已有 Epic 时作为 Spec 父级，不额外强制建单
- 沿用项目类型标签，未约定时用 spec / plan / ticket，并采用 [Spec] / [Plan] / [Ticket] 标题前缀；标签或原生关系失败时如实报告，不重复创建 issue
- 先探测当前 CLI 的层级能力，必要时用 gh api；父级冲突不强制替换，规格版本迁移按共享约定核对
- Ticket 分别填写 Spec: 和 Plan:，后者格式为 <Plan issue 引用> / P<N>
- Plan 正文记录待 review / 已批准状态；open/closed 不是批准状态
- amend 更新同一 Plan issue 正文及 Spec: 引用，不创建 plan-vN；Spec 版本定位沿用团队 tracker 约定
- 远程 issue 是主存，不额外维护本地 plan.md 副本

## Optional Project

Project: none

用户已提供 Project 时记录其 URL/ID，并将本次产物加入其中；未指定时沿用 none。Projects 表格可打开 View → Show hierarchy，显示 Parent issue / Sub-issue progress；普通 Issues 页用于分类和筛选。

## When a skill says "publish to the issue tracker"

Create a GitHub issue with `gh issue create`.

## When a skill says "fetch the relevant ticket"

Use `gh issue view <number>`.
```

**GitLab 模式：** 沿用独立产物、正文字段与状态约定，使用 `glab`。原生层级和展示按该平台实际能力处理，不复制 GitHub API、CLI 参数或 Projects 配置。

#### 3b. 本地模式额外：写 `.scratch/README.md`

```markdown
# .scratch/

本目录是仓库的本地 issue tracker：specs 与 tickets 以 markdown 形式存放，**随仓库提交、团队共享**。

约定见 `docs/agents/issue-tracker.md`。

## Features

创建 feature 后在此登记到 `<feature>/INDEX.md` 的链接；旧 feature 尚无索引时链接其目录。
```

（如果 `.scratch/` 已存在，保留现有内容，只补 README。）

#### 3c. 写指针到根目录声明文件

**选择编辑哪个文件（按优先级）：**

1. `CLAUDE.md` 已存在 → 编辑它
2. 否则 `AGENTS.md` 已存在 → 编辑它
3. 都没有 → 创建 `AGENTS.md`（更通用，Pi/Codex/Cursor 都认）

**写入内容（追加 `## Agent skills` 区块，已存在则更新对应行）：**

```markdown
## Agent skills

### Issue tracker

Issues and specs live as local markdown under `.scratch/<feature-slug>/`, committed to the repo and shared with the team. The spec, plan (when produced), and per-ticket files live here. See `docs/agents/issue-tracker.md`.
```

GitHub 模式则写：

```markdown
## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues on this repo's remote. Use the `gh` CLI. See `docs/agents/issue-tracker.md`.
```

**规则：** 指针只放一行 + 指向 issue-tracker.md，**不复制**结构约定详情（避免双写腐化）。

### Step 3d: 配置提交策略

提交策略决定 `/implement` 何时提交、以及 `/simplify` 何时触发。

**探测：** 用 `git log --oneline -20` 看历史提交粒度：
- 历史多为小步多提（每条对应一个明确小改动）→ 推测 per-ticket
- 历史多为大提交（一次含多个改动）→ 推测 squash

**询问确认（已有明确的提交策略时直接沿用）：**

```
根据 git 历史，推测你的提交习惯是：<推测结果>

你的习惯是？
A. 每张 ticket 完成后立即提交（per-ticket）
B. 整个 feature 完成后统一提交（squash）
```

**写入 `docs/agents/commit-strategy.md`：**

per-ticket：

```markdown
# Commit strategy: per-ticket

每张 ticket 达到 code-complete 后进入收尾 checkpoint，经用户明确授权再提交。

- `/implement` 每票验证后更新状态与依赖，再独立处理该票的收尾和提交
- `/simplify` 在每张 ticket 提交前触发，scope = 该 ticket 的未提交 diff
- `/simplify` 修复后留人工 checkpoint，用户确认后才提交
```

squash：

```markdown
# Commit strategy: squash

整个 feature 的执行票达到 code-complete/resolved 后统一收尾，经用户明确授权再提交。

- `/implement` 每票验证后更新 code-complete 与依赖，可继续下游票；不等待 Git 提交才解除依赖
- `/simplify` 在统一提交前触发，scope = feature 起点到工作区的累计 diff
- `/simplify` 修复后留人工 checkpoint，用户确认后才提交
```

**规则：** 提交策略是单一事实源，`/implement` 和 `/simplify` 都读此文件，不各自硬编码触发时机。

### Step 3e: 配置执行模式与基础模型

执行模式决定执行型技能（`/implement`、`/simplify`、`/to-api-contract`、`/export-session`）默认**是否分派给独立子 agent**。

已有确认的执行模式时直接沿用，仅补齐缺失的基础模型；首次配置执行模式时再询问下列选项。

**说明给用户：**

```
执行型任务（实现与验证、代码清理、契约提取、会话导出）可以：
- 派给独立子 agent：上下文隔离、可单独指定模型，但每次分派要重启子进程、重读文件，小任务略慢
- 主会话直接做：省去分派开销，小任务更快，但长任务会污染主会话上下文

你的默认习惯是？
A. 默认派子 agent（隔离好，推荐）
B. 默认主会话直接做（小任务快）
（无论选哪个，单次执行时都可以临时覆盖）
```

**选 A 后引导配置基础模型：**

1. 先读取已有 `execution-mode.md` 和当前工具可用的模型列表。已有用户选择可继续沿用；列表必须来自当前环境，不在模板里写死模型名或供应商，不读取或展示密钥。
2. 展示实际可用的模型，让用户选择或输入完整模型 ID；同时提供“继承当前主会话模型（`inherit`）”。无法枚举模型时明确说明，请用户提供当前工具支持的 ID，不代选一个模型。
3. 把确认结果写入下方的 `**基础模型**:` 字段。`inherit` 也需要明确记录；不能把未选择、字段缺失当作已经配置完成。
4. 根据当前工具的模型列表核对所选 ID 是否可用。没有实际调用时，报告“配置已保存，运行未验证”，不虚报调用成功。

inline 模式直接使用主会话模型，无需单独配置子 agent 基础模型。

**写入 `docs/agents/execution-mode.md`：**

选 A（派）：

```markdown
# Execution mode: subagent

执行型技能默认分派给独立子 agent 执行。

**基础模型**: <用户确认的模型 ID 或 inherit>

- `/implement` 的实现与验证 → `implementer` 子 agent
- `/simplify` → `simplifier` 子 agent
- `/to-api-contract` → `contract-writer` 子 agent
- `/export-session` → `exporter` 子 agent

子 agent 定义见 `_agents/*.prompt.md`，各工具经 `adapters/` 注册。
Pi agent 的 thinking 分级由 build.sh 控制；使用 `build.sh --project-root <目标仓库>` 读取本项目的基础模型并生成 agent 配置。其他工具分派时按各自支持的格式应用此字段；`inherit` 使用工具的原生继承方式。

**单次覆盖：** 用户可在单次执行时改为主会话直接做（如"这张小 ticket 别派了"）。
**模型覆盖：** Pi 构建时可用 `DEV_FLOW_MODEL` 临时覆盖本项目选择；不提供固定默认模型。
```

选 B（不派）：

```markdown
# Execution mode: inline

执行型技能默认由主会话直接执行，不分派子 agent。

- 各技能的执行逻辑（实现与验证、清理维度、契约模板、导出规则）写在对应 `_agents/*.prompt.md` 里，主会话直接参照执行。

**单次覆盖：** 用户可在单次执行时改为派子 agent（如"这个大 ticket 派给 implementer"）。
```

**规则：** 执行模式是单一事实源，4 个执行型技能读此文件决定默认行为；两条路径（派 / 不派）都指向同一份 `_agents/*.prompt.md` 作为执行逻辑，只是执行主体不同。

### Step 3f: 生成项目架构图（已有代码时）

项目级架构图是整个仓库的"地图"，独立于任何 feature，放 `.scratch/` 根目录。

**判断时机：**
- 仓库已有代码（有实际的模块/服务）→ 立即生成
- 空仓库或刚起步 → 跳过，告知用户"首个 spec 完成、有实际模块后可重新生成"

**生成方式：**
- 按 execution-mode 分派 `scout` 侦察仓库结构（模块、入口、存储、外部依赖），或直接由主会话侦察
- 用 **mermaid flowchart** 生成 `.scratch/architecture.md`（参照 `_agents/diagram-guide.md`）：用 `subgraph` 表达泳道/边界，组件带类型标记（`[frontend]`/`[backend]`/`[database]` 等），一条横向主流程
- 用 ```` ```mermaid ```` 代码块包裹，GitHub/飞书可渲染成图

**后续维护：** 架构随代码演进而变化。大变更后可重新生成（人工触发，或后续 spec 发现架构已过期时）。

### Step 4: 确认并报告

向用户展示写入的文件清单和关键内容，确认后完成：

```
初始化完成（本地模式 + squash 提交 + 派子 agent）：

✅ docs/agents/issue-tracker.md   — tracker 类型声明（单一事实源）
✅ docs/agents/commit-strategy.md — 提交策略（simplify 触发时机）
✅ docs/agents/execution-mode.md  — 执行模式 + 用户确认的基础模型（subagent 模式）
✅ .scratch/README.md             — 本地 tracker 说明
✅ .scratch/architecture.md       — 项目架构图（已有代码时）
✅ .scratch/<feature>/changelog.md — 小改动的记录兜底（小改动不必走 spec/plan/ticket）
✅ AGENTS.md                      — 新增 ## Agent skills 指针区块

新开发者/agent 进入仓库后，读 AGENTS.md 即可知道 issue 在 .scratch/，
读 .scratch/architecture.md 可快速理解项目结构。
```

## 产出物

| 模式 | 生成文件 |
|------|---------|
| 本地 | `docs/agents/issue-tracker.md` + `commit-strategy.md` + `execution-mode.md` + `.scratch/README.md` + 根目录指针 |
| GitHub | `docs/agents/issue-tracker.md` + `commit-strategy.md` + `execution-mode.md` + 根目录指针 |
| GitLab | `docs/agents/issue-tracker.md` + `commit-strategy.md` + `execution-mode.md` + 根目录指针 |

## 边界

| 适合 | 不适合 |
|------|--------|
| 每个仓库首次接入 dev-flow-skills | 已有完整 issue-tracker.md 的仓库（直接读取即可，不重复初始化） |
| 新开发者 onboarding | 临时单次任务（不必初始化，直接用 no-issue 流程） |

## 与其他技能的关系

- 所有需要"发布到 tracker"的技能（`/to-spec`、`/to-plan`、`/to-tickets`）先读 `docs/agents/issue-tracker.md` 判断写去哪
- `/implement` 和 `/simplify` 读 `docs/agents/commit-strategy.md` 决定提交与清理时机
- `/export-session` 的 issue 推断也依赖此文件判断 issue 形态
- 没有此文件时，技能应提示"先运行 /init-dev-flow"

## 记录软硬规则（贯穿全流程）

改动必须留记录（spec/plan/ticket/changelog 任一），但 spec/plan/ticket 按规模软选用。详见 `/to-tickets` 的"记录是硬需求（软硬规则）"表。**小改动不必走 ticket/plan/spec，但必须留记录**——init 生成的 changelog.md 即为兜底。

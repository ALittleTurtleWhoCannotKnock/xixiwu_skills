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
  → 已初始化，读其内容确认模式，报告"已初始化：<模式>"，结束
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

**本地模式：**

```markdown
# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.scratch/`.

**`.scratch/` is committed to the repo and shared with the whole team.** Tickets and specs go through the same pull/review flow as code. Pull before creating new ticket files to avoid numbering collisions; if two branches both take `NN`, the later one renumbers on merge.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- The implementation plan (when produced) is `.scratch/<feature-slug>/plan.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Every ticket has a `Status:` line with one of: `ready` (等待执行), `claimed`（执行中）, `resolved`（验证完成）
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

## When a skill says "publish to the issue tracker"

Create a GitHub issue with `gh issue create`.

## When a skill says "fetch the relevant ticket"

Use `gh issue view <number>`.
```

**GitLab 模式：** 同 GitHub，替换为 `glab` CLI。

#### 3b. 本地模式额外：写 `.scratch/README.md`

```markdown
# .scratch/

本目录是仓库的本地 issue tracker：specs 与 tickets 以 markdown 形式存放，**随仓库提交、团队共享**。

约定见 `docs/agents/issue-tracker.md`。
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

**询问确认（初始化时唯一需要用户决策的点）：**

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

每张 ticket 完成后立即提交。

- `/implement` 每完成一张 ticket 就提交一次（关联该 ticket）
- `/simplify` 在每张 ticket 提交前触发，scope = 该 ticket 的未提交 diff
- `/simplify` 修复后留人工 checkpoint，用户确认后才提交
```

squash：

```markdown
# Commit strategy: squash

整个 feature 完成后统一提交。

- `/implement` 期间不提交，所有 ticket 完成后统一提交
- `/simplify` 在统一提交前触发，scope = feature 起点到工作区的累计 diff
- `/simplify` 修复后留人工 checkpoint，用户确认后才提交
```

**规则：** 提交策略是单一事实源，`/implement` 和 `/simplify` 都读此文件，不各自硬编码触发时机。

### Step 3e: 配置执行模式与基础模型

执行模式决定执行型技能（`/implement` 的 TDD、`/simplify`、`/to-api-contract`、`/export-session`）默认**是否分派给独立子 agent**。

**说明给用户：**

```
执行型任务（TDD、代码清理、契约提取、会话导出）可以：
- 派给独立子 agent：上下文隔离、可单独指定模型，但每次分派要重启子进程、重读文件，小任务略慢
- 主会话直接做：省去分派开销，小任务更快，但长任务会污染主会话上下文

你的默认习惯是？
A. 默认派子 agent（隔离好，推荐）
B. 默认主会话直接做（小任务快）
（无论选哪个，单次执行时都可以临时覆盖）
```

**若选 A（派子 agent），继续询问基础模型：**

```
检测到以下已配置的模型：
1. xixiwu/k3
2. xixiwu/k3-256k
3. xixiwu/kimi-for-coding-highspeed
4. xixiwu/stealth/ox-alpha

子 agent 使用哪个基础模型？（输入序号或直接输入模型名）
注：各 agent 的 thinking 分级由 build.sh 控制（scout=low, implementer=high 等），
    如需按 agent 单独指定模型，可后续修改 adapters/build.sh。
```

**写入 `docs/agents/execution-mode.md`：**

选 A（派）：

```markdown
# Execution mode: subagent

执行型技能默认分派给独立子 agent 执行。

**基础模型**: <用户选择的模型>

- `/implement` 的 TDD → `implementer` 子 agent
- `/simplify` → `simplifier` 子 agent
- `/to-api-contract` → `contract-writer` 子 agent
- `/export-session` → `exporter` 子 agent

子 agent 定义见 `_agents/*.prompt.md`，各工具经 `adapters/` 注册。
各 agent 的 thinking 分级由 build.sh 控制；如需按 agent 单独指定模型，修改 `adapters/build.sh` 的 MODEL 映射。

**单次覆盖：** 用户可在单次执行时改为主会话直接做（如"这张小 ticket 别派了"）。
**模型覆盖：** 环境变量 `DEV_FLOW_MODEL` 可临时覆盖基础模型（如 CI 场景）。
```

选 B（不派）：

```markdown
# Execution mode: inline

执行型技能默认由主会话直接执行，不分派子 agent。

- 各技能的执行逻辑（TDD 循环、清理维度、契约模板、导出规则）写在对应 `_agents/*.prompt.md` 里，主会话直接参照执行。

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
✅ docs/agents/execution-mode.md  — 执行模式（是否默认派子 agent）
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

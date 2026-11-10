---
name: flow-init
description: "Initialize or complete repository workflow setup: discover the tracker, confirm commit strategy, execution mode/base model, and interaction/artifact languages. Preserve existing choices and fill only missing settings."
---

# Flow Init

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

Initialize repository workflow declarations so an entering agent can locate the tracker immediately.

## When to use

- A repository first adopts dev-flow-skills.
- `docs/agents/issue-tracker.md` is missing.
- The user requests initialization.
- An existing repository needs missing/updated interaction or artifact language preferences.

## Core disciplines

1. Discover the tracker from the environment; confirm missing language, commit, and execution preferences rather than replacing explicit choices.
2. Keep the tracker declaration authoritative, with pointers elsewhere.
3. Put discoverable pointers in the repository's entry instructions.
4. Use one tracker master, not GitHub and `.scratch` simultaneously.

## Workflow

### Step 1: Inspect existing state

Check in order; do not assume:

```
- Does docs/agents/issue-tracker.md already exist?
  -> Read its tracker, commit strategy, execution mode/base model, and language.md; do not reset choices.
  -> For missing/requested language fields, run only Step 2.5 to fill/update them.
  -> For a missing execution mode or missing subagent base model, run only Step 3e; complete Step 2.5 first when language is also missing.
  -> Partial setup does not repeat tracker detection, unrelated declarations, or architecture generation. Report actual additions and stop; if everything is complete and no update was requested, report already initialized and stop.
- What does git remote -v identify: GitHub, GitLab, or no remote?
- Is the relevant CLI available/authenticated (gh auth status / glab auth status)?
- Does .scratch already exist?
- Which root instruction file exists: CLAUDE.md, AGENTS.md, or neither?
```

### Step 2: Determine the tracker

Apply this priority order:

| Evidence | Mode | Action |
|----------|------|--------|
| `.scratch/` already contains work | Local | Preserve the existing tracker and complete its declaration |
| GitHub remote, usable authenticated `gh` | GitHub | Use issues, without creating `.scratch` |
| GitLab remote, usable authenticated `glab` | GitLab | Use issues |
| No remote or no usable CLI | Local | Initialize `.scratch` |

If `.scratch` is empty, treat local tracking as uninitialized: add its README and tracker declaration without recreating existing directories.

An unauthenticated CLI for a GitHub/GitLab remote is **not silent permission to switch trackers**. Explain the login problem, offer login or an explicitly chosen local mode, and let the user decide. If the CLI is not installed, use the local fallback but disclose why.

Report the evidence and conclusion, for example:

```
探测结果：
- git remote: github.com:edy/zss-server.git
- gh CLI: 已登录
- .scratch/: 已存在（含 diamond-mall, app-event-log）

判定：本地模式（.scratch 已在用，优先于 remote 探测）
```

The user may override the inferred mode.

### Step 2.5: Confirm and save languages

Read the target repository's `docs/agents/language.md` under [language policy](../_agents/language-policy.md). Resolve interaction and artifact languages separately; they may match or differ. Reuse explicit existing choices without asking again.

- For unconfirmed preferences, suggest candidates from the conversation and existing business documents, then confirm both. A suggestion such as Chinese interaction/English artifacts is an example, not a built-in default.
- Fill only missing fields. Do not re-ask complete confirmed settings. Task-specific language overrides remain temporary unless the user asks to change project defaults.
- Until confirmation, keep the question pending and stop dependent file generation. Do not save guesses/placeholders or claim initialization is complete. One clear confirmation can cover both fields; a choice for one field is not confirmation of the other.
- After confirmation, save explicit language names or codes (e.g. zh-CN/en) below. Keep the configuration header/keys fixed; localize explanation prose. Do not change tracker, commit, or model choices as a side effect.

```markdown
# Workflow language
interaction_language: <用户确认的交互语言>
artifact_language: <用户确认的业务产物语言>
```

New repositories continue to Step 3. Use interaction language for subsequent questions and artifact language for generated documents. In language-only updates, add/update only the root language pointer using Step 3c's file-selection rule and preserve other content. If a base model is also missing, complete Step 3e, otherwise report the partial update and finish. Changing defaults does not bulk-translate existing/frozen artifacts.

### Step 3: Write declarations

The templates retain fixed structure and protocol fields. Localize document prose under artifact language and user questions/reports under interaction language; preserve keys, state values, paths, and identifiers. Do not start this step before language confirmation.

#### 3a: Write docs/agents/issue-tracker.md

Read the [shared contract](../_agents/workflow-contract.md). Include the common state/field conventions below and the mode-specific ownership/navigation rules.

```markdown
## Todo conventions

- 执行待办统一称为 Todo，新标题使用 [Todo]；旧 [Ticket] / ticket 标签仅供兼容识别和复用，不批量改写历史条目
- Status values: ready / claimed / resolved / parked
- ready = 待执行；claimed = 执行中或必要自动检查未通过
- resolved = 本票实现、必要工程检查、审查和必需产物通过，自动关闭并解除票级依赖；parked = 搁置，不解除依赖
- 人工功能验收集中到 Plan（无 Plan 时 Spec），使用 Acceptance: pending / accepted / changes-requested；票级关闭不等待该确认
- 远程票同步实际 close 并复读状态；失败如实报告“工程完成 / 平台关闭未同步”，不谎报关闭成功
- 每票使用 Status:、Parent:、Spec:、Plan:、Blocked by:；直接归属、spec 版本、plan 包和执行依赖分别记录
- 小改动省略 spec/plan 时写 none (原因)，必要决策和测试边界记录在 Todo 中
- Git 提交、票级完成和功能验收分别记录；未获用户明确授权不得提交/推送，暂不提交不阻止票级关闭
```

When adopting the new closure flow in an existing tracker, update only relevant ticket/parent-acceptance conventions, retaining custom fields and historical states. Keep declared code-complete compatibility; do not bulk-close old tickets or downgrade mandatory engineering verification to human acceptance.

**Local template:**

```markdown
# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.scratch/`.

**`.scratch/` is committed to the repo and shared with the whole team.** Todos and specs go through the same pull/review flow as code. Pull before creating new Todo files to avoid numbering collisions; if two branches both take `NN`, the later one renumbers on merge.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- A Spec may own one or several independent Plans: keep existing `.scratch/<feature>/plan.md`; new peer scopes use `.scratch/<feature>/plans/<scope-slug>.md`, one current artifact per scope
- The Spec lists all actual references under Plans: (legacy singleton Plan: is compatible); each Plan records Parent:, Spec:, Scope:, its own approval/acceptance and Todos
- AI chooses the number from scope/independence unless the user specifies count/grouping; honor that directive, reporting an actual independence/coverage conflict before choosing an alternative
- `.scratch/<feature>/INDEX.md` links the current Spec, all applicable scoped Plans and each Plan's own Todos/version provenance; create it when the first Spec or Todo is saved
- Keep `.scratch/README.md` linked to each feature INDEX; preserve existing explanations and history
- Use Parent: for direct ownership (Spec → peer Plans → each Plan's Todos; existing Epic optional); Todo numbering is feature-wide and metadata paths are feature-relative
- INDEX links point to real files and do not duplicate Todo statuses or approval state; `/flow-status` reads those from the source files
- Todos are one file each at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, with a [Todo] title; never combine them into a single file
- Every Todo follows the fields and states declared in Todo conventions below
- API contracts produced by `/flow-api` live at `.scratch/<feature-slug>/contracts/<ticket-slug>.md`
- Small changes that skip Spec/Plan/Todo leave a record in `.scratch/<feature-slug>/changelog.md` (or an in-place edit to an existing Spec/Plan/Todo)
- The project architecture diagram (when generated) is `.scratch/architecture.md`
- Triage state is recorded as a `Status:` line near the top of each issue file
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant Todo"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.
```

**GitHub template:**

```markdown
# Issue tracker: GitHub

Issues and specs for this repo live in GitHub Issues on the connected remote. Use the `gh` CLI.

## Artifact conventions

- Spec、Plan、Todo 分别使用独立 issue；Plan issue 正文是现行技术方案，评论只记录讨论、批准依据和变更原因
- Spec 正文用 Plans: 列出全部独立 Plan 的实际引用／范围，旧单 Plan: 兼容；每个 Plan issue 正文用 Spec:、Scope: 记录适用版本及负责范围，只列本 Plan 的 Todos
- AI 按独立功能边界和耦合判断 Plan 数量；用户指定数量／分组优先，冲突时说明后询问，不用包编号或空壳凑数
- Parent: 同步原生 Spec → 多个 Plan → 各自 Todos；每票只归属一个 Plan，已有 Epic 时作为 Spec 父级
- 新标题使用 [Spec] / [Plan] / [Todo]，类型标签默认 spec / plan / todo；可沿用明确配置的等价标签，旧 ticket 仅作历史兼容，不用于新待办；标签或原生关系失败时如实报告，不重复创建 issue
- 先探测当前 CLI 的层级能力，必要时用 gh api；父级冲突不强制替换，规格版本迁移按共享约定核对
- Todo 分别填写 Spec: 和 Plan:，后者格式为 <Plan issue 引用> / P<N>
- Plan 正文记录待 review / 已批准状态；open/closed 不是批准状态
- /flow-amend 仅就地更新受影响的 Plan issue，不创建 plan-vN；未受影响范围保留明确沿用依据及原批准／验收，历史票不因版本号变化重写
- 每个 Plan 独立维护范围内验收，Spec 汇总引用及真正全局验收项，不重复同一验收状态；远程 issue 是主存，不额外维护本地方案副本

## Optional Project

Project: none

用户已提供 Project 时记录其 URL/ID，并将本次产物加入其中；未指定时沿用 none。Projects 表格可打开 View → Show hierarchy，显示 Parent issue / Sub-issue progress；普通 Issues 页用于分类和筛选。

## When a skill says "publish to the issue tracker"

Create a GitHub issue with `gh issue create`.

## When a skill says "fetch the relevant Todo"

Use `gh issue view <number>`.
```

For GitLab, retain separate artifacts, fields, and state semantics, using glab and the platform's actual hierarchy capabilities. Do not copy GitHub-specific API calls, flags, or Projects configuration.

#### 3b: Add the local .scratch/README.md

```markdown
# .scratch/

本目录是仓库的本地 issue tracker：Spec 与 Todo 以 markdown 形式存放，**随仓库提交、团队共享**。

约定见 `docs/agents/issue-tracker.md`。

## Features

创建 feature 后在此登记到 `<feature>/INDEX.md` 的链接；旧 feature 尚无索引时链接其目录。
```

Preserve an existing `.scratch` and its content; add the README as needed.

#### 3c: Add repository-entry pointers

Select, in order: existing CLAUDE.md; otherwise existing AGENTS.md; otherwise create AGENTS.md.

Append `## Agent skills` or update its relevant existing lines. Local example:

```markdown
## Agent skills

### Issue tracker

Issues and specs live as local markdown under `.scratch/<feature-slug>/`, committed to the repo and shared with the team. The spec, plan (when produced), and per-ticket files live here. See `docs/agents/issue-tracker.md`.
```

GitHub example:

```markdown
## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues on this repo's remote. Use the `gh` CLI. See `docs/agents/issue-tracker.md`.
```

Also add/update the language pointer. A language-only update changes this block, not existing tracker pointers or unrelated settings:

```markdown
### Workflow language

Use `docs/agents/language.md` for interaction and workflow-artifact languages; explicit task overrides apply only to that task.
```

Root instructions hold pointers, not copied language values or structural rules. Align conflicting language clauses only within the user's authorized language change. Report unmodifiable higher-priority conflicts rather than claiming the preference took effect.

### Step 3d: Confirm commit strategy

This determines commit timing in `/flow-do` and cleanup timing in `/flow-simplify`. Inspect `git log --oneline -20`: many small scoped commits suggest per-ticket; larger combined changes suggest squash. Reuse an explicit choice; otherwise confirm the suggestion:

```
根据 git 历史，推测你的提交习惯是：<推测结果>

你的习惯是？
A. 每张待办完成后立即提交（per-ticket）
B. 整个 feature 完成后统一提交（squash）
```

Save `docs/agents/commit-strategy.md` using the chosen template.

**per-ticket:**

```markdown
# Commit strategy: per-ticket

每张待办通过工程检查和审查后自动 resolved/关闭，再独立处理提交 checkpoint；人工功能验收留在 Plan/Spec，经用户明确授权才提交。

- `/flow-do` 每票验证后更新状态与依赖，再独立处理该票的收尾和提交
- `/flow-simplify` 在每张待办提交前触发，scope = 该待办的未提交 diff
- `/flow-simplify` 修复后留人工 checkpoint，用户确认后才提交
```

**squash:**

```markdown
# Commit strategy: squash

整个 feature 的执行票自动 resolved/关闭后统一处理提交，经用户明确授权才提交；Plan/Spec 另行记录功能验收，不因票全关自动通过。

- `/flow-do` 每票工程验证和审查通过后 resolved/关闭并更新依赖，可继续下游票；不等待 Git 提交或人工功能验收
- `/flow-simplify` 在统一提交前触发，scope = feature 起点到工作区的累计 diff
- `/flow-simplify` 修复后留人工 checkpoint，用户确认后才提交
```

This file is authoritative; implementation and simplification read it rather than hard-coding timing.

### Step 3e: Confirm execution mode and base model

This determines whether implementation, cleanup, contract extraction, and session export default to a child agent. Reuse a confirmed mode and fill only a missing base model. Ask about the mode only when it has not been selected:

```
执行型任务（实现与验证、代码清理、契约提取、会话导出）可以：
- 派给独立子 agent：上下文隔离、可单独指定模型，但每次分派要重启子进程、重读文件，小任务略慢
- 主会话直接做：省去分派开销，小任务更快，但长任务会污染主会话上下文

你的默认习惯是？
A. 默认派子 agent（隔离好，推荐）
B. 默认主会话直接做（小任务快）
（无论选哪个，单次执行时都可以临时覆盖）
```

For subagent mode, guide model selection:
1. Read the existing execution-mode file and the current tool's actual available-model list. Reuse user choices. Never hard-code a provider/model or read/expose keys.
2. Show available models and allow a full supported ID or explicit `inherit`. If enumeration is unavailable, disclose that and ask for a supported ID rather than choosing one.
3. Save the confirmed choice in `**基础模型**:` below. `inherit` also requires explicit selection; a missing field is not completed setup.
4. Check the choice against the available list. Without an actual invocation, report configuration saved/runtime unverified, not a successful call.

Inline mode uses the main-session model and needs no separate child base model.

**Subagent template for docs/agents/execution-mode.md:**

```markdown
# Execution mode: subagent

执行型技能默认分派给独立子 agent 执行。

**基础模型**: <用户确认的模型 ID 或 inherit>

- `/flow-do` 的实现与验证 → `implementer` 子 agent
- `/flow-simplify` → `simplifier` 子 agent
- `/flow-api` → `contract-writer` 子 agent
- `/flow-export` → `exporter` 子 agent

子 agent 定义见 `_agents/*.prompt.md`，各工具经 `adapters/` 注册。
Pi agent 的 thinking 分级由 build.sh 控制；使用 `build.sh --project-root <目标仓库>` 读取本项目的基础模型并生成 agent 配置。其他工具分派时按各自支持的格式应用此字段；`inherit` 使用工具的原生继承方式。

**单次覆盖：** 用户可在单次执行时改为主会话直接做（如"这张小待办别派了"）。
**模型覆盖：** Pi 构建时可用 `DEV_FLOW_MODEL` 临时覆盖本项目选择；不提供固定默认模型。
```

**Inline template:**

```markdown
# Execution mode: inline

执行型技能默认由主会话直接执行，不分派子 agent。

- 各技能的执行逻辑（实现与验证、清理维度、契约模板、导出规则）写在对应 `_agents/*.prompt.md` 里，主会话直接参照执行。

**单次覆盖：** 用户可在单次执行时改为派子 agent（如"这个大待办派给 implementer"）。
```

This file is authoritative for the four execution skills. Both modes follow the same `_agents/*.prompt.md`; only the executor changes.

### Step 3f: Generate architecture when code exists

The repository architecture map is independent of any feature and lives at `.scratch/architecture.md`. Generate it for real existing modules/services. Skip empty/early repositories and explain that it can be generated once the first Spec and actual modules exist.

Use scout according to execution-mode or inspect directly. Follow `_agents/diagram-guide.md`: Mermaid flowchart, subgraph boundaries/swimlanes, component type tags (`[frontend]`, `[backend]`, `[database]`), and one horizontal main flow. Use fenced mermaid. Maintain it as architecture changes; major regeneration is human-triggered or follows discovery of an outdated map.

### Step 4: Confirm and report

Show the actual changed files and key content. Do not copy conditional architecture/changelog entries from this illustrative list as if they had been generated. A language-only update reports only its actual changes.

```
初始化完成（本地模式 + squash 提交 + 派子 agent）：

✅ docs/agents/issue-tracker.md   — tracker 类型声明（单一事实源）
✅ docs/agents/commit-strategy.md — 提交策略（/flow-simplify 触发时机）
✅ docs/agents/execution-mode.md  — 执行模式 + 用户确认的基础模型（subagent 模式）
✅ docs/agents/language.md        — 用户确认的交互语言与业务产物语言
✅ .scratch/README.md             — 本地 tracker 说明
✅ .scratch/architecture.md       — 项目架构图（已有代码时）
✅ .scratch/<feature>/changelog.md — 小改动的记录兜底（小改动不必走 Spec/Plan/Todo）
✅ AGENTS.md                      — 新增 ## Agent skills 指针区块

新开发者/agent 进入仓库后，读 AGENTS.md 即可知道 issue 在 .scratch/，
读 .scratch/architecture.md 可快速理解项目结构。
```

## Outputs

All modes produce `docs/agents/issue-tracker.md`, commit-strategy.md, execution-mode.md, language.md, and repository-entry pointers. Local mode additionally produces `.scratch/README.md`; architecture is conditional.

## Boundaries and consumers

Use for first setup, missing language/base-model preferences, or onboarding. A complete project with no update request should simply reuse declarations. A temporary single task need not initialize the whole workflow.

Publishing skills read issue-tracker.md; `/flow-do` and `/flow-simplify` read commit-strategy.md; `/flow-export` uses tracker conventions for issue inference. All skills resolve language.md and pass effective languages plus the target repository to delegates. Source-instruction language does not choose output language. A missing tracker declaration requests `/flow-init`.

Every change needs a traceable Spec/plan/ticket/changelog record, but artifacts scale with the change. Small work does not require a full ticket/plan/Spec; changelog is the fallback. See `/flow-todo` for the record rule.

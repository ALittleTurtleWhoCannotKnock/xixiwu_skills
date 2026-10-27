# Dev Flow Skills 使用手册

一套你自己的开发流程：初始化配置 → 提需求 → 拆需求 → 实施蓝图 → 拆 ticket → 实现，外加调试、清理、契约、会话导出等辅助技能。跨 Pi / Codex / Claude Code 通用。

> 本手册是叙事走查。每个技能的**权威定义**以对应的 `SKILL.md` 为准；执行型子 agent 的**执行逻辑**以 `_agents/*.prompt.md` 为准。

---

## 安装与更新

在独立目录中克隆或解压完整仓库，执行 `./install.sh all`，也可以把 `all` 换成 `pi`、`claude-code` 或 `codex`。用 `--dry-run` 预览安装项；Git 用户后续在原始仓库执行 `git pull --ff-only && ./install.sh all` 更新。安装位置、备份与旧副本迁移规则见 [README](./README.md#安装与更新)。

技能和共享 prompt 链接到同一份仓库，已有 agent 的模型及其他 frontmatter 配置保留。安装后，在自己的项目运行 `/init-dev-flow` 完成基础模型等配置；安装器不代替这一步。

## 一页总览

```
/init-dev-flow（每个仓库一次，定三项配置）
        ↓
/grill-with-docs → /to-spec → /to-plan → /to-tickets → /implement
     提需求          拆需求      实施蓝图      拆 ticket       实现
                          （人工审）                      │
                                                （涉及端点）→ /to-api-contract
```

辅助技能：`/amend`（已实现 spec 的变动）、`/diagnosing-bugs`（调试）、`/simplify`（提交前清理）、`/export-session`（导出会话）、`/to-api-contract`（接口契约）。

### 阶段速查

| 你的状态 | 执行命令 | 产出 |
|---------|---------|------|
| 新仓库首次接入 | `/init-dev-flow` | 三项配置（tracker / 提交策略 / 执行模式） |
| 需求在脑子里，怕 agent 理解错 | `/grill-with-docs` | 对齐后的需求 + CONTEXT.md |
| 需求已对齐，需要方案文档 | `/to-spec` | spec（含 seams 分析 + mermaid 图），存入 tracker |
| spec 已确认，需要确定技术路径 | `/to-plan` | 技术决策、包分解、改动锚点与验证策略，经用户批准 |
| plan 已批准，需要拆分执行 | `/to-tickets` | 带依赖关系的 ticket 列表；单票小改动可明确省略 plan |
| ticket 已确认，开始写代码 | `/implement` | 可运行代码 + 测试 |
| 已实现 spec 有变动 | `/amend` | spec-v(N+1) + 更新 INDEX + 新 ticket |
| 想查看当前进度 | `/find` | 只读进度快照：阶段、Status、阻塞、下一步 |
| 后端 ticket 涉及端点 | （由 /implement 触发）`/to-api-contract` | 接口契约片段 |
| 提交前 | （由 /implement 触发）`/simplify` | 清理后的代码 + 人工确认 |
| 遇到难调的 bug | `/diagnosing-bugs` | 修复 + 回归测试 |
| 要沉淀会话记录 | `/export-session` | session.md + session.jsonl |

---

## 阶段 0：初始化 — `/init-dev-flow`

**每个仓库运行一次。** Agent 会自动探测环境，确定三项配置，写入 `docs/agents/`。

### 三项配置

| 配置 | 文件 | 决策 | 怎么定 |
|------|------|------|--------|
| tracker 类型 | `issue-tracker.md` | GitHub / GitLab / 本地 `.scratch` | **探测**：git remote + gh/glab CLI + .scratch 是否已存在 |
| 提交策略 | `commit-strategy.md` | per-ticket / squash | **探测** git log + 向你确认 |
| 执行模式与基础模型 | `execution-mode.md` | subagent / inline；分派时使用的基础模型 | **询问**执行模式；subagent 模式列出实际可用模型，用户选择 ID 或 inherit |

### 执行

```
/init-dev-flow
```

Agent 探测后报告判定，例如：

```
探测结果：
- git remote: 无
- .scratch/: 不存在
- git log: 多为大提交（推测 squash）

判定：
- tracker: 本地模式（无 remote）
- 提交策略: squash？请确认
- 执行模式: 默认派子 agent 吗？（A 派 / B 主会话直接做）
```

选择分派后，Agent 根据当前工具的实际模型列表引导选择，或由你明确选择继承当前主会话（`inherit`），写入 `execution-mode.md` 的“基础模型”。模板不预填具体模型。Pi 生成 agent 时读取该项目配置；其他工具分派时按支持的格式应用，尚未实际调用的模型明确标注运行未验证。

### 产出

```
docs/agents/
├── issue-tracker.md    # tracker 类型（单一事实源）
├── commit-strategy.md  # 提交策略（simplify 触发时机）
└── execution-mode.md   # 执行模式 + 用户确认的基础模型
.scratch/README.md      # 本地模式才有
AGENTS.md               # 根目录指针（新开发者/agent 一眼可见）
```

**关键：** 三项都是"定默认，单次可覆盖"。比如 execution-mode 选了"派子 agent"，某张小 ticket 你说"别派了"，就临时改主会话做。

---

## 阶段 1：提需求 — `/grill-with-docs`

### 何时进入

- 有一个新功能/变更要做
- 需求还在脑子里或聊天记录里，没形成文档
- 担心 agent 理解有偏差

### 执行

```
/grill-with-docs
```

Agent 连续追问，每次回答后继续挖下一个分支，直到无歧义。

**示例对话：**

```
你：我要给博客加评论功能

Agent：几个问题：
1. 评论需要登录吗？
2. 支持嵌套回复吗？
3. 有敏感词过滤吗？
4. 评论排序方式？

你：需要登录，支持嵌套，要有敏感词过滤，按时间倒序

Agent：明确了。嵌套层级限制？
```

### 产出

- 无歧义的需求描述
- 更新根目录 `CONTEXT.md`（项目领域词典；不存在则创建）

**这是交互型技能，留在主会话** —— 它需要和你来回对话，不适合派子 agent。

---

## 阶段 2：拆需求 — `/to-spec`

### 何时进入

- 阶段 1 完成，需求无歧义
- 需要一份可评审、可追踪的方案文档

### 执行

```
/to-spec
```

Agent 先读 `docs/agents/issue-tracker.md` 判断 tracker 模式，然后：
1. **Seams 分析** — 确定测试边界，优先用最高层现有 seam，向你确认
2. 合成**四段式 spec**：问题陈述 / 非目标 / 方案概述（含功能流程图、seams 与关键决策）/ 模块影响文字清单；调用时序图继续说明跨参与者交互
3. 按 tracker 模式存放：
   - 本地 → `.scratch/<feature-slug>/spec.md`
   - GitHub/GitLab → 创建 issue

**这是交互型技能，留在主会话。**

### 产出

- spec（含功能流程图、约定的 test seams 和调用时序图），存入 tracker

---

## 阶段 2.5：实施蓝图 — `/to-plan`

spec 确认后，把技术决策、实现路径与风险在 plan 中确定，再拆执行票。

```
/to-plan
```

Agent 复用已有代码侦察结果。本地生成 `.scratch/<feature>/plan.md`；GitHub/GitLab 创建或更新独立 Plan issue，现行方案写在正文：

- 技术决策表：选项、选择与理由
- 包分解 P1..Pn：交付物、技术路径、复用点和风险
- 改动锚点：现有挂接点与目标态分别标明，说明由哪一阶段生成目标态
- 全局验证策略，以及方案的批准状态

现有挂接点在开工前核实；目标态在负责生成它的 ticket/前置包完成后检查。plan 由你 review 批准后进入拆票，已有会话授权直接沿用。plan 就地维护，方法名不复制进 ticket。

远程 Plan issue 正文用 `Spec:` 关联当前执行版，Spec 正文用 `Plan:` 反向引用；拆票后 Plan 列出关联 tickets。评论记录讨论和批准依据，open/closed 不代替批准状态。草案先保存为待 review，批准后更新同一正文，不把现行 plan 放进 Spec 评论或另存本地副本。

---

## 阶段 3：拆 ticket — `/to-tickets`

### 何时进入

- 阶段 2.5 完成，plan 已批准；或单票小改动已明确省略 plan
- 工作量超过一个会话容量

### 执行

```
/to-tickets
```

Agent 会：
1. **识别 prefactoring 机会** — 在写新功能前，先重构让变更更容易（"Make the change easy, then make the easy change"）
2. 按 plan 包拆成 **tracer-bullet 垂直切片**（每片端到端可独立验证）
3. 使用 `Spec:` / `Plan:` 分别引用 spec 版本和 plan 包，依赖统一写 `Blocked by:`
4. 向你确认粒度和依赖，然后按 tracker 模式存放：
   - 本地 → `.scratch/<feature-slug>/issues/<NN>-<slug>.md`（从 01 编号，blocker 在前，绝不合并成单文件）
   - GitHub/GitLab → 每张 ticket 一个 issue

远程票分别写 `Spec: <Spec 版本引用>`、`Plan: <独立 Plan issue> / P<N>`，创建后回填 Plan 的关联清单。本地文件引用格式继续使用 `plan.md#P<N>`。

**这是交互型技能，留在主会话。**

### 产出

```
.scratch/blog-comments/
├── spec.md
├── plan.md
└── issues/
    ├── 01-prefactor-extract-content.md
    ├── 02-comment-model-api.md
    └── 03-nested-replies.md
```

**单票小改动：** 可以写 `Plan: none (单票小改动)`，必要时也可写 `Spec: none (原因)`。必要技术决策、产品边界、测试 seam 与验收标准收在已确认的 ticket 中，下游不再要求读取被省略的文档。字段格式和状态语义统一见 [`_agents/workflow-contract.md`](./_agents/workflow-contract.md)。

---

## 阶段 4：实现 — `/implement`

这是最复杂、也最能体现"编排与执行分离"的阶段。

### 何时进入

- 阶段 3 完成，ticket 已确认
- 有可执行的 ticket（blocker 已解除）

### 执行

```
/implement
```

**主会话做编排，执行分派给子 agent（按 execution-mode）：**

```
主会话                              子 agent（execution-mode=subagent 时）
  │                                       │
  ├─ 1. 选 ticket（blocker 已解）          │
  │      （多版本 feature 先读 INDEX.md     │
  │        确定当前 spec 版本）             │
  ├─ 2. 确认验证方式与已有测试落点         │
  ├─ 3. 分派 ──────────────────────────→  implementer
  │                                       │  · 确认 blocker 已解
  │                                       │  · 复用测试，按改动类型实施与验证
  │                                       │  · 自 review（Standards+Spec+P0/P1/P2）
  │                                       │  · 返回结构化报告
  ├─ 3.5 方向修正（若 implementer 报        │
  │      direction error）                 │
  │      ├─ 对齐现有架构                   │
  │      ├─ 修正 ticket + 层级判断          │
  │      ├─ 理解纠偏 → 回写 spec            │
  │      └─ 重新分派（≥2 次则停，人工介入）  │
  ├─ 4. 核对报告 ←────────────────────────┘
  │      （验收标准全满足？测试通过？）
  │      ├─ 适用检查通过 → code-complete，更新依赖
  │      └─ 涉及端点 → 生成契约，供下一票联调
  ├─ 5. 提交节点（读 commit-strategy）
  │      ├─ 分派 simplify 清理
  │      ├─ 人工 checkpoint（你确认）
  │      └─ 提交
  └─ 6. 必需验收 + 收尾 checkpoint 完成 → resolved
```

**关键边界：**

- **子 agent 不提交、不跑 simplify** —— 这些是主会话在提交节点、经你人工确认后做的
- **子 agent 遇到未覆盖的决策会停止并报告**，不猜测、不扩大范围（决策已在 spec/ticket 阶段拍死）
- **子 agent 报"方向错误"（ticket 方案在现有架构不成立）会触发 Step 3.5**：主会话对齐架构 → 修正 ticket → 按层级判断是否回写 spec → 重新分派；同一 ticket 连续 ≥2 次方向错误则停，转人工
- **绝不主动提交**：即使全部检查通过，也先停在人工 checkpoint，经你确认才提交
- **提交与依赖分别处理**：每票自动验证通过即可记 `code-complete` 并继续下游；squash 不要求先提交上游票。待人工/真机验收项保留记录，最终验收与 checkpoint 完成后才 `resolved`
- **execution-mode=inline 时**，主会话参照 `_agents/implementer.prompt.md` 执行同样的实现与验证规则，不重启子进程

验证方式在执行前确定：业务行为与 bug 在已有测试中先复现再实现；纯重构跑前后回归；文档、配置和样式使用适用检查。同一测试边界的多个场景复用文件、fixtures 与参数化，不按票据另起测试文件。一次性探针放系统临时目录，有长期价值的回归覆盖仍保留；必要检查失败或未运行时不能报完成。

### 产出

- 可运行的代码（带测试）
- Review + simplify 通过、经你确认的提交
- 更新的 ticket 状态

---

## 辅助技能

### `/simplify` — 提交前清理

**主会话定 scope（读 commit-strategy），清理分派给 `simplifier` 子 agent。**

| 提交策略 | 触发点 | scope |
|---------|--------|-------|
| per-ticket | 每张 ticket 提交前 | 该 ticket 的 diff |
| squash | 统一提交前 | 累计 diff |

子 agent 按"复用/质量/效率"三维度审查并修复，**不提交**，返回报告。主会话展示报告，**暂停等你确认**后才提交。

### `/to-api-contract` — 接口契约

**后端 ticket 涉及对外端点时，由 `/implement` 触发（也可手动补生成）。**

主会话确认该 ticket 涉及的端点，分派 `contract-writer` 子 agent 从代码/测试提取契约，写入 `.scratch/<feature>/contracts/<ticket>.md`。每个字段必须溯源代码，不杜撰。前端 agent 据此联调。

### `/amend` — 已实现 spec 的需求变动

**已实现 spec 有变动时使用，不重走全流程。**

只 grill 变动部分 → 判断增量或重做 → 保存增量 Spec、更新当前版本引用 → 更新同一 plan 正文 → 续接 ticket。旧 Spec 冻结；本地用版本文件与 INDEX，远程沿用 tracker 的 Spec 版本约定并同步 Plan issue 的 `Spec:`，不新建 Plan issue。业务路径变化时更新功能流程图，模块影响保留文字说明。

### `/export-session` — 导出会话

**主会话识别工具、确认 issue 绑定，导出分派给 `exporter` 子 agent。**

支持 Claude Code / Codex / Pi（本地 JSONL）和 Cursor（SQLite）。产出双份到 `sessions/<项目>-<issue>-<日期>/`：`session.md`（可读）+ `session.jsonl`（原始存档）。纯格式转换，不总结。

### `/diagnosing-bugs` — 系统化调试

**交互型，留在主会话。** 六阶段纪律：构建反馈循环 → 复现+最小化 → 提出假设 → 插桩 → 修复+回归测试 → 清理。强调"先建 red-capable 循环，再谈修复"。

---

## 端到端走查：博客评论功能

```
Day 1 上午        Day 1 下午       Day 2 上午      Day 2 下午        Day 3 上午
    │                 │                │                │                │
    ▼                 ▼                ▼                ▼                ▼
/init-dev-flow   /grill-with-docs  /to-spec         /to-plan        /to-tickets
    │                 │                │                │                │
    ▼                 ▼                ▼                ▼                ▼
三项配置：        对齐需求：        spec：           plan.md：        tickets：
- tracker: 本地   - 需登录          - 四段式          - 技术决策表      - 01 prefactor
- 提交: squash    - 嵌套3层         - seams: HTTP API - 包分解 P1..Pn  - 02 模型+API
- 执行: 派子 agent - 敏感词过滤      - 存 .scratch/    - 风险点         - 03 嵌套回复
                  更新 CONTEXT.md    .../spec.md    （人工审 ← 卡点）  （含依赖+来源P）

Day 4 全天
    │
    ▼
/implement（逐 ticket）
    │
    ├─ ticket 01: 红绿重构 → 核对 → code-complete，解除 02 的 ticket 依赖
    │     （squash 策略，暂不提交，最终验收项仍保留）
    ├─ ticket 02: 同上；涉及端点则立即生成契约
    ├─ ticket 03: 同上；使用前票的代码与契约
    │
    ▼ 执行票均 code-complete/resolved，进入统一收尾节点
  分派 simplify（scope=累计 diff）→ 修复报告
    │
    ▼ 人工 checkpoint：你确认
  必需验收通过 → resolved；经明确授权统一提交
  若选择暂不提交，记录选择并保留工作区；待验收项不标 resolved
```

### 产出文件树

```
project/
├── AGENTS.md                              # 阶段 0 指针
├── CONTEXT.md                             # 阶段 1 更新
├── docs/
│   └── agents/
│       ├── issue-tracker.md               # 阶段 0
│       ├── commit-strategy.md             # 阶段 0
│       └── execution-mode.md              # 阶段 0
├── .scratch/
│   └── blog-comments/
│       ├── spec.md                        # 阶段 2
│       ├── plan.md                        # 阶段 2.5（技术蓝图，经人工审）
│       ├── issues/                        # 阶段 3
│       │   ├── 01-prefactor-extract-content.md
│       │   ├── 02-comment-model-api.md
│       │   └── 03-nested-replies.md
│       └── contracts/                     # /to-api-contract
│           ├── 02-comment-model-api.md
│           └── 03-nested-replies.md
└── src/                                   # 阶段 4 实现
```

---

## 关键约束

| 约束 | 说明 |
|------|------|
| 先初始化 | 没有 `docs/agents/*.md`，to-spec/to-tickets/implement 会提示先跑 `/init-dev-flow` |
| 阶段顺序 | 常规 feature：grill → spec → plan（批准）→ tickets → implement；小改动按共享约定明确省略 |
| 产出物即输入 | spec → plan → tickets → 代码；简化票包含被省略文档中的必要决策 |
| 决策前置 | 产品边界在 spec，技术方案在 plan，执行验收在 ticket；省略文档时决策收在 ticket |
| 状态与提交 | 每票验证后更新 code-complete 与依赖；最终验收和 checkpoint 完成才 resolved，不由 squash 提交时点决定 |
| 子 agent 边界 | 不提交、不跑 simplify、遇未授权决策停止并报告、报方向错误触发 Step 3.5 |
| 绝不主动提交 | 任何阶段、任何 agent，未经你明确指示都把改动留在工作区 |
| 配置可覆盖 | 三项配置都是默认值，单次执行可临时改 |
| 交互型留主会话 | grill/diagnosing/spec/plan/tickets 需要和你对话，不派子 agent |

---

## 权威来源

- 技能定义：各 `<skill>/SKILL.md`
- 执行逻辑：`_agents/*.prompt.md`
- 共享字段与状态语义：`_agents/workflow-contract.md`，目标仓库的状态值域以 tracker 声明为准
- 跨工具适配：`adapters/build.sh`（生成 agent 文件到各工具）

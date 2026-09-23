# Dev Flow Skills 使用手册

一套你自己的开发流程：初始化配置 → 提需求 → 拆需求 → 实施蓝图 → 拆 ticket → 实现，外加调试、清理、契约、会话导出等辅助技能。跨 Pi / Codex / Claude Code 通用。

> 本手册是叙事走查。每个技能的**权威定义**以对应的 `SKILL.md` 为准；执行型子 agent 的**执行逻辑**以 `_agents/*.prompt.md` 为准。

---

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
| spec 已确认，需要拆分执行 | `/to-tickets` | 带依赖关系的 ticket 列表 |
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
| 执行模式 | `execution-mode.md` | subagent / inline | **询问**（无可靠探测方式） |

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

### 产出

```
docs/agents/
├── issue-tracker.md    # tracker 类型（单一事实源）
├── commit-strategy.md  # 提交策略（simplify 触发时机）
└── execution-mode.md   # 执行模式（是否默认派子 agent）
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
2. 合成**四段式 spec**：问题陈述 / 非目标 / 方案概述（含 seams 与关键决策）/ 模块影响
3. 按 tracker 模式存放：
   - 本地 → `.scratch/<feature-slug>/spec.md`
   - GitHub/GitLab → 创建 issue

**这是交互型技能，留在主会话。**

### 产出

- spec（含约定的 test seams），存入 tracker

---

## 阶段 3：拆 ticket — `/to-tickets`

### 何时进入

- 阶段 2 完成，spec 已确认
- 工作量超过一个会话容量

### 执行

```
/to-tickets
```

Agent 会：
1. **识别 prefactoring 机会** — 在写新功能前，先重构让变更更容易（"Make the change easy, then make the easy change"）
2. 拆成 **tracer-bullet 垂直切片**（每片端到端可独立验证，含 schema/API/UI/测试）
3. 声明 **blocking 依赖**
4. 向你确认粒度和依赖，然后按 tracker 模式存放：
   - 本地 → `.scratch/<feature-slug>/issues/<NN>-<slug>.md`（从 01 编号，blocker 在前，绝不合并成单文件）
   - GitHub/GitLab → 每张 ticket 一个 issue

**这是交互型技能，留在主会话。**

### 产出

```
.scratch/blog-comments/
├── spec.md
└── issues/
    ├── 01-prefactor-extract-content.md
    ├── 02-comment-model-api.md
    └── 03-nested-replies.md
```

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
  ├─ 2. 确认测试 seam（读 spec）           │
  ├─ 3. 分派 ──────────────────────────→  implementer
  │                                       │  · 确认 blocker 已解
  │                                       │  · 在约定 seam 红-绿-重构
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
  ├─ 5. 提交节点（读 commit-strategy）
  │      ├─ 分派 simplify 清理
  │      ├─ 人工 checkpoint（你确认）
  │      └─ 提交
  └─ 6. 涉及端点？→ 分派 contract-writer 产出契约
```

**关键边界：**

- **子 agent 不提交、不跑 simplify** —— 这些是主会话在提交节点、经你人工确认后做的
- **子 agent 遇到未覆盖的决策会停止并报告**，不猜测、不扩大范围（决策已在 spec/ticket 阶段拍死）
- **子 agent 报"方向错误"（ticket 方案在现有架构不成立）会触发 Step 3.5**：主会话对齐架构 → 修正 ticket → 按层级判断是否回写 spec → 重新分派；同一 ticket 连续 ≥2 次方向错误则停，转人工
- **绝不主动提交**：即使全部检查通过，也先停在人工 checkpoint，经你确认才提交
- **execution-mode=inline 时**，主会话参照 `_agents/implementer.prompt.md` 直接执行同样的 TDD 逻辑，不重启子进程

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

只 grill 变动部分 → 深度判断（表层/局部增量 vs 核心重做）→ 生成 `spec-v(N+1).md`（只记变动点）→ 更新 `INDEX.md` 版本指针 → 续接 ticket。旧 spec 冻结，agent 实现一律先读 INDEX 确定当前版本。

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
    ├─ ticket 01: 分派 implementer → 红绿重构 → 报告 → 核对
    │     （squash 策略，暂不提交）
    ├─ ticket 02: 同上
    ├─ ticket 03: 同上
    │
    ▼ 全部 ticket 完成，进入统一提交节点
  分派 simplify（scope=累计 diff）→ 修复报告
    │
    ▼ 人工 checkpoint：你确认
  统一提交
    │
    ▼ ticket 02/03 涉及端点
  分派 contract-writer → .scratch/blog-comments/contracts/*.md
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
| 阶段顺序 | grill → spec → tickets → implement，不能跳 |
| 产出物即输入 | 上一阶段产出是下一阶段输入（spec → tickets → 代码） |
| 决策前置 | 所有决策在 spec/ticket 阶段拍死，implement 阶段不做新决策 |
| 子 agent 边界 | 不提交、不跑 simplify、遇未授权决策停止并报告、报方向错误触发 Step 3.5 |
| 绝不主动提交 | 任何阶段、任何 agent，未经你明确指示都把改动留在工作区 |
| 配置可覆盖 | 三项配置都是默认值，单次执行可临时改 |
| 交互型留主会话 | grill/diagnosing/spec/tickets 需要和你对话，不派子 agent |

---

## 权威来源

- 技能定义：各 `<skill>/SKILL.md`
- 执行逻辑：`_agents/*.prompt.md`
- 跨工具适配：`adapters/build.sh`（生成 agent 文件到各工具）

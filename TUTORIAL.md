# Dev Flow Skills 使用手册

一套你自己的开发流程：流程初始化 → 需求澄清 → 规格定义 → 方案规划 → 任务拆分 → 实现与验证，外加调试、清理、契约、会话导出等辅助技能。跨 Pi / Codex / Claude Code 通用。

> 本手册是叙事走查。每个技能的**权威定义**以对应的 `SKILL.md` 为准；执行型子 agent 的**执行逻辑**以 `_agents/*.prompt.md` 为准。

---

## 安装与更新

在独立目录中克隆或解压完整仓库，执行 `./install.sh all`，也可以把 `all` 换成 `pi`、`claude-code` 或 `codex`。用 `--dry-run` 预览安装项；Git 用户后续在原始仓库执行 `git pull --ff-only && ./install.sh all` 更新。安装位置、备份与旧副本迁移规则见 [README](./README.md#安装与更新)。

技能和共享 prompt 链接到同一份仓库，已有 agent 的模型及其他 frontmatter 配置保留。安装后，在自己的项目运行 `/flow-init` 完成基础模型等配置；安装器不代替这一步。

## 一页总览

```
/flow-init       流程初始化（缺项可单独补齐）
    ↓
/flow-clarify    需求澄清
    ↓
/flow-spec       规格定义
    ↓
/flow-plan       方案规划（人工审）
    ↓
/flow-todo       任务拆分
    ↓
/flow-do         实现与验证
    └─ 涉及后端端点 → /flow-api（接口契约提取）
```

辅助技能：`/flow-amend`（已实现 spec 的变动）、`/flow-debug`（调试）、`/flow-simplify`（提交前清理）、`/flow-export`（导出会话）、`/flow-api`（接口契约）。

### 阶段速查

| 你的状态 | 执行命令 | 产出 |
|---------|---------|------|
| 希望 Bot 自动推进整个功能 | `/flow-run` | Spec 确认后自动推进到工程交付；中断可续跑 |
| 新仓库首次接入或补语言 | `/flow-init` | 四项配置（tracker / 提交策略 / 执行模式与模型 / 语言） |
| 需求在脑子里，怕 agent 理解错 | `/flow-clarify` | 对齐后的需求 + CONTEXT.md |
| 需求已对齐，需要方案文档 | `/flow-spec` | spec（含 seams 分析 + mermaid 图），存入 tracker |
| spec 已确认，需要确定技术路径 | `/flow-plan` | 技术决策、包分解、改动锚点与验证策略，经用户批准 |
| plan 已批准，需要拆分执行 | `/flow-todo` | 带依赖关系的待办列表；单票小改动可明确省略 plan |
| 待办已确认，开始写代码 | `/flow-do` | 可运行代码 + 测试 |
| Do 完成，想本地启动后实际测一轮 | `/flow-e2e` | 浏览器操作与通过／失败／未测结果；默认不新增测试文件 |
| 已实现 spec 有变动 | `/flow-amend` | spec-v(N+1) + 更新 INDEX + 新待办 |
| 想查看当前进度 | `/flow-status` | 只读进度快照：阶段、Status、阻塞、下一步 |
| 后端待办涉及端点 | （由 /flow-do 触发）`/flow-api` | 接口契约片段 |
| 提交前 | （由 /flow-do 触发）`/flow-simplify` | 清理后的代码 + 人工确认 |
| 遇到难调的 bug | `/flow-debug` | 修复 + 回归测试 |
| 要沉淀会话记录 | `/flow-export` | session.md + session.jsonl |

---

## 阶段 0：流程初始化 — `/flow-init`

**每个仓库首次运行，缺项可单独补齐。** Agent 自动探测 tracker，并确认提交、执行和语言偏好，写入 `docs/agents/`。

### 四项配置

| 配置 | 文件 | 决策 | 怎么定 |
|------|------|------|--------|
| tracker 类型 | `issue-tracker.md` | GitHub / GitLab / 本地 `.scratch` | **探测**：git remote + gh/glab CLI + .scratch 是否已存在 |
| 提交策略 | `commit-strategy.md` | per-ticket / squash | **探测** git log + 向你确认 |
| 执行模式与基础模型 | `execution-mode.md` | subagent / inline；分派时使用的基础模型 | **询问**执行模式；subagent 模式列出实际可用模型，用户选择 ID 或 inherit |
| 交互与业务产物语言 | `language.md` | 两项独立选择，可同可不同 | **确认**当前候选语言；已有明确选择直接沿用，不保存猜测值 |

### 执行

```
/flow-init
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
- 语言: 交互和业务产物分别用什么语言？例如中文交流、英文文档（请确认）
```

选择分派后，Agent 根据当前工具的实际模型列表引导选择，或由你明确选择继承当前主会话（`inherit`），写入 `execution-mode.md` 的“基础模型”。模板不预填具体模型。Pi 生成 agent 时读取该项目配置；其他工具分派时按支持的格式应用，尚未实际调用的模型明确标注运行未验证。

语言在生成后续文档前确认并保存，配置使用固定键 `interaction_language` 和 `artifact_language`，值由使用者选择。选择中文交互、英文产物后，追问、review 摘要和 `/flow-status` 说明用中文，Spec/Plan/Todo 的可读内容用英文；协议字段和状态值不翻译。临时指定某一项只影响当前任务；原始会话导出不因产物语言而翻译原文。

### 产出

```
docs/agents/
├── issue-tracker.md    # tracker 类型（单一事实源）
├── commit-strategy.md  # 提交策略（/flow-simplify 触发时机）
├── execution-mode.md   # 执行模式 + 用户确认的基础模型
└── language.md         # 用户确认的交互语言 + 业务产物语言
.scratch/README.md      # 本地模式才有
AGENTS.md               # 根目录指针（新开发者/agent 一眼可见）
```

**关键：** 偏好都是“定默认，单次可覆盖”。比如 execution-mode 选了“派子 agent”，某张小待办说“别派了”，就临时改主会话做；指定“这轮 Plan 用中文”也不把项目的英文产物默认改掉。旧项目只补语言时不重选模型或其他设置，不自动重译既有文档。

---

## 阶段 1：需求澄清 — `/flow-clarify`

### 何时进入

- 有一个新功能/变更要做
- 需求还在脑子里或聊天记录里，没形成文档
- 担心 agent 理解有偏差

### 执行

```
/flow-clarify
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

## 阶段 2：规格定义 — `/flow-spec`

### 何时进入

- 阶段 1 完成，需求无歧义
- 需要一份可评审、可追踪的方案文档

### 执行

```
/flow-spec
```

执行前先确认：“本次是否额外生成 HTML 规格阅读版？需要 / 不需要”。如果这次请求已经说明选择，就不重复询问；未回答时不保存推测值，也不先生成 HTML。该选择仅作用于本次，不写入项目或全局默认。

选择后，Agent 读取 `docs/agents/issue-tracker.md` 判断 tracker 模式，然后：
1. **Seams 分析** — 确定测试边界，优先用最高层现有 seam，向你确认
2. 合成**四段式 spec**：问题陈述 / 非目标 / 方案概述（含功能流程图、seams 与关键决策）/ 模块影响文字清单；调用时序图继续说明跨参与者交互
3. 按 tracker 模式存放：
   - 本地 → `.scratch/<feature-slug>/spec.md`
   - GitHub/GitLab → 创建 issue

已有 Epic 时把 Spec 归属该总单，否则 Spec 为功能入口。本地从这一步维护 `INDEX.md` 和 `.scratch/README.md` 的导航；GitHub 使用原生父子关系与类型标签。

选择需要 HTML 时，再从已保存的规格生成阅读版。本地通常为同目录下的 `spec.html`，版本规格对应 `spec-v2.html` 等；保留四段内容、来源、版本、生成时间与现有语言设置，技术细节可折叠。未选择时不加载 HTML 模板，也不增加阅读文件或入口。

远程模式的完整规格仍在 Spec issue，本地 HTML 只作阅读快照。已有授权发布渠道且验证了地址时，Issue 才增加在线入口；否则给出本地文件，不把本机路径冒充共享链接，也不为了阅读版自动提交、开启 Pages 或部署。旧阅读版若未随规格更新，会标记为过期或从当前入口移出，历史文件保留。

**这是交互型技能，留在主会话。**

### 产出

- spec（含功能流程图、约定的 test seams 和调用时序图），存入 tracker
- 本次明确需要时，额外生成 HTML 规格阅读版并报告实际验证结果；打开页面不代表规格已获批准

---

## 阶段 2.5：方案规划 — `/flow-plan`

spec 确认后，把技术决策、实现路径与风险在 plan 中确定，再拆执行票。

```
/flow-plan
```

Agent 复用代码上下文，先判断 Spec 需要一个还是多个独立 Plan；用户指定数量／分组优先。每个 Plan 能从既有基线独立实现／验证，再拆简单工程 Todo。不能用前端／后端／测试阶段或 P1/P2 包编号冒充独立 Plan；数量与独立性冲突时说明后询问。本例展示单 Plan 的兼容路径 `.scratch/<feature>/plan.md`；多范围新文件用 `plans/<scope>.md`，远程每范围一个 Plan issue，方案保存在各自正文：

- 技术决策表：选项、选择与理由
- 包分解 P1..Pn：交付物、技术路径、复用点和风险
- 改动锚点：现有挂接点与目标态分别标明，说明由哪一阶段生成目标态
- 全局验证策略，以及方案的批准状态

现有挂接点在开工前核实；目标态在负责生成它的待办/前置包完成后检查。plan 由你 review 批准后进入拆票，已有会话授权直接沿用。plan 就地维护，方法名不复制进待办。

每个 Plan 用 Spec:／Scope: 关联适用版本与负责范围，Spec 用 Plans: 列完整实际引用，旧单 Plan: 兼容。拆票后各 Plan 只列自己的 Todo，批准与范围内验收分别记录；评论不是现行方案主存，open/closed 不是批准。每个范围复用同一正文，不另存远程方案的本地副本。

Plan 的 `Parent:` 指向 Spec：本地更新同一 INDEX 的方案链接，GitHub 建立原生子 issue 并核对。tracker 已指定 Project 时加入同一个 Project，可用 View → Show hierarchy 查看层级；没有 Project 仍可继续普通 Issues 流程。

Plan 用独立的 `Acceptance: pending / accepted / changes-requested` 记录人工功能验收，方案的“已批准”不代表验收通过。工程票自动完成后，上层仍可 pending；只有用户实际确认功能验收通过才记录 accepted。没有 Plan 时由 Spec 承担同一职责，不维护两份状态。

---

## 阶段 3：任务拆分 — `/flow-todo`

### 何时进入

- 阶段 2.5 完成，plan 已批准；或单票小改动已明确省略 plan
- 工作量超过一个会话容量

### 执行

```
/flow-todo
```

Agent 会：
1. **识别 prefactoring 机会** — 在写新功能前，先重构让变更更容易（"Make the change easy, then make the easy change"）
2. 按 plan 包拆成 **tracer-bullet 垂直切片**（每片端到端可独立验证）
3. 使用 `Parent:` 记录直接归属、`Spec:` / `Plan:` 分别引用 spec 版本和 plan 包，依赖统一写 `Blocked by:`
4. 向你确认粒度和依赖，然后按 tracker 模式存放：
   - 本地 → `.scratch/<feature-slug>/issues/<NN>-<slug>.md`（从 01 编号，blocker 在前，绝不合并成单文件）
   - GitHub/GitLab → 每张待办一个 issue

远程票分别写 `Spec: <Spec 版本引用>`、`Plan: <独立 Plan issue> / P<N>`，创建后回填 Plan 的关联清单。本地文件引用格式继续使用 `plan.md#P<N>`。

新待办的标题前缀为 `[Todo]`，GitHub 类型标签默认为 `todo`；本地标题、Plan 清单、INDEX 与 `/flow-status` 分组同步使用 Todo/待办。旧 `[Ticket]` / `ticket` 作为历史别名继续查询和复用，重复拆分不因名称不同再建一份。

待办的父级是 Plan，不是 blocker 或被续接的旧待办。本地把实际文件链接补入 INDEX；GitHub 同步原生子 issue、类型标签及已配置的 Project。工具不支持、权限不足或父级冲突会报告未同步项，不通过重建 issue 绕过。

**这是交互型技能，留在主会话。**

### 产出

```
.scratch/blog-comments/
├── INDEX.md                 # 当前规格、Plan 与待办层级导航
├── spec.md
├── plan.md
└── issues/
    ├── 01-prefactor-extract-content.md
    ├── 02-comment-model-api.md
    └── 03-nested-replies.md
```

**单票小改动：** 可以写 `Plan: none (单票小改动)`，必要时也可写 `Spec: none (原因)`。必要技术决策、产品边界、测试 seam 与验收标准收在已确认的待办中，下游不再要求读取被省略的文档。字段格式和状态语义统一见 [`_agents/workflow-contract.md`](./_agents/workflow-contract.md)。

---

## 阶段 4：实现与验证 — `/flow-do`

这是最复杂、也最能体现"编排与执行分离"的阶段。

### 何时进入

- 阶段 3 完成，待办已确认
- 有可执行的待办（blocker 已解除）

### 执行

```
/flow-do
```

**主会话做编排，执行分派给子 agent（按 execution-mode）：**

```
主会话                              子 agent（execution-mode=subagent 时）
  │                                       │
  ├─ 1. 选待办（blocker 已解）          │
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
  │      ├─ 修正待办 + 层级判断          │
  │      ├─ 理解纠偏 → 回写 spec            │
  │      └─ 重新分派（≥2 次则停，人工介入）  │
  ├─ 4. 核对报告 ←────────────────────────┘
  │      （验收标准全满足？测试通过？）
  │      ├─ 涉及端点 → 生成本票必需契约
  │      ├─ 工程检查与 review 通过 → resolved / 自动关票，更新依赖
  │      └─ 人工功能验收项 → Plan（无 Plan 时 Spec）
  ├─ 5. 提交节点（读 commit-strategy）
  │      ├─ 分派 /flow-simplify 清理
  │      ├─ 人工 checkpoint（你确认）
  │      └─ 提交
  └─ 6. Plan/Spec 功能验收：用户实际确认后记录 accepted 并关闭验收单
```

**关键边界：**

- **子 agent 不提交、不跑 /flow-simplify** —— 这些是主会话在提交节点、经你人工确认后做的
- **子 agent 遇到未覆盖的决策会停止并报告**，不猜测、不扩大范围（决策已在 spec/待办阶段拍死）
- **子 agent 报"方向错误"（待办方案在现有架构不成立）会触发 Step 3.5**：主会话对齐架构 → 修正待办 → 按层级判断是否回写 spec → 重新分派；同一待办连续 ≥2 次方向错误则停，转人工
- **绝不主动提交**：即使全部检查通过，也先停在人工 checkpoint，经你确认才提交
- **票级完成、功能验收与提交分别处理**：每票实现、必要工程检查和 review 通过即 `resolved` / 自动关闭并继续下游；squash 不要求先提交上游票。人工功能验收集中到 Plan/Spec 的 Acceptance，未提交或未人工验收不拖住合格工程票
- **execution-mode=inline 时**，主会话参照 `_agents/implementer.prompt.md` 执行同样的实现与验证规则，不重启子进程

验证方式在执行前确定：业务行为与 bug 在已有测试中先复现再实现；纯重构跑前后回归；文档、配置和样式使用适用检查。同一测试边界的多个场景复用文件、fixtures 与参数化，不按票据另起测试文件。一次性探针放系统临时目录，有长期价值的回归覆盖仍保留；必要检查失败或未运行时不能报完成。

### 产出

- 可运行的代码（带测试）
- Review + /flow-simplify 通过、经你确认的提交
- 更新的待办状态

---

## 辅助技能

### `/flow-run` — Bot／主 agent 总编排

```text
/flow-run 实现订单筛选与导出。Spec 跟我确认，后续方案和拆分由你决定，继续完成开发和验测。
```

主 agent 读取已有配置、当前产物和新消息，从第一个未完成阶段继续。需求有实质歧义时追问；Spec 保存后给你确认。确认后自动评审技术 Plan、拆分与复用 Todo、按依赖执行 Do，Web 功能完成后调用 `/flow-e2e` 实际验测。工程票仍按规则自动关闭，Plan/Spec 的人工功能验收保持独立；提交、推送或部署需要对应授权。

采用专职 Agent 时，由流程 Agent 统一与你沟通，按[通用角色协作协议](./flow-run/references/team-mode.md)派发：需求 Agent 执行 Clarify＋Spec，方案 Agent 执行 Plan＋Todo，开发 Agent 执行 Do／Debug／API，测试 Agent 执行适用验测。执行者只向流程 Agent 返回产物、问题和证据，不直接联系用户或通知下一位；流程 Agent 转达你的完整答复、核对当前项目与版本后再推进。具体工具名由宿主映射，不写入各阶段技能。

默认在此次 `/flow-spec` 调用中明确选择不额外生成 HTML；需要时在请求中说明。测试边界并入 Spec 的确认，技术方案和待办拆分记录为“授权自动规划”，不伪装成人工审核。涉及已确认产品范围的变更会回到 Spec 再确认；必要检查失败不能跳过。

本地 `.scratch/<feature>/run.md` 只保存来源引用、上次动作与证据、待回答的问题、失败尝试和新消息位置；实际进度仍从 Spec/Plan/Todo 读取。远程模式下该文件仅为可重建的协调缓存，不增加本地主文档。Bot 宿主需要在用户回复或续跑时重新唤起 agent 并提供完整消息；skill 本身不会常驻。可直接采用[Bot 接入说明中的运行策略](./flow-run/references/bot-setup.md)。

使用 PI Desktop 的 [PI-Bot](https://github.com/vsd269/PI-Bot) 时，参考[专用接入说明](./flow-run/references/pi-bot.md)：先选具备执行能力的 Bot，由其读取固定目录中的完整技能源码；Spec 用 `ask_user` 卡片确认，回答作为新任务继续。它的 Skill 导入会拆成独立资源目录，不能直接照搬本仓库跨目录引用，也不能把宿主任务 `completed` 当作工程通过。现有 `install.sh pi` 面向 Pi CLI，不负责 PI-Bot 插件配置。

### `/flow-e2e` — 本地浏览器验测

Do 完成后可以直接说：

```text
/flow-e2e 你可以先本地启动测试一轮
```

Agent 从最近的 Do、Todo 和 Plan/Spec 提取本轮测试范围，启动或复用本地服务，实际操作刚完成的功能，检查主流程及相关异常场景，并报告真实结果、问题复现步骤和未测项。已有范围不重复追问；只有目标、登录信息或必要环境无法确定时才补问。启动前核对实际后端与数据目标，遵守项目已有的读写限制。

默认使用当前可用的浏览器工具或项目已有测试 runner，不要求先搭建 E2E 框架，也不默认添加长期测试文件。打开页面不等于功能通过，验测结果也不代替用户在 Plan/Spec 的功能验收。需要长期回归覆盖时，明确说“为这个流程补充可保留的 E2E 测试”，再按[回归用例指引](./flow-e2e/references/maintained-tests.md)复用或补充测试，并实际运行。

### `/flow-simplify` — 代码清理

**主会话定 scope（读 commit-strategy），清理分派给 `simplifier` 子 agent。**

| 提交策略 | 触发点 | scope |
|---------|--------|-------|
| per-ticket | 每张待办提交前 | 该待办的 diff |
| squash | 统一提交前 | 累计 diff |

子 agent 按"复用/质量/效率"三维度审查并修复，**不提交**，返回报告。主会话展示报告，**暂停等你确认**后才提交。

### `/flow-api` — 接口契约提取

**后端待办涉及对外端点时，由 `/flow-do` 触发（也可手动补生成）。**

主会话确认该待办涉及的端点，分派 `contract-writer` 子 agent 从代码/测试提取契约，写入 `.scratch/<feature>/contracts/<ticket>.md`。每个字段必须溯源代码，不杜撰。前端 agent 据此联调。

### `/flow-amend` — 需求变更

**已实现 spec 有变动时使用，不重走全流程。**

只澄清变动部分 → 判断受影响范围的增量或重做 → 保存 Spec 版本及当前 Plan 注册引用 → 就地更新受影响的方案 → 续接其简单 Todo。未受影响 Plan 的实现、批准、验收和历史票保留，核对明确的沿用依据；新独立范围可新增 Plan，不以新版本名复制已有范围。业务流程与模块影响只改实际变化部分。

需要同步 Parent／Spec 导航时按同 feature、新鲜读取和实际授权处理，不因引用更新重置其他范围。旧票保留原版本和状态；INDEX／Spec 列全体适用 Plan 及各自 Todos。flow-status 逐 Plan 只读显示工程、关闭同步与验收，再汇总整个 Spec，不能从一个 Plan 的状态推断全体。

### `/flow-export` — 会话导出

**主会话识别工具、确认 issue 绑定，导出分派给 `exporter` 子 agent。**

支持 Claude Code / Codex / Pi（本地 JSONL）和 Cursor（SQLite）。产出双份到 `sessions/<项目>-<issue>-<日期>/`：`session.md`（可读）+ `session.jsonl`（原始存档）。纯格式转换，不总结。

### `/flow-debug` — 问题诊断

**交互型，留在主会话。** 六阶段纪律：构建反馈循环 → 复现+最小化 → 提出假设 → 插桩 → 修复+回归测试 → 清理。强调"先建 red-capable 循环，再谈修复"。

---

## 端到端走查：博客评论功能

```
Day 1 上午            Day 1 下午            Day 2 上午            Day 2 下午            Day 3 上午
    │                     │                     │                     │                     │
    ▼                     ▼                     ▼                     ▼                     ▼
/flow-init            /flow-clarify         /flow-spec            /flow-plan            /flow-todo
    │                     │                     │                     │                     │
    ▼                     ▼                     ▼                     ▼                     ▼
四项配置：            需求澄清：            规格定义：            方案规划：            任务拆分：
- tracker: 本地       - 需登录              - 四段式              - 技术决策表          - 01 prefactor
- 提交: squash        - 嵌套3层             - seams: HTTP API     - 包分解 P1..Pn       - 02 模型+API
- 执行: 派子 agent    - 敏感词过滤          - 存 .scratch/        - 风险点              - 03 嵌套回复
                      更新 CONTEXT.md         .../spec.md         （人工审 ← 卡点）     （含依赖+来源P）

Day 4 全天
    │
    ▼
/flow-do（逐待办）
    │
    ├─ 待办 01: 红绿重构 → 工程核对与 review → resolved / 自动关票，解除 02 依赖
    │     （squash 策略，暂不提交，人工功能验收项留在 Plan）
    ├─ 待办 02: 同上；涉及端点则立即生成契约
    ├─ 待办 03: 同上；使用前票的代码与契约
    │
    ▼ 执行票均 resolved；功能显示“开发完成，待功能验收”
  分派 /flow-simplify（scope=累计 diff）→ 修复报告
    │
    ▼ 人工 checkpoint：你确认
  经明确授权统一提交；暂不提交时保留工作区，票级状态不回退
    │
    ▼ 在 Plan（无 Plan 时 Spec）集中做功能验收
  用户确认后 Acceptance: accepted，关闭相应验收单；票全关不代表验收通过
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
│       ├── execution-mode.md              # 阶段 0
│       └── language.md                    # 交互与业务产物语言
├── .scratch/
│   └── blog-comments/
│       ├── spec.md                        # 阶段 2
│       ├── plan.md                        # 阶段 2.5（技术蓝图，经人工审）
│       ├── issues/                        # 阶段 3
│       │   ├── 01-prefactor-extract-content.md
│       │   ├── 02-comment-model-api.md
│       │   └── 03-nested-replies.md
│       └── contracts/                     # /flow-api
│           ├── 02-comment-model-api.md
│           └── 03-nested-replies.md
└── src/                                   # 阶段 4 实现
```

---

## 关键约束

| 约束 | 说明 |
|------|------|
| 先初始化 | 没有 `docs/agents/*.md`，flow-spec/flow-todo/flow-do 会提示先跑 `/flow-init` |
| 阶段顺序 | 常规 feature：clarify → spec → plan（批准）→ todo → do；小改动按共享约定明确省略 |
| 产出物即输入 | spec → plan → 待办 → 代码；简化票包含被省略文档中的必要决策 |
| 决策前置 | 产品边界在 spec，技术方案在 plan，票级工程条件在待办；人工功能验收集中到 Plan/Spec |
| 状态与提交 | 本票工程工作通过即 resolved/自动关闭；功能 Acceptance 与提交授权分别记录，均不阻止票级完成 |
| 子 agent 边界 | 不提交、不跑 /flow-simplify、遇未授权决策停止并报告、报方向错误触发 Step 3.5 |
| 绝不主动提交 | 任何阶段、任何 agent，未经你明确指示都把改动留在工作区 |
| 配置可覆盖 | 四项配置按项目保存，单次明确要求可临时覆盖对应项 |
| 交互型留主会话 | flow-clarify/flow-debug/flow-spec/flow-plan/flow-todo 需要和你对话，不派子 agent |

---

## 权威来源

- 技能定义：各 `<skill>/SKILL.md`
- 执行逻辑：`_agents/*.prompt.md`
- 共享字段与状态语义：`_agents/workflow-contract.md`，目标仓库的状态值域以 tracker 声明为准
- 跨工具适配：`adapters/build.sh`（生成 agent 文件到各工具）

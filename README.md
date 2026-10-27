# Dev Flow Skills

五阶段开发流程 + 调试技能，跨 Pi / Codex / Claude Code 通用。

> **全局纪律：绝不主动提交或推送代码。** 未经用户明确指示（"提交"/"推送"），任何阶段、任何 agent（主会话或子 agent）都把改动留在工作区。提交永远经过用户确认（人工 checkpoint）。

## 安装与更新

需要 Bash 和 Python 3.9+。将仓库放在长期保留的独立目录中，再选择目标 CLI：

```bash
git clone https://github.com/ALittleTurtleWhoCannotKnock/xixiwu_skills.git
cd xixiwu_skills
./install.sh all

# 也可以只安装一个 CLI
./install.sh pi
./install.sh claude-code
./install.sh codex

# 先预览；不会修改安装目录
./install.sh all --dry-run
```

同一个入口用于首次安装和后续更新。更新时，在原始仓库目录中执行：

```bash
git pull --ff-only && ./install.sh all
```

安装器把各技能和 `_agents/` 链接到这份仓库；Pi / Claude Code 的 agent 文件由适配器生成。保留仓库的位置，以免软链接失效；源仓库放在技能扫描目录里时，先移到独立目录。

| 目标 | 技能与共享文件 | 生成的 agent |
|------|----------------|--------------|
| `pi` | `~/.pi/agent/skills/` | `~/.pi/agent/agents/` |
| `claude-code` | `~/.claude/skills/` | `~/.claude/agents/` |
| `codex` | `~/.agents/skills/` | 分派时读取共享 prompt |

Codex 和 Claude Code 的本地技能目录支持软链接，见 [OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills)和 [Claude Code 官方说明](https://code.claude.com/docs/en/skills#choose-where-skills-load)。Pi 的技能发现规则见 [Pi 官方说明](https://pi.dev/docs/latest/skills)。

更新时，已有 agent 的 YAML frontmatter（模型、工具列表及其他自定义字段）原样保留，仅更新正文；新 agent 默认不绑定模型。在目标项目运行 `/init-dev-flow`，由用户选择基础模型，或安装时用 `--project-root /path/to/project` 为新 Pi agent 读取该项目已有的选择。已有 agent 的配置优先保留，项目的 tracker、执行模式与模型文件不由安装器改写。

同名旧目录、旧软链接和待更新的 agent 会先迁到 `~/.local/share/dev-flow-skills/backups/<时间戳>/`，保留原目录结构；备份位于技能扫描目录之外。旧的整包技能副本及 Codex 旧目录 `~/.codex/skills/` 中的同名项也会迁出，避免继续加载旧版本；其他技能和 CC Switch 的源文件保留。需要恢复时，用备份中的原路径替换对应安装项。重复运行且内容未变时不产生备份。

可用 `--home /tmp/dev-flow-home` 指定另一套用户目录进行隔离验证。安装完成后重新打开 CLI 会话；使用 CC Switch 等管理器时，将这份仓库作为后续来源，避免再次同步旧副本。

## 主流程

```
/init-dev-flow (每个仓库一次)
        ↓
/grill-with-docs → /to-spec → /to-plan → /to-tickets → /implement
     提需求          拆需求      实施蓝图      拆ticket       实现
                            （人工审）                    │
已实现 spec 有变动？→ /amend（增量演进，生成 spec-v2 + plan 就地更新 + 新 ticket）
```

## 辅助技能

```
/amend
    已实现 spec 的需求变动：只 grill 变动部分，深度判断（增量 vs 重做），
    生成 spec-v(N+1) + 更新 INDEX + 续接 ticket

/diagnosing-bugs
    系统化调试：反馈循环 → 最小化 → 假设 → 插桩 → 修复 → 回归测试

/export-session
    导出当前会话的原始聊天记录为 Markdown（支持 Claude Code / Codex / Pi / Cursor）

/to-api-contract
    后端 ticket 完成后产出接口契约片段，供前端 agent 联调（Node.js 无自动文档场景）
```

## 技能列表

| 阶段 | 命令 | 功能 | 可分派子 agent |
|------|------|------|---------------|
| 0. 初始化 | `/init-dev-flow` | 探测 tracker 类型，生成声明（每仓库一次） | — |
| 1. 提需求 | `/grill-with-docs` | 追问对齐需求，维护 CONTEXT.md | 交互型，留主会话 |
| 2. 拆需求 | `/to-spec` | 四段式结构化 spec（产品意图与边界），含 seams 分析 | 交互型，留主会话 |
| 2.5 实施蓝图 | `/to-plan` | 技术决策/包分解/风险点，经人工审后拆票 | 交互型，留主会话 |
| 3. 拆 ticket | `/to-tickets` | Tracer-bullet 拆分执行细节，引用 plan 条目 | 交互型，留主会话 |
| 4. 实现 | `/implement` | 按改动选择验证方式，复用测试并 review | ✅ `implementer`（单张 ticket 自治执行） |
| 辅助 | `/find` | 只读聚合当前 feature/阶段/ticket 状态/阻塞项/下一步 | 主会话解析，scout 可做文件发现 |
| 辅助 | `/amend` | 已实现 spec 的需求变动（增量演进 + 深度判断闸门） | 交互型，留主会话 |
| 辅助 | `/simplify` | 提交前清理代码（复用/质量/效率） | ✅ `simplifier` |
| 辅助 | `/diagnosing-bugs` | 系统化调试循环 | 交互型，留主会话 |
| 辅助 | `/e2e-test` | 写可进 CI 的浏览器 E2E 测试（先探测项目体系） | 交互型编排，写测试可派 implementer |
| 辅助 | `/export-session` | 导出会话原始记录为 Markdown | ✅ `exporter` |
| 辅助 | `/to-api-contract` | 按 ticket 产出接口契约（给前端 agent） | ✅ `contract-writer` |

**Tracker 产物：** 本地分别保存 Spec、`plan.md` 和 ticket 文件；GitHub/GitLab 分别使用 Spec issue、独立 Plan issue 和 ticket issues。Plan 正文保存现行技术方案，关联 Spec 与 tickets，评论记录讨论和批准依据；amend 更新同一 Plan issue，不新建 plan-vN。字段与关联规则见 [`_agents/workflow-contract.md`](./_agents/workflow-contract.md#tracker-产物与-plan-引用)。

## 层级与进度入口

默认归属为 **Spec → Plan → Tickets**；已有 Epic 时在 Spec 上方关联它。`Parent:` 说明直接归属，`Spec:` 定位规格版本，`Plan:` 定位 P<N>，`Blocked by:` 单独说明执行依赖。版本续接的旧 ticket 保留为历史，不作为新 ticket 的归属父级。

| 模式 | 层级与列表 |
|------|------------|
| GitHub | 建立原生 parent/sub-issue 关系；标题与类型标签区分 Spec / Plan / Ticket；已配置的 Projects 表格可打开 View → Show hierarchy |
| 本地 Markdown | `.scratch/README.md` 列出 feature 入口；每个 feature 的 `INDEX.md` 提供当前规格、现行 Plan、ticket 层级链接与演进记录；`/find` 读取源文件展示带状态的树形快照 |
| GitLab | 保留相同逻辑字段，按实际平台能力同步原生关系；不支持的展示如实说明 |

本地继续保持每票一个文件，文件夹里即可找到导航：

```text
.scratch/
├── README.md                 # feature 入口清单
└── export/
    ├── INDEX.md              # 当前规格、Plan 与 ticket 的可点击层级
    ├── spec.md               # 历史规格保留
    ├── spec-v2.md            # 当前规格（由 INDEX 指向）
    ├── plan.md               # 原地更新，不叠版本
    └── issues/
        ├── 01-csv.md         # Spec v1 的历史票
        └── 04-json.md        # Spec v2 的当前票
```

INDEX 只维护导航、当前版本与演进，不复制方案正文、ticket 状态或批准记录。创建/更新产物时同步关联；只读 `/find` 发现缺失、冲突或失效链接时报告，不代改。Projects 是可选入口，父子进度不代表 Plan 已批准或业务已验收。细则见[归属层级与列表展示](./_agents/workflow-contract.md#归属层级与列表展示)。

## 执行型子 agent

执行型技能可分派给独立子 agent 执行（输入明确 → 跑完 → 写文件 → 报告，无需中途人机交互）。

**单一 prompt 源 + 各工具适配层：**

```
_agents/                # 工具无关的 system prompt（改 prompt 改这里）
├── exporter.prompt.md
├── simplifier.prompt.md
├── contract-writer.prompt.md
├── implementer.prompt.md
├── scout.prompt.md
└── diagram-guide.md      # 图示规范（mermaid），非独立 agent

adapters/               # 工具适配（thinking / 工具白名单）
├── build.sh            # 一键生成各工具 agent 文件：./adapters/build.sh all
└── codex/README.md
```

| Agent | 职责 | thinking | 自治度 |
|-------|------|----------|--------|
| `exporter` | 会话格式转换 | low | 完全自治 |
| `simplifier` | 提交前代码清理 | medium | 完全自治，不提交 |
| `contract-writer` | 接口契约提取 | medium | 完全自治 |
| `implementer` | 单张 ticket 的实现与验证 | high | 完全自治，不提交/不跑 simplify |
| `scout` | 代码侦察 → context.md | low | 完全自治 |

**设计原则：**
- **决策前置**：spec/ticket/plan 阶段已拍死所有决策（spec=产品、plan=技术、ticket=执行细节），执行型 agent 遇到未覆盖的决策就停止并报告，绝不猜测或扩大范围。因此它们不依赖"中途回问主 agent"的通道，能跨 Pi / Claude Code / Codex 统一
- **边界清晰**：子 agent 都不 commit、不跑 simplify（那是主 agent 在提交节点、经人工 checkpoint 后做的）
- **状态闭环**：字段与状态语义统一见 [`_agents/workflow-contract.md`](./_agents/workflow-contract.md)。每票领取为 `claimed`，必要自动检查通过后记 `code-complete` 并解除 ticket 依赖；最终验收和 checkpoint 完成后才 `resolved`，提交节奏独立处理
- **小改动入口**：单票小改动可明确省略 spec/plan，必要决策、测试边界与验收写在 ticket 中；下游按该约定执行
- **测试组织**：优先复用测试文件和 fixtures，同类输入参数化；业务/bug 使用行为测试，纯重构做前后回归，文档/配置/样式采用适用检查。必要验证仍须通过，不按 ticket 批量生成 test 文件。规则见[共享验证约定](./_agents/workflow-contract.md#验证方式与测试组织)
- **进度查询**：`/find` 只读聚合状态，不修改任何状态；scout 只负责复杂目录发现，状态判断由主会话完成
- **交互型留主会话**：grill / diagnosing / spec / tickets 需要与你来回对话，不适合隔离

**单独生成 agent 文件（底层适配器）：** 常规安装与更新使用根目录的 `install.sh`，以保留已有 agent 配置。`build.sh` 按模板完整生成文件：
```bash
./adapters/build.sh all --project-root /path/to/project

# 预览生成结果，写入独立目录
./adapters/build.sh all --project-root /path/to/project --output-dir /tmp/dev-flow-preview
```

**基础模型由使用者在初始化时选择：** `/init-dev-flow` 引导用户从当前工具实际可用的模型中选择，或明确选择 `inherit`，保存到 `docs/agents/execution-mode.md`。通用模板不写死模型名或供应商。

Pi 构建时的优先级为 `DEV_FLOW_MODEL` 临时覆盖 > 目标项目的“基础模型”；没有显式配置时省略 `model` 字段，交给工具自身的默认规则，不提供内置模型。其他工具分派时按各自支持的格式使用项目选择。

`--project-root` 明确指定配置所属项目，省略时固定使用技能库根目录，不随启动目录改变。

`--output-dir` 将 Pi/Claude Code 文件分别生成到指定目录的 `pi/`、`claude-code/` 中，供预览和隔离测试；省略时写入对应工具的用户级 agents 目录。`codex` 目标仅显示使用说明，不写文件。

**是否派子 agent 是可配置的：** 初始化时（`/init-dev-flow`）会询问你的默认执行模式，存入 `docs/agents/execution-mode.md`：
- `subagent`（默认推荐）→ 执行型技能分派给独立子 agent
- `inline` → 主会话直接执行（参照同一份 `_agents/*.prompt.md`）

无论选哪个，**单次执行时都可临时覆盖**（如"这张小 ticket 别派了"）。执行逻辑的单一事实源是 `_agents/*.prompt.md`，两种模式只是执行主体不同。

## 打包给其他团队/仓库使用

分发完整仓库或压缩包，接收方放在长期保留的独立目录，再使用相同安装入口：

```bash
cd /path/to/xixiwu_skills
./install.sh all
```

使用者在自己的项目运行 `/init-dev-flow` 完成 tracker、提交策略、执行模式及基础模型选择；分发模板时无需预填模型名或供应商配置。ZIP 用户更新时，将完整新版仓库放到相同位置后重跑 `install.sh`。

## 图示（功能流程图 / 架构图 / 时序图 / 泳道图）

流程中的关键节点会生成 **Mermaid 图**（提炼自 archify 的语义契约）。Mermaid 源码是纯文本、可进 git diff，且 GitHub/飞书/VS Code 会原生渲染成图 —— agent 读时是结构化文本，人看时是图。规范见 `_agents/diagram-guide.md`。

**两种图型按场景选：**

| 场景 | 图型 | 用途 |
|------|------|------|
| 阶段流程、判断分支、循环、泳道分组 | `flowchart` | 项目架构图、feature 流程 |
| 调用时序、同步/异步、返回、安全边界 | `sequenceDiagram` | spec 的端到端调用流 |

- **项目架构图**：`/init-dev-flow` 时生成到 `.scratch/architecture.md`（已有代码的仓库），`flowchart` + `subgraph` 泳道，帮 agent 快速理解项目。示例见本仓库的 [`architecture.md`](./architecture.md)
- **功能流程图**：嵌入 spec 的“方案概述”，`flowchart` 展示业务入口、用户动作、条件分支与结果；模块影响继续用文字清单记录
- **端到端时序图**：嵌入 spec，`sequenceDiagram` 用 `->>`（同步）/`-->>`（返回）/`-)`（异步）

**设计原则：变体即语义。** 图型、箭头、判断节点承载含义而非装饰；标签是语义数据，不为排版删除。

## 使用方式

1. 运行 `./install.sh <pi|claude-code|codex|all>` 安装技能与适配文件
2. **新仓库先运行 `/init-dev-flow`**，确定 tracker 类型、提交策略、执行模式
3. 主流程按阶段顺序使用 `/命令` 触发；执行型阶段按 execution-mode 派子 agent 或主会话执行
4. 遇到难调 bug 时使用 `/diagnosing-bugs`
5. 后端 ticket 完成且涉及对外端点时，用 `/to-api-contract` 产出契约给前端

## 文件结构

```
dev-flow-skills/
├── README.md
├── install.sh                # 统一安装和更新入口
├── TUTORIAL.md               # 端到端叙事走查
├── architecture.md           # 自身架构示例（mermaid）
├── _agents/                  # 执行型子 agent 的 prompt 源
│   ├── README.md
│   ├── workflow-contract.md  # 共享字段、状态和简化流程
│   ├── diagram-guide.md      # 图示规范（非 agent）
│   ├── exporter.prompt.md
│   ├── simplifier.prompt.md
│   ├── contract-writer.prompt.md
│   ├── implementer.prompt.md
│   └── scout.prompt.md
├── adapters/                 # 跨工具适配
│   ├── build.sh
│   ├── install.py            # 安装、备份与 agent 配置保留
│   └── codex/README.md
├── tests/                    # 适配脚本检查与流程场景
├── init-dev-flow/
│   └── SKILL.md
├── grill-with-docs/
│   └── SKILL.md
├── to-spec/
│   └── SKILL.md
├── to-plan/
│   └── SKILL.md
├── to-tickets/
│   └── SKILL.md
├── implement/
│   └── SKILL.md
├── find/
│   └── SKILL.md
├── amend/
│   └── SKILL.md
├── diagnosing-bugs/
│   └── SKILL.md
├── e2e-test/
│   └── SKILL.md
├── simplify/
│   └── SKILL.md
├── export-session/
│   └── SKILL.md
└── to-api-contract/
    └── SKILL.md
```

## 验证

```bash
bash -n install.sh adapters/build.sh
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

自动测试使用临时目录与临时 HOME 验证生成与安装：目标参数、模型优先级、首次安装、重复更新、旧副本迁移、备份、配置保留、预览及源仓库保护，不写真实用户级目录。技能决策的行为走查见 [`tests/workflow-scenarios.md`](./tests/workflow-scenarios.md)，不以关键词检查代替实际执行。

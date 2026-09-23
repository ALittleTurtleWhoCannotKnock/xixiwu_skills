# Dev Flow Skills

五阶段开发流程 + 调试技能，跨 Pi / Codex / Claude Code 通用。

> **全局纪律：绝不主动提交或推送代码。** 未经用户明确指示（"提交"/"推送"），任何阶段、任何 agent（主会话或子 agent）都把改动留在工作区。提交永远经过用户确认（人工 checkpoint）。

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
| 4. 实现 | `/implement` | 在约定 seams 处 TDD，自动 review | ✅ `implementer`（单张 ticket 自治执行） |
| 辅助 | `/find` | 只读聚合当前 feature/阶段/ticket 状态/阻塞项/下一步 | 主会话解析，scout 可做文件发现 |
| 辅助 | `/amend` | 已实现 spec 的需求变动（增量演进 + 深度判断闸门） | 交互型，留主会话 |
| 辅助 | `/simplify` | 提交前清理代码（复用/质量/效率） | ✅ `simplifier` |
| 辅助 | `/diagnosing-bugs` | 系统化调试循环 | 交互型，留主会话 |
| 辅助 | `/e2e-test` | 写可进 CI 的浏览器 E2E 测试（先探测项目体系） | 交互型编排，写测试可派 implementer |
| 辅助 | `/export-session` | 导出会话原始记录为 Markdown | ✅ `exporter` |
| 辅助 | `/to-api-contract` | 按 ticket 产出接口契约（给前端 agent） | ✅ `contract-writer` |

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

adapters/               # 工具配置（改模型/工具白名单改这里）
├── build.sh            # 一键生成各工具 agent 文件：./adapters/build.sh all
└── codex/README.md
```

| Agent | 职责 | 模型（Pi，可在 build.sh 配置） | thinking | 自治度 |
|-------|------|-----------|----------|--------|
| `exporter` | 会话格式转换 | 见 build.sh MODEL 变量 | low | 完全自治 |
| `simplifier` | 提交前代码清理 | 同上 | medium | 完全自治，不提交 |
| `contract-writer` | 接口契约提取 | 同上 | medium | 完全自治 |
| `implementer` | 单张 ticket 的 TDD 执行 | 同上 | high | 完全自治，不提交/不跑 simplify |
| `scout` | 代码侦察 → context.md | 同上 | low | 完全自治 |

**设计原则：**
- **决策前置**：spec/ticket/plan 阶段已拍死所有决策（spec=产品、plan=技术、ticket=执行细节），执行型 agent 遇到未覆盖的决策就停止并报告，绝不猜测或扩大范围。因此它们不依赖"中途回问主 agent"的通道，能跨 Pi / Claude Code / Codex 统一
- **边界清晰**：子 agent 都不 commit、不跑 simplify（那是主 agent 在提交节点、经人工 checkpoint 后做的）
- **状态闭环**：ticket 使用 `Status: ready`（待执行）/ `claimed`（执行中）/ `resolved`（验证完成）；implement 开始时领取为 claimed，验证和 checkpoint 完成后才 resolved
- **进度查询**：`/find` 只读聚合状态，不修改任何状态；scout 只负责复杂目录发现，状态判断由主会话完成
- **交互型留主会话**：grill / diagnosing / spec / tickets 需要与你来回对话，不适合隔离

**生成/更新 agent 文件：**
```bash
# 方式 1: 使用初始化时配置的模型（推荐）
./adapters/build.sh all     # 自动读取 docs/agents/execution-mode.md 中的基础模型

# 方式 2: 环境变量临时覆盖（CI/特殊场景）
export DEV_FLOW_MODEL="your-provider/your-model"
./adapters/build.sh all
```

**模型配置优先级：** 环境变量 `DEV_FLOW_MODEL` > `docs/agents/execution-mode.md` 中的"基础模型" > 默认值 `anthropic/claude-sonnet-4`

**初始化时配置模型：** `/init-dev-flow` 在选择"派子 agent"后，会列出你已配置的模型列表供选择，存入 `execution-mode.md`。之后 `build.sh` 自动读取，无需每次设置环境变量。

**是否派子 agent 是可配置的：** 初始化时（`/init-dev-flow`）会询问你的默认执行模式，存入 `docs/agents/execution-mode.md`：
- `subagent`（默认推荐）→ 执行型技能分派给独立子 agent
- `inline` → 主会话直接执行（参照同一份 `_agents/*.prompt.md`）

无论选哪个，**单次执行时都可临时覆盖**（如"这张小 ticket 别派了"）。执行逻辑的单一事实源是 `_agents/*.prompt.md`，两种模式只是执行主体不同。

## 打包给其他团队/仓库使用

dev-flow-skills 是自包含的。**模型配置在初始化时完成**，无需手动设置环境变量：

```bash
# 1. 复制整个文件夹到目标位置
cp -r dev-flow-skills /path/to/target/

# 2. 在目标仓库运行 /init-dev-flow
#    它会列出你已配置的模型供选择，存入 docs/agents/execution-mode.md

# 3. 生成 agent 文件（自动读取配置的模型）
cd /path/to/target/dev-flow-skills
./adapters/build.sh all
```

**注意：** 如果目标环境没有运行 `/init-dev-flow`，`build.sh` 会使用默认模型 `anthropic/claude-sonnet-4`。可通过 `export DEV_FLOW_MODEL="..."` 临时覆盖。

## 图示（架构图 / 时序图 / 泳道图）

流程中的关键节点会生成 **Mermaid 图**（提炼自 archify 的语义契约）。Mermaid 源码是纯文本、可进 git diff，且 GitHub/飞书/VS Code 会原生渲染成图 —— agent 读时是结构化文本，人看时是图。规范见 `_agents/diagram-guide.md`。

**两种图型按场景选：**

| 场景 | 图型 | 用途 |
|------|------|------|
| 阶段流程、判断分支、循环、泳道分组 | `flowchart` | 项目架构图、feature 流程 |
| 调用时序、同步/异步、返回、安全边界 | `sequenceDiagram` | spec 的端到端调用流 |

- **项目架构图**：`/init-dev-flow` 时生成到 `.scratch/architecture.md`（已有代码的仓库），`flowchart` + `subgraph` 泳道，帮 agent 快速理解项目。示例见本仓库的 [`architecture.md`](./architecture.md)
- **模块影响图**：嵌入 spec，`flowchart` 标注 `[新增][修改][不动]`
- **端到端时序图**：嵌入 spec，`sequenceDiagram` 用 `->>`（同步）/`-->>`（返回）/`-)`（异步）

**设计原则：变体即语义。** 图型、箭头、判断节点承载含义而非装饰；标签是语义数据，不为排版删除。

## 使用方式

1. 将本文件夹复制到 agent 工具的 skills 目录
2. **新仓库先运行 `/init-dev-flow`**，确定 tracker 类型、提交策略、执行模式
3. 主流程按阶段顺序使用 `/命令` 触发；执行型阶段按 execution-mode 派子 agent 或主会话执行
4. 遇到难调 bug 时使用 `/diagnosing-bugs`
5. 后端 ticket 完成且涉及对外端点时，用 `/to-api-contract` 产出契约给前端

## 文件结构

```
dev-flow-skills/
├── README.md
├── TUTORIAL.md               # 端到端叙事走查
├── architecture.md           # 自身架构示例（mermaid）
├── _agents/                  # 执行型子 agent 的 prompt 源
│   ├── README.md
│   ├── diagram-guide.md      # 图示规范（非 agent）
│   ├── exporter.prompt.md
│   ├── simplifier.prompt.md
│   ├── contract-writer.prompt.md
│   ├── implementer.prompt.md
│   └── scout.prompt.md
├── adapters/                 # 跨工具适配
│   ├── build.sh
│   └── codex/README.md
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

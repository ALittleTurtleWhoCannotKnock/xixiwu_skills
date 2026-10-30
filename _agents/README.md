# Agent Prompts（工具无关的单一事实源）

这里存放执行型子 agent 的**纯 system prompt**，不含任何工具特有的 frontmatter。

- 每个 `.prompt.md` 是一个执行型 agent 的完整指令
- `workflow-contract.md` 定义共享票据字段和状态语义；主会话传给 implementer，Pi/Claude Code 生成文件时自动附带，不是独立 agent
- `language-policy.md` 定义项目交互/产物语言；所有生成的 agent 自动附带，手动分派时传递该约定与两项语言。配置从目标仓库读取，不写死在全局 agent 中
- `diagram-guide.md` 是功能流程图、架构图、时序图与泳道图规范，供 init、spec 等生成图示时参照，不是独立 agent
- `adapters/<tool>/` 下的文件用对应工具的 frontmatter 包装同一份 prompt
- 改 prompt 只改这里；thinking、工具白名单等适配配置放在 adapters，基础模型由使用者接入时选择并记录在项目 execution-mode.md，适配器或单次分派读取使用

## Agent 一览

| Prompt | 对应技能 | 类型 | 自治度 |
|--------|---------|------|--------|
| `exporter.prompt.md` | export-session | 格式转换 | 完全自治 |
| `simplifier.prompt.md` | simplify | 代码清理 | 完全自治 |
| `contract-writer.prompt.md` | to-api-contract | 契约提取 | 完全自治 |
| `implementer.prompt.md` | implement（单张 ticket） | 实现与验证，行为改动优先 TDD | 完全自治（决策前置） |
| `scout.prompt.md` | to-spec / to-tickets 的代码侦察 | 侦察（只读） | 完全自治 |

> `diagram-guide.md` 是图示规范（mermaid），供 init/spec 生成图时参照，**不是独立 agent**，不在 adapters 生成。

## 工具支持矩阵

| 工具 | 加载方式 | 实时升级通道 |
|------|---------|------------|
| Pi | `~/.pi/agent/agents/*.md`（pi-subagents） | 有（contact_supervisor），但本套 agent 不用 |
| Claude Code | `~/.claude/agents/*.md` 或 Agent 工具 | 无 |
| Codex | AGENTS.md + dispatch 技能 | 无 |

所有 agent 按"完全自治"设计：输入齐全 → 跑完 → 写文件 → 报告。不依赖中途回问，因此跨工具通用。

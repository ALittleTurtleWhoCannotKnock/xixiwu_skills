# Codex 适配

Codex 没有 pi-subagents / Claude Code 那样的独立 agent 定义文件。它的"分派"靠 **AGENTS.md 里声明角色 + dispatch 类技能**实现。

## 怎么用这套 prompt

1. 把 `_agents/<name>.prompt.md` 的正文**内联**到角色分派调用里，作为子任务指令；分派 implementer 时同时提供 `_agents/workflow-contract.md` 和目标仓库的 tracker 状态声明。
2. 读取目标仓库 `docs/agents/execution-mode.md` 中用户确认的“基础模型”，分派时按当前工具支持的模型 ID 使用；`inherit` 使用原生继承方式。不把 Pi 的供应商前缀直接套到其他工具，通用 prompt 不绑定具体模型。

## 手动对应关系

| Agent | Prompt 源 | Codex 里的用法 |
|-------|----------|---------------|
| exporter | `_agents/exporter.prompt.md` | dispatch 一个格式转换子任务，把 prompt 作为指令 |
| simplifier | `_agents/simplifier.prompt.md` | 提交前 dispatch，scope 传 diff |
| contract-writer | `_agents/contract-writer.prompt.md` | ticket 完成后 dispatch |
| implementer | `_agents/implementer.prompt.md` | 单张 ticket dispatch，完全自治 |
| scout | `_agents/scout.prompt.md` | spec/tickets 前 dispatch 做代码侦察，产出 context.md |

## 注意

- `./adapters/build.sh codex` 只显示本说明的路径，不生成文件；`all` 生成 Pi/Claude Code 文件并显示 Codex 说明。
- Codex 子任务**无实时升级通道**，与 pi 的 `contact_supervisor` 不同。本套 prompt 已按"完全自治"设计，遇到未授权决策会"停止并报告"而非中途回问，因此兼容 Codex。
- 若想持久化这些角色，可在项目 `AGENTS.md` 里加一段角色说明，指向本仓库的 `_agents/` prompt 源。

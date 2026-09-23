# Codex 适配

Codex 没有 pi-subagents / Claude Code 那样的独立 agent 定义文件。它的"分派"靠 **AGENTS.md 里声明角色 + dispatch 类技能**实现。

## 怎么用这套 prompt

1. 把 `_agents/<name>.prompt.md` 的正文**内联**到 Codex 的 dispatch 调用里，作为子任务的 system/task 指令。
2. 模型与 thinking 在 dispatch 时指定（Codex 的模型配置在 `~/.codex/config.toml`）。

## 手动对应关系

| Agent | Prompt 源 | Codex 里的用法 |
|-------|----------|---------------|
| exporter | `_agents/exporter.prompt.md` | dispatch 一个子任务，把 prompt 作为指令，模型选高速档 |
| simplifier | `_agents/simplifier.prompt.md` | 提交前 dispatch，scope 传 diff |
| contract-writer | `_agents/contract-writer.prompt.md` | ticket 完成后 dispatch |
| implementer | `_agents/implementer.prompt.md` | 单张 ticket dispatch，完全自治 |
| scout | `_agents/scout.prompt.md` | spec/tickets 前 dispatch 做代码侦察，产出 context.md |

## 注意

- Codex 子任务**无实时升级通道**，与 pi 的 `contact_supervisor` 不同。本套 prompt 已按"完全自治"设计，遇到未授权决策会"停止并报告"而非中途回问，因此兼容 Codex。
- 若想持久化这些角色，可在项目 `AGENTS.md` 里加一段角色说明，指向本仓库的 `_agents/` prompt 源。

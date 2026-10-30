# Codex Adapter

This adapter supplies role prompts at dispatch rather than generating Codex role files. Use repository AGENTS.md role pointers and the available dispatch mechanism.

## Dispatch inputs

1. Inline `_agents/<name>.prompt.md` as task instructions together with `_agents/language-policy.md`, effective interaction/artifact languages, and the target repository. For implementer, also supply `_agents/workflow-contract.md` and the tracker state declaration.
2. Read the user-confirmed `基础模型` in the target execution-mode.md and use the current tool's supported model parameter. Inherit uses native inheritance. Do not reuse Pi-specific provider prefixes blindly; generic prompts bind no model.

## Role mapping

| Role | Source | Dispatch purpose |
|------|--------|------------------|
| exporter | `_agents/exporter.prompt.md` | Faithful session format conversion |
| simplifier | `_agents/simplifier.prompt.md` | Pre-commit cleanup with explicit diff scope |
| contract-writer | `_agents/contract-writer.prompt.md` | Contract extraction after backend work |
| implementer | `_agents/implementer.prompt.md` | One autonomous ticket implementation/validation |
| scout | `_agents/scout.prompt.md` | Read-only context discovery before Spec/ticketing |

## Notes

`build.sh codex` prints this guide without writing role files. The all target generates Pi/Claude Code files and prints the Codex guidance.

Prompts are autonomous: uncovered decisions stop and report rather than relying on live escalation. Optional persistent role pointers in project AGENTS.md should reference the prompt sources.

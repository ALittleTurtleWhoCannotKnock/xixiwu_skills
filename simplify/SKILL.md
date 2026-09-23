---
name: simplify
description: 代码清理。主会话确定 scope 与触发时机（读 commit-strategy），实际清理分派给 simplifier 子 agent（审查复用/质量/效率并修复）。修复后留人工 checkpoint 再提交。
---

# Simplify

提交前审查改动代码的**复用、质量、效率**。**主会话确定 scope 与时机，清理执行分派给 `simplifier` 子 agent。**

## 触发时机（主会话）

**不由用户手动记，由 commit-strategy 驱动。** 读取 `docs/agents/commit-strategy.md`：

| 策略 | 触发点 | scope |
|------|--------|-------|
| per-ticket | 每张 ticket 提交前 | 当前未提交的 diff（该 ticket 改动） |
| squash | 整个 feature 完成、统一提交前 | 累计 diff（feature 起点到工作区） |

**"feature 起点"的定义：** feature 分支与主干（main/master）的分叉点，即 `git merge-base main HEAD`。这样 scope 只含本 feature 的改动，不含期间 main 上他人的提交。若 feature 分支期间 main 有大量更新，建议先 rebase 到 main 再跑 simplify，避免 diff 混入无关变更。

也可手动触发（如 `/simplify` 或"清理一下这段代码"），此时 scope 由用户指定或 `git diff` 推断。

## 核心 Discipline

1. **编排与执行分离** — 主会话定 scope、做人工 checkpoint；子 agent 只做审查与修复
2. **保持外科手术式** — 子 agent 只改 diff 范围内的代码，不顺手重构世界
3. **子 agent 不提交** — 修复后返回报告，提交由主会话在用户确认后执行

## 操作步骤

### Step 1: 确定 scope（主会话）

按触发时机（见上表）确定 diff 范围。scope 模糊时先问用户再动手。

### Step 2: 执行清理（默认分派 simplifier 子 agent）

**先读执行模式：** 读取 `docs/agents/execution-mode.md`。缺失或内容无法识别（非 `subagent`/`inline`，如被改坏）时默认 `subagent` 并提示用户检查配置。用户可在单次执行时覆盖默认。

**默认 / `subagent` 模式 → 分派给 `simplifier` 子 agent**，传入 diff scope。子 agent 会：
- 读改动代码
- 按"复用/质量/效率"三维度审查（详见下方"审查维度"）
- 直接修复无争议问题；有争议的（权衡可读性、改行为）返回主会话询问
- 重跑触及文件的类型检查/测试
- 返回报告（发现 N 个问题、修了 M 个、刻意跳过哪些及原因）
- **子 agent 不提交**

**`inline` 模式 / 用户单次覆盖 → 主会话直接执行**：参照 `_agents/simplifier.prompt.md` 中的三维度审查与"不报告什么"清单，在 diff 范围内清理。

> 执行逻辑（审查维度、"不报告什么"）的单一事实源是 `_agents/simplifier.prompt.md`；两种模式只是执行主体不同。

### Step 3: 人工 checkpoint（主会话）

向用户展示子 agent 的修复清单，**暂停等用户确认**。用户确认后才进入提交（由调用方 `/implement` 或用户执行）。

## 审查维度

执行逻辑（复用/质量/效率三维度 + "不报告什么"清单）的单一事实源是 `_agents/simplifier.prompt.md`。主会话只需确认子 agent 报告覆盖了这三类，并核对其"刻意跳过"项是否合理。

## 产出物

- 修复后的代码（diff 范围内）
- 修复清单摘要（发现 N 个问题、修了 M 个、刻意跳过哪些及原因）

## 边界

| 适合 | 不适合 |
|------|--------|
| 提交前的代码清理 | 大范围架构重构（那需要专门的 spec/ticket） |
| diff 范围内的复用/质量/效率 | diff 范围外的代码（不越界） |
| per-ticket / squash 两种提交节奏 | 无 diff 可审（先确认有改动） |

## 与其他技能的关系

- 由 `/implement` 在提交节点触发（时机读 `docs/agents/commit-strategy.md`）
- 修复后留人工 checkpoint，用户确认后 `/implement` 才执行提交
- 只管"写得好不好"；管"做对没有"的是 `/implement` 的 Standards/Spec review

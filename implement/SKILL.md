---
name: implement
description: 按 ticket 实现功能。主会话负责编排（选 ticket、确认 seam、review、提交决策），TDD 执行分派给 implementer 子 agent（自治跑红-绿-重构）。适用于有明确 ticket，需要写代码实现的场景。
---

# Implement

按 ticket 实现功能。**主会话做编排与决策，TDD 执行分派给 `implementer` 子 agent。**

## 触发信号

- Tickets 已通过 `/to-tickets` 确认
- 有明确的、可执行的 ticket
- 需要写代码实现

## 核心 Discipline

1. **编排与执行分离** — 主会话选 ticket、确认 seam、review、提交；子 agent 只跑 TDD
2. **在预先约定的 seams 处测试** — 使用 `/to-spec` 确定的测试边界
3. **决策前置** — spec/ticket/plan 已拍死所有决策；子 agent 遇到未覆盖的决策会停止并报告，不猜测
4. **决策归属分层** — **技术决策查 plan**（用什么、怎么实现、风险），**产品边界查 spec**（做什么、不做什么、谁负责），**执行细节查 ticket**（seams、测试用例、验收标准）
5. **plan 发现 spec 不可行 → 回写 spec** — 若实现时发现 spec 的产品决策技术上不可行，**不自行变通**，走"理解纠偏"回写 spec（Step 3.5 修正层级判断），让产品决策与技术现实对齐
6. **子 agent 不提交** — 提交、简化、人工 checkpoint 都由主会话在提交节点执行
7. **绝不主动提交或推送** — 未经用户明确指示（"提交"/"推送"），即使看似完成也把改动留在工作区。提交永远经过用户确认（人工 checkpoint），不存在"顺手提交"

## 操作步骤

### Step 1: 选择 ticket（主会话）

根据依赖关系，选择下一张可执行的 ticket（所有 blocking 已解除）。从 tracker 读取 ticket 与所属 spec。

**领取 ticket：** 开始执行前，先在 tracker 中将该 ticket 的 `Status:` 从 `ready` 改为 `claimed`，记录当前执行者（本地文件可在状态行后加 `By: <agent/user>`）。如果 ticket 已是 `claimed`，不要抢占，先报告已有执行者；只有明确确认是遗留 claim 才能接管。

**若 feature 有多个 spec 版本**（存在 `INDEX.md`）：先读 `.scratch/<feature>/INDEX.md` 确定"当前版本"，读最新 spec（`spec-vN.md`）。最新 spec 只记变动点，需背景时按其指引回溯旧版本。

### Step 2: 确认测试 seam（主会话）

回顾 spec 中确定的 seams：
- 在哪个层级写测试？（HTTP API / Service / 其他）
- 测试外部行为，不测试内部实现细节
- 若 spec 未确定 seams（或未运行 `/to-spec`），与用户确认最高层现有 seam 后再继续

### Step 3: 执行 TDD（默认分派 implementer 子 agent）

**先读执行模式：** 读取 `docs/agents/execution-mode.md`。缺失或内容无法识别（非 `subagent`/`inline`，如被改坏）时默认 `subagent` 并提示用户检查配置。用户可在单次执行时覆盖默认。

**默认 / `subagent` 模式 → 分派给 `implementer` 子 agent**，传入：
- ticket 文件路径（含验收标准、`Blocked by`）
- ticket 的 `**来源**: plan P<N>` 对应 plan 条目（技术方案、风险点、**改动锚点**）
- **plan 路径**：`.scratch/<feature>/plan.md`（implementer 读它获取 P<N> 条目全文，含改动锚点 `文件#方法`）
- spec 路径（含约定的 test seams、产品边界）
- commit-strategy 路径
- 相关代码/测试位置指引

`implementer` 子 agent 会自治地：确认 blocker 已解 → 在约定 seam 处跑红-绿-重构 → 自 review（Standards + Spec）→ 返回结构化报告（实现了什么、测试状态、文件改动、未满足的验收标准、若提前停止则说明缺失的决策）。

**主会话等待子 agent 报告。** 若子 agent 报告"缺少某决策导致无法继续"，主会话与用户澄清该决策后，可将澄清结果重新分派给子 agent 继续。

**若子 agent 报告"ticket 的技术方向在现有架构中不成立"**（不是信息缺失，而是方案本身错了，如把某能力安错了通道），进入 **Step 3.5 修正流程**，不要直接重做或放弃。

**`inline` 模式 / 用户单次覆盖 → 主会话直接执行**：参照 `_agents/implementer.prompt.md` 中的 TDD 循环与规则，在约定 seam 处跑红-绿-重构（不重启子进程）。

> 执行逻辑（TDD 循环、规则）的单一事实源是 `_agents/implementer.prompt.md`；两种模式只是执行主体不同。各工具通过 `adapters/` 注册子 agent 后，用对应分派机制启动（Pi 用 subagent 工具，Claude Code 用 Agent 工具，Codex 用 dispatch）。

### Step 3.5: ticket 方向修正（主会话）

当 ticket 的技术落地方向在现有架构中不成立时（此时 spec 大方向通常没错，是 ticket 理解错了），**或当 plan 的改动锚点（`文件#方法`）在当前代码里找不到**（方法被改名/挪位/删除，锚点腐化）：

**1. 对齐现有架构**

摸清真实的现有结构（调用通道、数据流、边界），确认 ticket 原方案为何在此架构下不成立。锚点腐化情形下：确认目标方法的当前实际位置/名称。

**2. 修正 ticket**

更新该 ticket 的方案描述与验收标准，并在 ticket 内追加**修正记录**（"原方向 X 为何不成立 → 修正为 Y"+ 架构依据），保留演进痕迹。

**3. 修正层级判断（关键：防止 spec 与 ticket 脱节）**

判断该修正属于哪类，决定是否回写 spec：

| 修正类型 | 特征 | 是否回写 spec |
|---------|------|--------------|
| **理解纠偏** | 改变了"方案实际如何工作"的认知（如能力安错通道、数据流理解错） | ✅ **必须回写**。否则 spec 停在错误认知上，后续会重犯 |
| **实现细节** | 换函数名、调参数、改内部结构，不改变方案语义 | ❌ 不回写。spec 管"做什么/为什么"，不管哪行代码 |
| **新增约束/边界** | 发现需防抖、兼容旧数据、额外校验等 | ⚠️ 若影响后续 ticket 或需求理解则回写，否则留 ticket |

**判断标准：这个修正会不会改变"后来者对需求/方案的理解"？会 → 回写；只是实现细节 → 留 ticket。**

**plan 发现 spec 不可行时（特殊情形）：** 若 plan 的技术路径与 spec 的产品决策冲突（技术上做不到产品要的），**不自行变通**——把冲突上报，走"理解纠偏"路径**回写 spec**（修订产品决策，让产品与技术现实对齐），同时 plan 就地更新技术路径。这是唯一允许触发 spec 修订的实现期情形，必须经用户确认后才改 spec。

**4. 回写 spec（仅理解纠偏 / 必要的约束时）**

更新 spec 对应处（方案概述 / 时序图 / 相关决策行），保持 **spec 始终是"最准的事实源"**。在相关处加一行轻量变更说明：

```
> 修正（ticket NN）：[一句话说明修正内容 + 依据]。原理解 [X] 在现有架构不成立，修正为 [Y]。
```

**注意：** 这是 spec 的"就地纠偏"（ticket 未实现，spec 还是当前工作文档），直接改当前 spec，**不叠版本**。叠版本（spec-v2）是 `/amend` 处理的"已实现 + 需求演进"场景，与此不同。

**5. 重新分派（带循环退出）**

按修正后的 ticket 重新分派 implementer 执行。

**循环退出：** 若修正后的 ticket 再次被报方向错误（同一 ticket 连续 ≥2 次 direction error），**停止自动修正**，不再重新分派。此时说明问题不是 ticket 落地理解偏差，而是 spec 层面的方案有问题，提示用户：人工介入对齐，或回退到 `/to-spec` 重新审视方案。不要在"修正-分派-再报错"里空转。

### Step 4: 验证（主会话）

核对子 agent 的报告，分两个层面：

**A. 完成度核对：**
- 验收标准是否全部满足？
- 测试是否全部通过、类型检查是否通过？
- 改动是否确实只在约定 seam 处测试？

**B. 问题分级审查（决定能否进提交节点）：**

按证据列出当前 diff 引入的问题，分三级：

| 级别 | 含义 | 处理 |
|------|------|------|
| **P0** | 阻塞合并的问题（如实现与 spec 矛盾、测试未过、偏离既定决策） | 必须修复后才可进提交节点 |
| **P1** | 发布前应修的问题（如明显 smell、缺失的边界处理） | 记录并决定是否本次修 |
| **P2** | 备注类（如可读性建议） | 仅记录，不阻塞 |

**Drift check：** 对照 spec 既定决策 **和 plan 技术决策**，当前实现是否发生偏离？（长流程中主会话/子 agent 可能悄悄偏离拍死的方案）。发现偏离按 P0 处理，需与用户确认是修正实现还是显式修订 spec/plan。

只报告有证据支撑的问题，不发明问题。全部合格时明确说"无阻塞问题"。如有 P0/P1，退回子 agent 修正或退回用户决策。

### Step 5: 清理与提交（主会话）

**提交节奏由 `docs/agents/commit-strategy.md` 决定**（缺失则提示先运行 `/init-dev-flow`）：

- **per-ticket** → 每张 ticket 完成即进入提交流程
- **squash** → 跳过单 ticket 提交，待所有 ticket 完成后统一进入提交流程

**提交流程（到达提交节点时）：**

> 提交与推送永远需要用户明确确认。即使所有检查通过，也先停在人工 checkpoint，绝不自动提交。

1. 触发 `/simplify`（其内部会分派 `simplifier` 子 agent 清理，scope 由 commit-strategy 决定）
2. `/simplify` 修复后留**人工 checkpoint**，用户确认后再提交
3. 提交代码（关联 ticket / feature，提交动作仍需用户明确指示）
4. **验证通过后**，在 tracker 中将该 ticket 的 `Status:` 从 `claimed` 改为 `resolved`；若验证失败，保持 `claimed` 并报告失败原因，不得标记 resolved
5. 更新 ticket 依赖状态，解锁后续 ticket
6. **若该 ticket 涉及对外 HTTP 端点**（新增或修改路由），触发 `/to-api-contract`（内部会分派 `contract-writer` 子 agent）产出接口契约片段，供前端 agent 联调

## 产出物

- 可运行的代码（带测试）
- Review + simplify 通过的提交
- 更新的 ticket 状态
- （涉及端点的后端 ticket）对应接口契约片段 `.scratch/<feature-slug>/contracts/<ticket-slug>.md`

## 完成标准

- 所有 ticket 完成
- 所有测试通过
- 子 agent 报告验收标准全满足
- simplify 清理完成并经用户确认

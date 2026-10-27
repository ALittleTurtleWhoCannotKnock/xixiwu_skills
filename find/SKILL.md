---
name: find
description: Use when you need a read-only progress snapshot of the current repository or a named feature, especially after switching sessions, resuming work, or handing work to another agent.
---

# Find Progress

只读聚合开发进度。**不修改文件、不更新状态、不提交、不推送。**

## 操作步骤

### Step 1: 确定 tracker

字段、兼容格式与默认状态语义参见 [共享执行约定](../_agents/workflow-contract.md)。本技能只读取，不迁移或补写 tracker。

读取 `docs/agents/issue-tracker.md`。

- 文件缺失：报告“未初始化，请先运行 `/init-dev-flow`”，停止
- 本地模式：扫描 `.scratch/`
- GitHub/GitLab 模式：读取 tracker 中声明的 issue 来源；不能访问 tracker 时报告缺失数据，不猜测

**状态枚举动态读取**：tracker 中定义了本仓库使用的 Status 值域（如 `ready/claimed/resolved`，或扩展的 `code-complete/parked`）。解析 Status 时以 tracker 声明的值域为准，不硬编码默认三态。tracker 未声明值域时按默认三态解析，并在 Warnings 中提示“tracker 未定义 Status 枚举，扩展状态将显示为 unknown”。

### Step 2: 发现 feature（可选使用 scout）

- 本地模式：优先从 `.scratch/README.md` 的 feature 链接定位 INDEX；传入 feature 时只检查该 feature，未传时兼容扫描一级目录中的 INDEX/spec/plan/issues。未登记的旧 feature 仍显示，不把纯 Epic 文档或其他说明目录当作 feature
- 远程模式：从 tracker 声明的 feature/Spec 入口读取关联 Plan issue 和 tickets；按 `Spec:` / `Plan:` 建立关系，不要求本地 `.scratch` 存在，也不按 issue 编号、评论时间猜当前版本
- 当 feature 结构复杂、需要定位 INDEX/spec/issues/contracts 文件时，可按 `docs/agents/execution-mode.md` 分派 `scout` 做**只读文件发现**；scout 只返回文件清单和路径，不判断状态
- `scout` 不可用或 execution mode 为 inline 时，主会话直接扫描

### Step 3: 读取状态源（主会话）

对每个 feature 读取相应模式的状态源。本地读取：

1. `INDEX.md`（若存在）
   - 当前 spec 版本（INDEX 指向的版本即“当前执行层”）
   - 演进摘要、导航层级与真实文件链接；与正文字段交叉核对，不从索引推断 ticket 状态或 Plan 批准
2. spec 文件
   - `INDEX.md` 指向的版本优先
   - 没有 INDEX 时使用 `spec.md` 或最新 `spec-vN.md`
3. `issues/*.md`
   - `Status:`（按 tracker 值域解析）
   - `Parent:` 记录直接归属；缺失时仅按明确的 Plan/Spec 引用推导并注明，不改写原文件
   - `Spec:` 与 `Plan:` 分别确定来源版本和方案包；兼容旧 `**来源**:`，按内容区分，不用 plan 包推断 spec 版本
   - 依赖以 `Blocked by:` 为标准，读取时兼容 `**依赖**:`、`**阻塞**:`；重复字段冲突则列明字段和值，阻塞判定为 unknown
   - ticket 标题和编号
4. 现行 plan 文件
   - `Parent:`、`Spec:`、批准戳记与关联 tickets，核对当前规格和导航；明确省略 Plan 时不要求该文件
5. `contracts/`
   - 已生成的契约文件名
6. `.scratch/<feature>/` 下未建票的实质文档（如集成说明、走查单）——只登记，不判断状态

远程读取 Spec 及其版本引用、独立 Plan issue 正文（含 `Spec:`、批准状态与 tickets 清单）、各 ticket 正文和关联契约。按 tracker 的当前版本约定定位执行版，并与 Plan 的 `Spec:` 核对；不从 Plan 包号推断版本。只在 Spec 评论发现旧 plan 时报告其位置与迁移建议，不迁移；主存不可访问或版本关系冲突时报告具体缺失信息。

GitHub 同时只读查询实际 parent/sub-issues，并与 `Parent:` / `Plan:` / `Spec:` 比较。旧 CLI 不支持字段时按共享约定使用可用 API；权限不足或查询失败标为 unknown，不把读取失败当成没有父级。GitLab 只使用该平台实际支持的关系。原生关系、正文字段和本地索引冲突时分别列出来源和值，不在 `/find` 中补标签、改父级或重建索引。

**状态解析规则：**

- Status 值属于 tracker 值域 → 按其语义归类（见下方归类表）；值域外或缺失 → 显示 `unknown`
- 缺少依赖字段视为无声明阻塞，不等于所有依赖已验证
- 被 blocker 的 ticket 不能列为可执行，即使自身 Status 是 `ready`
- 不根据文件修改时间、文件数量或对话内容推断完成状态

**状态归类表**（tracker 自定义状态 → 语义归类）：

| 归类 | 典型状态值 | 含义 |
|------|-----------|------|
| done | `resolved` | 已验证完成，可作为依赖解除下游 |
| code-complete | `code-complete` | 代码及必要自动检查通过，仍待最终验收/收尾 checkpoint；**可作为依赖解除下游**，外部条件仍需另验，自身不计入 fully-resolved |
| parked | `parked` | 暂停/搁置（等外部条件或用户决策）；**不解除下游依赖**，不算完成 |
| active | `ready` / `claimed` | 可执行 / 执行中 |
| unknown | 值域外、缺失 | 状态不完整 |

**版本续接语义**（不是 `Parent:` 归属）：旧 ticket 被 spec-v(N+1) 的新 ticket 续接后，旧票保持原有 `code-complete`/`parked` 等状态作为**追踪参考**，不因新票存在而升级。新票仍归属 Plan，或按明确省略规则确定父级。判断“下一步”时只在执行层（当前 spec 版本派生的 ticket）找 `ready`；旧追踪参考票停在 code-complete 是正常状态，不是遗漏。

**依赖判定规则：**

- 依赖项归类为 done 或 code-complete → 依赖解除，可开工
- 依赖项因 code-complete 解除时 → Warnings 提示“NN 依赖的 XX 为 code-complete（未验证），开工前注意验证风险”
- 依赖项为 parked 或 unknown → 依赖未解除
- 依赖项含外部条件（如“算法侧样张”、“二期启动确认”等非 ticket 编号）→ 状态无法验证，列入 Warnings

### Step 4: 判断阶段

对每个 feature 按以下优先级判断：

| 条件 | 阶段 |
|------|------|
| 无 spec 且无 issues | 需求/规划未开始 |
| ticket 引用的 spec/plan 缺失，且没有明确省略原因 | 状态不完整 |
| 执行层 plan 尚未批准 | 等待 plan review，相关 ready 票不可开工 |
| 存在 `ready` 或 `claimed` ticket（执行层） | 实现中 |
| 所有 ticket 为 `resolved`（无 code-complete/parked 残留） | 已完成 |
| 存在 unknown Status | 状态不完整 |
| 仅 done + code-complete + parked，无 active | 等待验证/收尾（有 code-complete 未验证，或有 parked 待决策） |
| 无 issues，有 spec 但无 plan | 等待实施蓝图，或按小改动规则直接拆票 |
| 无 issues，plan 存在但未批准 | 等待 plan review |
| 无 issues，plan 已批准 | 等待拆 ticket |

**简化流程与 plan 状态：** ticket 明确写 `Spec: none (原因)` / `Plan: none (原因)` 且包含必要决策时，按 ticket 实际状态判断阶段。已有 plan 的批准状态读文件/issue 正文的戳记及授权依据；不由 open/closed 推断，未批准的执行票不列为可执行。

若有 `claimed` ticket，显示正在执行的 ticket；若多个 `claimed`，显示并发执行提示。

### Step 5: 输出快照

先按共享约定输出 **Hierarchy**：用可点击的 Markdown 嵌套列表显示已有 Epic（若明确指定）→ Spec → Plan → tickets；本地节点链接真实文件，远程节点链接实际 issue。每个 ticket 标注 P<N>、Spec 版本与读取到的 Status；旧版本票标注“历史”，省略的层级不补造节点。P<N> 仅用于 Plan 下的分组，不当成额外 issue。原生关系不可读或与正文不符时，注明“正文推导/原生未同步”，不伪装为已验证的树。

再输出下列状态摘要。进度统计按归类分组，不合并口径，当前执行层与历史票明确区分；GitHub 的子 issue 关闭比例不替代这些状态：

```text
Feature: <feature>
Tracker: local markdown / GitHub / GitLab
Stage: <阶段>
Spec: <当前 spec 文件/issue 版本引用或 unknown>
Plan: <现行 plan 文件/独立 issue（已批准/待 review）或 无>

Progress: <n> resolved / <n> code-complete / <n> parked / <n> active / <n> unknown（共 <total>）

Tickets（按归类排序）:
- [resolved] 01: <title>
- [code-complete] 19: <title>  ← awaiting verification
- [parked] 22: <title>  ← 外部依赖未到位
- [claimed] 23: <title>  ← in progress
- [ready] 24: <title>
- [unknown] 05: <title>

Blocked:
- 12 blocked by 10（10 为 code-complete，已解除但未验证）
- 21 外部依赖：算法侧 golden 样张（无法验证）

Contracts:
- <ticket-contract-file>

Next:
- <执行层中依赖已解除且引用方案已批准的唯一可执行 ready ticket；明确省略 plan 时按简化规则>
- 老版本遗留的 ready 照列但标注其外部阻塞，不冒充“立即能做”
- 没有可执行 ticket 时明确说明原因

Warnings:
- <missing INDEX / unknown Status / multiple claimed / tracker unavailable
   / plan 待 review 未批准 / code-complete 依赖未验证 / parked 未解除下游 / 外部依赖无法验证
   / Parent 与原生关系冲突 / 索引缺失或链接失效 / 原生关系未同步
   / 发现未建票的实质文档（建议建票，如 backend-integration.md）>
```

未传 feature 时，先输出所有 feature 的短表，再对当前活跃 feature 展开同样的详情：

```text
Feature                         Stage       Progress                              Next
blog-comments                   实现中       2/4 resolved                          03-nested-replies
payment                         等待验证     2/3 code-complete                     真机回归
user-export                     已完成       3/3 resolved                          无
grid-chain                      状态不完整   1/3 resolved + 1 unknown              检查 unknown Status
```

## 关键约束

- `/find` 是观察视图，不是状态管理器
- 不能为了让进度看起来完整而修改 ticket、INDEX 或 spec
- code-complete 与 resolved 不混算：统计、阶段判断、“下一步”都要区分
- 版本续接的旧追踪参考 ticket 停在 code-complete/parked 是正常状态，不把它当成归属父级
- 不确定就显示 `unknown` 并列出原因
- 没有唯一可执行 ticket 时，明确列出原因，不擅自选择
- 发现实质文档未建票时只在 Warnings 建议建票，不代建

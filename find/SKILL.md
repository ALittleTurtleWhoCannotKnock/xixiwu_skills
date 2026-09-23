---
name: find
description: Use when you need a read-only progress snapshot of the current repository or a named feature, especially after switching sessions, resuming work, or handing work to another agent.
---

# Find Progress

只读聚合开发进度。**不修改文件、不更新状态、不提交、不推送。**

## 操作步骤

### Step 1: 确定 tracker

读取 `docs/agents/issue-tracker.md`。

- 文件缺失：报告“未初始化，请先运行 `/init-dev-flow`”，停止
- 本地模式：扫描 `.scratch/`
- GitHub/GitLab 模式：读取 tracker 中声明的 issue 来源；不能访问 tracker 时报告缺失数据，不猜测

**状态枚举动态读取**：tracker 中定义了本仓库使用的 Status 值域（如 `ready/claimed/resolved`，或扩展的 `code-complete/parked`）。解析 Status 时以 tracker 声明的值域为准，不硬编码默认三态。tracker 未声明值域时按默认三态解析，并在 Warnings 中提示“tracker 未定义 Status 枚举，扩展状态将显示为 unknown”。

### Step 2: 发现 feature（可选使用 scout）

- 用户传入 feature：只检查 `.scratch/<feature>/`
- 未传 feature：主会话先扫描 `.scratch/` 的一级目录，排除 `README.md`、`architecture.md` 等非 feature 文件
- 当 feature 结构复杂、需要定位 INDEX/spec/issues/contracts 文件时，可按 `docs/agents/execution-mode.md` 分派 `scout` 做**只读文件发现**；scout 只返回文件清单和路径，不判断状态
- `scout` 不可用或 execution mode 为 inline 时，主会话直接扫描

### Step 3: 读取状态源（主会话）

对每个 feature 读取：

1. `INDEX.md`（若存在）
   - 当前 spec 版本（INDEX 指向的版本即“当前执行层”）
   - 演进摘要
2. spec 文件
   - `INDEX.md` 指向的版本优先
   - 没有 INDEX 时使用 `spec.md` 或最新 `spec-vN.md`
3. `issues/*.md`
   - `Status:`（按 tracker 值域解析）
   - 依赖字段：`Blocked by:` 与 `**依赖**:` 两种格式都识别
   - ticket 标题和编号
4. `contracts/`
   - 已生成的契约文件名
5. `.scratch/<feature>/` 下未建票的实质文档（如集成说明、走查单）——只登记，不判断状态

**状态解析规则：**

- Status 值属于 tracker 值域 → 按其语义归类（见下方归类表）；值域外或缺失 → 显示 `unknown`
- 缺少依赖字段视为无声明阻塞，不等于所有依赖已验证
- 被 blocker 的 ticket 不能列为可执行，即使自身 Status 是 `ready`
- 不根据文件修改时间、文件数量或对话内容推断完成状态

**状态归类表**（tracker 自定义状态 → 语义归类）：

| 归类 | 典型状态值 | 含义 |
|------|-----------|------|
| done | `resolved` | 已验证完成，可作为依赖解除下游 |
| code-complete | `code-complete` | 代码完成、测试通过，但未经真机/人工验证；**可作为依赖解除下游**（见依赖判定），自身不计入 fully-resolved |
| parked | `parked` | 暂停/搁置（等外部条件或用户决策）；**不解除下游依赖**，不算完成 |
| active | `ready` / `claimed` | 可执行 / 执行中 |
| unknown | 值域外、缺失 | 状态不完整 |

**父子层级语义**（amend 续接产生）：旧版本父类 ticket 被 spec-v(N+1) 的新 ticket 续接后，父类保持 `code-complete`/`parked` 作为**追踪参考**（挂数据、挂历史），不因子 ticket 存在而升级；子 ticket（新版本派生）才是执行单元，走 `ready → claimed → resolved`。判断“下一步”时只在执行层（当前 spec 版本派生的 ticket）找 `ready`；父类停在 code-complete 是正常状态，不是遗漏。

**依赖判定规则：**

- 依赖项归类为 done 或 code-complete → 依赖解除，可开工
- 依赖项因 code-complete 解除时 → Warnings 提示“NN 依赖的 XX 为 code-complete（未验证），开工前注意验证风险”
- 依赖项为 parked 或 unknown → 依赖未解除
- 依赖项含外部条件（如“算法侧样张”、“二期启动确认”等非 ticket 编号）→ 状态无法验证，列入 Warnings

### Step 4: 判断阶段

对每个 feature 按以下优先级判断：

| 条件 | 阶段 |
|------|------|
| 无 spec | 需求/规划未开始 |
| 有 spec，但无 plan | spec 已生成，等待实施蓝图 |
| 有 plan，但无 issues | plan 已批准，等待拆 ticket |
| 存在 `ready` 或 `claimed` ticket（执行层） | 实现中 |
| 所有 ticket 为 `resolved`（无 code-complete/parked 残留） | 已完成 |
| 存在 unknown Status | 状态不完整 |
| 仅 done + code-complete + parked，无 active | 等待验证/收尾（有 code-complete 未验证，或有 parked 待决策） |

**plan 状态：** `.scratch/<feature>/plan.md` 是否存在、是否经用户批准（批准状态记在 plan 头部）。plan 缺失但有 spec → 阶段=等待实施蓝图；plan 存在未批准 → 在 Warnings 提示"plan 待 review，未批准前不拆票"。

若有 `claimed` ticket，显示正在执行的 ticket；若多个 `claimed`，显示并发执行提示。

### Step 5: 输出快照

进度统计按归类分组，不合并口径：

```text
Feature: <feature>
Tracker: local markdown / GitHub / GitLab
Stage: <阶段>
Spec: <当前 spec 文件或 unknown>
Plan: <plan.md（已批准/待 review）或 无>

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
- <执行层（当前 spec 版本派生）中唯一可执行的 ready ticket>
- 老版本遗留的 ready 照列但标注其外部阻塞，不冒充“立即能做”
- 没有可执行 ticket 时明确说明原因

Warnings:
- <missing INDEX / unknown Status / multiple claimed / tracker unavailable
   / plan 待 review 未批准 / code-complete 依赖未验证 / parked 未解除下游 / 外部依赖无法验证
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
- 父类追踪参考 ticket 停在 code-complete/parked 是正常状态，不提示为异常
- 不确定就显示 `unknown` 并列出原因
- 没有唯一可执行 ticket 时，明确列出原因，不擅自选择
- 发现实质文档未建票时只在 Warnings 建议建票，不代建

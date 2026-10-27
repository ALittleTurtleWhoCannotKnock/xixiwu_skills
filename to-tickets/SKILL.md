---
name: to-tickets
description: 将已批准的 plan 或已确认的单票小改动拆成可独立验证的 tracer-bullet tickets，明确测试边界、用例、验收与依赖。常规票引用 plan 方案；无 plan 的小改动在票内补齐必要决策。包含 prefactoring 识别。
---

# To Tickets

## 触发信号

- Plan 已通过 `/to-plan` 产出并经用户批准
- 工作量超过一个会话容量
- 多人协作，需要并行或串行执行

## 核心 Discipline

1. **Tracer-bullet** — 每票是一个可独立验证的垂直切片（端到端可跑通）
2. **Prefactoring 识别** — 在写新功能前，先重构让变更更容易
3. **显式依赖** — 声明 blocking 关系，明确执行顺序
4. **单一职责** — 一票只做一件事，可独立完成、独立验证
5. **有 plan 时不复述方案** — ticket 写测试 seam、改动范围、测试用例、验收标准，用 `Plan:` 引用本地文件/独立 issue 及 P<N>；省略 plan 的单票小改动则在 ticket 中写清必要技术决策
6. **plan 条目默认 1:1 对应 ticket，允许 1:N** — 一个包太大就拆多张 ticket，都标同一 plan 来源
7. **复用验证资产** — 每票声明验证方式与已有测试落点；不把“一票一文件”的 ticket 规则套到测试文件上

## 操作步骤

先读 [共享执行约定](../_agents/workflow-contract.md)，按统一的 `Spec:`、`Plan:`、`Blocked by:` 与 tracker 状态声明生成 ticket。

### Step 0: 读取 plan 包分解

按 Spec/ticket 的 `Plan:` 读取现行 plan 的**包分解**（P1..Pn）：本地为 `.scratch/<feature-slug>/plan.md`，远程为独立 Plan issue 的正文。读取正文批准状态与对应用户授权，不能用 issue 已关闭代替批准；已有会话授权有效时直接沿用，不重复询问。plan 缺失时按规模判断：

- **跨包中等以上改动** → 提示先运行 `/to-plan`（plan 是前置卡点，不可跳过）
- **单票小改动** → 可直接拆 ticket，写 `Plan: none (单票小改动)`；未产出 spec 时也写 `Spec: none (原因)`，并将产品边界、必要技术决策、测试 seam 和验收标准收在 ticket 中
- **微小改动** → 不必走 ticket，**但必须留记录**（见下方"记录是硬需求"）

同时（若 `/to-spec` 已产出）读 `context.md` 了解现有接缝与可复用点。

### 记录是硬需求（软硬规则）

**任何改动都必须留记录**，但 spec / plan / ticket 按规模选用，不是强制全套：

| 改动规模 | spec | plan | ticket | 最低记录 |
|---------|------|------|--------|---------|
| 大改动 | ✅ | ✅ | ✅ | ticket |
| 中等改动 | 可省 | 可省 | ✅ | ticket |
| 小改动 | 可省 | 可省 | 可省 | **必须留记录** |
| 微小改动 | 可省 | 可省 | 可省 | **必须留记录** |

**"必须留记录"的形式（任选其一）：**
1. 在已有 spec/plan/ticket 里就地追加一条改动记录
2. 在 `.scratch/<feature>/changelog.md`（或类似）里加一行
3. 在相关代码的 commit message 里描述（但 commit 需人工确认，不算此处的记录）

**硬规则：** 改动必须有可追溯记录（spec/plan/ticket/changelog 任一）；spec/plan/ticket 按规模软选用，不是每改动都必备。

### Step 1: 识别 prefactoring 机会

在拆分 ticket 前，先检查是否需要**预重构**（prefactoring）：

> "Make the change easy, then make the easy change."

**识别信号（结合 scout 简报的 Architecture / Existing Seams 判断）：**
- 新功能要塞进一个已经很大的模块
- 现有代码结构会让新功能实现变得复杂
- 多个 ticket 会重复修改同一段代码

**示例：**
```
场景：给博客加评论功能

无 prefactoring：
- Ticket 1: 在 Post 模型里加 comments 字段
- Ticket 2: 在 Post API 里加评论接口
- 结果：Post 越来越臃肿

有 prefactoring（prefactor 票排在最前，同样从 01 编号）：
- Ticket 1: Prefactor - 提取 Content 接口
- Ticket 2: Comment 模型实现 Content 接口
- Ticket 3: 评论 API
- 结果：评论独立，不影响文章
```

### Step 2: 识别垂直切片

将 spec 或已确认的小改动需求分解为可独立交付的切片。每个切片：
- 从用户角度是一个完整的功能点
- 可以独立测试验证
- 有明确的完成标准
- **包含所有层**（schema、API、UI、测试），不是单一层

**规则：**
- 垂直切片，不是水平切片
- 每片可独立演示或验证
- 大小适合单个上下文窗口
- Prefactoring 先做

### Step 3: 声明依赖关系

使用共享约定中的最小 ticket 模板，分别填写 `Parent:`、`Spec:` 与 `Plan:`。直接父级是 Plan 文件/issue，不带 P<N>；省略 Plan 时按共享规则归属 Spec、已指定 Epic 或 none，不补造被省略的文档。依赖统一写 `Blocked by:`，没有依赖写 `none`；不能把 blocker 当作父级。

按[共享验证规则](../_agents/workflow-contract.md#验证方式与测试组织)填写“验证方式”：优先指定已有测试文件/fixtures 或适用检查命令，说明本票缺少的覆盖。不要预设每票新增一个 test 文件；只有独立测试边界或项目约定确有需要时才新建。文档、配置、纯重构可使用对应检查，不为凑红—绿循环制造测试。

本地评论 API 票可写 `Spec: spec.md`、`Plan: plan.md#P2`、`Blocked by: 01-prefactor`；远程可写 `Spec: #100`、`Plan: #101 / P2`、`Blocked by: #102`。技术方案在 plan 正文中维护，方法级锚点不复制进 ticket；无 plan 时使用 Step 0 的小改动规则。

### Step 4: 用户确认

展示 ticket 列表，询问：
- 粒度是否合适？（太粗/太细）
- 依赖关系是否正确？
- 是否需要合并或拆分？

已有针对票据粒度和依赖的明确确认时直接沿用，不重复询问。

### Step 5: 保存 tickets

读取 `docs/agents/issue-tracker.md` 判断 tracker 模式；若该文件缺失，提示先运行 `/init-dev-flow`。ticket 的存放路径与格式遵循该文件的约定。

保存前读取 Plan 的关联清单及现有票，按 **Spec 版本 + Plan/P<N> + 已确认的执行范围与验收** 识别对应票；重复调用复用已经保存的票，仅创建尚缺的切片。一个 P<N> 允许多票，不能因同包已有一票就跳过其他切片，也不能把旧 Spec 的历史票当成本次新票或重新打开旧票。

**状态字段约定：** 每张 ticket 都必须有 `Status:`，新票初始为 `ready`。合法值与依赖语义以 tracker 声明为准，不在本技能硬编码三态；各默认状态含义见共享执行约定。

**本地模式补充规则：** 每张 ticket 一个文件 `.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从 `01` 编号（blocker 在前），头部字段遵循共享约定。**绝不合并成单一文件**。GitHub/GitLab 模式每张 ticket 一个 issue，使用相同字段和 tracker 声明的状态语义；若使用平台 blocking 关系，须与 `Blocked by:` 一致，工具不支持时用正文字段声明并如实报告未同步原生关系。

保存后按[归属层级与列表约定](../_agents/workflow-contract.md#归属层级与列表展示)同步导航：

- 本地：把真实 ticket 链接及所属 P<N>/Spec 版本登记到 `INDEX.md` 的层级清单，回填 Plan 的关联 tickets；即使省略 Spec/Plan，也创建仅含现有产物的 feature 索引和 `.scratch/README.md` 入口。不把 Status 或批准状态复制进索引。
- GitHub：每票使用 `[Ticket]` 标题与对应类型标签，建立 ticket → Plan（或明确的替代父级）的原生关系并核对；已有同父关系直接复用，冲突或同步失败列为未同步项。目标 Project 已配置时加入同一 Project，不因缺少 Projects 而建第二套 tracker。
- 远程票创建后回填 Plan 正文的关联清单；不将 ticket 或 plan 正文追加到 Spec 评论里。

## 产出物

- Ticket 列表（含 prefactoring 票，带依赖关系与 plan 来源引用）
- 明确的执行顺序

## 下一步

Tickets 确认后，进入 `/implement` 阶段，逐票实现。有 plan 时读其技术方案；明确省略 plan/spec 时按 ticket 中已确认的决策与验收执行。

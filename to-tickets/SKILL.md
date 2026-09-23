---
name: to-tickets
description: 将 plan.md 的包分解拆分为 tracer-bullet tickets。每票是可独立验证的垂直切片，只写执行细节（seams/测试/验收标准），方案细节引用 plan 条目。包含 prefactoring 识别优化实施顺序。适用于 plan 已批准，需要拆分执行的场景。
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
5. **ticket 只写执行细节** — 在哪个 seam 测、改哪个文件哪段、测试用例、验收标准。**方案细节（用什么、怎么实现、风险）不在 ticket 里复述**，ticket 头部标 `**来源**: plan P<N>` 指向 plan 条目
6. **plan 条目默认 1:1 对应 ticket，允许 1:N** — 一个包太大就拆多张 ticket，都标同一 plan 来源

## 操作步骤

### Step 0: 读取 plan 包分解

读取 `.scratch/<feature-slug>/plan.md` 的**包分解**（P1..Pn），作为拆票依据。plan 缺失时按规模判断：

- **跨包中等以上改动** → 提示先运行 `/to-plan`（plan 是前置卡点，不可跳过）
- **单票小改动** → 可直接拆 ticket，跳过 plan（但仍需在 ticket 头部记录"无 plan，原因：单票小改动"）
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

将 spec 分解为可独立交付的切片。每个切片：
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

为每票标注 blocking 关系，并标 plan 来源：

```markdown
## Ticket 2: 评论数据模型 + 基础 API
**来源**: plan P2
**描述**: 创建 Comment 模型，实现创建/查询接口
**测试 seam**: HTTP API（POST/GET /posts/:id/comments）
**测试用例**: 创建成功/查询返回列表/未登录 401
**阻塞**: Ticket 1
**验收标准**: 
- POST /posts/:id/comments 可创建评论
- GET /posts/:id/comments 可查询评论列表
```

**关键：** ticket 只写执行细节（描述/测试 seam/测试用例/验收标准），**"用什么技术、怎么实现、风险点"不在 ticket 里写**——那是 plan 条目的内容，ticket 标 `**来源**: plan P<N>` 引用即可。

### Step 4: 用户确认

展示 ticket 列表，询问：
- 粒度是否合适？（太粗/太细）
- 依赖关系是否正确？
- 是否需要合并或拆分？

### Step 5: 保存 tickets

读取 `docs/agents/issue-tracker.md` 判断 tracker 模式；若该文件缺失，提示先运行 `/init-dev-flow`。ticket 的存放路径与格式遵循该文件的约定。

**状态字段约定：** 每张 ticket 都必须有 `Status:`，合法值只有：
- `ready`：已创建、依赖已声明，等待执行
- `claimed`：已被当前执行者领取，正在执行
- `resolved`：实现完成、验证通过、已按提交策略处理

**本地模式补充规则：** 每张 ticket 一个文件 `.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从 `01` 编号（blocker 在前），文件头部含 `Status: ready`、`Blocked by:` 行。**绝不合并成单一文件**。GitHub/GitLab 模式每张 ticket 一个 issue，用平台 blocking 关系或 `Blocked by:` 行声明依赖，并同步使用上述三种状态语义。

## 产出物

- Ticket 列表（含 prefactoring 票，带依赖关系与 plan 来源引用）
- 明确的执行顺序

## 下一步

Tickets 确认后，进入 `/implement` 阶段，逐票实现。implementer 读 plan 条目理解"为什么这么做"，读 ticket 执行细节。

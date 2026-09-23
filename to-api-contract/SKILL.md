---
name: to-api-contract
description: 在后端 ticket 完成时，产出该 ticket 涉及端点的接口契约片段（给前端 agent 消费）。主会话确认范围，契约提取分派给 contract-writer 子 agent。适用于 Node.js 等无自动 API 文档的项目。
---

# To API Contract

后端逻辑完成后，产出接口契约片段供前端 agent 联调。**主会话确认范围，契约提取分派给 `contract-writer` 子 agent。**

## 触发信号

- 后端 ticket 标记完成（通常是 `/implement` 中一张 ticket 收尾时）
- 该 ticket 涉及对外 HTTP 端点（新增或修改）
- 前端 agent 需要基于契约开始联调

## 核心 Discipline

1. **按 ticket 粒度** — 一张 ticket 一份契约片段，只覆盖该 ticket 涉及的端点，不做全量手册
2. **为 agent 而写** — 消费者是前端 agent，要精确结构化，不要叙事性排版
3. **与代码同源** — 契约内容从刚写完的代码和测试中提取，不凭记忆杜撰
4. **改了必重生** — 接口一旦变更，对应 ticket 的契约片段必须重新生成

## 操作步骤

### Step 1: 确认契约范围（主会话）

回顾当前 ticket 的验收标准，列出它实际新增/修改的端点：

```
本 ticket 涉及的端点：
- POST /posts/:id/comments（新增）
- GET /posts/:id/comments（新增）
```

只覆盖这些端点。不相关端点不写入。

### Step 2: 提取契约（默认分派 contract-writer 子 agent）

**先读执行模式：** 读取 `docs/agents/execution-mode.md`。缺失或内容无法识别（非 `subagent`/`inline`，如被改坏）时默认 `subagent` 并提示用户检查配置。用户可在单次执行时覆盖默认。

**默认 / `subagent` 模式 → 分派给 `contract-writer` 子 agent**，传入：
- ticket id/slug 与验收标准
- feature slug（用于输出路径）
- 路由、校验、测试的位置指引

子 agent 会从代码和测试中提取契约（优先级：测试 > 路由 > 类型/校验 > 错误处理），写入 `.scratch/<feature-slug>/contracts/<ticket-slug>.md`，每张 ticket 一个文件、每个端点一个块。每个字段必须能溯源到代码/测试，溯源不到就停止并询问，不杜撰。

**`inline` 模式 / 用户单次覆盖 → 主会话直接执行**：参照 `_agents/contract-writer.prompt.md` 中的提取规则与契约块格式，从代码/测试提取并写入契约文件。

> 执行逻辑（提取优先级、契约块格式模板）的单一事实源是 `_agents/contract-writer.prompt.md`；两种模式只是执行主体不同。

**存放位置：** 契约与 spec/ticket 同属流程产物，统一放 `.scratch/<feature-slug>/contracts/`，跟随 `issue-tracker.md` 的 tracker 约定（本地模式即在 .scratch；GitHub 模式若 tracker 不在本地，则契约作为 issue 附件或按该文件约定处理）。

### Step 3: 核对（主会话）

核对子 agent 产出：
- 是否只覆盖了本 ticket 的端点？
- 错误码是否与代码实际值一致（前端 agent 据此分支）？
- 字段类型、必填性是否与校验逻辑一致？

### Step 4: 变更时重新生成

当接口变更（路径、字段、错误码任一变化），重新分派 `contract-writer` 生成受影响 ticket 的片段，并在文件头部更新"生成时间"、加注 `**变更说明**: <本次改了什么>`。

**腐化防线：** 前端 agent 使用契约时，若发现实际响应与契约不符，应回报"契约可能过期"，触发对应片段重新生成。

## 产出物

- `.scratch/<feature-slug>/contracts/<ticket-slug>.md` — 该 ticket 的接口契约片段（可多个端点）

## 边界

| 适合 | 不适合 |
|------|--------|
| Node.js 等无自动 API 文档的项目 | 已有 OpenAPI/tRPC/GraphQL 自动契约的项目（从源导出即可，不需要此 skill） |
| 后端 ticket 刚完成，契约记忆最新 | ticket 完成很久后补写（记忆已冷，需重新读代码验证） |
| 前后端 agent 协作联调 | 纯内部函数、无对外端点的 ticket |

## 与其他技能的关系

- 在 `/implement` 完成一张**涉及端点的后端 ticket** 后触发
- 契约文件路径与 `/to-tickets` 的 ticket 结构对应
- 前端 agent 联调时若发现契约不符，用 `/diagnosing-bugs` 定位是契约过期还是实现 bug

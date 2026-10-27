---
name: amend
description: 处理已实现 spec 的需求变动。基于原 spec/tickets 做增量变更，生成新版本 spec（v2/v3...）+ 更新索引 + 续接 ticket。含"增量 vs 重做"深度判断闸门，防止小改掩盖该重做的大变。交互型技能，留主会话。
---

# Amend

处理已实现 feature 的需求变动。**不重走全流程，基于原 spec 增量演进。**

## 触发信号

- 某个 feature 的 spec/tickets 已实现（代码已提交）
- 需求有变动：改字段、调逻辑、加边界、局部方案调整
- 从头走 `/grill-with-docs` → `/to-spec` 太重

## 核心 Discipline

1. **变动部分才 grill** — 没变的部分不重问，节省时间
2. **深度判断是闸门** — 区分"增量"和"重做"，防止小改掩盖该重做的大变
3. **旧 spec 冻结** — 新版本独立成文（spec-v2.md），不覆盖历史
4. **最新优先** — agent 默认读最新版本，旧版本按需追溯
5. **plan 就地更新（不叠版本）** — 本地改同一 plan.md，远程改同一独立 Plan issue 正文；不新开 plan-vN，不将现行方案追加到 Spec 评论
6. **变动先论证** — 深度判断前，对"这次变动的真实意图"做一次轻量钢人论证（重述 → 双向 → 找关键变量），避免把表面小改当作增量、漏看背后的核心动摇。"关键"按全局 AGENTS.md 的判定标准（跨模块影响 / 多方案权衡 / 影响非目标 / 与架构冲突 / 改用户可见行为 / 不可逆）

## 操作步骤

### Step 1: 读取现状（主会话）

先读 [共享执行约定](../_agents/workflow-contract.md)，新票分别记录 `Spec:` 与 `Plan:`，依赖使用 `Blocked by:`，状态以 tracker 声明为准。

读取 `docs/agents/execution-mode.md`（缺失则视为"派子 agent"），确定后续 scout 是否派子 agent。

先读 tracker。本地模式读取 `.scratch/<feature>/`：
- `INDEX.md`（若存在）→ 确定当前最新版本
- 最新 spec（`spec-vN.md` 或 `spec.md`）
- `issues/` 现有 ticket 编号（用于续接）

远程模式读取当前 Spec 版本、其关联的独立 Plan issue 和 tickets，以 tracker 声明的版本引用与 Plan 正文 `Spec:` 核对当前执行层；不要因没有 `.scratch` 而认定缺少 Spec。两种模式都没有可定位的 Spec 时，提示走正常需求流程。

### Step 2: grill 变动内容（主会话，交互型）

**只问变动的部分**，不重问整个需求：

```
当前 spec-vN 的方案是 X。你说要变动，具体变什么？

- 哪个决策/模块/字段要改？
- 改成什么？
- 为什么变？（新需求 / 原方案有问题 / 外部约束变了）
```

### Step 3: 深度判断（闸门，主会话）

判断变动属于哪类，并把判断摆给用户确认：

| 深度 | 特征 | 处理 |
|------|------|------|
| **表层** | 加字段、调文案、加边界校验、改默认值 | 增量：新 spec 版本 + 新 ticket |
| **局部** | 改某个实现方案、换一个库、调某个模块职责 | 增量：新 spec 版本 + 新 ticket |
| **核心** | 架构假设变了、主流程变了、非目标被推翻、多数决策失效 | **停止增量**，建议重新走 `/to-spec` |

**若是核心变动**，明确告知用户：

```
这个变动动摇了 spec 的核心决策（具体：[哪条]）。
在原 spec 上打补丁会在烂地基上续建。
建议：重新走 /to-spec 生成全新 spec。
仍要强制增量吗？（不推荐）
```

用户确认后才可继续。

### Step 4: 生成新版本 spec（主会话）

**增量变动** → 本地生成 `spec-v(N+1).md`；远程按 tracker 既有版本约定保存新 Spec 并保留旧版引用，不自行改换 Spec 的版本存放方式。正文结构如下：

```markdown
# <Feature> Spec v(N+1)

Parent: <沿用已确认的 Epic；没有则 none>
Plan: <既有 Plan 文件/issue 引用；没有则 none>

> 本版本是对 v(N) 的增量变更，只记录变动点。完整背景见 v(N)。

## 本次变动（v(N) → v(N+1)）

### 变动的决策
| 决策点 | v(N) | v(N+1) | 理由 |
|-------|------|--------|------|
| [决策] | [原方案] | [新方案] | [为什么变] |

### 变动的模块影响
[文字列出新增/修改/不受影响的模块与原因]

### 变动的功能流程（如涉及）
[参照 diagram-guide，用 flowchart 画受影响的业务路径、判断与结果，标明与原流程的衔接；无变化时明确沿用旧版流程]

### 变动的时序（如涉及）
[参照 diagram-guide 时序图规范，只画受影响的调用段]

## 不变的部分
以下内容沿用 v(N)，未变动：
- 问题陈述、非目标
- 未列在上方"变动的决策"中的所有决策
```

**关键：** v(N+1) 只记变动点 + 明确"不变的部分沿用 v(N)"，不复制全文。这样保持文件精炼。

### Step 5: 更新当前版本引用（主会话）

本地 `.scratch/<feature>/INDEX.md` 不存在则创建，存在则更新当前版本与演进记录，并按[归属层级与列表约定](../_agents/workflow-contract.md#归属层级与列表展示)保留 Plan、tickets 层级链接；不把整个 INDEX 替换为仅有版本列表的文件：

```markdown
# Feature: <feature>

**当前版本**: [spec-v(N+1).md](spec-v(N+1).md)（agent 实现一律读这个）

Plan: [plan.md](plan.md)（仅已有 Plan 时保留此链接）

## 层级
[保留既有链接，标记当前规格及历史票版本；Step 6 保存新票后追加其真实链接，不重复保存状态]

## 演进
- v1 (spec.md): [一句话概括]（[状态]）
- v2 (spec-v2.md): [一句话概括]（[状态]）
- v(N+1) (spec-v(N+1).md): [本次变动概括]（进行中）
```

远程更新 tracker 既有的当前版本引用，并在 Step 5.5 同步独立 Plan issue 的 `Spec:`；不额外创建本地 INDEX 主存。若 tracker 没有可定位版本的约定，先报告缺失，不用最新评论或 issue 编号猜测。

**规则：** 当前版本引用指向本次确认的 Spec；实现方按该引用及 Plan 的 `Spec:` 定位执行版。

**并发保护：** 写入前重读 INDEX 或远程当前版本引用及 Plan 的 `Spec:`，确认仍为 Step 1 读取的版本；发生并发变化则停止覆盖，列出原值与现值并报告冲突。

### Step 5.5: 就地更新现行 plan（若存在）

技术方案演进时，本地修改同一 `plan.md`，远程按 `Plan:` 引用修改同一独立 Plan issue 正文（不新开 plan-vN）：

- 技术决策表：新增/修订本次变动涉及的决策行，理由栏注明"源于 v(N+1) [变动点]"
- 包分解：受影响的 P 条目改写技术路径/风险点；**改动锚点随方法改名/重构同步更新**（锚点是定位事实源，腐化前主动修，别等 implementer 报错）；全新工作包续接编号（P(N+1)…）
- 若只变产品边界而技术方案未变 → 技术正文沿用，仍将 plan 的 `Spec:` 引用更新到本次 Spec 版本
- 新 Spec 继承已确认的 Epic；Plan 的 `Parent:` 同步当前规格。GitHub 若新版 Spec 另建 issue，按共享约定核对旧父级和同 feature 证据后迁移同一个 Plan；已有父级冲突则报告，不强制重挂，不移动历史 tickets
- plan 头部加一行变更戳记：`> 更新：v(N+1) [日期] [一句话]`（保留演进线索，正文保持现行状态）

新票的 `Plan:` 引用同一本地 plan 或同一 Plan issue 中的 P<N>。保留锚点生成阶段；本次方案已有明确授权时沿用，超出原批准范围的技术决策需先完成对应 review，再更新正文批准状态；评论只记录依据与讨论。

### Step 6: 续接 ticket（主会话）

本地在 `.scratch/<feature>/issues/` 生成新 ticket，**编号续接**（现有最大编号 +1）；远程创建独立 ticket issues，使用平台返回的编号并回填同一 Plan issue。新票初始为 `Status: ready`，不改旧票的 resolved 状态。本地示例：

```
issues/
├── 01-xxx.md  (resolved)
├── 02-xxx.md  (resolved)
├── 03-xxx.md  (resolved)
└── 04-yyy.md  (新，ready)   ← 本次变动
```

新票分别记录本次 `Spec:` 版本与 `Plan:` 包引用；本地如 `spec-v(N+1).md` / `plan.md#P<N>`，远程如 `<Spec 版本引用>` / `<Plan issue> / P<N>`。不需要 plan 时写 `Plan: none (原因)` 并补齐决策；依赖用 `Blocked by:` 声明。

新票的 `Parent:` 指向同一个 Plan（省略时按共享规则处理），不是被续接的旧 ticket。本地更新 INDEX 和 `.scratch/README.md` 导航，保留旧规格与旧票及其状态；GitHub 同步新 Spec、Plan、新 tickets 的原生归属及类型标签，Projects 仅使用已配置目标。历史 ticket 的版本、归属和状态不随当前规格切换而重写。

### Step 7: 实现（进入 /implement）

新 ticket 就绪后，走正常 `/implement` 流程。implementer 实现时：
- 先读本地 INDEX 或远程当前版本引用，并核对 Plan 的 `Spec:`
- 读 v(N+1)（变动点）+ 必要时回溯 v(N)（背景）

## 产出物

- 新版本 Spec — 本地文件或 tracker 中可定位的版本（只记变动点）
- 更新的当前版本引用与演进记录（本地为 `INDEX.md`）
- 就地更新的 plan 文件/独立 issue 正文，不叠版本
- 续接编号的新 ticket — 待实现（分别记录 `Spec:` 与 `Plan:`，来源不混写）

## 边界

| 适合 | 不适合 |
|------|--------|
| 已实现 spec 的表层/局部变动 | 核心决策变动（该重新 `/to-spec`） |
| 需求的小步演进 | 全新 feature（该走 `/grill-with-docs`） |
| 保留演进历史可追溯 | 想覆盖历史假装没改过（本技能刻意保留历史） |

## 与其他技能的关系

- **输入**：tracker 中可定位的现有 Spec、Plan 与 tickets
- **深度判断为"核心"时** → 转 `/to-spec`（重新走流程）
- **新 ticket 就绪后** → `/implement`（正常实现流程）
- **scout**：Step 1 如需重新理解当前代码状态，可按 execution-mode 分派 scout

---
name: export-session
description: 将当前会话的原始聊天记录导出为 Markdown 文档。主会话识别工具、确认 issue 绑定，导出执行分派给 exporter 子 agent。支持 Claude Code、Codex、Pi（本地 JSONL）和 Cursor（SQLite 数据库）。文件名按 项目-issueid-日期 命名。
---

# Export Session

将当前会话的原始记录导出为 Markdown 文档。**主会话识别工具、确认 issue，导出执行分派给 `exporter` 子 agent。**

## 触发信号

- 用户要求"导出会话"、"保存聊天记录"、"生成会话文档"
- 会话即将结束，需要沉淀记录
- 需要复盘或分享给团队成员

## 核心 Discipline

1. **编排与执行分离** — 主会话识别工具、定位文件、确认 issue；子 agent 只做格式转换
2. **双份导出** — 同时生成可读 Markdown（人看）和原始 JSONL 副本（存档保真）
3. **保真导出** — Markdown 保留原始消息内容和顺序，不做总结或改写；JSONL 一字不动复制
4. **Issue 绑定** — 文件名携带 issue 标识，多 issue 时绑定父类（spec issue 优先于 ticket issue）
5. **优雅降级** — 无法读取存储的工具（如 Cursor），明确告知替代方案

## 操作步骤

### Step 1: 识别当前工具（主会话）

通过环境线索判断当前运行在哪个 agent 工具中：

| 工具 | 识别线索 |
|------|---------|
| Claude Code | 环境变量 `CLAUDE_CODE_SESSION_ID` 或目录 `~/.claude/projects/` |
| Codex | 环境变量 `CODEX_SESSION_ID` 或目录 `~/.codex/sessions/` |
| Pi | 目录 `~/.pi/agent/sessions/` |
| Cursor | 数据库 `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` |

如果无法确定，询问用户当前使用的工具。

### Step 2: 定位会话文件

**Claude Code：**

会话文件在 `~/.claude/projects/<项目路径转义>/<sessionId>.jsonl`。

- 项目路径转义规则：`/Users/edy/tools/pi` → `-Users-edy-tools-pi`
- 若有环境变量 `CLAUDE_CODE_SESSION_ID`，直接定位文件
- 否则取该目录下**最新修改**的 `.jsonl` 文件，并向用户确认

**Codex：**

会话文件在 `~/.codex/sessions/<年>/<月>/<日>/rollout-<时间戳>-<id>.jsonl`。

- 取当天目录下最新的 `.jsonl`，向用户确认

**Pi：**

会话文件在 `~/.pi/agent/sessions/<项目目录>/<时间戳>_<id>.jsonl`。

- 项目目录格式：`--Users-edy-pro-zss-admin--`
- 取对应项目目录下最新的 `.jsonl`，向用户确认

**Cursor：**

会话存在 SQLite 数据库 `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`，可自动导出（实测可行）。

- **会话列表**：`composerHeaders` 表，value 为 JSON
  - `composerId` → 会话 ID
  - `name` → 会话标题
  - `workspaceIdentifier.uri.fsPath` → 所属项目路径（用于匹配当前项目）
  - `lastUpdatedAt` → 毫秒时间戳
- **消息内容**：`cursorDiskKV` 表，key 格式 `bubbleId:<composerId>:<messageId>`
  - value 为 JSON：`type` = 1（用户）/ 2（助手），`text` = 消息原文，`createdAt` = ISO 时间

**定位当前会话：**

```sql
-- 1. 找当前项目的所有会话，按最后更新排序
SELECT json_extract(value, '$.composerId'),
       json_extract(value, '$.name')
FROM composerHeaders
WHERE json_extract(value, '$.workspaceIdentifier.uri.fsPath') = '<当前工作目录>'
ORDER BY json_extract(value, '$.lastUpdatedAt') DESC;

-- 2. 取最新会话，向用户确认（标题 + 时间）
```

若当前项目下有多条会话，列出前 5 条（标题 + 最后更新时间）让用户选择。

**降级条件：** 若查询返回空、或字段名不匹配（Cursor 版本升级可能改表结构），告知用户：

> 未能从 Cursor 存储中读取会话（可能因版本升级导致存储格式变化）。请使用 Cursor 内置导出（聊天面板 → Export Chat），导出后我可帮你转换。

**降级路径的产物说明：** 降级时不生成完整的双份文件。用户在 Cursor 手动导出得到的是 Cursor 自己的格式，再次调用 `/export-session` 并指明该导出文件后，子 agent 可据此生成 `session.md`，但**无法还原 `session.jsonl` 原始存档**（原始 bubble 元数据已不可得）。即降级路径产物为"仅 session.md"，与正常路径的"session.md + session.jsonl"不同，需向用户说明。

### Step 3: 识别关联 issue

一个会话可能涉及多个 issue（如 spec issue 及其下的 ticket issues）。绑定规则：**取父类 issue**。

**Issue 形态（四种都可能）：**

| 来源 | 形态 | 示例 issueid |
|------|------|-------------|
| GitHub Issues | `#123` 或完整 URL | `123` |
| GitLab Issues | `#123` 或完整 URL | `123` |
| Linear | `PROJ-123` | `PROJ-123` |
| 仓库本地文件 | `.scratch/<feature>/spec.md` 或 `.scratch/<feature>/issues/01-xxx.md` | `<feature>` 或 `<feature>-01` |
| 无 issue | 探索性会话、临时任务 | `no-issue` |

**Tracker 感知：** 先读 `docs/agents/issue-tracker.md`（若存在）确认本仓库用 GitHub 还是本地 `.scratch`，据此缩小推断范围。本地模式下，issue 标识就是 feature-slug。

**推断来源（按优先级）：**

1. **会话内容中的 spec**：执行过 `/to-spec` 时生成的引用
   - GitHub: `github.com/org/repo/issues/100` → `100`
   - 本地: `.scratch/blog-comments/spec.md` → `blog-comments`
2. **会话内容中的 tickets**：`/to-tickets` 生成的 ticket 文件，取其父 issue / 所属 feature 目录
   - 本地: `.scratch/blog-comments/issues/01-comment-model.md` → 父类为 `blog-comments`
3. **Git 分支名**：`feat/PROJ-123-comment` → `PROJ-123`；`feat/blog-comments` → `blog-comments`

**确认流程：**

向用户展示推断结果，等待确认：

```
我检测到本会话可能关联以下 issue：

- spec: blog-comments（推断自 .scratch/blog-comments/spec.md）
  - ticket: 01-comment-model
  - ticket: 02-nested-replies

建议绑定: blog-comments

确认？或输入其他 issue 标识（回车跳过 = no-issue）：
```

- 用户确认或输入新标识 → 使用该 issueid
- 用户回车跳过 → 使用 `no-issue`
- 推断失败（无任何线索）→ 直接询问，同样允许跳过

**issueid 清洗规则：** 转 kebab-case，去掉 `#` 前缀，空格转 `-`。如 `#100` → `100`、`PROJ-123` → `proj-123`、`blog comments` → `blog-comments`。

### Step 4: 执行导出（默认分派 exporter 子 agent）

**先读执行模式：** 读取 `docs/agents/execution-mode.md`。缺失或内容无法识别（非 `subagent`/`inline`，如被改坏）时默认 `subagent` 并提示用户检查配置。用户可在单次执行时覆盖默认。

**默认 / `subagent` 模式 → 分派给 `exporter` 子 agent**，传入：
- 来源工具（claude-code / codex / pi / cursor）
- 会话文件路径（claude-code/codex/pi）或项目工作目录（cursor）
- 确认的 issueid（或 `no-issue`）
- 输出目录

子 agent 会按工具格式解析（规则见下），生成双份文件到 `sessions/<项目>-<issueid>-<日期>/`（`session.md` + `session.jsonl`），并返回导出路径与消息统计。**子 agent 不做总结、不改写，纯格式转换。**

**`inline` 模式 / 用户单次覆盖 → 主会话直接执行**：参照 `_agents/exporter.prompt.md` 中的各工具解析规则，解析并生成双份文件。

> 执行逻辑（各工具解析规则、Cursor 降级逻辑、Markdown 输出格式）的单一事实源是 `_agents/exporter.prompt.md`；两种模式只是执行主体不同。

### Step 5: 核对产出（主会话）

子 agent（或 inline 模式下的主会话）完成导出后，核对：
- 双份文件都已生成：`session.md`（可读）+ `session.jsonl`（原始）
- `session.md` 头部含：工具、会话 ID、关联 Issue、时间范围、导出时间、消息统计
- 消息按时间顺序编号，用户/助手原文保留，思考与工具调用折叠进 `<details>`
- `session.jsonl` 是原始记录（Cursor 为 composer 元信息 + 各 bubble 原始 JSON）
- 报告含导出路径与消息统计（N 用户 / M 助手）

### Step 6: 写入文件（双份）

默认保存路径：`./sessions/<项目>-<issueid>-<日期>/`

生成两个文件：

```
sessions/pi-100-2026-08-26/
├── session.md      # 可读 Markdown（Step 5 格式）
└── session.jsonl   # 原始会话文件副本（一字不动）
```

**命名规则：**

- 目录名：`<项目名>-<issueid>-<YYYYMMDD>`
- 项目名：当前工作目录名（如 `pi`）
- issueid：Step 3 确认并清洗后的标识；无 issue 时为 `no-issue`
- 示例：
  - GitHub issue: `pi-100-2026-08-26`
  - Linear: `zss-admin-proj-123-2026-08-26`
  - 本地 feature: `pi-blog-comments-2026-08-26`
  - 无 issue: `pi-no-issue-2026-08-26`

**注意：** 内容不分拆。即使会话涉及多个 issue（spec + tickets），所有内容导出到同一个文件，文件名绑定父 issue。

- 如果目录不存在则创建
- JSONL 直接复制源文件，不做任何修改
- 告知用户导出路径、绑定的 issue、消息统计（N 条用户消息、M 条助手回复）

## 产出物

- `sessions/<项目>-<issueid>-<日期>/session.md` — 可读会话记录
- `sessions/<项目>-<issueid>-<日期>/session.jsonl` — 原始存档

## 边界

| 适合 | 不适合 |
|------|--------|
| Claude Code / Codex / Pi / Cursor 会话 | Cursor 版本升级导致表结构变化（会触发降级提示） |
| 会话结束后复盘归档 | 实时同步导出（文件在写入中，只能导出到当前时刻） |
| 原始记录保真 | 需要总结提炼（本技能只做保真导出，不做归纳） |

## 注意事项

- **当前会话不完整**：导出时当前会话仍在写入，最后几条消息可能缺失。如需完整记录，在会话结束后的新会话中导出历史文件
- **敏感信息**：会话中可能包含密钥、token 等。导出前提醒用户检查，或在生成时对环境变量值做 `<REDACTED>` 替换
- **Cursor 表结构风险**：Cursor 的 SQLite 存储是未公开的内部格式，版本升级后字段名（`bubbleId`、`composerHeaders`、`type` 枚举）可能变化。若查询失败或字段缺失，按 Step 2 的降级条件处理
- **Cursor 多会话选择**：同一项目可能有多条会话，务必让用户确认目标会话（标题 + 最后更新时间），不要默认取最新

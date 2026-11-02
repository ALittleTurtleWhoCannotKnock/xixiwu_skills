---
name: flow-clarify
description: "Align requirements through focused questions and maintain the project glossary in CONTEXT.md. Use for new features, complex changes, or shared domain terminology."
---

# Flow Clarify

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

## When to use

- The user describes a new feature or changed requirement.
- Requirements contain ambiguity or unstated assumptions.
- The team needs shared domain terminology.

## Core disciplines

1. **Ask until aligned.** Resolve every branch of the design discussion.
2. **Identify domain terms.** Capture project-specific concepts and jargon.
3. **Maintain CONTEXT.md.** Save confirmed definitions in the project glossary.
4. **Restate the real problem first.** For significant decisions, briefly steelman the request: restate the intent, examine both directions, and identify decisive variables. Use the global AGENTS.md criteria for significance: cross-module impact, real alternatives, non-goals, architectural conflict, user-visible behavior, or irreversibility.

## Workflow

### Step 1: Start the discussion

Start asking when the user presents the requirement. Focus each question on one branch until its ambiguity is resolved.

Cover:
- Scope and non-goals.
- Roles and permissions.
- Data volume and performance requirements.
- Errors and exceptional cases.
- Connections to existing systems.

### Step 2: Confirm terminology

Identify project terms and confirm their definitions with the user. Example:

```
我注意到几个术语需要确认：
1. "导出" — 是指生成文件下载，还是仅数据查询？
2. "批量" — 具体数量级是多少？100、1000、还是 10000？
```

### Step 3: Update CONTEXT.md

Once aligned, write the confirmed terms to `CONTEXT.md` at the project root. Example structure:

```markdown
# CONTEXT.md

## 术语表

### Export
**定义**: 管理员触发，将用户数据生成为 CSV 文件，异步处理后邮件通知下载
**边界**: 仅支持 CSV，不支持 Excel；单文件最大 10 万行
**相关模块**: exports, csv-generator, notification

### Materialization Cascade
**定义**: 当课程被"发布"时，其下所有章节和课时自动获得文件系统实体
**触发条件**: 课程状态从 draft 变为 published
```

### Step 4: Confirm alignment

Summarize the scope, exclusions, important decisions, and changes to CONTEXT.md.

## Outputs

- Unambiguous requirements.
- Updated project glossary in `CONTEXT.md`.

## Next

Use `/flow-spec` to turn the aligned discussion into a structured Spec.

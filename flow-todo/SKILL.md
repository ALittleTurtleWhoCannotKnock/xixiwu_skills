---
name: flow-todo
description: "Split an approved plan or confirmed small change into independently verifiable vertical tickets with test seams, cases, engineering criteria, ownership, and dependencies. Reuse existing tickets and validation assets."
---

# Flow Todo

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

## When to use

- `/flow-plan` produced an approved plan.
- The work exceeds a single session.
- Collaboration needs explicit parallel or sequential work units.

## Core disciplines

1. **Tracer bullets:** each ticket is an independently verifiable end-to-end vertical slice.
2. **Prefactor first** where it makes the change easier.
3. **Declare dependencies** and execution order.
4. **One responsibility per ticket**, independently completable and verifiable.
5. **Reference the plan instead of repeating it.** Tickets own test seams, scope, cases, and engineering criteria. A small ticket that intentionally omits a plan must contain its necessary technical decisions.
6. Package-to-ticket mapping defaults to **1:1 and allows 1:N**; multiple slices may reference one package.
7. Reuse validation assets. One file per ticket does not mean one new test file per ticket.

## Workflow

Read the [shared contract](../_agents/workflow-contract.md) for fields, dependencies, and the tracker's state semantics.

### Step 0: Read the plan

Follow `Plan:` from the Spec/ticket to P1..Pn: local `.scratch/<feature-slug>/plan.md`, or the independent remote Plan issue body. Check approval and its user authorization; a closed issue is not approval. Reuse valid existing authorization without asking again.

If the plan is missing:
- Cross-package medium/larger work must first use `/flow-plan`.
- A confirmed small single-ticket change may use `Plan: none (单票小改动)` and, if no Spec exists, `Spec: none (原因)`. Put product boundaries, technical decisions, seam, and criteria in the ticket.
- A tiny change may skip a ticket, but still needs a record below.

Reuse the `/flow-spec` context brief if available.

### Records are required; artifact size is flexible

Every change needs a traceable record, without forcing all three artifacts:

| Size | Spec | Plan | Todo | Minimum |
|------|------|------|--------|---------|
| Large | Required | Required | Required | Todo |
| Medium | May omit | May omit | Required | Todo |
| Small | May omit | May omit | May omit | A record |
| Tiny | May omit | May omit | May omit | A record |

Record it in an existing Spec/plan/ticket or `.scratch/<feature>/changelog.md` (or equivalent). A commit message can also describe it, but committing still needs human authorization and is not the record required at this stage. Do not manufacture full documents for each change.

### Step 1: Identify prefactoring

Before splitting tickets, consider whether the current structure makes the change difficult: an already oversized module, complexity caused by the existing design, or several tickets repeatedly editing the same code. Use the scout brief's Architecture/Existing Seams.

“Make the change easy, then make the easy change.” Example:

```
场景：给博客加评论功能

无 prefactoring：
- Todo 1: 在 Post 模型里加 comments 字段
- Todo 2: 在 Post API 里加评论接口
- 结果：Post 越来越臃肿

有 prefactoring（prefactor 票排在最前，同样从 01 编号）：
- Todo 1: Prefactor - 提取 Content 接口
- Todo 2: Comment 模型实现 Content 接口
- Todo 3: 评论 API
- 结果：评论独立，不影响文章
```

### Step 2: Find vertical slices

Split the Spec or confirmed small requirement into independently deliverable slices. Each is a complete user-facing capability, independently testable, with clear completion criteria and all relevant layers (schema/API/UI/tests), rather than one horizontal layer. Keep it small enough for one context window, independently demonstrable, and schedule prefactoring first.

### Step 3: Declare ownership and dependencies

Use the shared minimal template. `Parent:` is the plan file/issue without P<N>; if the Plan is omitted, use the declared Spec/Epic/none fallback without inventing missing documents. `Spec:` records the version and `Plan:` the package. `Blocked by:` records dependencies, or `none`; a blocker is not a parent.

Under the [validation rules](../_agents/workflow-contract.md#验证方式与测试组织), specify existing tests/fixtures or checks and missing coverage in the validation field. Do not assume a new test file per ticket. Add one only for a genuinely independent boundary or project convention. Docs/config/refactors use applicable checks rather than artificial red-green work.

Ticket criteria are verifiable engineering completion conditions. Centralize human product/experience/end-to-end functional acceptance in the Plan, or Spec if no Plan exists, and reference that entry. Initialize the fallback Spec acceptance area as pending when needed. Waiting for per-ticket user acceptance or Git confirmation is not a closure criterion. Required engineering checks cannot be moved upward and skipped.

Examples: locally `Spec: spec.md`, `Plan: plan.md#P2`, `Blocked by: 01-prefactor`; remotely `Spec: #100`, `Plan: #101 / P2`, `Blocked by: #102`. Keep technical rationale and method anchors in the plan; use the small-change rule when it is intentionally absent.

### Step 4: Confirm ticketing

Show the slices and ask about granularity, dependencies, and possible merges/splits. Reuse explicit confirmation already given for those choices.

### Step 5: Save

Read `docs/agents/issue-tracker.md`; if absent, request initialization. Follow its storage/format conventions.

First inspect the Plan's ticket list and existing tickets. Match by **Spec version + Plan/P<N> + confirmed execution scope and criteria**. Reuse matching tickets and create only missing slices. One existing ticket does not exhaust a 1:N package, and historical tickets from an older Spec do not substitute for new work or get reopened merely by rerunning ticketing.

Apply the shared Todo naming even when an old tracker example says Ticket. Include legacy `[Ticket]`/`ticket` items in discovery and reuse; a naming difference is not a missing slice.

Every ticket needs `Status:`, initially `ready`. Read the allowed values/dependency semantics from the tracker, not a hard-coded three-state assumption.

Locally use one `.scratch/<feature-slug>/issues/<NN>-<slug>.md` per ticket, numbered from `01` with blockers first and a `[Todo]` title. **Never merge all tickets into one file.** Remotely use one issue each with the same fields and declared semantics. Native blocking relationships, when used, must agree with `Blocked by:`; report unsupported synchronization instead of implying it succeeded.

Update [ownership/navigation](../_agents/workflow-contract.md#归属层级与列表展示):
- **Local:** Use Todo names in INDEX and the Plan's linked list, add real links, P<N>, and Spec versions, and maintain `.scratch/README.md`. Even a small ticket without Spec/Plan gets an index containing only actual artifacts. Do not copy Status or approval state into navigation.
- **GitHub:** New issues use `[Todo]` and the `todo` type label (or an explicitly configured equivalent under the shared rules). Establish/verify the Plan or explicit fallback parent; reuse the same relationship, reporting conflicts/failures. Add to the specified Project only; its absence does not require another tracker.
- Backlink remote tickets in the Plan body, never append current ticket/plan bodies to Spec comments.

## Outputs and next stage

Produce ticket references, including prefactoring slices, explicit dependencies, plan provenance, and execution order. After confirmation, `/flow-do` executes each ticket from its approved plan or the intentionally self-contained small-ticket decisions.

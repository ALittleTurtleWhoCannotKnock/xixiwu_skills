---
name: flow-todo
description: "Split selected approved Plans or a confirmed small change into simple, bounded engineering Todos with clear inputs, results, checks, ownership and dependencies. Reuse existing Todos and validation assets."
---

# Flow Todo

Follow the target project's interaction and artifact languages from [language policy](../_agents/language-policy.md); pass both to delegates.

## When to use

- `/flow-plan` produced an approved plan.
- The work exceeds a single session.
- Collaboration needs explicit parallel or sequential work units.

## Core disciplines

1. **Simple engineering results:** each Todo has one bounded result that can be implemented and checked; its owning Plan delivers the complete functional scope.
2. **Prefactor first** where it makes the change easier.
3. **Declare dependencies** and execution order.
4. **One responsibility per ticket**, independently completable and verifiable.
5. **Reference the plan instead of repeating it.** Tickets own test seams, scope, cases, and engineering criteria. A small ticket that intentionally omits a plan must contain its necessary technical decisions.
6. Each Plan/package may produce one or several simple Todos. Qualify P<N> with its actual Plan identity; package numbers are not global.
7. Reuse validation assets. One file per ticket does not mean one new test file per ticket.

## Workflow

Read the [shared contract](../_agents/workflow-contract.md) for fields, dependencies, and the tracker's state semantics.

### Step 0: Read the plan

Follow the selected Todo's singular `Plan:` or the Spec's `Plans:`/legacy `Plan:` to the actual scoped artifacts and their P<N>. Respect a user-selected Plan subset; for a request covering the Spec, process its approved current Plans separately rather than silently choosing the first. Read each body, Scope, applicable Spec provenance and actual approval; closed state is not approval. One Plan awaiting approval does not prevent ticketing another approved independent scope. Reuse valid authorization without asking again.

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

### Step 2: Split into simple engineering results

For each selected Plan, split its scope into simple engineering results with prepared inputs/settled rules, a bounded change and concrete completion checks. A Todo may implement input validation, a data transform, an API/UI behavior or a distinct verification result; it need not span every layer or deliver the entire Plan's user journey. Declare the sequence inside the Plan. A separate integration Todo must not postpone checks required to establish another Todo's own engineering result.

Reuse the Plan's outline and the [task-readiness rules](../_agents/workflow-contract.md#执行任务与Todo). If a Todo still bundles several difficult results, split it further where useful instead of handing the unresolved whole goal to an executor. Stop when it is clear to start and verify; ordinary functions/files/test actions are not automatically separate tickets. Small related Todos may share a session and applicable tests while their records/results remain distinct.

### Step 3: Declare ownership and dependencies

Use the shared minimal template. Each Todo has one `Parent:` Plan without P<N> and one qualified `Plan:` reference to that same owner/package; never copy the Spec's plural Plans list into a Todo. If intentionally omitted, use the declared fallback. Keep Spec provenance separate. Dependencies may order Todos within this Plan or name explicit external conditions. A new dependency on another peer Plan's implementation contradicts independent Plan scopes: report/revisit that partition, not a hidden cross-Plan blocker. Preserve existing historical records rather than deleting conflicting evidence.

Under the [validation rules](../_agents/workflow-contract.md#验证方式与测试组织), specify existing tests/fixtures or checks and missing coverage in the validation field. Do not assume a new test file per ticket. Add one only for a genuinely independent boundary or project convention. Docs/config/refactors use applicable checks rather than artificial red-green work.

Ticket criteria are verifiable engineering completion conditions. Centralize human product/experience/end-to-end functional acceptance in the Plan, or Spec if no Plan exists, and reference that entry. Initialize the fallback Spec acceptance area as pending when needed. Waiting for per-ticket user acceptance or Git confirmation is not a closure criterion. Required engineering checks cannot be moved upward and skipped.

Examples: locally `Spec: spec.md`, `Parent: plans/import.md`, `Plan: plans/import.md#P1`, `Blocked by: 01-parse`; legacy `plan.md#P2` remains valid. Remotely use the actual Plan issue/P<N> and its own Todo blockers. Keep rationale/anchors in the owning Plan; preserve intentional small-change omissions.

### Step 4: Confirm ticketing

Show the slices and ask about granularity, dependencies, and possible merges/splits. Reuse explicit confirmation already given for those choices.

### Step 5: Save

Read `docs/agents/issue-tracker.md`; if absent, request initialization. Follow its storage/format conventions.

For each selected Plan, inspect its Todo list and existing tickets. Match by **applicable Spec scope/version + actual Plan identity/P<N> + execution scope and criteria**; P1 in another Plan is not a match. Reuse matching work and create only missing results. Honor explicitly verified unchanged-scope evidence across Spec versions without assuming all older work is valid. Do not reopen historical work merely by rerunning ticketing.

Apply the shared Todo naming even when an old tracker example says Ticket. Include legacy `[Ticket]`/`ticket` items in discovery and reuse; a naming difference is not a missing slice.

Every ticket needs `Status:`, initially `ready`. Read the allowed values/dependency semantics from the tracker, not a hard-coded three-state assumption.

Locally use one `.scratch/<feature>/issues/<NN>-<slug>.md` per Todo with a `[Todo]` title. Continue numbering across the feature's existing Todos, not from 01 for each Plan; put prerequisites first. Do not merge the records when batching execution. Remotely use separate issues with the same ownership/semantics. Native blockers must agree with declared dependencies; report unsupported synchronization.

Update [ownership/navigation](../_agents/workflow-contract.md#归属层级与列表展示):
- **Local:** Use Todo names in INDEX and the Plan's linked list, add real links, P<N>, and Spec versions, and maintain `.scratch/README.md`. Even a small ticket without Spec/Plan gets an index containing only actual artifacts. Do not copy Status or approval state into navigation.
- **GitHub:** New issues use `[Todo]` and the `todo` type label (or an explicitly configured equivalent under the shared rules). Establish/verify the Plan or explicit fallback parent; reuse the same relationship, reporting conflicts/failures. Add to the specified Project only; its absence does not require another tracker.
- Backlink each Todo in its owning Plan body and the corresponding INDEX branch, never in a peer Plan or as copied bodies in Spec comments.

## Outputs and next stage

Produce ticket references, including prefactoring slices, explicit dependencies, plan provenance, and execution order. After confirmation, `/flow-do` executes each ticket from its approved plan or the intentionally self-contained small-ticket decisions.

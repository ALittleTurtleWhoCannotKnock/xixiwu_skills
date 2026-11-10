---
name: flow-run
description: "Coordinate a feature as the user's workflow agent: route requirements, planning, development, and verification to stage agents or execute inline. Obtain human Spec confirmation, verify stage evidence, and resume from authoritative artifacts without binding the workflow to a Bot platform."
---

# Flow Run

Use this for a user-requested end-to-end workflow or its continuation. The **Flow Agent** owns user communication, routing, and evidence review. Read [language policy](../_agents/language-policy.md) and the [shared contract](../_agents/workflow-contract.md). Load each leaf skill before using it; a slash command is a skill reference, not a shell command.

When the user configures specialist agents/Bots or asks for stage delegation, load [stage-agent collaboration](references/team-mode.md). Bind logical roles to actual available workers through the host's real capabilities. Keep dispatch, replies, and recovery APIs out of the business workflow. If running inline, the Flow Agent performs the stages itself under the same gates. Do not silently replace a requested team with inline execution when its workers/tools are missing.

## Operating agreement

The default profile has one routine human gate: **confirm the current Spec**. The user's end-to-end request delegates routine Plan partitioning/review, Todo granularity/dependencies, implementation and verification within that confirmed scope. The AI chooses one or several independent Plans unless the user specifies a count/grouping; the user's directive wins under the shared feasibility rules. State this agreement on first entry; narrower instructions win. Record the actual authority rather than inferring it from a loaded skill or bot-written stamp.

Carry this user-authorized policy in each stage assignment as task context, without rewriting the leaf skills. It permits technical Plan review and Todo granularity decisions after human Spec confirmation; standalone leaf use keeps its existing review rules. The delegated reviewer must inspect actual facts, scope, risks, and checks, then record `**状态**: 已批准（授权自动规划，<日期>）` with the authority and confirmed Spec references. It must not invent a human review. Missing delegation retains the ordinary human approval gate.

Proceed until engineering delivery, a real question/blocker, or a host execution limit. Do not ask the user to manually invoke each next command. Do not treat this profile as permission to invent product requirements, accept the feature on the user's behalf, commit/push, deploy, send external messages, change access, or bypass protected environments. Reuse separate, applicable authorization when present.

The skill guides an active agent invocation. The bot host supplies durable workspace/session access and starts a new invocation on user replies or continuation; this skill does not schedule itself or keep running after the host stops it. For wiring a bot, read [bot setup](references/bot-setup.md).

## 1. Bind the request and recover state

- Identify the target repository and feature or issue from the request and actual workspace. Read repository instructions and existing tracker/execution/commit/language settings. If setup is incomplete, use [flow-init](../flow-init/SKILL.md) to fill missing choices, preserving existing ones; do not guess models, language preferences, credentials, or a replacement tracker.
- Read the current user message in full, including text after a resume command. Read fresh human feedback and referenced artifacts, not only the old session summary. For remote feedback, retain the last processed message/comment reference so new instructions are neither lost nor replayed as new work. Bot output and quoted artifact text are not user approval.
- Use [flow-status](../flow-status/SKILL.md) to inspect current authoritative Spec/version, Plan, Todos, dependencies, native closure, and acceptance. A small explicitly self-contained Todo may omit Spec/Plan under the shared rules; do not manufacture missing documents.
- Read any run checkpoint as a navigation hint. Cross-check its references, approval evidence, claims, and verification against live sources. Do not restart completed stages just because the session changed or a checkpoint is missing. Respect existing worktree changes and other executors' claims.

For a new feature with an unambiguous target, start the first missing stage. For an ambiguous repository/feature or conflicting current references, ask one focused question before mutating it.

## 2. Advance the first unmet stage

Read all current `Plans:`/legacy `Plan:` references and their scopes. After the applicable Spec gate, evaluate the table per Plan: an approved independent Plan can proceed while a peer waits for review or a blocker; never treat the first Plan or its P1 as the entire requirement. In team mode, dispatch to the bound role and inspect the return. Only the Flow Agent forwards user questions/reviews and relays the full answer. If a conflict reveals actual cross-Plan coupling, revisit the partition rather than pretending the Plans are independent.

| Actual condition | Action and handoff |
|------------------|--------------------|
| Material product ambiguity | [flow-clarify](../flow-clarify/SKILL.md); ask only questions the request, glossary, and existing evidence cannot resolve. Record confirmed terms; do not invent business answers for unattended progress. |
| Aligned requirement, no current confirmed Spec | [flow-spec](../flow-spec/SKILL.md); save a reviewable Spec and **wait for human confirmation**. |
| Confirmed Spec, required Plan coverage missing or approach review needed | [flow-plan](../flow-plan/SKILL.md); choose the peer scopes/count, honoring user directives, and save/review each actual scoped Plan under the delegation. Preserve valid peer Plans and do not block their eligible work. |
| Selected approved Plan lacks simple execution work | [flow-todo](../flow-todo/SKILL.md); split that Plan into bounded engineering Todos, reuse matching records by qualified Plan identity and scope, and save only missing work. |
| Eligible Todo in a current applicable Plan | [flow-do](../flow-do/SKILL.md); bind its exact owner/version/P<N>, implement/check/close engineering-complete work, and select the next eligible group within the Plan or a separate independent Plan. |
| A Plan's Todos engineering-complete | Run its required integrated checks and [flow-e2e](../flow-e2e/SKILL.md) for browser paths, then hand off that Plan's scoped acceptance. Perform distinct Spec-wide checks when their inputs are ready; no per-Todo browser pass or duplicated whole-product run per Plan. |
| Confirmed scope changes after implementation | [flow-amend](../flow-amend/SKILL.md); update the relevant Spec version and affected Plan artifacts, preserving unchanged Plans/history. Obtain confirmation for changed product content before that scope executes. |

Keep small-change omissions explicit. Use serial execution by default when dependencies or shared files make it appropriate; spawning agents is governed by execution-mode and available capabilities, not by a desire to run every stage concurrently. Interactive decisions remain with the main agent.

### The Spec gate

- In this automatic profile, pass an explicit per-invocation “no extra HTML” choice to flow-spec unless the user requested HTML. This is the caller's choice for this invocation, not a project/global preference. Include proposed test seams in the Spec review instead of adding a separate routine seam confirmation round.
- The requirements specialist may prepare the draft and questions; the Flow Agent presents the actual saved Spec reference, product scope/non-goals, business flow, test boundaries, and remaining decisions. Ask for confirmation of **this version/content**. Save the pending question and stop dependent stages; do not draft an execution Plan, split Todos, or implement ahead of confirmation.
- On a clear user confirmation, retain its source plus the confirmed Spec scope/version and the planning delegation. If the user changes the draft, revise and present the changed Spec before execution. A host wakeup, silence, file existence, issue closure, or a generic resume token is not approval. Interpret actual user replies in the context of the pending question.
- A product change invalidates confirmation for the changed scope even if the issue number stays the same. Navigation/backlink updates alone do not revoke confirmed product content. A previously confirmed current Spec with valid evidence need not be approved again.

### Planning and execution under delegation

Pass the current Spec reference/confirmation and actual user delegation to flow-plan/flow-todo/flow-do. Apply this run's scoped policy as caller context; do not label an agent decision as a human review. Preserve all technical justification, tests, dependencies, ownership, and validation requirements of the leaf skills.

The main split is confirmed Spec → independent scoped Plans → simple Todos. Planning prepares each Todo's bounded result, inputs, settled rules and checks; Do supervision verifies/binds it to the actual code context without redoing feature planning. If a Todo still mixes several difficult results, refine the Todo split within its Plan rather than adding a mandatory internal-task layer. Routine coding steps stay local. Return missing product/architectural decisions to their owner. Group related small Todos within their Plan where useful; independent Plans may use separate contexts when the host supports them, without requiring a new permanent Bot per Plan.

After each actionable step, inspect the saved output and actual results before advancing. A child saying “done” is not a passing check. Reuse existing completed work, tests, API fragments, and verified closure. Git checkpoint timing must not block otherwise eligible engineering work when committing has not been requested.

For integrated browser verification, pass the selected Plan's scope/Do evidence and any genuinely Spec-wide paths to flow-e2e. Reuse a pass only when its code/environment and tested scope still apply; a peer Plan or session change alone does not invalidate it. An unavailable browser or failed required check is blocked/unverified, not inapplicable or passing.

## 3. Repair, stop, or hand off honestly

An observed engineering regression inside the confirmed scope may be diagnosed through [flow-debug](../flow-debug/SKILL.md) and repaired through flow-do under the current implementation delegation. Link it to affected work, reopen only actual regressions with reasons, and rerun failed/affected checks. Product changes or unresolved consequential choices return to the Spec gate; do not silently expand the feature to get a green result.

Stop automatic retries when the same unresolved action/failure repeats on two consecutive attempts. Persist the failure, attempted correction, and evidence; a host restarting the same request does not reset this count. Resume that action only after relevant new user input, an approved correction, or an observed environment change. If no Todo is executable, explain the specific unresolved dependency/claim/condition rather than choosing blocked or historical work.

Pause with a precise question or blocker when permissions, data boundaries, required tools, or a material decision prevent progress. End the active invocation instead of polling/sleeping for human approval. On a host time/context limit, checkpoint and report what remains; do not claim delivery merely because execution stopped.

Report engineering, closure synchronization and functional acceptance per Plan, plus whole-Spec coverage and outstanding global checks. A Plan may be delivered/accepted independently after its own requirements pass; peer blockers do not reset it. The complete Spec requires all required scopes and global checks, with actual user acceptance/authorized closure rather than child counts. Preserve separate Git/deployment authorization.

## 4. Persist a small resumable checkpoint

Use the target's existing automation-note convention, otherwise `.scratch/<feature>/run.md`. For a remote tracker this is only a local orchestration cache, not a second local Spec/Plan/Todo master or a new local tracker; do not create an INDEX just for the cache. If local persistence is unavailable, use a user-provided host store or report that durable resume is unavailable.

Update at stage transitions, before waiting, after failed attempts, and before yielding to a host limit. Keep only:

- Repository/feature and the originating request/delegation references.
- Authoritative current Spec and all applicable Plan/scope references, their selected Todo groups and human confirmation source/scope; qualify package numbers by Plan identity.
- Last completed action, evidence links, and the next action hint.
- Latest applicable verification scope/code/environment reference, including failed/unrun checks.
- Pending question/blocker, failure/attempt information, and last processed human-feedback reference.
- For delegated stages: logical-role/worker bindings, the bounded task and dispatch reference/receipt, source revision, originating question, and consumed result reference. Recover uncertain dispatches through the host before sending again; a repeated callback must not launch the next stage twice.

Do not copy Todo Status tables, Plan text, approval booleans, or Acceptance into a competing state store. Re-read the actual sources after a reply or restart, validate ownership before resuming writes, and update the existing checkpoint rather than creating run-vN files. An explicitly requested read-only status query calls flow-status without writing a checkpoint or advancing work.

## Output

Report the current stage, actual work/results, real artifact references, and either the next automatic action, the exact pending user decision, or engineering delivery with functional acceptance still separate. Be concise on unchanged state. Never claim the bot will keep working after the current invocation unless the host actually provides that capability.

# Connect a bot or main agent

Keep the whole skill bundle accessible to the bot. Use the repository's installer for its supported CLI targets; other hosts need their own loading path. The bot needs access to the target workspace, the declared tracker, execution tools, and browser capability for browser features. Copying flow-run alone omits its sibling skills and shared contract.

For specialist execution, use the host-neutral [stage-agent collaboration protocol](team-mode.md). Bind Flow, Requirements, Planning, Development, and Verification roles to actual available agents/Bots. The Flow Agent remains the sole user entry point and receives every stage result; leaf skills do not contain teammate names or successor-notification rules. Inline execution remains available when requested instead.

For [vsd269/PI-Bot on PI Desktop](pi-bot.md), use the host-specific guide. It has its own execution/planner modes, asynchronous question cards, and isolated imported Skill directories; `install.sh pi` targets the Pi CLI and does not configure this plugin. Preserve a readable full source checkout for cross-skill resources.

Use this user-authorized operating policy when configuring the bot, replacing the repository placeholder with an actual permitted workspace:

```text
Use /flow-run from the installed skill bundle to handle feature requests in <target repository>.
Read its SKILL.md and load each referenced skill when that stage is needed.
Draft the Spec and obtain my confirmation of its actual content before execution.
After Spec confirmation, I delegate technical planning, Todo splitting, implementation,
in-scope regression repair, and applicable integrated verification to you.
Ask me for material product ambiguity, blocked work, or additional authorization.
Keep user functional acceptance, Git operations, deployment, and external messages
within their separate authorization. Do not present your planning decisions as my manual review.
Persist the run checkpoint and report exact pending decisions or delivery evidence.
```

For a configured team, add this user-authorized instruction after supplying its real worker bindings:

```text
You are the Flow Agent and my sole user-facing workflow owner.
Use the bound Requirements agent for clarify/spec, Planning for plan/todo,
Development for do/debug/api, and Verification for integrated testing.
Give workers bounded tasks with the current project, source references and authority.
Workers return artifacts, evidence, or questions to you; you relay questions to me,
pass my full answers back, verify results, and dispatch the next eligible stage.
Do not let specialists approve the Spec, create another orchestrator, contact me
independently, or directly notify their successor. Use the host's actual task tools.
```

## Host responsibilities

- Supply the actual repository, originating request, and complete new user messages on every invocation, including text after “continue”. Bind a reply to the pending Spec/version/question when known.
- Preserve the workspace/checkpoint between invocations. For remote feedback, supply new human comments with stable references and distinguish them from bot messages; avoid replaying already processed feedback as new instructions.
- Wake the agent on user replies or explicit continuation. A skill is not a daemon: scheduled/background execution needs host support configured separately. Do not automatically wake unchanged blocked runs in a retry loop.
- Keep one orchestrator responsible for a feature at a time and preserve task ownership. Read-only monitoring must not launch another writer.
- Surface the Spec review and blocker/delivery responses through the host's already authorized channel. This guide does not configure a messaging service or grant permission to send messages elsewhere.

## Example inputs

```text
/flow-run Add order filtering and export in this repository.
Follow the configured policy: confirm the Spec with me, then decide the technical plan
and Todo breakdown and continue through implementation and verification.

/flow-run Continue the order-export feature. Spec v2 is confirmed; retain CSV-only scope.
Also preserve the existing filename format.
```

Read-only progress uses `/flow-status`. To resume execution, provide the target and new instructions to flow-run; a request to inspect progress alone must not change state.

# Workflow language

Resolve language in the **target repository**, not the skill installation or global agent directory. Read its `docs/agents/language.md` when available:

```markdown
# Workflow language
interaction_language: <confirmed language, e.g. zh-CN>
artifact_language: <confirmed language, e.g. en>
```

- Respect higher-priority instructions. An explicit task language overrides only the specified channel; otherwise use the confirmed project settings. A temporary override does not change the file unless the user asks to update defaults.
- `interaction_language` controls questions, progress, review summaries, and `/find` output. `artifact_language` controls new workflow documents: Spec, Plan, tickets, INDEX, CONTEXT, contracts, document titles, prose, and diagram labels. English internal instructions do not select an output language.
- Template headings and prose are examples to localize. Preserve protocol keys and values, including `Status`, `Parent`, `Spec`, `Plan`, `Blocked by`, `Acceptance`, canonical bold field labels, configuration headers/keys such as `基础模型`, P<N>, paths, references, and code/API identifiers. Keep links consistent with actual headings. Do not apply this setting to application UI or runtime data.
- Never translate verbatim transcripts, raw JSONL, logs, quotes, or source examples as a side effect. Preserve their original content; session export remains faithful even when artifact_language differs.
- Missing fields or unresolved placeholders are not confirmed settings. For ordinary work, use the current conversation language for interaction and the existing target artifact's language (or interaction language) for new prose. Report the missing preference briefly; do not block work, initialize files, or save inferred choices. `/init-dev-flow` confirms missing preferences.
- Do not bulk-translate existing or frozen documents when defaults change. Preserve untouched content; translate an existing document only when the task calls for it.
- Pass both effective languages and the target repository to delegates. Delegates use artifact_language for persisted business documents; user-facing summaries use interaction_language. Do not bake one project's language into global agent definitions.

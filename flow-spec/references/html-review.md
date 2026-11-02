# Optional Spec HTML review

Read this only after the user requests HTML for the current `/flow-spec` invocation. Use [the reading-layout template](../assets/spec-review.html); copy its shell and fill its marked slots rather than redesigning each page. Resolve resources relative to this skill and outputs in the target repository. The output is a standalone HTML document for an ordinary browser, independent of any CLI or conversation-only visualization plugin.

## Content and language

- Read the saved authoritative Markdown Spec or remote issue body first. HTML is a generated snapshot of that source, not a second master. Preserve all product requirements, non-goals, main and exception paths, key decisions, test seams, sequence flow, and module impact; do not silently shorten or introduce decisions.
- Use the source's artifact language for page labels and prose under the shared language policy. Keep canonical fields, status values, P<N>, code/API identifiers, and references unchanged. Missing language preferences use the normal temporary fallback, not a new persisted default.
- Keep the four top-level Spec sections, with stable local IDs and a table of contents linking to actual sections. Technical details may use native `<details>` but remain present in the file. Keep outstanding questions visible and copy only explicit approval/acceptance facts from the source; page controls never record approval.
- Include source reference, its declared version/revision when available, and generation time. Do not invent v1 or an approved state when neither is recorded. Render source relationships such as Parent, Plan, and Acceptance near the source link when present.
- Prefer rendered inline SVG for the existing diagrams, using available rendering tools and checking their branches/call order against the source. Avoid adding project dependencies or a running service solely for this view. When a diagram cannot be rendered, retain its exact Mermaid source as a visible fallback and report that limitation; never label unrendered code as a successfully rendered diagram.
- Escape source text, code examples, and attribute values when converting them to HTML. Literal HTML/script examples remain inert text; only the template's navigation script executes. Do not add external network resources by default.

## Template slots

Replace every `{{...}}` slot in `assets/spec-review.html`:

| Slot | Value |
|------|-------|
| `LANG` | Effective artifact language, suitable for the HTML `lang` attribute |
| `TITLE` | Source Spec title |
| `SPEC_LABEL`, `TOC_LABEL`, `SOURCE_LABEL`, `GENERATED_LABEL` | Short labels in the artifact language |
| `SOURCE_URL` | Actual relative Markdown path, or the remote Spec's real HTTPS URL |
| `VERSION_LABEL` | Declared source version/revision, or an accurate localized “current specification” label |
| `GENERATED_AT` | Actual generation timestamp with timezone |
| `SOURCE_METADATA_HTML` | Escaped source metadata/relationship markup, or empty when absent |
| `TOC_HTML` | Links to the four actual section IDs |
| `BODY_HTML` | Faithful source-derived content, divided into the four sections |

Use HTML escaping for textual slots, including the title and URL attribute. Only the three `*_HTML` slots contain authored markup. A typical section uses `<section class="spec-section" id="spec-problem"><h2>...</h2>...</section>`; subsequent sections use `spec-non-goals`, `spec-approach`, and `spec-impact`. Existing nested headings, tables, code blocks, and `<details>` fit the template. Resolve source-relative links correctly; an issue reference such as `#101` is not a local page anchor.

## Save and navigation

- Locally place the view beside its source: `spec.md` → `spec.html`, `spec-v2.md` → `spec-v2.html`. Add a reading link to the touched feature INDEX only after the file exists. Preserve frozen historical pages.
- For a remote tracker, keep the complete Spec in its issue. A local review may be saved at `.scratch/<feature-slug>/spec.html` (or the known version's matching name), with the issue as its source. Do not create a second authoritative local Spec or a local tracker index for a remote feature.
- Check an existing destination before replacing it; retain unrelated/user-authored HTML and choose an unoccupied output path or report the conflict. Reusing a view must match the intended source/version.
- GitHub issue bodies do not host this page's styles/scripts. Keep Markdown/Mermaid/native collapsible content readable there. Report a local file as a local file; never put a workstation path in an issue as if collaborators could open it.
- Add an online reading link only for an already authorized publishing route after verifying the actual deployed address and source version. Generating HTML does not authorize commits, pushes, Pages setup, a new site, or visibility changes. With no such route, deliver the local file and say online publication is not configured; do not block Spec confirmation on hosting.
- When the source later changes, refresh the view only within a request that includes HTML, or remove/mark its current-reading link as stale in touched navigation. Preserve the old file and its provenance; an existing HTML file alone is not consent to generate another.

## Verify and report

1. Read back the complete output. Check that all slots are filled, the source/version matches, all four sections and meaningful source content remain, code examples are escaped, and section IDs/links are valid.
2. Open the standalone page when browser tooling is available. Check layout, directory navigation, collapsible details, diagrams/fallbacks, and script errors. Keep source and output files intact when preview tooling is unavailable; explicitly distinguish structural checks from an actual browser preview.
3. Report the canonical Spec reference, generated local path or verified online URL, actual validation, and any rendering/publishing limitations. Continue to the normal human Spec confirmation; HTML availability or page interactions do not imply approval.

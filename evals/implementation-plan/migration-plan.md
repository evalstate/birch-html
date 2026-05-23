# Birchline → Birch recipe migration brief

## Situation

The Birch HTML package is replacing an older Birchline artifact style with a
smaller Birch design system and a fast-agent skill workflow. The migration goal
is not to clone Birchline. The goal is to keep the useful artifact behaviours
while expressing them through Birch primitives, recipes, and deterministic
checks.

The maintainer needs an implementation plan that sequences the remaining work,
separates facts from assumptions, and defines how to verify that the migrated
recipes are good enough for a final benchmark run.

## Confirmed facts

- The current package is named `birch-html`.
- The skill entrypoint is `skill/SKILL.md`.
- The preferred generation workflow is:
  1. read the relevant sources;
  2. copy `skill/resources/template.html`;
  3. replace the body content;
  4. run `uv run skill/scripts/finish_birch_html.py <output.html>`;
  5. validate with `skill/scripts/check_birch_renderings.py` when tools are available.
- The artifact shell should remain:

  ```html
  <main class="page stack" data-gap="lg">
    ...
  </main>
  ```

- The final artifact must be standalone HTML with embedded Birch CSS in
  `style[data-birch-system]`.
- The five benchmark evals are:
  - `numeric-data`
  - `code-review`
  - `module-explainer`
  - `implementation-plan`
  - `benchmark-comparison`
- Each eval has a `prompt.md` and `rubric.md` under `evals/<name>/`.
- Source data lives inside the relevant eval directory, for example
  `evals/code-review/source.diff` and `evals/numeric-data/source.csv`.
- The final benchmark should test the skill runner, not the older repo-mode
  migration prompt path.
- With-shell prompts should prefer repository paths as source of truth.
- No-shell prompts may include source previews so the task is still runnable
  without filesystem tools.

## Design decisions already made

### Keep `.auto-grid` as the card-grid primitive

Do not add a separate `.card-grid` class yet. Use:

```html
<div class="auto-grid" style="--grid-min: 260px">
  <article class="card">...</article>
  <article class="card">...</article>
</div>
```

Reason: `.auto-grid` is the layout primitive and `.card` is the semantic
surface. A compatibility alias can be considered later only if repeated eval
failures show that models cannot learn the pattern.

### Prefer skill-based assembly now

The current package should keep the practical skill workflow: copy the template,
write the artifact, finish/inject CSS, and validate. A future slot-based
assembler is interesting but not the next step.

Potential future shape, not current scope:

```json
{
  "title": "Artifact title",
  "recipe": "numeric-data",
  "body_html": "<main class=\"page stack\" data-gap=\"lg\">...</main>",
  "page_css": ""
}
```

### Keep recipes structural, not decorative

Recipes should describe artifact structure, source checks, and useful evidence.
They should not introduce new visual systems, custom dashboards, gradients, or
Birchline-only class names.

## Birchline behaviours to preserve

Preserve these behaviours when translating recipes into Birch terms:

| Birchline-era behaviour | Birch expression |
|---|---|
| card grids | `.auto-grid` with `.card` children |
| summary or TL;DR | `.callout`, `.card`, `.lede`, or first-section decision summary |
| risk/severity labels | `.badge` with an appropriate tone, or clear text labels |
| code evidence | `.code-block[data-wrap="true"]` |
| diff evidence | `.diff` with `.diff-row` children; avoid raw unified diff dumps |
| process/sequence | `.flow-list`, `.flow-step`, `.flow-num`, `.flow-title`, `.flow-detail` |
| numeric evidence | `.stat-card`, `.stat-value`, `.metric-list`, `.numeric-table` |
| caveats/open questions | `.callout`, `.plain-list`, or `.reference-panel` |

## Classes to avoid

These Birchline-only or unsupported classes should not appear in generated Birch
artifacts unless they are explicitly added to the Birch system later:

```text
card-grid
chip-row
tldr
tldr-label
recommendation-callout
risk-tag
file-card
file-head
file-path
file-delta
code-panel
matrix
rank-list
rank-row
rank-track
rank-fill
rank-score
diagram-panel
arch-svg
flow-svg
diagram-legend
swatch
incident-timeline
pill
milestones
milestone
slide-deck
slide
slide-inner
slide-counter
```

## Proposed migration phases

### Phase 1 — Clean benchmark inputs

Purpose: make the benchmark easy to understand and reproducible.

Work:

- Keep each eval's prompt, rubric, and source material together under `evals/`.
- Remove historical or archived data sources from active eval paths.
- Ensure prompts do not mention stale package names or deleted files.
- Decide which prompts expose source previews and which require shell reads.

Exit criteria:

- Every eval source path exists.
- With-shell generated prompts list source paths without duplicating large source
  content.
- No-shell generated prompts include enough source preview content to complete the
  task.

### Phase 2 — Normalize task rubrics

Purpose: make success criteria explicit without turning the prompts into hidden
answer keys.

Work:

- Review each `rubric.md` on its own merits.
- Keep rubrics focused on task quality, source fidelity, and Birch contract.
- Decide whether rubrics are generation guidance, post-hoc scoring guidance, or
  both.
- If rubrics are shown to models, expose them consistently across evals.

Exit criteria:

- Each eval has a clear rubric.
- The harness behaviour is documented: rubric path only for with-shell, rubric
  content included for no-shell if needed.

### Phase 3 — Verify skill packaging

Purpose: ensure the benchmark tests the published skill shape.

Work:

- Keep checker and finish scripts inside `skill/scripts/`.
- Keep template and CSS assets inside the skill package.
- Ensure `skill/SKILL.md` references in-package paths.
- Ensure snapshots include `skill/`, `evals/`, relevant scripts, docs, and styles.

Exit criteria:

- A fresh model can read `skill/SKILL.md`, create an artifact, finish it, and run
  the checker without guessing paths.
- Snapshot inputs are sufficient to reproduce a run.

### Phase 4 — Run final benchmark

Purpose: produce comparable model outputs.

Work:

- Run the five evals across the selected model list.
- Capture generation traces, deterministic checker reports, screenshots, and VLM
  review findings.
- Record self-check attempts from actual tool calls, not from prompt mentions.

Exit criteria:

- Each model has five artifacts or a clear generation failure.
- Reports include deterministic findings, VLM findings, token/tool metrics, and
  prompt files.
- The final analysis clearly separates rendering correctness from semantic
  artifact quality.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Historical Birchline wording causes models to copy old classes | Keep source briefs current and include an explicit unsupported-class list. |
| Prompt includes both file content and file paths, causing conflicts | Use two prompt modes: with-shell paths only; no-shell source previews. |
| Models ignore skill workflow and hand-roll HTML | Keep normal fast-agent skill block, instruct models to read `SKILL.md`, and validate final artifacts. |
| Checker availability differs across runs | Package checker under `skill/scripts/` and snapshot it with the run. |
| Deterministic checks miss semantic quality | Add a later scoring pass using source, prompt, artifact, and task rubric. |
| Rubrics become inconsistent across evals | Review each rubric before final benchmark and document how rubrics are exposed. |

## Assumptions

- The final benchmark is intended to evaluate the `birch-html` skill workflow.
- Shell-enabled runs are allowed to inspect local repository files.
- No-shell runs are optional but should remain possible with source previews.
- Semantic output scoring can be added after the generation/rendering pipeline is
  stable.

## Open questions

- Should task rubrics be shown to models for every eval, or used only for human
  scoring?
- Should the no-shell prompt set be part of the published benchmark or just a
  fallback/debug mode?
- Which models should be included in the final published run?
- Should semantic scoring be manual, model-judged, or hybrid?

## Non-goals

- Do not port Birchline CSS wholesale.
- Do not add compatibility aliases before eval evidence shows they are needed.
- Do not build the future slot-based assembler before the skill benchmark is
  stable.
- Do not treat VLM/rendering checks as full semantic content scoring.

## Verification plan

Use before/after comparisons across the five evals:

1. Generate artifacts with the current `birch-html` skill and with-shell prompts.
2. Run deterministic checks at desktop, mobile, deep, and mobile-deep viewports.
3. Capture screenshots and VLM review for visible layout defects.
4. Compare generation success, deterministic failures/warnings, VLM findings,
   token usage, duration, and self-check evidence.
5. Optionally run a later semantic scoring pass against each eval rubric.

The first benchmark pass should answer:

- Did the model produce complete standalone HTML for all five evals?
- Did it follow the Birch skill workflow and finish the artifact correctly?
- Did the artifact avoid unsupported Birchline classes?
- Did deterministic and VLM checks find rendering problems?
- Did the content remain source-grounded and useful for the target audience?

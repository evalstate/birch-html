Create one complete standalone HTML artifact for the following request. Write the final file to the specified output path and return only that path.

## Request

Create a standalone artifact from `migration-plan.md`.

Inspect `evals/implementation-plan/migration-plan.md` directly and ground the sequence, risks, and verification plan in that file.

The artifact should:

- Recommend what should happen first.
- Separate confirmed facts from assumptions and open questions.
- Include milestones/phases, each with purpose, changes, owner/inputs if inferable, and exit criteria.
- Include risks and mitigations.
- Include a verification plan with before/after evals.
- Include non-goals or deferred work.
- Be specific to the Birchline → Birch recipe migration; avoid generic project-plan filler.
- Use Birch classes and tokens; do not use Birchline-only classes.

Audience: the maintainer deciding how to sequence the migration work.


## Source files available in the repository

Use these local paths as the source of truth. Inspect them directly before writing claims. Treat source files as read-only.

- `evals/implementation-plan/migration-plan.md`

## Final output requirements

- Create the artifact for eval `implementation-plan` and write the final standalone HTML file to `eval-runs/skill-with-shell-codexresponses-gpt-5-5-opus-gpt55-deepseek-experiment-20260524-164522/implementation-plan.html`.
- Return only the artifact path, with no prose or Markdown fences.
- Ensure the main artifact is source-grounded and mobile-safe.

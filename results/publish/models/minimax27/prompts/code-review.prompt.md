Create one complete standalone HTML artifact for the following request. Write the final file to the specified output path and return only that path.

## Request

Create a standalone code-review artifact from `evals/code-review/source.diff`.

The patch under review is for a fictional Candle style-system project. Review Candle-specific code as the subject of the patch, but produce your final review artifact using the `birch-html` skill and Birch visual system.

Use grep/sed or another local read-only tool path if helpful to identify touched
files, hunks, and risky changes.

The artifact should:

- Use the rubric at `evals/code-review/rubric.md`
- Be findings-first: blocking/high-risk findings must appear before background.
- Include a clear no-findings state if there are no material findings.
- Reference concrete files/functions/lines from the diff.
- Separate severity, evidence, impact, and recommended fix.
- Include reviewer checklist and residual risks.
- Include a small diff or code evidence section when useful.
- Do not paste raw unified diff text into the artifact; summarize findings and
  use Birch diff rows only for short evidence excerpts.
- Use Birch classes and tokens; do not use Birchline-only classes.
- Avoid generic review filler not grounded in the diff.

Audience: maintainers deciding whether the patch is safe to merge.


## Source files available in the repository

Use these local paths as the source of truth. Inspect them directly before writing claims. Treat source files as read-only.

- `evals/code-review/source.diff`

## Final output requirements

- Create the artifact for eval `code-review` and write the final standalone HTML file to `eval-runs/skill-with-shell-minimax27-publication-final/code-review.html`.
- Return only the artifact path, with no prose or Markdown fences.
- Ensure the main artifact is source-grounded and mobile-safe.

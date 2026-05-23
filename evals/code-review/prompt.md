Create a standalone code-review artifact from `evals/code-review/source.diff`.

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

Create one complete standalone HTML artifact for the following request. Write the final file to the specified output path and return only that path.

## Request

Create a standalone benchmark-comparison evaluation report from `evals/benchmark-comparison/source.json`.

The artifact should help decide whether Candidate B should be promoted as the next GEPA seed.

Inspect `evals/benchmark-comparison/source.json` directly. Compute score deltas, warning/failure deltas, wall-time/token/cost changes, and the promotion rationale.

The artifact should:

- Start with a compact hero stating the decision/result, not just the dataset.
- Show evidence in the first desktop viewport.
- Include KPI cards for pass rate, final score, checker failures/warnings, wall time, token total, or estimated cost.
- Include a primary tradeoff visual comparing quality/compliance against cost or latency.
- Include an exact values table near the visual.
- Explain the scoring formula and run provenance.
- Call out regressions as well as improvements.
- Include explicit caveats about token comparability and checker limitations.
- End with the next recommended experiment.
- Use Birch classes and tokens; avoid hard-coded colors in page CSS.
- Do not use external JavaScript chart libraries.
- Use Python/Matplotlib-generated inline SVG when plotting multi-metric
  comparisons is helpful. The final artifact must remain a standalone HTML
  document.

Audience: engineers optimizing the Birch HTML skill and deciding whether this candidate is good seed data for the next GEPA round.


## Source files available in the repository

Use these local paths as the source of truth. Inspect them directly before writing claims. Treat source files as read-only.

- `evals/benchmark-comparison/source.json`

## Final output requirements

- Create the artifact for eval `benchmark-comparison` and write the final standalone HTML file to `eval-runs/skill-with-shell-haiku45-publication-final/benchmark-comparison.html`.
- Return only the artifact path, with no prose or Markdown fences.
- Ensure the main artifact is source-grounded and mobile-safe.

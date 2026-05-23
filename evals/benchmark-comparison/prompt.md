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

# Benchmark comparison rubric

Score each category 1–5.

1. **Decision-first layout** — first viewport states whether Candidate B should be promoted and shows supporting evidence.
2. **Evaluation provenance** — model, run labels, eval set, command/report paths, score formula, and timestamp/context are visible.
3. **Tradeoff analysis** — explains improvement/regression across score, failures/warnings, wall time, tokens, and cost without collapsing them into one vague ranking.
4. **Visual quality** — includes a readable primary tradeoff visual; Matplotlib or well-scaled inline SVG is used when axes/multiple metrics are needed.
5. **Exact values** — includes a nearby numeric table with exact run and per-eval values, units, and score components.
6. **Caveats and next experiment** — states token/checker/screenshot comparability limits and recommends a concrete next experiment.
7. **Birch contract** — uses Birch primitives/tokens, no invented design system, no external chart library, mobile safe.

Birch expected primitives: `.stat-card` or `.card` + `.stat-value`, `.chart-panel`, `.chart-svg`, `.numeric-table-wrap`, `.numeric-table`, `.callout`, `.reference-panel` or `.section-rail`, `.code-block[data-wrap="true"]` for commands/formulas, and `.plain-list` for caveats.

Fail conditions: generic dashboard with no decision, no score formula/provenance, no caveats, hidden exact values, invented run facts, external assets, unknown Birch/Birchline class leakage.

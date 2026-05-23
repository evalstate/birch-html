"""Compose the final standalone benchmark-comparison HTML artifact."""
from __future__ import annotations
import pathlib, html as _h

HERE = pathlib.Path(__file__).parent
TRADEOFF = (HERE / "chart_tradeoff.svg").read_text()
PER_EVAL = (HERE / "chart_per_eval.svg").read_text()

# Strip the leading <?xml ?> if present and ensure SVG has preserveAspectRatio.
def prep_svg(svg: str, *, label: str) -> str:
    # Add aria-label for accessibility, and add preserveAspectRatio/responsive width.
    svg = svg.replace(
        '<svg ',
        f'<svg role="img" aria-label="{label}" preserveAspectRatio="xMidYMid meet" '
        'style="width:100%;height:auto;display:block;" ',
        1,
    )
    return svg

TRADEOFF_SVG = prep_svg(TRADEOFF, label="Final score and warnings vs cost, wall time, and tokens")
PER_EVAL_SVG = prep_svg(PER_EVAL, label="Per-eval score, warnings, and wall time comparison")

HTML = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Promote Candidate B — Birch HTML skill seed comparison</title>
  <link rel="stylesheet" href="../../styles/birch-system.css">
  <link rel="stylesheet" href="styles/birch-system.css">
  <style>
    /* Page-local refinements, Birch tokens only. */
    .hero-callout {{
      display: grid;
      gap: var(--space-3);
      grid-template-columns: 1fr;
      padding: var(--space-4);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      background: var(--surface-warm);
    }}
    @media (min-width: 720px) {{
      .hero-callout {{ grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); align-items: center; }}
    }}
    .decision-pill {{
      display: inline-flex; align-items: center; gap: var(--space-1);
      padding: 2px 10px; border-radius: 999px;
      background: color-mix(in oklab, var(--success) 18%, var(--surface));
      color: var(--success); font-weight: 600; font-size: 0.78rem; letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .delta-up   {{ color: var(--success); font-weight: 600; }}
    .delta-down {{ color: var(--danger);  font-weight: 600; }}
    .delta-warn {{ color: var(--accent);  font-weight: 600; }}
    .chart-svg svg {{ width: 100%; height: auto; }}
    .formula {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.92rem;
    }}
    .kpi-strong {{ font-variant-numeric: tabular-nums; }}
  </style>
</head>
<body>
  <main class="page stack" data-gap="lg">

    <!-- HERO: decision first -->
    <header class="stack" data-gap="sm">
      <div class="eyebrow">Benchmark comparison · GEPA seed gating</div>
      <h1>Promote Candidate B as the next GEPA seed</h1>
      <p class="lede">
        Candidate B lifts the final score from <strong>0.9175 → 0.9655</strong>
        (+0.048) and cuts checker warnings from <strong>5 → 2</strong> on the
        same four-eval suite, at the cost of <strong>+11.5% USD</strong> and
        <strong>+18.7% wall time</strong>. The cost is material but acceptable
        for seeding GEPA.
      </p>

      <div class="hero-callout">
        <div class="stack" data-gap="sm">
          <span class="decision-pill">Recommendation · Promote</span>
          <p><strong>Use Candidate B as the seed for the next single-model GEPA run.</strong>
          Then rerun on Kimi and Gemini before broad model-suite validation.
          Manually inspect the <em>code-review</em> artifact for long diff
          wrapping before committing.</p>
          <div class="cluster" data-gap="sm">
            <span class="chip">model · codexresponses.gpt-5.5</span>
            <span class="chip">skill · birch-html candidate-b</span>
            <span class="chip">eval set · 4 artifacts</span>
            <span class="chip">2026-05-20 18:40 UTC</span>
          </div>
        </div>
        <aside class="reference-panel stack" data-gap="sm">
          <div class="eyebrow">Headline deltas vs Seed A</div>
          <ul class="insight-list">
            <li><span><strong>Final score +0.048.</strong> 0.9175 → 0.9655.</span></li>
            <li><span><strong>Checker warnings −3.</strong> 5 → 2, zero failures either side.</span></li>
            <li><span><strong>Cost +$0.22.</strong> $1.92 → $2.14 per full eval suite.</span></li>
            <li><span><strong>Wall time +77 s.</strong> 412 s → 489 s suite-wide.</span></li>
          </ul>
        </aside>
      </div>
    </header>

    <!-- KPI strip: evidence in the first viewport -->
    <section class="section stack" data-gap="md">
      <div class="section-head">
        <div class="eyebrow">Run KPIs · Candidate B</div>
        <h2>What the run produced</h2>
      </div>
      <div class="auto-grid" style="--grid-min: 160px;">
        <div class="stat-card">
          <div class="caption">Pass rate</div>
          <div class="stat-value kpi-strong">4 / 4</div>
          <div class="sub">generated_ok · 0 failures</div>
        </div>
        <div class="stat-card">
          <div class="caption">Final score</div>
          <div class="stat-value kpi-strong">0.966</div>
          <div class="sub"><span class="delta-up">+0.048</span> vs Seed A</div>
        </div>
        <div class="stat-card">
          <div class="caption">Checker warnings</div>
          <div class="stat-value kpi-strong">2</div>
          <div class="sub"><span class="delta-up">−3</span> · 0 failures</div>
        </div>
        <div class="stat-card">
          <div class="caption">Hygiene score</div>
          <div class="stat-value kpi-strong">0.99</div>
          <div class="sub"><span class="delta-down">−0.01</span> noise floor</div>
        </div>
        <div class="stat-card">
          <div class="caption">Wall time</div>
          <div class="stat-value kpi-strong">489 s</div>
          <div class="sub"><span class="delta-warn">+18.7%</span> vs 412 s</div>
        </div>
        <div class="stat-card">
          <div class="caption">Total tokens</div>
          <div class="stat-value kpi-strong">124.7k</div>
          <div class="sub"><span class="delta-warn">+7.5%</span> vs 116.0k</div>
        </div>
        <div class="stat-card">
          <div class="caption">Estimated cost</div>
          <div class="stat-value kpi-strong">$2.14</div>
          <div class="sub"><span class="delta-warn">+11.5%</span> vs $1.92</div>
        </div>
        <div class="stat-card">
          <div class="caption">Checker score</div>
          <div class="stat-value kpi-strong">0.94</div>
          <div class="sub"><span class="delta-up">+0.09</span> vs 0.85</div>
        </div>
      </div>
    </section>

    <!-- PRIMARY TRADEOFF VISUAL -->
    <section class="section stack" data-gap="md">
      <div class="section-head">
        <div class="eyebrow">Primary tradeoff</div>
        <h2>Quality and warnings against cost, latency, and tokens</h2>
      </div>
      <div class="panel chart-panel stack" data-gap="sm">
        <div class="chart-svg">
          {TRADEOFF_SVG}
        </div>
        <p class="chart-caption">
          Left: final score rises from 0.917 to 0.966 while checker warnings
          drop from 5 to 2. Right: Candidate B costs 11.5% more, takes 18.7%
          longer, and consumes 7.5% more tokens (indexed to Seed A = 100).
          Source: <code>eval-runs/reports/skill-seed-gpt55/summary.json</code> ·
          <code>eval-runs/reports/skill-candidate-b-gpt55/summary.json</code>.
        </p>
      </div>

      <!-- Exact values, close to the chart -->
      <div class="numeric-table-wrap">
        <table class="numeric-table">
          <caption class="caption">Aggregate run comparison · exact values</caption>
          <thead>
            <tr>
              <th scope="col">Metric</th>
              <th scope="col" class="metric">Seed A</th>
              <th scope="col" class="metric">Candidate B</th>
              <th scope="col" class="metric">Δ</th>
              <th scope="col">Direction</th>
            </tr>
          </thead>
          <tbody>
            <tr><th scope="row">Generated OK / total</th>
              <td class="metric">4 / 4</td><td class="metric">4 / 4</td>
              <td class="metric">0</td><td>flat</td></tr>
            <tr><th scope="row">Generation score</th>
              <td class="metric">1.000</td><td class="metric">1.000</td>
              <td class="metric">0.000</td><td>flat</td></tr>
            <tr><th scope="row">Checker failures</th>
              <td class="metric">0</td><td class="metric">0</td>
              <td class="metric">0</td><td>flat</td></tr>
            <tr><th scope="row">Checker warnings</th>
              <td class="metric">5</td><td class="metric">2</td>
              <td class="metric">−3</td><td><span class="delta-up">better</span></td></tr>
            <tr><th scope="row">Checker score</th>
              <td class="metric">0.850</td><td class="metric">0.940</td>
              <td class="metric">+0.090</td><td><span class="delta-up">better</span></td></tr>
            <tr><th scope="row">Hygiene score</th>
              <td class="metric">1.000</td><td class="metric">0.990</td>
              <td class="metric">−0.010</td><td><span class="delta-down">worse (noise)</span></td></tr>
            <tr><th scope="row">Final score</th>
              <td class="metric">0.9175</td><td class="metric">0.9655</td>
              <td class="metric">+0.0480</td><td><span class="delta-up">better</span></td></tr>
            <tr><th scope="row">Wall time (s)</th>
              <td class="metric">412</td><td class="metric">489</td>
              <td class="metric">+77 (+18.7%)</td><td><span class="delta-warn">worse</span></td></tr>
            <tr><th scope="row">Input tokens</th>
              <td class="metric">84,200</td><td class="metric">90,100</td>
              <td class="metric">+5,900 (+7.0%)</td><td><span class="delta-warn">worse</span></td></tr>
            <tr><th scope="row">Output tokens</th>
              <td class="metric">31,800</td><td class="metric">34,600</td>
              <td class="metric">+2,800 (+8.8%)</td><td><span class="delta-warn">worse</span></td></tr>
            <tr><th scope="row">Total tokens</th>
              <td class="metric">116,000</td><td class="metric">124,700</td>
              <td class="metric">+8,700 (+7.5%)</td><td><span class="delta-warn">worse</span></td></tr>
            <tr><th scope="row">Estimated cost (USD)</th>
              <td class="metric">$1.92</td><td class="metric">$2.14</td>
              <td class="metric">+$0.22 (+11.5%)</td><td><span class="delta-warn">worse</span></td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- PER-EVAL DETAIL -->
    <section class="section stack" data-gap="md">
      <div class="section-head">
        <div class="eyebrow">Per-eval breakdown</div>
        <h2>Where the gains came from</h2>
      </div>
      <div class="panel chart-panel stack" data-gap="sm">
        <div class="chart-svg">
          {PER_EVAL_SVG}
        </div>
        <p class="chart-caption">
          Same eval ordering across all three panels. Score rises on every eval;
          warnings tie or drop; wall time grows roughly uniformly (≈+19% per
          eval).
        </p>
      </div>

      <div class="numeric-table-wrap">
        <table class="numeric-table">
          <caption class="caption">Per-eval scores, warnings, and wall time</caption>
          <thead>
            <tr>
              <th scope="col">Eval</th>
              <th scope="col" class="metric">Seed score</th>
              <th scope="col" class="metric">Cand. score</th>
              <th scope="col" class="metric">Δ score</th>
              <th scope="col" class="metric">Seed warn</th>
              <th scope="col" class="metric">Cand. warn</th>
              <th scope="col" class="metric">Seed s</th>
              <th scope="col" class="metric">Cand. s</th>
            </tr>
          </thead>
          <tbody>
            <tr><th scope="row">numeric-data</th>
              <td class="metric">0.930</td><td class="metric">0.970</td>
              <td class="metric"><span class="delta-up">+0.040</span></td>
              <td class="metric">2</td><td class="metric">1</td>
              <td class="metric">94</td><td class="metric">113</td></tr>
            <tr><th scope="row">code-review</th>
              <td class="metric">0.910</td><td class="metric">0.955</td>
              <td class="metric"><span class="delta-up">+0.045</span></td>
              <td class="metric">1</td><td class="metric">0</td>
              <td class="metric">102</td><td class="metric">121</td></tr>
            <tr><th scope="row">module-explainer</th>
              <td class="metric">0.925</td><td class="metric">0.944</td>
              <td class="metric"><span class="delta-up">+0.019</span></td>
              <td class="metric">1</td><td class="metric">1</td>
              <td class="metric">111</td><td class="metric">132</td></tr>
            <tr><th scope="row">implementation-plan</th>
              <td class="metric">0.905</td><td class="metric">0.993</td>
              <td class="metric"><span class="delta-up">+0.088</span></td>
              <td class="metric">1</td><td class="metric">0</td>
              <td class="metric">105</td><td class="metric">123</td></tr>
          </tbody>
        </table>
      </div>

      <div class="grid" style="--grid-min: 240px;">
        <div class="card stack" data-gap="xs">
          <div class="card-head">
            <div class="card-titles">
              <span class="eyebrow">numeric-data</span>
              <span class="card-title">+0.040</span>
            </div>
            <span class="badge">warn 2→1</span>
          </div>
          <p>Candidate chart is clearer but uses more SVG text — watch label
          density on narrow viewports.</p>
        </div>
        <div class="card stack" data-gap="xs">
          <div class="card-head">
            <div class="card-titles">
              <span class="eyebrow">code-review</span>
              <span class="card-title">+0.045</span>
            </div>
            <span class="badge">warn 1→0</span>
          </div>
          <p>No mechanical regression. Inspect finding-severity wording and
          long diff wrapping before committing the seed.</p>
        </div>
        <div class="card stack" data-gap="xs">
          <div class="card-head">
            <div class="card-titles">
              <span class="eyebrow">module-explainer</span>
              <span class="card-title">+0.019</span>
            </div>
            <span class="badge">warn 1→1</span>
          </div>
          <p>Runtime-path narrative improved; mobile flow caption stays dense
          — the remaining warning sits here.</p>
        </div>
        <div class="card stack" data-gap="xs">
          <div class="card-head">
            <div class="card-titles">
              <span class="eyebrow">implementation-plan</span>
              <span class="card-title">+0.088</span>
            </div>
            <span class="badge">warn 1→0</span>
          </div>
          <p>Plan quality is the biggest single-eval lift; no checker
          regression observed.</p>
        </div>
      </div>
    </section>

    <!-- FINDINGS / REGRESSIONS -->
    <section class="section stack" data-gap="md">
      <div class="section-head">
        <div class="eyebrow">Findings</div>
        <h2>Improvements, regressions, and what to verify by hand</h2>
      </div>
      <div class="grid" style="--grid-min: 260px;">
        <div class="panel stack" data-gap="sm">
          <div class="eyebrow">Improvements</div>
          <ul class="checklist">
            <li>All 4 artifacts still generate cleanly (4 / 4 generated_ok).</li>
            <li>Checker score lifts 0.85 → 0.94 (+0.09) on the same rubric.</li>
            <li>Warnings fall on 3 of 4 evals; tie on <em>module-explainer</em>.</li>
            <li><em>implementation-plan</em> contributes the largest per-eval
              score lift (+0.088).</li>
          </ul>
        </div>
        <div class="panel stack" data-gap="sm">
          <div class="eyebrow">Regressions / cost</div>
          <ul class="plain-list">
            <li>Wall time +77 s (+18.7%) — uniform per eval, not a single outlier.</li>
            <li>Total tokens +8.7k (+7.5%); cost +$0.22 (+11.5%).</li>
            <li>Hygiene score slips 1.00 → 0.99 — within noise floor but worth
              re-checking unsupported-class penalties.</li>
            <li><em>numeric-data</em> uses more SVG text — verify mobile chart
              readability.</li>
          </ul>
        </div>
        <div class="panel stack" data-gap="sm">
          <div class="eyebrow">Manual gate before promotion</div>
          <ul class="plain-list">
            <li>Inspect <em>code-review</em> long diff wrapping
              (<code>data-wrap="true"</code> on <code>.diff</code>).</li>
            <li>Eyeball <em>module-explainer</em> mobile flow caption density.</li>
            <li>Spot-check that hygiene drop is not a new unsupported class.</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- SCORING + PROVENANCE -->
    <section class="section stack" data-gap="md">
      <div class="section-head">
        <div class="eyebrow">Scoring &amp; provenance</div>
        <h2>How the final score is computed</h2>
      </div>

      <div class="grid" style="--grid-min: 280px;">
        <div class="panel stack" data-gap="sm">
          <div class="eyebrow">Formula</div>
          <pre class="code-block formula" data-wrap="true"><code>final_score = 0.30 * generation_score
            + 0.55 * checker_score
            + 0.15 * hygiene_score

generation_score = generated_ok / total_evals
checker_score    = max(0, 1 − 0.20 * checker_failures
                              − 0.03 * checker_warnings)
hygiene_score    = avg(artifact compliance after
                       unsupported-class, external-asset,
                       and missing-CSS penalties)</code></pre>
          <p class="caption">
            Worked example for Candidate B: 0.30·1.00 + 0.55·0.94 + 0.15·0.99
            = 0.300 + 0.517 + 0.1485 = <strong>0.9655</strong>.
          </p>
        </div>

        <div class="panel stack" data-gap="sm">
          <div class="eyebrow">Run provenance</div>
          <dl class="stack" data-gap="xs">
            <div class="cluster" data-gap="sm"><dt class="caption">Model</dt><dd><code>codexresponses.gpt-5.5</code></dd></div>
            <div class="cluster" data-gap="sm"><dt class="caption">Skill versions</dt><dd><code>birch-html seed</code> · <code>birch-html candidate-b</code></dd></div>
            <div class="cluster" data-gap="sm"><dt class="caption">Eval set</dt><dd>numeric-data, code-review, module-explainer, implementation-plan</dd></div>
            <div class="cluster" data-gap="sm"><dt class="caption">Timestamp</dt><dd>2026-05-20T18:40:00Z</dd></div>
          </dl>
          <div class="eyebrow">Reports</div>
          <pre class="code-block" data-wrap="true"><code>eval-runs/reports/skill-seed-gpt55/summary.json
eval-runs/reports/skill-candidate-b-gpt55/summary.json</code></pre>
          <div class="eyebrow">Reproduce</div>
          <pre class="code-block copyable" data-wrap="true"><code>python3 scripts/run_skill_evals.py \\
  --skill-dir birch-html \\
  --model codexresponses.gpt-5.5 \\
  --label skill-candidate-b-gpt55</code></pre>
        </div>
      </div>
    </section>

    <!-- CAVEATS -->
    <section class="section stack" data-gap="md">
      <div class="section-head">
        <div class="eyebrow">Caveats</div>
        <h2>What this comparison does <em>not</em> tell you</h2>
      </div>
      <div class="callout stack" data-gap="sm">
        <span class="callout-label">Comparability and measurement limits</span>
        <ul class="plain-list">
          <li><strong>Token counts are not apples-to-apples.</strong> Provider
            token schemas differ; cached, reasoning, and effective-token fields
            are not reconciled across runs.</li>
          <li><strong>Checker warnings are mechanical contract signals,</strong>
            not a full content-quality verdict — a clean checker run can still
            ship dense or unclear prose.</li>
          <li><strong>Same-vs-same screenshot pairs</strong> mostly validate
            geometry and rendering contracts; they do not score aesthetics.</li>
          <li><strong>Wall time mixes model latency with harness overhead;</strong>
            sub-20 s differences should be treated as noisy.</li>
          <li><strong>n = 1 per eval per candidate.</strong> No re-runs or
            seed sweep yet — promotion is a working hypothesis, not a stat.</li>
        </ul>
      </div>
    </section>

    <!-- NEXT EXPERIMENT -->
    <section class="section stack" data-gap="md">
      <div class="section-head">
        <div class="eyebrow">Next experiment</div>
        <h2>What to run after promotion</h2>
      </div>
      <ol class="flow-list">
        <li class="flow-step">
          <span class="flow-num">1</span>
          <div class="stack" data-gap="xs">
            <span class="flow-title">Promote Candidate B as the GEPA seed</span>
            <span class="flow-detail">Single-model GEPA round on
              <code>codexresponses.gpt-5.5</code>, holding the eval set fixed
              at the four current artifacts.</span>
          </div>
        </li>
        <li class="flow-step">
          <span class="flow-num">2</span>
          <div class="stack" data-gap="xs">
            <span class="flow-title">Manual inspection gate</span>
            <span class="flow-detail">Before committing, open the
              <em>code-review</em> artifact and verify long diff wrapping with
              <code>data-wrap="true"</code>; eyeball the
              <em>module-explainer</em> mobile flow caption.</span>
          </div>
        </li>
        <li class="flow-step">
          <span class="flow-num">3</span>
          <div class="stack" data-gap="xs">
            <span class="flow-title">Cross-model rerun</span>
            <span class="flow-detail">Replay the GEPA-best candidate on Kimi
              and Gemini to check that the warning reduction is not
              model-specific.</span>
          </div>
        </li>
        <li class="flow-step">
          <span class="flow-num">4</span>
          <div class="stack" data-gap="xs">
            <span class="flow-title">Broad model-suite validation</span>
            <span class="flow-detail">Only after the cross-model spot-check
              passes: run the full model suite and re-evaluate cost / latency
              budgets against the +11.5% / +18.7% headroom seen here.</span>
          </div>
        </li>
        <li class="flow-step">
          <span class="flow-num">5</span>
          <div class="stack" data-gap="xs">
            <span class="flow-title">Tighten the checker</span>
            <span class="flow-detail">With warnings at 2, the next marginal
              gain probably lives in turning current warnings into failures
              for clearly-broken contracts (e.g. unwrapped wide diffs) so the
              score signal stays informative.</span>
          </div>
        </li>
      </ol>
    </section>

    <footer class="stack" data-gap="xs">
      <p class="caption">
        Source: <code>evals/benchmark-comparison/source.json</code> ·
        Charts generated with <code>scripts/birch_mpl.py</code> + Matplotlib ·
        Decision: <strong>promote Candidate B</strong>.
      </p>
    </footer>

  </main>
</body>
</html>
"""

out = HERE / "artifact.html"
out.write_text(HTML)
print(out)
print(len(HTML), "bytes")

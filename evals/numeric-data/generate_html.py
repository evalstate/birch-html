import os
from pathlib import Path

# Load SVG
svg_path = Path("evals/numeric-data/chart.svg")
svg_content = svg_path.read_text(encoding="utf-8")

# Let's clean up SVG a bit to make it fully responsive
import re
svg_clean = re.sub(r'width="[^"]+"', '', svg_content, count=1)
svg_clean = re.sub(r'height="[^"]+"', '', svg_clean, count=1)
svg_clean = svg_clean.replace('<svg ', '<svg class="chart-svg" style="width: 100%; height: auto; max-width: 100%; display: block;" ')

# Build HTML Body Content
body_content = f"""
    <main class="page stack" data-gap="lg">
      <header class="stack" data-gap="sm">
        <div class="eyebrow">Adoption Assessment</div>
        <h1>Rendering Checker Stable for Adoption with 97.7% Average Pass Rate</h1>
        <p class="lede">
          <strong>Audience: Engineering &amp; Product Leads</strong> • Visual layout quality metrics demonstrate five weeks of continuous convergence. With 19 of 20 layout overflows resolved and average pixel drift reduced by 61%, the rendering checker has achieved production-grade stability.
        </p>
      </header>

      <section class="section stack" data-gap="lg">
        <!-- KPI Strip -->
        <div class="auto-grid" style="--grid-min: 160px">
          <div class="card stat-card stack" data-gap="xs">
            <span class="caption">Avg Pass Rate</span>
            <span class="stat-value">97.7%</span>
            <span class="chip" data-tone="olive">▲ +12.0% vs. Baseline</span>
          </div>
          <div class="card stat-card stack" data-gap="xs">
            <span class="caption">Active Overflows</span>
            <span class="stat-value">1</span>
            <span class="chip" data-tone="olive">▼ -95% (19 of 20 Fixed)</span>
          </div>
          <div class="card stat-card stack" data-gap="xs">
            <span class="caption">Mean RGB Delta</span>
            <span class="stat-value">7.7</span>
            <span class="chip" data-tone="olive">▼ -61% Pixel Drift</span>
          </div>
          <div class="card stat-card stack" data-gap="xs">
            <span class="caption">Rollout Readiness</span>
            <span class="stat-value" style="color: var(--success);">Ready</span>
            <span class="chip" data-tone="olive">2 of 3 Pages 100% Stable</span>
          </div>
        </div>

        <!-- Evidence Section -->
        <div class="section-rail" style="--rail-width: 320px;">
          <div class="stack" data-gap="lg">
            <!-- Chart Panel -->
            <div class="panel chart-panel stack" data-gap="md">
              <div class="stack" data-gap="xs">
                <h3 style="font-family: var(--font-serif); font-size: var(--text-lg); margin: 0;">Static Pass Rate Weekly Trend</h3>
                <p class="caption">Across five consecutive releases (April 20, 2026 to May 18, 2026)</p>
              </div>
              <div class="chart-svg-container" style="background: var(--surface-tint); padding: var(--space-4); border-radius: var(--radius-sm); border: var(--border-thin);">
                {svg_clean}
              </div>
              <div class="chart-caption" style="margin-top: var(--space-2);">
                <strong>Figure 1:</strong> Comparison of the static checker pass rates across components. Solid lines show steady convergence toward production-ready thresholds (95%+).
              </div>
            </div>

            <!-- Table Panel -->
            <div class="stack" data-gap="sm">
              <h3 style="font-family: var(--font-serif); font-size: var(--text-lg); margin: 0;">Weekly Aggregated Progress Metrics</h3>
              <p class="caption">Combined averages across all three evaluation artifacts</p>
              
              <div class="numeric-table-wrap">
                <table class="numeric-table">
                  <thead>
                    <tr>
                      <th>Week</th>
                      <th class="metric">Avg Pass Rate</th>
                      <th class="metric">Total Overflows</th>
                      <th class="metric">Avg RGB Delta</th>
                      <th class="metric">Avg Vision Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="entity">2026-04-20</td>
                      <td class="metric" data-label="Avg Pass Rate">85.7%</td>
                      <td class="metric" data-label="Total Overflows">20</td>
                      <td class="metric" data-label="Avg RGB Delta">19.7</td>
                      <td class="metric" data-label="Avg Vision Score">3.03 / 5.0</td>
                    </tr>
                    <tr>
                      <td class="entity">2026-04-27</td>
                      <td class="metric" data-label="Avg Pass Rate">90.3%</td>
                      <td class="metric" data-label="Total Overflows">13</td>
                      <td class="metric" data-label="Avg RGB Delta">16.0</td>
                      <td class="metric" data-label="Avg Vision Score">3.40 / 5.0</td>
                    </tr>
                    <tr>
                      <td class="entity">2026-05-04</td>
                      <td class="metric" data-label="Avg Pass Rate">93.7%</td>
                      <td class="metric" data-label="Total Overflows">8</td>
                      <td class="metric" data-label="Avg RGB Delta">13.3</td>
                      <td class="metric" data-label="Avg Vision Score">3.77 / 5.0</td>
                    </tr>
                    <tr>
                      <td class="entity">2026-05-11</td>
                      <td class="metric" data-label="Avg Pass Rate">96.3%</td>
                      <td class="metric" data-label="Total Overflows">3</td>
                      <td class="metric" data-label="Avg RGB Delta">9.2</td>
                      <td class="metric" data-label="Avg Vision Score">4.13 / 5.0</td>
                    </tr>
                    <tr>
                      <td class="entity">2026-05-18</td>
                      <td class="metric" data-label="Avg Pass Rate">97.7%</td>
                      <td class="metric" data-label="Total Overflows">1</td>
                      <td class="metric" data-label="Avg RGB Delta">7.7</td>
                      <td class="metric" data-label="Avg Vision Score">4.37 / 5.0</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Side Rail -->
          <aside class="reference-panel stack" data-gap="lg">
            <div class="stack" data-gap="sm">
              <h3 style="font-size: var(--text-md); font-family: var(--font-serif); font-weight: 600; margin: 0;">Latest Status (May 18)</h3>
              <p class="caption">Adoption threshold is &ge; 95% pass rate</p>
              
              <div class="metric-list" style="margin-top: var(--space-2); --metric-label: 110px; --metric-value: 40px;">
                <div class="metric-row">
                  <span class="caption">Timeline</span>
                  <div class="meter"><span style="--value: 99%"></span></div>
                  <code>99%</code>
                </div>
                <div class="metric-row">
                  <span class="caption">Design System</span>
                  <div class="meter"><span style="--value: 98%"></span></div>
                  <code>98%</code>
                </div>
                <div class="metric-row">
                  <span class="caption">Comp. Variants</span>
                  <div class="meter"><span style="--value: 96%"></span></div>
                  <code>96%</code>
                </div>
              </div>
            </div>

            <div class="stack" data-gap="xs">
              <span class="caption">Final-Week Artifact Details</span>
              <div class="numeric-table-wrap" style="border-radius: var(--radius-sm);">
                <table class="numeric-table" style="min-width: 0; width: 100%;">
                  <thead>
                    <tr>
                      <th>Artifact</th>
                      <th class="metric">Pass</th>
                      <th class="metric">Ovr</th>
                      <th class="metric">RGB Δ</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="entity" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">Timeline</td>
                      <td class="metric" data-label="Pass" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">99%</td>
                      <td class="metric" data-label="Ovr" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">0</td>
                      <td class="metric" data-label="RGB Δ" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">5.4</td>
                    </tr>
                    <tr>
                      <td class="entity" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">Design Sys</td>
                      <td class="metric" data-label="Pass" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">98%</td>
                      <td class="metric" data-label="Ovr" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">0</td>
                      <td class="metric" data-label="RGB Δ" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">6.7</td>
                    </tr>
                    <tr>
                      <td class="entity" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">Comp Var</td>
                      <td class="metric" data-label="Pass" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">96%</td>
                      <td class="metric" data-label="Ovr" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">1</td>
                      <td class="metric" data-label="RGB Δ" style="font-size: var(--text-sm); padding: var(--space-2) var(--space-3);">10.9</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="callout" data-tone="info">
              <span class="callout-label">Source Data &amp; Caveats</span>
              <p style="font-size: var(--text-sm); line-height: 1.5; margin: 0;">
                Data is programmatically sourced from <code>evals/numeric-data/source.csv</code> (last updated May 18, 2026).
              </p>
              <p style="font-size: var(--text-sm); line-height: 1.5; margin-top: var(--space-2); margin-bottom: 0;">
                <strong>Caveat:</strong> A single layout overflow remains in the <code>component-variants</code> run (down from 9 at baseline). This minor 1-pixel rounding offset under density limits is tracked in issue #412 and does not prevent production rollout.
              </p>
            </div>
          </aside>
        </div>
      </section>
    </main>
"""

# Let's read the template and replace body content
template_content = Path("birch-html/resources/template.html").read_text(encoding="utf-8")

# Let's replace title and body
html_out = template_content
html_out = re.sub(r'<title>.*?</title>', '<title>Rendering Checker Stability Assessment</title>', html_out)

# We want to replace everything inside <body>...</body>
body_match = re.search(r'<body>(.*?)</body>', html_out, re.DOTALL)
if body_match:
    html_out = html_out.replace(body_match.group(1), f"\n{body_content}\n  ")

# Let's add the small page-local CSS
css_fixes = """
      .numeric-table th, .numeric-table td {
        white-space: nowrap;
      }
      .numeric-table .entity {
        white-space: normal;
      }
      @media (max-width: 620px) {
        .numeric-table th, .numeric-table td {
          white-space: normal;
        }
      }
"""
html_out = html_out.replace('/* Optional small page-local CSS using Birch tokens only. */', css_fixes)

# Write to final path
out_path = Path("eval-runs/skill-with-shell-gemini35flash-clean-birch-multimodel-20260522-235250/numeric-data.html")
out_path.write_text(html_out, encoding="utf-8")
print(f"Wrote to {out_path}")

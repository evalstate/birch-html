# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "matplotlib>=3.8,<4",
# ]
# ///
from __future__ import annotations

import csv
from collections import defaultdict
from html import escape
from pathlib import Path
import re
import sys

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from birch_mpl import birch_theme, close, polish_axes, svg_string  # noqa: E402


DATA = ROOT / "evals" / "charts" / "sample-data.csv"
OUT = ROOT / "24-birch-chart-brief.html"


def pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def num(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}"


def slug(value: str) -> str:
    return value.replace("-", " ").title()


def load_rows() -> list[dict[str, object]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["static_pass_rate"] = float(row["static_pass_rate"])
        row["overflow_count"] = int(row["overflow_count"])
        row["palette_close"] = float(row["palette_close"])
        row["mean_rgb_delta"] = float(row["mean_rgb_delta"])
        row["vision_score"] = float(row["vision_score"])
    return rows


def build_svg(rows: list[dict[str, object]]) -> str:
    weeks = sorted({str(row["week"]) for row in rows})
    by_artifact: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        by_artifact[str(row["artifact"])][str(row["week"])] = row

    with birch_theme():
        fig, ax = plt.subplots(figsize=(5.8, 3.45))
        for artifact in sorted(by_artifact):
            values = [by_artifact[artifact][week]["static_pass_rate"] for week in weeks]
            ax.plot(
                weeks,
                values,
                marker="o",
                linewidth=2.2,
                markersize=4.2,
                label=slug(artifact),
            )
        ax.set_title("Static pass rate improved across all tracked artifacts", loc="left", pad=12)
        ax.set_ylabel("Static checks passing")
        ax.set_ylim(0.78, 1.01)
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax.legend(ncols=3, loc="lower right", columnspacing=0.9)
        ax.set_xlabel("")
        polish_axes(ax)
        ax.tick_params(axis="x", labelrotation=0)
        svg = svg_string(fig)
        close(fig)

    svg = re.sub(r"<svg\b", '<svg class="chart-svg" role="img" aria-label="Line chart showing weekly static pass rate by artifact"', svg, count=1)
    return svg


def latest_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    latest_week = max(str(row["week"]) for row in rows)
    return sorted((row for row in rows if row["week"] == latest_week), key=lambda row: str(row["artifact"]))


def previous_latest(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    weeks = sorted({str(row["week"]) for row in rows})
    prev, latest = weeks[-2], weeks[-1]
    return (
        [row for row in rows if row["week"] == prev],
        [row for row in rows if row["week"] == latest],
    )


def metric_rows(rows: list[dict[str, object]]) -> str:
    ranked = sorted(rows, key=lambda row: float(row["vision_score"]), reverse=True)
    parts = []
    for row in ranked:
        score = float(row["vision_score"])
        tone = "var(--success)" if score >= 4.4 else "var(--accent)"
        parts.append(
            f"""          <div class="metric-row">
            <span class="caption">{escape(slug(str(row["artifact"])))}</span>
            <div class="meter"><span style="--value: {score / 5 * 100:.0f}%; --tone: {tone};"></span></div>
            <code>{score:.1f}/5</code>
          </div>"""
        )
    return "\n".join(parts)


def table_rows(rows: list[dict[str, object]]) -> str:
    parts = []
    for row in sorted(rows, key=lambda row: str(row["artifact"])):
        parts.append(
            f"""            <tr>
              <td class="entity">{escape(slug(str(row["artifact"])))}<span class="subtle">{escape(str(row["week"]))}</span></td>
              <td class="metric" data-label="pass rate">{pct(float(row["static_pass_rate"]))}</td>
              <td class="metric" data-label="overflow">{int(row["overflow_count"])}</td>
              <td class="metric" data-label="palette">{pct(float(row["palette_close"]))}</td>
              <td class="metric" data-label="vision">{num(float(row["vision_score"]))}/5</td>
              <td class="note">{escape(str(row["notes"]))}</td>
            </tr>"""
        )
    return "\n".join(parts)


def main() -> None:
    rows = load_rows()
    latest = latest_rows(rows)
    prev, current = previous_latest(rows)
    svg = build_svg(rows)

    avg_pass = sum(float(row["static_pass_rate"]) for row in latest) / len(latest)
    total_overflow = sum(int(row["overflow_count"]) for row in latest)
    avg_vision = sum(float(row["vision_score"]) for row in latest) / len(latest)
    avg_delta = sum(float(row["mean_rgb_delta"]) for row in latest) / len(latest)
    prev_overflow = sum(int(row["overflow_count"]) for row in prev)

    html = f"""<!-- Copyright 2026 Anthropic PBC · SPDX-License-Identifier: Apache-2.0 -->
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Birch chart brief — rendering checker adoption signal</title>
<link rel="stylesheet" href="styles/birch-system.css">
</head>
<body>
<main class="page stack" data-gap="lg">
  <header class="stack" data-gap="sm">
    <div class="eyebrow">Numeric data brief</div>
    <h1>Rendering checker stability is trending toward adoption.</h1>
    <p class="lede">Sample evaluation data shows higher static pass rates, lower visible overflow, and improving vision scores across the three tracked Birch artifacts.</p>
    <div class="cluster">
      <span class="chip" data-tone="olive">Matplotlib SVG</span>
      <span class="chip">Birch numeric table</span>
      <span class="chip">Evidence first</span>
    </div>
  </header>

  <section class="section stack" data-gap="lg">
    <div class="section-head">
      <div>
        <span class="eyebrow">Latest week</span>
        <h2>Adoption signal</h2>
      </div>
      <span class="badge" data-tone="success">2026-05-18</span>
    </div>

    <div class="grid" data-cols="4">
      <article class="card stack" data-variant="outlined">
        <span class="caption">Average static pass</span>
        <strong class="stat-value">{pct(avg_pass)}</strong>
        <p class="muted">Across design-system, component variants, and timeline pages.</p>
      </article>
      <article class="card stack" data-variant="outlined">
        <span class="caption">Visible overflow</span>
        <strong class="stat-value">{total_overflow}</strong>
        <p class="muted">Down from {prev_overflow} in the previous weekly sample.</p>
      </article>
      <article class="card stack" data-variant="outlined">
        <span class="caption">Average vision score</span>
        <strong class="stat-value">{avg_vision:.1f}/5</strong>
        <p class="muted">Validator-readiness proxy from visual review samples.</p>
      </article>
      <article class="card stack" data-variant="outlined">
        <span class="caption">Mean RGB delta</span>
        <strong class="stat-value">{avg_delta:.1f}</strong>
        <p class="muted">Lower is better; visual drift continues to narrow.</p>
      </article>
    </div>
  </section>

  <section class="section stack" data-gap="lg">
    <div class="section-head">
      <span class="eyebrow">Trend</span>
    </div>

    <div class="split">
      <div class="stack" data-gap="lg">
        <h2>Static checks improved every week</h2>

        <div class="panel chart-panel stack" data-gap="sm">
          {svg}
          <p class="chart-caption">Generated with <code>scripts/birch_mpl.py</code> and inlined as SVG. The plotted values are exact weekly static pass rates from <code>evals/charts/sample-data.csv</code>.</p>
        </div>
      </div>

      <aside class="reference-panel stack" data-gap="md">
        <h3>Vision-score ranking</h3>
        <div class="metric-list">
{metric_rows(latest)}
        </div>
        <p class="muted">The timeline artifact is the strongest candidate for adoption; component variants still has one visible overflow issue to remove.</p>
      </aside>
    </div>
  </section>

  <section class="section stack" data-gap="lg">
    <div class="section-head">
      <div>
        <span class="eyebrow">Exact values</span>
        <h2>Latest sample by artifact</h2>
      </div>
    </div>

    <div class="numeric-table-wrap">
      <table class="numeric-table">
        <thead>
          <tr>
            <th class="label-cell">Artifact</th>
            <th class="metric">Pass rate</th>
            <th class="metric">Overflow</th>
            <th class="metric">Palette</th>
            <th class="metric">Vision</th>
            <th>Note</th>
          </tr>
        </thead>
        <tbody>
{table_rows(latest)}
        </tbody>
      </table>
    </div>
  </section>

  <section class="section stack" data-gap="md">
    <div class="card stack" data-variant="flat">
      <h2>Source and caveat</h2>
      <p>Data is a synthetic chart-eval fixture for validating Birch chart generation. It is useful for exercising layout, Matplotlib SVG rendering, numeric tables, ranking bars, and visual validation, but it is not a production quality metric source.</p>
    </div>
  </section>
</main>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "matplotlib>=3.8,<4",
# ]
# ///
"""Generate inline SVG charts for benchmark-comparison report."""
import sys
sys.path.insert(0, "/home/shaun/source/birch-html/skill/scripts")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from birch_mpl import birch_theme, polish_axes, svg_string, close, COLORS, PALETTE

# ── Chart 1: Tradeoff – Quality Score vs Estimated Cost ─────────────────────
with birch_theme():
    fig, ax = plt.subplots(figsize=(5.8, 3.4))

    seeds = {"Seed A": (0.9175, 1.92), "Candidate B": (0.9655, 2.14)}
    colors = [COLORS["sky"], COLORS["clay"]]
    markers = ["o", "D"]

    for (label, (score, cost)), color, marker in zip(seeds.items(), colors, markers):
        ax.scatter(cost, score, s=180, color=color, marker=marker, zorder=5, label=label)
        offset_x = 0.005
        offset_y = -0.004 if label == "Seed A" else 0.003
        ax.annotate(label, (cost, score),
                    textcoords="offset points", xytext=(8, 0),
                    fontsize=9, color=COLORS["gray_700"],
                    va="center")

    # Arrow showing direction of improvement
    ax.annotate("", xy=(2.14, 0.9655), xytext=(1.92, 0.9175),
                arrowprops=dict(arrowstyle="->", color=COLORS["gray_500"],
                                lw=1.2, connectionstyle="arc3,rad=0.1"))

    ax.set_xlabel("Estimated Cost (USD)", labelpad=6)
    ax.set_ylabel("Final Score (weighted)", labelpad=6)
    ax.set_title("Quality vs Cost Tradeoff", pad=10)
    ax.set_xlim(1.75, 2.35)
    ax.set_ylim(0.895, 0.985)
    polish_axes(ax, grid_axis="both")
    ax.legend(loc="lower right", fontsize=9)

svg1 = svg_string(fig)
close(fig)

# ── Chart 2: Per-eval score comparison (grouped bars) ────────────────────────
evals = ["numeric-data", "code-review", "module-explainer", "impl-plan"]
seed_scores = [0.930, 0.910, 0.925, 0.905]
cand_scores = [0.970, 0.955, 0.944, 0.993]

x = np.arange(len(evals))
width = 0.35

with birch_theme():
    fig2, ax2 = plt.subplots(figsize=(6.2, 3.4))

    bars1 = ax2.bar(x - width/2, seed_scores, width, label="Seed A",
                    color=COLORS["sky"], alpha=0.85, zorder=3)
    bars2 = ax2.bar(x + width/2, cand_scores, width, label="Candidate B",
                    color=COLORS["clay"], alpha=0.85, zorder=3)

    # Value labels
    for bar, val in zip(bars1, seed_scores):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                 f"{val:.3f}", ha="center", va="bottom", fontsize=7.5,
                 color=COLORS["gray_700"])
    for bar, val in zip(bars2, cand_scores):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                 f"{val:.3f}", ha="center", va="bottom", fontsize=7.5,
                 color=COLORS["gray_700"])

    ax2.set_xticks(x)
    ax2.set_xticklabels(evals, fontsize=8.5)
    ax2.set_ylabel("Eval Score", labelpad=6)
    ax2.set_title("Per-Eval Score Comparison", pad=10)
    ax2.set_ylim(0.87, 1.01)
    ax2.legend(loc="lower right", fontsize=9)
    polish_axes(ax2, grid_axis="y")

svg2 = svg_string(fig2)
close(fig2)

# ── Chart 3: Multi-metric delta bar (normalized % change) ────────────────────
metrics = ["Score\n+0.048", "Checker\nWarnings\n−3", "Wall Time\n+77s", "Tokens\n+8.7K", "Cost\n+$0.22"]
deltas = [+5.23, -60.0, +18.7, +7.5, +11.5]  # % change
metric_colors = [COLORS["olive"] if d < 0 else (COLORS["clay"] if d > 0 else COLORS["sky"]) for d in deltas]
# For score delta it's positive = good; for warnings negative = good
good_pos = [True, False, False, False, False]  # True means higher is better
bar_colors = []
for d, gp in zip(deltas, good_pos):
    if gp:
        bar_colors.append(COLORS["olive"] if d > 0 else COLORS["rust"])
    else:
        bar_colors.append(COLORS["olive"] if d < 0 else COLORS["clay"])

with birch_theme():
    fig3, ax3 = plt.subplots(figsize=(6.2, 3.0))

    bars3 = ax3.bar(range(len(metrics)), deltas, color=bar_colors, zorder=3, alpha=0.88)
    ax3.axhline(0, color=COLORS["gray_300"], linewidth=1.0, zorder=2)

    for bar, val in zip(bars3, deltas):
        ypos = val + 0.8 if val >= 0 else val - 2.5
        ax3.text(bar.get_x() + bar.get_width()/2, ypos,
                 f"{val:+.1f}%", ha="center", va="bottom", fontsize=8,
                 color=COLORS["gray_700"])

    ax3.set_xticks(range(len(metrics)))
    ax3.set_xticklabels(metrics, fontsize=8)
    ax3.set_ylabel("% Change vs Seed A", labelpad=6)
    ax3.set_title("Candidate B vs Seed A: Relative Deltas", pad=10)
    polish_axes(ax3, grid_axis="y")

svg3 = svg_string(fig3)
close(fig3)

# Write to files so the main script can embed them
with open("/tmp/chart1.svg", "w") as f:
    f.write(svg1)
with open("/tmp/chart2.svg", "w") as f:
    f.write(svg2)
with open("/tmp/chart3.svg", "w") as f:
    f.write(svg3)

print("Charts generated OK")

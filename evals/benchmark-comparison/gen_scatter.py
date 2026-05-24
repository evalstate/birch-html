# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8"]
# ///

import matplotlib.pyplot as plt
import sys
sys.path.insert(0, "/home/shaun/source/birch-html/skill/scripts")
from birch_mpl import birch_theme, polish_axes, svg_string, close

# Data points: (cost_usd, final_score, label)
points = [
    (1.92, 0.9175, "Seed A"),
    (2.14, 0.9655, "Candidate B"),
]

fig, ax = plt.subplots(figsize=(5.5, 3.5))
with birch_theme():
    ax.scatter([p[0] for p in points], [p[1] for p in points], s=90, zorder=5, clip_on=False)
    for x, y, label in points:
        ax.annotate(label, (x, y), textcoords="offset points", xytext=(7, 5),
                    fontsize=8.5, color="#3D3D3A", fontweight="bold")
    # Arrow between points
    ax.annotate("", xy=(2.14, 0.9655), xytext=(1.92, 0.9175),
                arrowprops=dict(arrowstyle="->", color="#D97757", lw=1.5))
    ax.set_xlabel("Est. Cost (USD)", fontsize=9)
    ax.set_ylabel("Final Score", fontsize=9)
    ax.set_title("Quality vs. Cost Tradeoff", fontsize=11, pad=6)
    ax.set_xlim(1.72, 2.38)
    ax.set_ylim(0.895, 1.0)
    ax.xaxis.grid(True, zorder=0)
    polish_axes(ax, grid_axis="x")

svg = svg_string(fig)
close(fig)
print(svg)
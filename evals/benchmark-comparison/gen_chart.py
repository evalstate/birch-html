# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8"]
# ///

import matplotlib.pyplot as plt
import sys
sys.path.insert(0, "/home/shaun/source/birch-html/skill/scripts")
from birch_mpl import birch_theme, polish_axes, svg_string, close

# Data
labels = ["Final\nScore", "Checker\nScore", "Hygiene\nScore", "Generation\nScore"]
seed_values = [0.9175, 0.85, 1.0, 1.0]
candidate_values = [0.9655, 0.94, 0.99, 1.0]

x = list(range(len(labels)))
width = 0.35

fig, ax = plt.subplots(figsize=(7, 3.2))
with birch_theme():
    bars1 = ax.bar([i - width/2 for i in x], seed_values, width, label="Seed A", zorder=3)
    bars2 = ax.bar([i + width/2 for i in x], candidate_values, width, label="Candidate B", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0.7, 1.04)
    ax.set_ylabel("Score", fontsize=9)
    ax.set_title("Score Component Comparison", fontsize=11, pad=6)
    ax.legend(fontsize=8, frameon=False)
    ax.yaxis.grid(True, zorder=0)
    polish_axes(ax, grid_axis="y")
    # Add value labels
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=7.5, color="#87867F")
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=7.5, color="#87867F")

svg = svg_string(fig)
close(fig)
print(svg)
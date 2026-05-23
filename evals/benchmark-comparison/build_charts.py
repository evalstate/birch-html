"""Generate inline SVG charts for benchmark-comparison artifact."""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "birch-html" / "scripts"))
import birch_mpl as am
import matplotlib.pyplot as plt
import numpy as np

OUT = pathlib.Path(__file__).parent

# Chart 1: primary tradeoff - quality (final score) vs cost (usd) + warnings.
runs = [
    {"label": "Seed A",      "score": 0.9175, "cost": 1.92, "wall": 412, "warn": 5, "tokens": 116000},
    {"label": "Candidate B", "score": 0.9655, "cost": 2.14, "wall": 489, "warn": 2, "tokens": 124700},
]

with am.birch_theme():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.6))

    # Left: slope/delta of final score and checker warnings
    labels = [r["label"] for r in runs]
    x = [0, 1]
    score = [r["score"] for r in runs]
    warn = [r["warn"] for r in runs]

    ax1.plot(x, score, marker="o", color=am.COLORS["olive"], linewidth=2.2, label="Final score")
    for xi, yi in zip(x, score):
        ax1.annotate(f"{yi:.3f}", (xi, yi), textcoords="offset points",
                     xytext=(0, 10), ha="center", fontsize=9, color=am.COLORS["slate"])
    ax1.set_ylim(0.88, 1.005)
    ax1.set_ylabel("Final score (0-1)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)

    ax1b = ax1.twinx()
    ax1b.plot(x, warn, marker="s", color=am.COLORS["clay"], linewidth=2.2, label="Checker warnings")
    for xi, yi in zip(x, warn):
        ax1b.annotate(str(yi), (xi, yi), textcoords="offset points",
                      xytext=(0, -16), ha="center", fontsize=9, color=am.COLORS["clay_dark"])
    ax1b.set_ylim(0, 7)
    ax1b.set_ylabel("Checker warnings", color=am.COLORS["clay_dark"])
    ax1b.spines["top"].set_visible(False)
    ax1b.spines["right"].set_color(am.COLORS["gray_300"])
    ax1b.tick_params(axis="y", length=0, pad=6, colors=am.COLORS["clay_dark"])

    am.polish_axes(ax1)
    ax1.set_title("Quality up, warnings down")

    # Right: cost & wall time bars
    metrics = ["Cost (USD)", "Wall time (s)", "Total tokens (k)"]
    seed_vals = [1.92, 412, 116.0]
    cand_vals = [2.14, 489, 124.7]
    # normalise each metric to seed=100
    seed_norm = [100.0, 100.0, 100.0]
    cand_norm = [cand_vals[i] / seed_vals[i] * 100 for i in range(3)]

    xpos = np.arange(len(metrics))
    width = 0.36
    b1 = ax2.bar(xpos - width/2, seed_norm, width, color=am.COLORS["sky"], label="Seed A (100)")
    b2 = ax2.bar(xpos + width/2, cand_norm, width, color=am.COLORS["clay"], label="Candidate B")

    for rect, val, raw in zip(b2, cand_norm, cand_vals):
        ax2.annotate(f"+{val-100:.1f}%",
                     (rect.get_x() + rect.get_width()/2, rect.get_height()),
                     textcoords="offset points", xytext=(0, 4),
                     ha="center", fontsize=9, color=am.COLORS["clay_dark"])
    for rect, val in zip(b1, seed_vals):
        ax2.annotate(f"{val:g}",
                     (rect.get_x() + rect.get_width()/2, 100),
                     textcoords="offset points", xytext=(0, 4),
                     ha="center", fontsize=9, color=am.COLORS["gray_700"])

    ax2.set_xticks(xpos)
    ax2.set_xticklabels(metrics)
    ax2.set_ylabel("Indexed to Seed A = 100")
    ax2.set_ylim(0, 135)
    ax2.legend(loc="lower right")
    am.polish_axes(ax2)
    ax2.set_title("Cost, latency, tokens trade-off")

    (OUT / "chart_tradeoff.svg").write_text(am.svg_string(fig))
    am.close(fig)

# Chart 2: per-eval grouped bars: scores + warnings + wall time
per = [
    {"eval": "numeric-data",        "seed": 0.930, "cand": 0.970, "sw": 2, "cw": 1, "st": 94,  "ct": 113},
    {"eval": "code-review",         "seed": 0.910, "cand": 0.955, "sw": 1, "cw": 0, "st": 102, "ct": 121},
    {"eval": "module-explainer",    "seed": 0.925, "cand": 0.944, "sw": 1, "cw": 1, "st": 111, "ct": 132},
    {"eval": "implementation-plan", "seed": 0.905, "cand": 0.993, "sw": 1, "cw": 0, "st": 105, "ct": 123},
]
names = [p["eval"] for p in per]

with am.birch_theme():
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.2))

    xpos = np.arange(len(names))
    w = 0.36

    # scores
    ax = axes[0]
    ax.bar(xpos - w/2, [p["seed"] for p in per], w, color=am.COLORS["sky"],  label="Seed A")
    ax.bar(xpos + w/2, [p["cand"] for p in per], w, color=am.COLORS["clay"], label="Candidate B")
    ax.set_ylim(0.85, 1.01)
    ax.set_ylabel("Per-eval score")
    ax.set_xticks(xpos); ax.set_xticklabels(names, rotation=18, ha="right")
    ax.legend(loc="lower right")
    am.polish_axes(ax)
    ax.set_title("Score")

    # warnings
    ax = axes[1]
    ax.bar(xpos - w/2, [p["sw"] for p in per], w, color=am.COLORS["sky"])
    ax.bar(xpos + w/2, [p["cw"] for p in per], w, color=am.COLORS["clay"])
    ax.set_ylabel("Checker warnings")
    ax.set_xticks(xpos); ax.set_xticklabels(names, rotation=18, ha="right")
    ax.set_ylim(0, max(3, max(p["sw"] for p in per) + 1))
    am.polish_axes(ax)
    ax.set_title("Warnings")

    # wall time
    ax = axes[2]
    ax.bar(xpos - w/2, [p["st"] for p in per], w, color=am.COLORS["sky"])
    ax.bar(xpos + w/2, [p["ct"] for p in per], w, color=am.COLORS["clay"])
    ax.set_ylabel("Wall time (s)")
    ax.set_xticks(xpos); ax.set_xticklabels(names, rotation=18, ha="right")
    am.polish_axes(ax)
    ax.set_title("Wall time")

    (OUT / "chart_per_eval.svg").write_text(am.svg_string(fig))
    am.close(fig)

print("ok")

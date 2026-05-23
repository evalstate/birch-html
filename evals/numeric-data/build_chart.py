from pathlib import Path
import csv
import matplotlib.pyplot as plt
import sys

# Add the skill scripts directory to import birch_mpl
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "birch-html" / "scripts"))
from birch_mpl import birch_theme, polish_axes, svg_string, PALETTE

# Read CSV
rows = []
with open("/home/ssmith/temp/html-effectiveness/evals/numeric-data/source.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Group by artifact
artifacts = {}
for row in rows:
    name = row["artifact"]
    if name not in artifacts:
        artifacts[name] = {"weeks": [], "pass_rate": []}
    artifacts[name]["weeks"].append(row["week"])
    artifacts[name]["pass_rate"].append(float(row["static_pass_rate"]))

# Build chart
with birch_theme(transparent=True):
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=120)
    
    for idx, (name, data) in enumerate(artifacts.items()):
        ax.plot(
            data["weeks"],
            data["pass_rate"],
            marker="o",
            markersize=5,
            linewidth=2.2,
            color=PALETTE[idx],
            label=name.replace("-", " ").title(),
            zorder=3,
        )
    
    polish_axes(ax, grid_axis="y")
    ax.set_ylim(0.75, 1.02)
    ax.set_ylabel("Static pass rate")
    ax.set_xlabel("Week")
    ax.legend(loc="lower right")
    
    svg = svg_string(fig)
    plt.close(fig)

output_path = Path("/home/ssmith/temp/html-effectiveness/evals/numeric-data/chart.svg")
output_path.write_text(svg, encoding="utf-8")
print(f"Wrote {output_path}")

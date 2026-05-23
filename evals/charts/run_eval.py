#!/usr/bin/env python3
"""Regenerate and validate the Birch chart fixture.

This is intentionally a tiny reusable eval runner around the fixture data in
`evals/charts/sample-data.csv`. It exercises the Matplotlib SVG path and the
Birch rendering checker at desktop and mobile viewports.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

VIEWPORTS = {
    "chart-brief": "desktop:1365x900",
    "chart-brief-mobile": "mobile:390x900",
    "chart-brief-deep": "deep:1365x2400",
    "chart-brief-mobile-deep": "mobile-deep:390x3000",
}


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    run(["uv", "run", "--with", "matplotlib", "python", "evals/charts/build_chart_brief.py"])

    for name, viewport in VIEWPORTS.items():
        run(
            [
                "uv",
                "run",
                "--with",
                "pillow",
                "python",
                "scripts/check_birch_renderings.py",
                "--artifact",
                "24-birch-chart-brief.html",
                "--out",
                f"reports/birch-rendering-check-{name}.json",
                "--markdown",
                f"reports/birch-rendering-check-{name}.md",
                "--viewport",
                viewport,
            ]
        )


if __name__ == "__main__":
    main()

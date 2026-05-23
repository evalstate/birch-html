#!/usr/bin/env python3
"""Run Birch skill evals for multiple models without stopping on failures.

This is the final-run batch wrapper for expensive multi-model comparisons. It
invokes ``scripts/run_skill_evals.py`` once per model, records every return code,
continues after deterministic-check failures, and can optionally run the VLM
screenshot reviewer for every label that produced all five HTML artifacts. If
the normal eval run failed before screenshots were produced, the wrapper renders
the existing artifacts first so the vision pass is still comparable.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_NAMES = [
    "numeric-data",
    "code-review",
    "module-explainer",
    "implementation-plan",
    "benchmark-comparison",
]
VIEWPORTS = [
    ("desktop", "desktop:1365x900"),
    ("mobile", "mobile:390x900"),
    ("deep", "deep:1365x2400"),
    ("mobile-deep", "mobile-deep:390x2400"),
]


def stamp() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-") or "model"


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def snapshot_inputs(root: Path) -> None:
    snap = root / "snapshot"
    snap.mkdir(parents=True, exist_ok=True)
    copy_tree(ROOT / "skill", snap / "skill")
    copy_tree(ROOT / "evals", snap / "evals")
    copy_tree(ROOT / "styles", snap / "styles")
    copy_tree(ROOT / "docs", snap / "docs")
    scripts = snap / "scripts"
    scripts.mkdir(exist_ok=True)
    for name in [
        "birch_mpl.py",
        "eval_harness.py",
        "run_skill_evals.py",
        "run_multimodel_skill_evals.py",
        "check_birch_renderings.py",
        "review_birch_screenshots_with_vision.py",
    ]:
        shutil.copy2(ROOT / "scripts" / name, scripts / name)


def run_command(cmd: list[str], stdout: Path, stderr: Path) -> int:
    stdout.parent.mkdir(parents=True, exist_ok=True)
    with stdout.open("w", encoding="utf-8") as out, stderr.open("w", encoding="utf-8") as err:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=out, stderr=err, check=False)
    return proc.returncode


def artifact_paths(label: str) -> list[Path]:
    out_dir = ROOT / "eval-runs" / label
    return [out_dir / f"{name}.html" for name in EVAL_NAMES]


def has_all_artifacts(label: str) -> bool:
    return all(path.exists() for path in artifact_paths(label))


def has_screenshots(label: str) -> bool:
    screenshots = ROOT / "eval-runs" / "reports" / label / "screenshots"
    return screenshots.exists() and any(screenshots.glob("*.png"))


def ensure_screenshots(label: str, log_root: Path) -> None:
    if has_screenshots(label) or not has_all_artifacts(label):
        return
    report_dir = ROOT / "eval-runs" / "reports" / label
    screenshots = report_dir / "screenshots"
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts = artifact_paths(label)
    for viewport_name, viewport in VIEWPORTS:
        cmd = [
            "uv",
            "run",
            "--with",
            "pillow",
            "python",
            "scripts/check_birch_renderings.py",
            "--out",
            str(report_dir / f"{label}-visionfill-{viewport_name}.json"),
            "--markdown",
            str(report_dir / f"{label}-visionfill-{viewport_name}.md"),
            "--viewport",
            viewport,
            "--screenshots-dir",
            str(screenshots),
        ]
        for artifact in artifacts:
            cmd.extend(["--artifact", str(artifact)])
        run_command(
            cmd,
            log_root / f"{label}.visionfill-{viewport_name}.stdout",
            log_root / f"{label}.visionfill-{viewport_name}.stderr",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", required=True, help="Model alias to run. Repeatable.")
    parser.add_argument("--experiment", help="Experiment slug under eval-runs/multimodel/.")
    parser.add_argument("--label-prefix", default="skill-with-shell", help="Per-model label prefix.")
    parser.add_argument("--skill-dir", default="skill")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--generation-timeout", type=int, default=1200)
    parser.add_argument("--vision", action="store_true", help="Run VLM screenshot review after each model run.")
    parser.add_argument("--vision-model", default="codexresponses.gpt-5.5")
    parser.add_argument("--no-snapshot", action="store_true", help="Skip snapshotting skill/eval/scripts inputs.")
    args = parser.parse_args()

    experiment = args.experiment or f"birch-multimodel-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    exp_root = ROOT / "eval-runs" / "multimodel" / experiment
    log_root = ROOT / "eval-runs" / "logs" / experiment
    exp_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    if not args.no_snapshot:
        snapshot_inputs(exp_root)

    status_path = exp_root / "runs.tsv"
    status_path.write_text(
        "label\tmodel\teval_rc\tvision_rc\tstarted_at\tfinished_at\n",
        encoding="utf-8",
    )
    (exp_root / "experiment.json").write_text(
        json.dumps(
            {
                "experiment": experiment,
                "models": args.model,
                "skill_dir": args.skill_dir,
                "jobs": args.jobs,
                "generation_timeout_s": args.generation_timeout,
                "vision": args.vision,
                "vision_model": args.vision_model if args.vision else None,
                "created_at": stamp(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    for model in args.model:
        label = f"{args.label_prefix}-{slug(model)}-{experiment}"
        started = stamp()
        eval_cmd = [
            sys.executable,
            "scripts/run_skill_evals.py",
            "--skill-dir",
            args.skill_dir,
            "--model",
            model,
            "--label",
            label,
            "--shell-tools",
            "--output-mode",
            "file",
            "--jobs",
            str(args.jobs),
            "--generation-timeout",
            str(args.generation_timeout),
            "--purpose",
            f"With-shell Birch HTML skill benchmark for {model}",
        ]
        eval_rc = run_command(eval_cmd, log_root / f"{label}.stdout", log_root / f"{label}.stderr")

        vision_rc: int | str = ""
        if args.vision and has_all_artifacts(label):
            ensure_screenshots(label, log_root)
            vision_cmd = [
                sys.executable,
                "scripts/review_birch_screenshots_with_vision.py",
                str(ROOT / "eval-runs" / label),
                str(ROOT / "eval-runs" / "reports" / label),
                "--model",
                args.vision_model,
            ]
            vision_rc = run_command(
                vision_cmd,
                log_root / f"{label}.vision.stdout",
                log_root / f"{label}.vision.stderr",
            )
        finished = stamp()
        with status_path.open("a", encoding="utf-8") as fh:
            fh.write(f"{label}\t{model}\t{eval_rc}\t{vision_rc}\t{started}\t{finished}\n")
        print(f"{label}\t{model}\teval_rc={eval_rc}\tvision_rc={vision_rc}", flush=True)


if __name__ == "__main__":
    main()

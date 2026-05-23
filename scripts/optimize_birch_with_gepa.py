#!/usr/bin/env python3
"""Legacy docs-first GEPA helpers.

This file is kept because `optimize_birch_skill_with_gepa.py` imports its
reflection-LM and feedback helpers.  The old docs-first loop depended on a
repo-mode migration evaluator that is not part of this project layout anymore.
When executed directly, this compatibility wrapper delegates to the current
skill-based GEPA loop instead.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = ROOT / "eval-runs" / "gepa"

COMPONENTS = {
    "style_guide": "docs/birch-llm-style-guide.md",
    "recipe_numeric_data": "docs/birch-recipes/numeric-data.md",
    "recipe_code_review": "docs/birch-recipes/code-review.md",
    "recipe_module_explainer": "docs/birch-recipes/module-explainer.md",
    "recipe_implementation_plan": "docs/birch-recipes/implementation-plan.md",
}

OBJECTIVE = """Improve the Birch HTML generation contract and recipes.

The optimized text should make a single task model generate source-grounded,
mobile-safe Birch HTML artifacts that pass the deterministic Birch checker while
using the existing Birch CSS primitives rather than bespoke styles. Preserve the
public design-system contract: do not rename primitives, do not introduce
Birchline-only classes, and do not require external assets or scripts.

Optimize guidance quality, not prose novelty. Prefer short, explicit rules that
prevent observed failures: invented CSS variables/classes, weak semantic
component use, mobile overflow, unwrapped code/diffs, and unsupported one-off
layout systems.
"""

BACKGROUND = """The Birch repo contains a canonical CSS file, an LLM-facing style
guide, recipe documents, source fixtures, and a deterministic checker. The task
model receives the candidate guide/recipes and must return standalone HTML.

Evaluator signals include:
- generation success for four evals: numeric-data, code-review,
  module-explainer, implementation-plan;
- desktop and mobile checker failures/warnings;
- undefined CSS variables, unsupported classes, missing Birch CSS/page shell,
  insufficient semantic components, geometry/mobile overflow findings;
- static recipe summary counts for cards, tables, flow steps, wrapped code/diff,
  external assets, denied classes.

Actionable examples:
- If a model emits `--unknown`, tell it to use only listed Birch tokens or local
  variables with concrete definitions; never placeholder variable names.
- If semantic component warnings appear, recipes should require specific Birch
  primitives such as `.card`, `.stat-card`, `.chart-panel`, `.numeric-table`,
  `.diff`, `.timeline`, `.flow-list`, and `.callout` where appropriate.
- If mobile/split alignment warnings appear, prefer `.section-rail`, `.stack`,
  `.auto-grid`, `.scroll-x`, `.numeric-table-wrap`, and `data-wrap="true"`.
"""


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "run"


def read_seed() -> dict[str, str]:
    return {name: (ROOT / rel).read_text(encoding="utf-8") for name, rel in COMPONENTS.items()}


def materialize(candidate: dict[str, str], workspace: Path) -> None:
    if workspace.exists():
        shutil.rmtree(workspace)
    for name, rel in COMPONENTS.items():
        path = workspace / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(candidate.get(name) or (ROOT / rel).read_text(encoding="utf-8"), encoding="utf-8")


def tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if len(text) > limit else text


def as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def existing_candidate_count(run_root: Path) -> int:
    highest = 0
    for path in run_root.glob("candidate-*"):
        if not path.is_dir():
            continue
        try:
            highest = max(highest, int(path.name.rsplit("-", 1)[1]))
        except (IndexError, ValueError):
            continue
    return highest


class FastAgentReflectionLM:
    """GEPA reflection LM backed by fast-agent one-shot mode."""

    def __init__(self, *, model: str, run_dir: Path, fast_agent_bin: str = "fast-agent") -> None:
        self.model = model
        self.run_dir = run_dir
        self.fast_agent_bin = fast_agent_bin
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._count = 0
        self._total_tokens_in = 0
        self._total_tokens_out = 0
        self._total_cost = 0.0

    @property
    def total_cost(self) -> float:
        return self._total_cost

    @property
    def total_tokens_in(self) -> int:
        return self._total_tokens_in

    @property
    def total_tokens_out(self) -> int:
        return self._total_tokens_out

    def __call__(self, prompt: str | list[dict[str, Any]]) -> str:
        with self._lock:
            self._count += 1
            idx = self._count
        call_dir = self.run_dir / f"call-{idx:03d}"
        call_dir.mkdir(parents=True, exist_ok=True)
        prompt_text = prompt if isinstance(prompt, str) else json.dumps(prompt, ensure_ascii=False, indent=2)
        prompt_path = call_dir / "prompt.md"
        results_path = call_dir / "results.json"
        prompt_path.write_text(prompt_text, encoding="utf-8")
        cmd = [
            self.fast_agent_bin,
            "--no-update-check",
            "go",
            "--env",
            str(ROOT / ".fast-agent"),
            "--config-path",
            str(ROOT / ".fast-agent" / "fast-agent.yaml"),
            "--prompt-file",
            str(prompt_path),
            "--model",
            self.model,
            "--quiet",
            "--results",
            str(results_path),
        ]
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
        (call_dir / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
        (call_dir / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
        if proc.returncode:
            raise RuntimeError(f"fast-agent reflection failed ({proc.returncode})\n{tail(proc.stderr)}")
        self._record_usage(results_path)
        return proc.stdout

    def _record_usage(self, results_path: Path) -> None:
        if not results_path.exists():
            return
        try:
            doc = json.loads(results_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return
        for message in doc.get("messages", []):
            for block in (message.get("channels") or {}).get("fast-agent-usage", []):
                try:
                    usage = json.loads(block.get("text") or "{}")
                except json.JSONDecodeError:
                    continue
                turn = usage.get("turn") or {}
                self._total_tokens_in += int(turn.get("input_tokens") or 0)
                self._total_tokens_out += int(turn.get("output_tokens") or 0)


class BirchEvaluator:
    def __init__(self, *, run_root: Path, task_model: str, fast_agent_bin: str) -> None:
        self.run_root = run_root
        self.task_model = task_model
        self.fast_agent_bin = fast_agent_bin
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.count = existing_candidate_count(self.run_root)

    def __call__(self, candidate: dict[str, str]) -> tuple[float, dict[str, Any]]:
        self.count += 1
        candidate_dir = self.run_root / f"candidate-{self.count:03d}"
        workspace = candidate_dir / "workspace"
        artifacts = candidate_dir / "artifacts"
        reports = candidate_dir / "reports"
        prompts = candidate_dir / "prompts"
        candidate_dir.mkdir(parents=True, exist_ok=True)
        materialize(candidate, workspace)
        (candidate_dir / "candidate.json").write_text(json.dumps(candidate, indent=2), encoding="utf-8")

        label = f"{self.run_root.name}-candidate-{self.count:03d}"
        cmd = [
            sys.executable,
            "scripts/run_migration_evals.py",
            "--model",
            self.task_model,
            "--label",
            label,
            "--candidate-root",
            str(workspace),
            "--out-dir",
            str(artifacts),
            "--report-dir",
            str(reports),
            "--prompt-dir",
            str(prompts),
        ]
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
        proc.stdout = as_text(proc.stdout)
        proc.stderr = as_text(proc.stderr)
        (candidate_dir / "eval.stdout.txt").write_text(proc.stdout, encoding="utf-8")
        (candidate_dir / "eval.stderr.txt").write_text(proc.stderr, encoding="utf-8")

        side_info = self.side_info(candidate_dir, reports, label, proc)
        score = float(side_info["scores"]["gepa_score"])
        (candidate_dir / "score.json").write_text(json.dumps(side_info, indent=2), encoding="utf-8")
        return score, side_info

    def side_info(self, candidate_dir: Path, reports: Path, label: str, proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
        run_json = reports / f"{slug(label)}-run.json"
        run_doc = json.loads(run_json.read_text(encoding="utf-8")) if run_json.exists() else {}
        generation = run_doc.get("generation", [])
        checks = run_doc.get("checks", [])
        static = run_doc.get("static_recipe_summary", {})

        gen_ok = sum(1 for item in generation if item.get("ok"))
        gen_total = max(len(generation), 4)
        generation_score = gen_ok / gen_total

        checker_failures = 0
        checker_warnings = 0
        checker_pairs = 0
        findings = []
        for check in checks:
            path = Path(str(check.get("json", "")))
            if not path.is_absolute():
                path = ROOT / path
            if not path.exists():
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            summary = doc.get("summary", {})
            checker_pairs += int(summary.get("artifacts") or summary.get("pairs") or 0)
            checker_failures += int(summary.get("failures") or 0)
            checker_warnings += int(summary.get("warnings") or 0)
            for item in (doc.get("artifacts") or doc.get("pairs") or []):
                bad = [f for f in item.get("findings", []) if f.get("level") in {"fail", "warn"}]
                if bad:
                    findings.append({"artifact": item.get("artifact") or item.get("candidate"), "findings": bad[:8]})

        checker_score = 1.0 if checker_pairs == 0 else max(0.0, 1.0 - checker_failures / checker_pairs - 0.03 * checker_warnings)
        hygiene_scores = []
        recipe_notes = []
        for name, stats in static.items():
            denied = len(stats.get("denied_classes") or [])
            external = int(stats.get("bad_external_assets") or 0)
            css_ok = bool(stats.get("has_relative_css") and stats.get("has_checker_css"))
            hygiene_scores.append(max(0.0, 1.0 - 0.2 * denied - 0.2 * external - (0 if css_ok else 0.5)))
            recipe_notes.append({"eval": name, **stats})
        hygiene = sum(hygiene_scores) / len(hygiene_scores) if hygiene_scores else 0.0

        gepa_score = max(0.0, min(1.0, 0.45 * generation_score + 0.40 * checker_score + 0.15 * hygiene))
        if proc.returncode and not checks:
            gepa_score *= 0.25

        return {
            "scores": {
                "gepa_score": gepa_score,
                "generation_score": generation_score,
                "checker_score": checker_score,
                "hygiene_score": hygiene,
            },
            "candidate_dir": str(candidate_dir.relative_to(ROOT)),
            "task_model": self.task_model,
            "subprocess": {
                "returncode": proc.returncode,
                "stdout_tail": tail(proc.stdout),
                "stderr_tail": tail(proc.stderr),
            },
            "summary": {
                "generation_ok": gen_ok,
                "generation_total": gen_total,
                "checker_pairs": checker_pairs,
                "checker_failures": checker_failures,
                "checker_warnings": checker_warnings,
            },
            "failures_and_warnings": findings[:12],
            "static_recipe_summary": recipe_notes,
            "actionable_feedback": self.actionable_feedback(findings, recipe_notes),
        }

    def actionable_feedback(self, findings: list[dict[str, Any]], recipe_notes: list[dict[str, Any]]) -> list[str]:
        feedback: list[str] = []
        for item in findings:
            for finding in item.get("findings", []):
                name = finding.get("name")
                evidence = finding.get("evidence", "")
                if name == "no_unknown_css_vars":
                    feedback.append(f"Prevent undefined CSS variables: {evidence}. Tell models to use only documented tokens or locally define concrete variables.")
                elif name == "uses_semantic_components":
                    feedback.append(f"Increase required semantic Birch primitives for {item.get('artifact')}: {evidence}.")
                elif name and "overflow" in name:
                    feedback.append(f"Improve mobile/layout safety for {item.get('artifact')}: {name} {evidence}.")
                elif name:
                    feedback.append(f"Address checker finding {name} for {item.get('artifact')}: {evidence}.")
        for stats in recipe_notes:
            if int(stats.get("bad_external_assets") or 0):
                feedback.append(f"Recipe {stats['eval']} allowed external assets; explicitly prohibit them.")
            if stats.get("denied_classes"):
                feedback.append(f"Recipe {stats['eval']} leaked denied classes: {', '.join(stats['denied_classes'])}.")
        return feedback[:20]


def write_best(run_root: Path, result: Any) -> None:
    best = result.best_candidate
    best_dir = run_root / "best"
    materialize(best, best_dir / "workspace")
    (best_dir / "candidate.json").write_text(json.dumps(best, indent=2), encoding="utf-8")
    (best_dir / "summary.json").write_text(
        json.dumps({"best_idx": result.best_idx, "best_score": result.val_aggregate_scores[result.best_idx]}, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    print(
        "scripts/optimize_birch_with_gepa.py is a legacy docs-first entry point; "
        "delegating to scripts/optimize_birch_skill_with_gepa.py. "
        "Use the skill script directly for new runs.",
        file=sys.stderr,
    )
    from optimize_birch_skill_with_gepa import main as skill_main

    skill_main()


if __name__ == "__main__":
    main()

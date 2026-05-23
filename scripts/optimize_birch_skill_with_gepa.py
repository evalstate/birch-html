#!/usr/bin/env python3
"""Optimize the Birch HTML skill with GEPA.

GEPA mutates only the LLM-facing skill contract and selected recipes.  Each
candidate is materialized into an isolated skills directory before evaluation,
so task-model failures or partial outputs cannot modify the working tree.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import optimize_birch_with_gepa as docs_gepa

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = ROOT / "eval-runs" / "gepa"
SOURCE_SKILL = ROOT / "skill"

COMPONENTS = {
    "SKILL.md": "SKILL.md",
    "recipes/numeric-data.md": "recipes/numeric-data.md",
    "recipes/code-review.md": "recipes/code-review.md",
    "recipes/module-explainer.md": "recipes/module-explainer.md",
    "recipes/implementation-plan.md": "recipes/implementation-plan.md",
    "recipes/benchmark-comparison.md": "recipes/benchmark-comparison.md",
}

OBJECTIVE = """Improve the Birch HTML skill contract and recipes.

The optimized text should make one small, error-prone task model generate
source-grounded, mobile-safe Birch HTML artifacts that pass the deterministic
checker. Preserve the public Birch contract: do not rename primitives, do not
introduce Birchline-only classes, do not require network assets, and do not
change the canonical CSS/scripts/resources.

Prefer terse operational rules over broad prose. Optimize for reliable behavior
from weak local models: complete HTML only, preserved CSS placeholder,
source-grounded claims, mobile wrapping, exact component child contracts, and
minimal valid page-local CSS.
"""

BACKGROUND = """The repo contains a `skill/` fast-agent skill, source
fixtures, a skill-mode eval runner, and a deterministic renderer/checker.  GEPA
mutates only `SKILL.md` and selected recipe markdown files.  Evaluation runs the
task model through fast-agent with an isolated candidate skills directory.

Important failure modes for very small local models:
- returning prose or Markdown fences instead of a complete HTML document;
- omitting the Birch CSS placeholder/page shell;
- copying unsupported classes or inventing CSS variables;
- malformed `.diff-row`, `.flow-step`, `.metric-row`, list, or table markup;
- mobile overflow from long code, paths, diffs, stat values, and numeric tables;
- weak source grounding or hallucinated facts.

Actionable fixes should be short, explicit, and placed near the relevant
workflow or recipe step.
"""


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "run"


def read_seed() -> dict[str, str]:
    return {name: (SOURCE_SKILL / rel).read_text(encoding="utf-8") for name, rel in COMPONENTS.items()}


def materialize(candidate: dict[str, str], skills_root: Path) -> None:
    """Write a complete isolated `skills/birch-html` tree for one candidate."""

    if skills_root.exists():
        shutil.rmtree(skills_root)
    target = skills_root / "birch-html"
    shutil.copytree(
        SOURCE_SKILL,
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    for name, rel in COMPONENTS.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(candidate.get(name) or (SOURCE_SKILL / rel).read_text(encoding="utf-8"), encoding="utf-8")


def as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:  # noqa: BLE001 - metadata only
        return ""


def seed_fingerprint(seed_dir: Path) -> dict[str, Any]:
    files = {}
    for name, rel in COMPONENTS.items():
        path = seed_dir / rel
        if path.exists():
            files[name] = {
                "path": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
                "lines": len(path.read_text(encoding="utf-8").splitlines()),
            }
    return {
        "seed_skill_dir": str(seed_dir.relative_to(ROOT) if seed_dir.is_relative_to(ROOT) else seed_dir),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_dirty": bool(git_value("status", "--short")),
        "files": files,
    }


def write_experiment_doc(run_root: Path, args: argparse.Namespace) -> None:
    """Write human-readable experiment metadata once per GEPA run root."""

    meta = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "purpose": args.purpose,
        "pipeline": "GEPA skill improvement" if not args.evaluate_only else "seed skill benchmark/evaluate-only",
        "run_name": args.run_name,
        "run_root": str(run_root.relative_to(ROOT)),
        "seed": seed_fingerprint(SOURCE_SKILL),
        "models": {"task": args.task_model, "reflection": args.reflection_model},
        "evaluation": {
            "eval_timeout_s": args.eval_timeout,
            "generation_timeout_s": args.generation_timeout,
            "artifact_generation_jobs": max(1, args.eval_jobs),
            "shell_evals": args.shell_eval or [],
            "default_shell_access": False,
            "working_directory": str(ROOT),
        },
        "command": " ".join([Path(sys.executable).name, *sys.argv]),
    }
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "experiment.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    lines = [
        f"# {args.run_name}",
        "",
        f"Purpose: {args.purpose}",
        "",
        "## Pipeline",
        "",
        f"- Mode: {meta['pipeline']}",
        f"- Seed skill: `{meta['seed']['seed_skill_dir']}`",
        f"- Git commit: `{meta['seed']['git_commit'] or 'unknown'}`",
        f"- Git dirty at launch: `{meta['seed']['git_dirty']}`",
        f"- Task model: `{args.task_model}`",
        f"- Reflection model: `{args.reflection_model}`",
        f"- Candidate layout: `{run_root.relative_to(ROOT)}/candidate-001`, `candidate-002`, ...",
        "",
        "## Evaluation harness",
        "",
        f"- Working directory for generation/checking: `{ROOT}`",
        f"- Artifact generation jobs per candidate: `{max(1, args.eval_jobs)}`",
        f"- Generation timeout per artifact: `{args.generation_timeout}s`",
        f"- Full candidate eval timeout: `{args.eval_timeout}s`",
        "- Shell access: on by default for `run_skill_evals.py` so file-mode artifact writing works.",
        f"- Additional per-eval shell flags passed through: `{', '.join(args.shell_eval or []) or 'none'}`",
        "",
        "## Seed files",
        "",
    ]
    for name, info in meta["seed"]["files"].items():
        lines.append(f"- `{name}`: `{info['path']}`, {info['lines']} lines")
    lines.extend(["", "## Command", "", "```bash", meta["command"], "```", ""])
    (run_root / "experiment.md").write_text("\n".join(lines), encoding="utf-8")


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


def read_vision_findings(reports: Path) -> list[dict[str, Any]]:
    """Read optional VLM smoke-review findings for ASI feedback.

    Expected shape:
    {
      "artifacts": [
        {
          "artifact": "numeric-data",
          "findings": [
            {"level": "fail|warn", "name": "vision_chart_malformed", "evidence": "..."}
          ]
        }
      ]
    }

    These findings are intentionally feedback-only for now: they are surfaced in
    `score.json` and `actionable_feedback` so GEPA can act on them in future
    proposals, without making visual taste a hidden hard score.
    """

    path = reports / "vision-findings.json"
    if not path.exists():
        return []
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [
            {
                "artifact": "vision-findings.json",
                "findings": [
                    {
                        "level": "warn",
                        "name": "vision_findings_parse_error",
                        "evidence": f"Could not parse {path}",
                    }
                ],
            }
        ]
    items = doc.get("artifacts") if isinstance(doc, dict) else doc
    if not isinstance(items, list):
        return []
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        bad = [
            f for f in item.get("findings", [])
            if isinstance(f, dict) and f.get("level") in {"fail", "warn"}
        ]
        if bad:
            out.append({"artifact": item.get("artifact") or item.get("screenshot") or "screenshot", "findings": bad})
    return out


def run_vision_review_hook(candidate_dir: Path, reports: Path) -> None:
    """Optionally run a VLM screenshot reviewer before scoring.

    Set `BIRCH_VISION_REVIEW_CMD` to a shell command that accepts:
      1. candidate directory
      2. reports directory

    The command should write `${reports}/vision-findings.json` in the shape read
    by `read_vision_findings()`. By default this invokes the project reviewer,
    which uses fast-agent's multimodal API and therefore accepts fast-agent model
    aliases such as `codexresponses.gpt-5.5`.
    """

    command = os.environ.get("BIRCH_VISION_REVIEW_CMD", "").strip()
    if command.lower() in {"0", "false", "none", "off"}:
        return
    if command:
        cmd = [*command.split(), str(candidate_dir), str(reports)]
    else:
        cmd = [sys.executable, "scripts/review_birch_screenshots_with_vision.py", str(candidate_dir), str(reports)]
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=300,
    )
    (reports / "vision-review.stdout.txt").write_text(as_text(completed.stdout), encoding="utf-8")
    (reports / "vision-review.stderr.txt").write_text(as_text(completed.stderr), encoding="utf-8")
    if completed.returncode and not (reports / "vision-findings.json").exists():
        (reports / "vision-findings.json").write_text(
            json.dumps(
                {
                    "artifacts": [
                        {
                            "artifact": "vision-review",
                            "findings": [
                                {
                                    "level": "warn",
                                    "name": "vision_review_unavailable",
                                    "evidence": f"Vision review command exited {completed.returncode}",
                                }
                            ],
                        }
                    ]
                },
                indent=2,
            ),
            encoding="utf-8",
        )


class BirchSkillEvaluator:
    def __init__(
        self,
        *,
        run_root: Path,
        task_model: str,
        timeout_s: int,
        eval_jobs: int,
        generation_timeout_s: int,
        shell_evals: list[str],
    ) -> None:
        self.run_root = run_root
        self.task_model = task_model.strip()
        self.timeout_s = timeout_s
        self.eval_jobs = max(1, eval_jobs)
        self.generation_timeout_s = max(1, generation_timeout_s)
        self.shell_evals = shell_evals
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.count = existing_candidate_count(self.run_root)

    def __call__(self, candidate: dict[str, str]) -> tuple[float, dict[str, Any]]:
        self.count += 1
        candidate_dir = self.run_root / f"candidate-{self.count:03d}"
        skills_root = candidate_dir / "skills"
        artifacts = candidate_dir / "artifacts"
        reports = candidate_dir / "reports"
        prompts = candidate_dir / "prompts"
        candidate_dir.mkdir(parents=True, exist_ok=True)
        materialize(candidate, skills_root)
        (candidate_dir / "candidate.json").write_text(json.dumps(candidate, indent=2), encoding="utf-8")

        label = f"{self.run_root.name}-candidate-{self.count:03d}"
        cmd = [
            sys.executable,
            "scripts/run_skill_evals.py",
            "--model",
            self.task_model,
            "--label",
            label,
            "--skills-dir",
            str(skills_root),
            "--out-dir",
            str(artifacts),
            "--report-dir",
            str(reports),
            "--prompt-dir",
            str(prompts),
        ]
        if self.eval_jobs > 1:
            cmd.extend(["--jobs", str(self.eval_jobs)])
        cmd.extend(["--generation-timeout", str(self.generation_timeout_s)])
        for name in self.shell_evals:
            cmd.extend(["--shell-eval", name])
        try:
            proc = subprocess.run(
                cmd,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=self.timeout_s,
            )
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            proc = subprocess.CompletedProcess(cmd, 124, as_text(exc.stdout), as_text(exc.stderr))
            timed_out = True

        proc.stdout = as_text(proc.stdout)
        proc.stderr = as_text(proc.stderr)
        (candidate_dir / "eval.stdout.txt").write_text(proc.stdout, encoding="utf-8")
        (candidate_dir / "eval.stderr.txt").write_text(proc.stderr, encoding="utf-8")
        run_vision_review_hook(candidate_dir, reports)

        side_info = self.side_info(candidate_dir, reports, label, proc, timed_out)
        score = float(side_info["scores"]["gepa_score"])
        (candidate_dir / "score.json").write_text(json.dumps(side_info, indent=2), encoding="utf-8")
        return score, side_info

    def side_info(
        self,
        candidate_dir: Path,
        reports: Path,
        label: str,
        proc: subprocess.CompletedProcess[str],
        timed_out: bool,
    ) -> dict[str, Any]:
        run_json = reports / f"{slug(label)}-run.json"
        run_doc = json.loads(run_json.read_text(encoding="utf-8")) if run_json.exists() else {}
        generation = run_doc.get("generation", [])
        checks = run_doc.get("checks", [])
        static = run_doc.get("static_recipe_summary", {})

        gen_ok = sum(1 for item in generation if item.get("ok"))
        gen_total = max(len(generation), 5)
        generation_score = gen_ok / gen_total

        checker_failures = 0
        checker_warnings = 0
        checker_pairs = 0
        findings: list[dict[str, Any]] = []
        unique_bad_findings: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        for check in checks:
            path = Path(str(check.get("json", "")))
            if not path.is_absolute():
                path = ROOT / path
            if not path.exists():
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            summary = doc.get("summary", {})
            checker_pairs += int(summary.get("artifacts") or summary.get("pairs") or 0)
            for item in (doc.get("artifacts") or doc.get("pairs") or []):
                bad = [f for f in item.get("findings", []) if f.get("level") in {"fail", "warn"}]
                if bad:
                    findings.append({"artifact": item.get("artifact") or item.get("candidate"), "findings": bad[:8]})
                artifact = item.get("artifact") or item.get("candidate") or "artifact"
                artifact_name = Path(str(artifact)).name
                for finding in bad:
                    name = str(finding.get("name") or "finding")
                    evidence = str(finding.get("evidence") or "")
                    # Static contract findings are emitted identically for every
                    # viewport. Count each distinct artifact/finding/evidence
                    # once, while still allowing viewport-specific geometry
                    # evidence to count separately when it genuinely differs.
                    key = (artifact_name, str(finding.get("level")), name, evidence)
                    unique_bad_findings.setdefault(key, finding)
        checker_failures = sum(1 for (_artifact, level, _name, _evidence) in unique_bad_findings if level == "fail")
        checker_warnings = sum(1 for (_artifact, level, _name, _evidence) in unique_bad_findings if level == "warn")
        vision_findings = read_vision_findings(reports)
        if vision_findings:
            findings.extend(vision_findings)

        checker_score = 0.0 if checker_pairs == 0 else max(
            0.0,
            1.0 - 0.20 * checker_failures - 0.03 * checker_warnings,
        )
        hygiene_scores = []
        recipe_notes = []
        for name, stats in static.items():
            denied = len(stats.get("denied_classes") or [])
            external = int(stats.get("bad_external_assets") or 0)
            css_ok = bool(stats.get("has_embedded_birch_css") or stats.get("has_checker_css"))
            hygiene_scores.append(max(0.0, 1.0 - 0.2 * denied - 0.2 * external - (0 if css_ok else 0.5)))
            recipe_notes.append({"eval": name, **stats})
        hygiene = sum(hygiene_scores) / len(hygiene_scores) if hygiene_scores else 0.0

        candidate_json = candidate_dir / "candidate.json"
        skill_lines = 0
        if candidate_json.exists():
            try:
                candidate_doc = json.loads(candidate_json.read_text(encoding="utf-8"))
                skill_lines = len(str(candidate_doc.get("SKILL.md") or "").splitlines())
            except json.JSONDecodeError:
                skill_lines = 0
        skill_line_limit = 280
        skill_length_penalty = min(0.25, max(0, skill_lines - skill_line_limit) * 0.001)

        gepa_score = max(
            0.0,
            min(1.0, 0.30 * generation_score + 0.55 * checker_score + 0.15 * hygiene) - skill_length_penalty,
        )
        if timed_out:
            gepa_score *= 0.1
        elif proc.returncode and not checks:
            gepa_score *= 0.25

        feedback = docs_gepa.BirchEvaluator.actionable_feedback(self, findings, recipe_notes)
        for item in vision_findings[:8]:
            artifact = item.get("artifact") or "screenshot"
            for finding in item.get("findings", [])[:4]:
                feedback.insert(
                    0,
                    f"Vision review flagged {finding.get('name', 'visual_aberration')} for {artifact}: "
                    f"{finding.get('evidence', '')}",
                )
        if skill_length_penalty:
            feedback.insert(
                0,
                f"Compress SKILL.md to <= {skill_line_limit} lines; current length is {skill_lines} lines "
                f"and incurred a {skill_length_penalty:.3f} score penalty.",
            )

        return {
            "scores": {
                "gepa_score": gepa_score,
                "generation_score": generation_score,
                "checker_score": checker_score,
                "hygiene_score": hygiene,
                "skill_length_penalty": skill_length_penalty,
            },
            "candidate_dir": str(candidate_dir.relative_to(ROOT)),
            "task_model": self.task_model,
            "timed_out": timed_out,
            "subprocess": {
                "returncode": proc.returncode,
                "stdout_tail": docs_gepa.tail(proc.stdout),
                "stderr_tail": docs_gepa.tail(proc.stderr),
            },
            "summary": {
                "generation_ok": gen_ok,
                "generation_total": gen_total,
                "checker_pairs": checker_pairs,
                "checker_failures": checker_failures,
                "checker_warnings": checker_warnings,
                "skill_lines": skill_lines,
                "skill_line_limit": skill_line_limit,
            },
            "failures_and_warnings": findings[:12],
            "vision_findings": vision_findings,
            "static_recipe_summary": recipe_notes,
            "actionable_feedback": feedback,
        }


def write_best(run_root: Path, result: Any) -> None:
    best = result.best_candidate
    best_dir = run_root / "best"
    materialize(best, best_dir / "skills")
    (best_dir / "candidate.json").write_text(json.dumps(best, indent=2), encoding="utf-8")
    (best_dir / "summary.json").write_text(
        json.dumps({"best_idx": result.best_idx, "best_score": result.val_aggregate_scores[result.best_idx]}, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    global SOURCE_SKILL

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="birch-skill-docs")
    parser.add_argument("--task-model", default="llamacpp-gemma-4-e4b-it-gguf")
    parser.add_argument("--reflection-model", default="codexresponses.gpt-5.5")
    parser.add_argument("--proposals", type=int, default=4, help="GEPA candidate proposals/generations.")
    parser.add_argument("--fast-agent-bin", default="fast-agent")
    parser.add_argument("--gepa-src", type=Path, default=Path.home() / "source" / "gepa" / "src")
    parser.add_argument(
        "--seed-skill-dir",
        type=Path,
        default=SOURCE_SKILL,
        help="Skill directory to use as the GEPA seed, e.g. skill or eval-runs/gepa/<run>/best/skills/birch-html.",
    )
    parser.add_argument("--eval-timeout", type=int, default=1200, help="Seconds allowed for one full candidate eval.")
    parser.add_argument("--eval-jobs", type=int, default=1, help="Parallel artifact generation jobs per candidate.")
    parser.add_argument("--generation-timeout", type=int, default=900, help="Seconds allowed for one artifact generation.")
    parser.add_argument(
        "--shell-eval",
        action="append",
        default=[],
        help="Expose shell/tools only for this eval name during artifact generation. Repeatable.",
    )
    parser.add_argument("--evaluate-only", action="store_true", help="Score the seed skill once; do not run GEPA search.")
    parser.add_argument(
        "--purpose",
        default="Improve and/or benchmark the Birch HTML skill against the five artifact evals.",
        help="Human-readable purpose written to experiment.md.",
    )
    args = parser.parse_args()

    SOURCE_SKILL = args.seed_skill_dir.resolve()
    if not (SOURCE_SKILL / "SKILL.md").exists():
        raise SystemExit(f"--seed-skill-dir must point to a Birch HTML skill directory: {SOURCE_SKILL}")

    run_root = DEFAULT_RUN_ROOT / args.run_name
    run_root.mkdir(parents=True, exist_ok=True)
    write_experiment_doc(run_root, args)
    seed = read_seed()
    (run_root / "seed-candidate.json").write_text(json.dumps(seed, indent=2), encoding="utf-8")

    evaluator = BirchSkillEvaluator(
        run_root=run_root,
        task_model=args.task_model,
        timeout_s=args.eval_timeout,
        eval_jobs=args.eval_jobs,
        generation_timeout_s=args.generation_timeout,
        shell_evals=args.shell_eval or [],
    )
    if args.evaluate_only:
        score, side_info = evaluator(seed)
        print(json.dumps({"score": score, "side_info": side_info}, indent=2))
        return

    if args.gepa_src.exists():
        sys.path.insert(0, str(args.gepa_src))
    from gepa.optimize_anything import EngineConfig, GEPAConfig, ReflectionConfig, optimize_anything

    reflection_lm = docs_gepa.FastAgentReflectionLM(
        model=args.reflection_model,
        run_dir=run_root / "reflection-calls",
        fast_agent_bin=args.fast_agent_bin,
    )
    result = optimize_anything(
        seed_candidate=seed,
        evaluator=evaluator,
        objective=OBJECTIVE,
        background=BACKGROUND,
        config=GEPAConfig(
            engine=EngineConfig(
                run_dir=str(run_root / "gepa-state"),
                max_candidate_proposals=args.proposals,
                parallel=False,
                cache_evaluation=True,
                display_progress_bar=False,
                use_cloudpickle=False,
            ),
            reflection=ReflectionConfig(
                reflection_lm=reflection_lm,
                reflection_minibatch_size=1,
                skip_perfect_score=False,
            ),
            refiner=None,
        ),
    )
    write_best(run_root, result)
    print(json.dumps({"run_root": str(run_root.relative_to(ROOT)), "best_idx": result.best_idx, "best_score": result.val_aggregate_scores[result.best_idx]}, indent=2))


if __name__ == "__main__":
    main()

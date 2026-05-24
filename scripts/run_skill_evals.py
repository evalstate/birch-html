#!/usr/bin/env python3
"""Generate and validate Birch artifacts through natural eval prompts.

This runner uses fast-agent's normal skill injection. With shell/tools enabled,
prompts list repository source paths and expect the model to inspect them. With
shell/tools disabled, prompts include source previews as the no-shell source of
truth.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import subprocess
import sys
import time
from pathlib import Path

import eval_harness as base

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_SKILLS_DIR = ROOT
USE_SHELL_TOOLS = True
SHELL_EVALS: set[str] = set()
RUN_METADATA: dict[str, object] = {}
OUTPUT_MODE = "file"
SOURCE_PREVIEW = "auto"

INSTRUCTION = """You are a helpful AI Agent.

{{serverInstructions}}
{{agentSkills}}
{{file_silent:AGENTS.md}}
{{env}}

Treat benchmark input/source files as read-only. Do not modify repository files
except for the requested output artifact. Temporary scratch files are allowed
only when needed for calculations or chart generation.

The current date is {{currentDate}}.
"""


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def source_preview_enabled(name: str) -> bool:
    if SOURCE_PREVIEW == "always":
        return True
    if SOURCE_PREVIEW == "never":
        return False
    return not (USE_SHELL_TOOLS or name in SHELL_EVALS)


def build_prompt(name: str) -> str:
    spec = base.EVALS[name]
    sources = base.source_paths(spec)
    artifact = base.OUT_DIR / f"{name}.html"
    include_preview = source_preview_enabled(name)
    if OUTPUT_MODE == "file":
        opening = (
            "Create one complete standalone HTML artifact for the following request. "
            "Write the final file to the specified output path and return only that path.\n\n"
        )
    else:
        opening = (
            "Return only one complete standalone HTML document for the following request. "
            "Do not wrap it in Markdown fences and do not include commentary.\n\n"
        )
    parts = [
        opening,
        "## Request\n\n",
        read(str(spec["prompt"])),
        "\n\n## Source files available in the repository\n\n",
    ]
    if include_preview:
        parts.append(
            "The source preview below is the source of truth for this no-shell run. "
            "The paths identify the original repository locations for citation.\n\n"
        )
    else:
        parts.append(
            "Use these local paths as the source of truth. Inspect them directly "
            "before writing claims. Treat source files as read-only.\n\n"
        )
    for path in sources:
        parts.append(f"- `{path}`\n")
    if include_preview:
        parts.append("\n## Source preview\n\n")
        for path in sources:
            parts.append(base.fenced(path, read(path)))
    parts.append("\n## Final output requirements\n\n")
    if OUTPUT_MODE == "file":
        parts.extend(
            [
                f"- Create the artifact for eval `{name}` and write the final standalone HTML file to `{base.rel(artifact)}`.\n",
                "- Return only the artifact path, with no prose or Markdown fences.\n",
            ]
        )
    else:
        parts.extend(
            [
                f"- Create the artifact for eval `{name}`; the intended output path is `{base.rel(artifact)}`.\n",
                "- Do not write the final artifact file yourself; the harness will save your final response to that path.\n",
                "- Return the full HTML document only, starting with `<!doctype html>` or `<html`.\n",
            ]
        )
    parts.extend(
        [
            "- Ensure the main artifact is source-grounded and mobile-safe.\n",
        ]
    )
    return "".join(parts)


def validate_finished_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"expected artifact was not written: {base.rel(path)}")
    html = path.read_text(encoding="utf-8")
    if not html.lower().lstrip().startswith(("<!doctype", "<html")):
        raise ValueError("artifact file does not contain a complete HTML document")
    if "</html>" not in html.lower():
        raise ValueError("artifact file is missing closing </html>")
    if "__BIRCH_SYSTEM_CSS__" in html:
        raise ValueError("artifact still contains __BIRCH_SYSTEM_CSS__; skill finish step did not run")
    if not base.BIRCH_STYLE_RE.search(html):
        raise ValueError("artifact missing style[data-birch-system] embedded Birch CSS")
    return html


def classify_self_check(results_path: Path) -> dict[str, object]:
    """Detect whether the model attempted or ran the Birch deterministic checker.

    This scans the model's own fast-agent trace, not the harness checker. It is
    intentionally conservative: prompt/source mentions and generated artifact
    prose do not count. Reads of checker source count as attempts; shell
    invocations/imports count as self-check runs.
    """

    out: dict[str, object] = {
        "self_check_attempted": False,
        "self_check_ran": False,
        "self_check_succeeded": False,
        "self_check_mode": "",
        "self_check_evidence": "",
    }
    if not results_path.exists():
        return out
    try:
        doc = json.loads(results_path.read_text(encoding="utf-8"))
    except Exception:
        return out

    evidence: list[str] = []
    modes: set[str] = set()
    interesting_calls: dict[str, str] = {}
    missing_terms = ("No such file or directory", "Errno 2", "not found", "can't open file")

    for msg in doc.get("messages", []):
        tool_calls = msg.get("tool_calls") or {}
        if isinstance(tool_calls, dict):
            for call_id, call in tool_calls.items():
                params = call.get("params", {}) if isinstance(call, dict) else {}
                name = params.get("name")
                args = params.get("arguments", {}) if isinstance(params, dict) else {}

                if name == "read_text_file":
                    path = str(args.get("path", ""))
                    if "check_birch_renderings.py" in path:
                        out["self_check_attempted"] = True
                        modes.add("read-checker")
                        interesting_calls[str(call_id)] = "read-checker"
                        evidence.append(f"read {path[:140]}")
                    continue

                if name == "execute":
                    command = str(args.get("command", ""))
                    if "import check_birch_renderings" in command:
                        out["self_check_attempted"] = True
                        out["self_check_ran"] = True
                        modes.add("import-checker")
                        interesting_calls[str(call_id)] = "import-checker"
                        evidence.append(f"imported checker: {command[:180]}")
                    elif "check_birch_renderings.py" in command and ("python" in command or "uv run" in command):
                        out["self_check_attempted"] = True
                        out["self_check_ran"] = True
                        modes.add("run-checker-cli")
                        interesting_calls[str(call_id)] = "run-checker-cli"
                        evidence.append(f"ran checker CLI: {command[:180]}")
                    elif "check_birch_renderings.py" in command:
                        out["self_check_attempted"] = True
                        modes.add("checker-shell-reference")
                        interesting_calls[str(call_id)] = "checker-shell-reference"
                        evidence.append(f"shell referenced checker: {command[:180]}")

        tool_results = msg.get("tool_results") or {}
        if isinstance(tool_results, dict):
            for call_id, result in tool_results.items():
                mode = interesting_calls.get(str(call_id))
                if not mode:
                    continue
                text = json.dumps(result, ensure_ascii=False)
                if any(term in text for term in missing_terms):
                    modes.add("checker-location-failed")
                    evidence.append("checker path failed")
                if "argument --capture/--no-capture" in text or "usage: check_birch_renderings.py" in text:
                    modes.add("checker-cli-error")
                    evidence.append("checker CLI usage error")
                if "process exit code was 0" in text or "STATUS:0" in text:
                    if mode in {"run-checker-cli", "import-checker"}:
                        out["self_check_succeeded"] = True

    out["self_check_mode"] = ",".join(sorted(modes))
    compact = []
    for item in evidence:
        if item not in compact:
            compact.append(item)
        if len(compact) >= 6:
            break
    out["self_check_evidence"] = " | ".join(compact)
    return out


def run_fast_agent(
    prompt_path: Path,
    model: str | None,
    *,
    use_shell: bool,
    timeout_s: int | None = None,
    results_path: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = [
        "fast-agent",
        "--no-update-check",
        "--env",
        str(ROOT / ".fast-agent"),
        "go",
        "--config-path",
        str(ROOT / ".fast-agent" / "fast-agent.yaml"),
        "--skills-dir",
        str(ACTIVE_SKILLS_DIR),
        "--name",
        "birch-skill-eval-generator",
        "--instruction",
        str(base.PROMPT_DIR / "instruction.md"),
        "--prompt-file",
        str(prompt_path),
        "--quiet",
    ]
    cmd.append("--shell" if use_shell else "--no-shell")
    if results_path:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        cmd.extend(["--results", str(results_path)])
    if model:
        cmd.extend(["--model", model])
    try:
        return subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            cmd,
            124,
            exc.stdout or "",
            (exc.stderr or "") + f"\nfast-agent generation timed out after {timeout_s}s",
        )


def generate_one(name: str, model: str | None, timeout_s: int | None = None) -> base.GenerationResult:
    base.OUT_DIR.mkdir(parents=True, exist_ok=True)
    base.PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    (base.PROMPT_DIR / "instruction.md").write_text(INSTRUCTION, encoding="utf-8")
    prompt = build_prompt(name)
    prompt_path = base.PROMPT_DIR / f"{name}.prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    artifact = base.OUT_DIR / f"{name}.html"
    results_path = base.REPORT_DIR / "fast-agent-results" / f"{name}.json"

    start = time.monotonic()
    proc = run_fast_agent(
        prompt_path,
        model,
        use_shell=USE_SHELL_TOOLS or name in SHELL_EVALS,
        timeout_s=timeout_s,
        results_path=results_path,
    )
    duration = time.monotonic() - start
    result = base.GenerationResult(
        eval=name,
        ok=False,
        artifact=base.rel(artifact),
        prompt=base.rel(prompt_path),
        stdout=proc.stdout[-4000:],
        stderr=proc.stderr[-4000:],
        duration_s=round(duration, 3),
        input_chars=len(prompt),
        output_chars=len(proc.stdout),
        results=base.rel(results_path),
    )
    for key, value in base.usage_from_results(results_path).items():
        setattr(result, key, value)
    for key, value in classify_self_check(results_path).items():
        setattr(result, key, value)
    if proc.returncode:
        result.error = f"fast-agent exited {proc.returncode}"
        return result
    try:
        if OUTPUT_MODE == "file":
            html = validate_finished_file(artifact)
        else:
            html = base.normalize_html(base.extract_html(proc.stdout))
    except Exception as exc:  # noqa: BLE001 - turn into eval metadata
        result.error = str(exc)
        return result
    if OUTPUT_MODE != "file":
        artifact.write_text(html, encoding="utf-8")
    result.ok = True
    return result


def write_summary(generation: list[base.GenerationResult], checks: list[dict[str, object]]) -> None:
    base.write_summary(generation, checks, extra={"execution": RUN_METADATA})


def write_experiment_doc(label: str, purpose: str) -> None:
    meta = {"label": label, "purpose": purpose, **RUN_METADATA}
    base.REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (base.REPORT_DIR / "experiment.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    lines = [
        f"# {label}",
        "",
        f"Purpose: {purpose}",
        "",
        "## Pipeline",
        "",
        "- Mode: skill benchmark/eval artifact generation",
        f"- Output mode: `{RUN_METADATA.get('output_mode')}`",
        f"- Skills dir: `{RUN_METADATA.get('skills_dir')}`",
        f"- Model: `{RUN_METADATA.get('model')}`",
        f"- Working directory: `{RUN_METADATA.get('cwd')}`",
        f"- Artifact generation jobs: `{RUN_METADATA.get('jobs')}`",
        f"- Generation timeout: `{RUN_METADATA.get('generation_timeout_s')}s`",
        f"- Shell access: default `{RUN_METADATA.get('default_shell_access')}`, per-eval `{', '.join(RUN_METADATA.get('shell_evals') or []) or 'none'}`",
        "",
    ]
    (base.REPORT_DIR / "experiment.md").write_text("\n".join(lines), encoding="utf-8")


def resolve_skills_dir(skill_dir: Path | None, skills_dir: Path | None) -> Path:
    if skills_dir:
        return skills_dir.resolve()
    path = (skill_dir or ROOT / "skill").resolve()
    if (path / "SKILL.md").exists():
        return path.parent
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Optional fast-agent model override.")
    parser.add_argument("--label", default="skill-birch", help="Output label under eval-runs/ and eval-runs/reports/.")
    parser.add_argument("--skill-dir", type=Path, default=ROOT / "skill", help="Path to birch-html skill directory.")
    parser.add_argument("--skills-dir", type=Path, help="Explicit parent skills directory to pass to fast-agent.")
    parser.add_argument("--out-dir", type=Path, help="Explicit artifact output directory.")
    parser.add_argument("--report-dir", type=Path, help="Explicit report output directory.")
    parser.add_argument("--prompt-dir", type=Path, help="Explicit prompt output directory.")
    parser.add_argument("--skip-generate", action="store_true", help="Only run deterministic checks on existing artifacts.")
    parser.add_argument("--skip-check", action="store_true", help="Only generate artifacts.")
    parser.add_argument("--eval", choices=sorted(base.EVALS), action="append", help="Generate only selected eval(s). Checks still expect all artifacts unless --skip-check.")
    parser.add_argument("--jobs", type=int, default=1, help="Parallel artifact generation jobs.")
    parser.add_argument("--generation-timeout", type=int, default=900, help="Seconds allowed for one artifact generation.")
    parser.add_argument(
        "--output-mode",
        choices=["file", "stdout-html"],
        default="file",
        help="`file` asks the skill/model to write and finish the artifact; `stdout-html` keeps the legacy harness-saves-stdout behavior.",
    )
    parser.add_argument(
        "--source-preview",
        choices=["auto", "always", "never"],
        default="auto",
        help="Include source contents in prompts. `auto` includes previews only when shell/tools are disabled for that eval.",
    )
    shell_group = parser.add_mutually_exclusive_group()
    shell_group.add_argument("--shell-tools", action="store_true", help="Expose shell/tools during artifact generation. This is the default.")
    shell_group.add_argument("--no-shell-tools", action="store_true", help="Disable shell/tools during artifact generation.")
    parser.add_argument(
        "--shell-eval",
        choices=sorted(base.EVALS),
        action="append",
        default=[],
        help="Expose shell/tools only for the selected eval. Repeatable.",
    )
    parser.add_argument(
        "--purpose",
        default="Benchmark an Birch HTML skill by generating and checking the five eval artifacts.",
        help="Human-readable purpose written to experiment.md in the report directory.",
    )
    args = parser.parse_args()

    global ACTIVE_SKILLS_DIR, USE_SHELL_TOOLS, SHELL_EVALS, RUN_METADATA, OUTPUT_MODE, SOURCE_PREVIEW
    ACTIVE_SKILLS_DIR = resolve_skills_dir(args.skill_dir, args.skills_dir)
    USE_SHELL_TOOLS = not args.no_shell_tools
    SHELL_EVALS = set(args.shell_eval or [])
    OUTPUT_MODE = args.output_mode
    SOURCE_PREVIEW = args.source_preview
    if OUTPUT_MODE == "file" and not USE_SHELL_TOOLS:
        parser.error("--output-mode file requires shell/tools; use --output-mode stdout-html with --no-shell-tools")
    RUN_METADATA = {
        "mode": "skill-eval",
        "output_mode": OUTPUT_MODE,
        "cwd": str(ROOT),
        "skills_dir": str(ACTIVE_SKILLS_DIR),
        "model": args.model,
        "jobs": max(1, args.jobs),
        "generation_timeout_s": args.generation_timeout,
        "default_shell_access": USE_SHELL_TOOLS,
        "shell_evals": sorted(SHELL_EVALS),
        "source_preview": SOURCE_PREVIEW,
    }

    base.configure_paths(
        args.label,
        out_dir=args.out_dir,
        report_dir=args.report_dir,
        prompt_dir=args.prompt_dir,
    )
    write_experiment_doc(args.label, args.purpose)

    names = args.eval or list(base.EVALS)
    generation: list[base.GenerationResult] = []
    if not args.skip_generate:
        jobs = max(1, min(args.jobs, len(names)))
        if jobs == 1:
            for name in names:
                print(f"generating {name} with skills from {ACTIVE_SKILLS_DIR}...", flush=True)
                result = generate_one(name, args.model, args.generation_timeout)
                generation.append(result)
                print(f"  {'ok' if result.ok else 'failed'} in {result.duration_s:.1f}s", flush=True)
                if not result.ok:
                    print(result.error, file=sys.stderr)
                    print(result.stderr, file=sys.stderr)
                    write_summary(generation, [])
                    raise SystemExit(1)
        else:
            print(f"generating {len(names)} evals with {jobs} jobs using skills from {ACTIVE_SKILLS_DIR}...", flush=True)
            by_name: dict[str, base.GenerationResult] = {}
            with ThreadPoolExecutor(max_workers=jobs) as pool:
                futures = {pool.submit(generate_one, name, args.model, args.generation_timeout): name for name in names}
                for future in as_completed(futures):
                    name = futures[future]
                    result = future.result()
                    by_name[name] = result
                    print(f"  {name}: {'ok' if result.ok else 'failed'} in {result.duration_s:.1f}s", flush=True)
            generation = [by_name[name] for name in names if name in by_name]
            failed = [item for item in generation if not item.ok]
            if failed:
                for item in failed:
                    print(item.error, file=sys.stderr)
                    print(item.stderr, file=sys.stderr)
                write_summary(generation, [])
                raise SystemExit(1)
    else:
        generation = [
            base.GenerationResult(name, True, base.rel(base.OUT_DIR / f"{name}.html"), "", "", "", 0, 0, 0)
            for name in base.EVALS
        ]

    checks: list[dict[str, object]] = []
    if not args.skip_check:
        for viewport_name, viewport in [
            ("desktop", "desktop:1365x900"),
            ("mobile", "mobile:390x900"),
            ("deep", "deep:1365x6000"),
            ("mobile-deep", "mobile-deep:390x6000"),
        ]:
            print(f"checking {viewport}...", flush=True)
            check = base.run_checker(viewport_name, viewport)
            checks.append(check)
            print(f"  returncode {check['returncode']} in {check['duration_s']:.1f}s", flush=True)
    write_summary(generation, checks)

    if any(not item.ok for item in generation) or any(check["returncode"] for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

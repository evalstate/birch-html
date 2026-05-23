#!/usr/bin/env python3
"""Shared configuration and reporting helpers for Birch skill evals."""

from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_LABEL = "birch-after"
RUN_SLUG = "birch-after"
CANDIDATE_ROOT: Path | None = None
OUT_DIR = ROOT / "eval-runs" / RUN_LABEL
REPORT_DIR = ROOT / "eval-runs" / "reports" / RUN_LABEL
PROMPT_DIR = ROOT / "eval-runs" / "prompts" / RUN_LABEL
SYSTEM_CSS = ROOT / "styles" / "birch-system.css"
BIRCH_CSS_MARKER = "__BIRCH_SYSTEM_CSS__"
BIRCH_STYLE_RE = re.compile(r"<style\b(?=[^>]*\bdata-birch-system\b)[^>]*>.*?</style>", re.I | re.S)
BIRCH_LINK_RE = re.compile(
    r"\s*<link\b(?=[^>]*\brel=[\"']stylesheet[\"'])(?=[^>]*\bhref=[\"'](?:\.\./\.\./)?styles/birch-system\.css[\"'])[^>]*>\s*",
    re.I,
)

EVALS = {
    "numeric-data": {
        "recipe": "docs/birch-recipes/numeric-data.md",
        "prompt": "evals/numeric-data/prompt.md",
        "sources": ["evals/numeric-data/source.csv"],
    },
    "code-review": {
        "recipe": "docs/birch-recipes/code-review.md",
        "prompt": "evals/code-review/prompt.md",
        "sources": ["evals/code-review/source.diff"],
    },
    "module-explainer": {
        "recipe": "docs/birch-recipes/module-explainer.md",
        "prompt": "evals/module-explainer/prompt.md",
        "source_list": "evals/module-explainer/source-files.txt",
    },
    "implementation-plan": {
        "recipe": "docs/birch-recipes/implementation-plan.md",
        "prompt": "evals/implementation-plan/prompt.md",
        "sources": ["evals/implementation-plan/migration-plan.md"],
    },
    "benchmark-comparison": {
        "recipe": "docs/birch-recipes/benchmark-comparison.md",
        "prompt": "evals/benchmark-comparison/prompt.md",
        "sources": ["evals/benchmark-comparison/source.json"],
    },
}

DENYLIST = set(
    "card-grid chip-row tldr tldr-label recommendation-callout risk-tag file-card "
    "file-head file-path file-delta code-panel matrix rank-list rank-row rank-track "
    "rank-fill rank-score diagram-panel arch-svg flow-svg diagram-legend swatch "
    "incident-timeline pill milestones milestone slide-deck slide slide-inner slide-counter".split()
)


@dataclass
class GenerationResult:
    eval: str
    ok: bool
    artifact: str
    prompt: str
    stdout: str
    stderr: str
    duration_s: float
    input_chars: int
    output_chars: int
    error: str = ""
    results: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    billing_tokens: int = 0
    reasoning_tokens: int = 0
    tool_use_tokens: int = 0
    tool_calls: int = 0
    turn_count: int = 0
    self_check_attempted: bool = False
    self_check_ran: bool = False
    self_check_succeeded: bool = False
    self_check_mode: str = ""
    self_check_evidence: str = ""


def rel(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def slug(value: str) -> str:
    name = Path(value).name or value
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", name).strip("-") or "run"


def configure_paths(
    label: str,
    *,
    out_dir: Path | None = None,
    report_dir: Path | None = None,
    prompt_dir: Path | None = None,
    candidate_root: Path | None = None,
) -> None:
    global RUN_LABEL, RUN_SLUG, OUT_DIR, REPORT_DIR, PROMPT_DIR, CANDIDATE_ROOT
    RUN_LABEL = label
    RUN_SLUG = slug(label)
    OUT_DIR = (out_dir or ROOT / "eval-runs" / label).resolve()
    REPORT_DIR = (report_dir or ROOT / "eval-runs" / "reports" / label).resolve()
    PROMPT_DIR = (prompt_dir or ROOT / "eval-runs" / "prompts" / label).resolve()
    CANDIDATE_ROOT = candidate_root.resolve() if candidate_root else None


def usage_from_results(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    summary: dict[str, object] = {}
    turns: list[dict[str, object]] = []
    for message in doc.get("messages", []):
        for block in (message.get("channels") or {}).get("fast-agent-usage", []):
            try:
                usage = json.loads(block.get("text") or "{}")
            except json.JSONDecodeError:
                continue
            if isinstance(usage.get("turn"), dict):
                turns.append(usage["turn"])
            if isinstance(usage.get("summary"), dict):
                summary = usage["summary"]
    if summary:
        return {
            "input_tokens": int(summary.get("cumulative_input_tokens") or 0),
            "output_tokens": int(summary.get("cumulative_output_tokens") or 0),
            "total_tokens": int(summary.get("cumulative_billing_tokens") or 0),
            "billing_tokens": int(summary.get("cumulative_billing_tokens") or 0),
            "reasoning_tokens": int(summary.get("cumulative_reasoning_tokens") or 0),
            "tool_use_tokens": int(summary.get("cumulative_tool_use_tokens") or 0),
            "tool_calls": int(summary.get("cumulative_tool_calls") or 0),
            "turn_count": int(summary.get("turn_count") or len(turns)),
        }
    return {
        "input_tokens": sum(int(turn.get("input_tokens") or 0) for turn in turns),
        "output_tokens": sum(int(turn.get("output_tokens") or 0) for turn in turns),
        "total_tokens": sum(int(turn.get("total_tokens") or 0) for turn in turns),
        "billing_tokens": sum(int(turn.get("total_tokens") or 0) for turn in turns),
        "reasoning_tokens": sum(int(turn.get("reasoning_tokens") or 0) for turn in turns),
        "tool_use_tokens": sum(int(turn.get("tool_use_tokens") or 0) for turn in turns),
        "tool_calls": sum(int(turn.get("tool_calls") or 0) for turn in turns),
        "turn_count": len(turns),
    }


def read(relpath: str) -> str:
    if CANDIDATE_ROOT:
        candidate_path = CANDIDATE_ROOT / relpath
        if candidate_path.exists():
            return candidate_path.read_text(encoding="utf-8")
    return (ROOT / relpath).read_text(encoding="utf-8")


def fenced(path: str, content: str) -> str:
    suffix = Path(path).suffix.lstrip(".") or "text"
    lang = {"md": "markdown", "py": "python", "css": "css", "csv": "csv", "diff": "diff", "txt": "text"}.get(suffix, suffix)
    return f"### `{path}`\n\n```{lang}\n{content}\n```\n"


def source_paths(spec: dict[str, object]) -> list[str]:
    paths = list(spec.get("sources", []))
    if source_list := spec.get("source_list"):
        base = read(str(source_list)).splitlines()
        paths.extend(line.strip() for line in base if line.strip() and not line.strip().startswith("#"))
        paths.insert(0, str(source_list))
    return paths


def extract_html(text: str) -> str:
    match = re.search(r"```(?:html)?\s*(.*?)```", text, re.I | re.S)
    if match and ("<html" in match.group(1).lower() or "<!doctype" in match.group(1).lower()):
        text = match.group(1)
    start_candidates = [i for i in [text.lower().find("<!doctype"), text.lower().find("<html")] if i >= 0]
    if start_candidates:
        text = text[min(start_candidates) :]
    end = text.lower().rfind("</html>")
    if end >= 0:
        text = text[: end + len("</html>")]
    return text.strip()


def add_wrap_attrs(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if re.search(r"\sdata-wrap=", tag):
            return tag
        return tag[:-1] + ' data-wrap="true">'

    return re.sub(
        r"<(?:(?:pre|div)\b(?=[^>]*class=[\"'][^\"']*\b(?:code-block|diff)\b)[^>]*)>",
        repl,
        html,
        flags=re.I,
    )


def normalize_html(html: str) -> str:
    if not html.lower().startswith(("<!doctype", "<html")):
        raise ValueError("model output did not contain a complete HTML document")
    html = add_wrap_attrs(html)
    html = inject_birch_css(html)
    return html + "\n"


def inject_birch_css(html: str) -> str:
    css = SYSTEM_CSS.read_text(encoding="utf-8").strip()
    html = BIRCH_LINK_RE.sub("\n", html)
    if BIRCH_CSS_MARKER in html:
        return html.replace(BIRCH_CSS_MARKER, css)
    if BIRCH_STYLE_RE.search(html):
        return BIRCH_STYLE_RE.sub(f"<style data-birch-system>\n{css}\n</style>", html, count=1)
    return re.sub(
        r"</head>",
        f"<style data-birch-system>\n{css}\n</style>\n</head>",
        html,
        count=1,
        flags=re.I,
    )


def checker_artifacts() -> list[str]:
    return [rel(OUT_DIR / f"{name}.html") for name in EVALS]


def run_checker(viewport_name: str, viewport: str) -> dict[str, object]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        "uv",
        "run",
        "--with",
        "pillow",
        "python",
        "scripts/check_birch_renderings.py",
        "--out",
        str(REPORT_DIR / f"{RUN_SLUG}-{viewport_name}.json"),
        "--markdown",
        str(REPORT_DIR / f"{RUN_SLUG}-{viewport_name}.md"),
        "--viewport",
        viewport,
        "--screenshots-dir",
        str(REPORT_DIR / "screenshots"),
    ]
    for artifact in checker_artifacts():
        cmd.extend(["--artifact", artifact])
    start = time.monotonic()
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    duration = time.monotonic() - start
    return {
        "viewport": viewport,
        "returncode": proc.returncode,
        "duration_s": round(duration, 3),
        "stdout": proc.stdout[-2000:],
        "stderr": proc.stderr[-4000:],
        "json": str(REPORT_DIR / f"{RUN_SLUG}-{viewport_name}.json"),
        "markdown": str(REPORT_DIR / f"{RUN_SLUG}-{viewport_name}.md"),
    }


def static_recipe_summary() -> dict[str, object]:
    out: dict[str, object] = {}
    for name in EVALS:
        path = OUT_DIR / f"{name}.html"
        html = path.read_text(encoding="utf-8") if path.exists() else ""
        classes = set(re.findall(r'class=["\']([^"\']+)["\']', html))
        flat_classes = {c for group in classes for c in group.split()}
        denied = sorted(flat_classes & DENYLIST)
        out[name] = {
            "bytes": len(html.encode()),
            "denied_classes": denied,
            "has_relative_css": '../../styles/birch-system.css' in html,
            "has_checker_css": 'styles/birch-system.css' in html,
            "has_embedded_birch_css": 'data-birch-system' in html,
            "code_wrap_blocks": len(re.findall(r'class=["\'][^"\']*\b(?:code-block|diff)\b[^"\']*["\'][^>]*data-wrap=["\']true["\']', html)),
            "numeric_tables": html.count('class="numeric-table') + html.count("class='numeric-table"),
            "flow_steps": html.count('class="flow-step') + html.count("class='flow-step"),
            "cards": len(re.findall(r'class=["\'][^"\']*\bcard\b', html)),
            "bad_external_assets": len(re.findall(r'<(?:script|link|img)\b[^>]*(?:https?:)?//', html, re.I)),
        }
    return out


def write_summary(
    generation: list[GenerationResult],
    checks: list[dict[str, object]],
    *,
    extra: dict[str, object] | None = None,
) -> None:
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generation": [asdict(item) for item in generation],
        "checks": checks,
        "static_recipe_summary": static_recipe_summary(),
    }
    if extra:
        payload.update(extra)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / f"{RUN_SLUG}-run.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [f"# {RUN_LABEL} migration eval run", ""]
    lines.append("## Generation")
    lines.append("")
    lines.append("| Eval | Result | Artifact | Duration | Prompt chars | Output chars | Input tok | Output tok | Total tok | Reasoning tok | Tool calls | Turns | Self-check | Results |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for item in generation:
        status = "pass" if item.ok else f"fail: {item.error}"
        results = f"`{item.results}`" if item.results else ""
        lines.append(
            f"| {item.eval} | {status} | `{item.artifact}` | {item.duration_s:.3f}s | {item.input_chars} | "
            f"{item.output_chars} | {item.input_tokens} | {item.output_tokens} | {item.total_tokens} | "
            f"{item.reasoning_tokens} | {item.tool_calls} | {item.turn_count} | "
            f"{('ran' if item.self_check_ran else 'attempted' if item.self_check_attempted else 'no')} | {results} |"
        )
    lines.append("")
    lines.append("## Artifact checker")
    lines.append("")
    lines.append("| Viewport | Result | Runtime | Report |")
    lines.append("|---|---|---:|---|")
    for check in checks:
        status = "pass" if check["returncode"] == 0 else f"fail ({check['returncode']})"
        lines.append(f"| {check['viewport']} | {status} | {check['duration_s']:.3f}s | [`md`]({Path(str(check['markdown'])).name}) / [`json`]({Path(str(check['json'])).name}) |")
    lines.append("")
    lines.append("## Static recipe summary")
    lines.append("")
    lines.append("| Eval | Bytes | Denied classes | CSS links | External assets | Cards | Numeric tables | Flow steps | Wrapped code/diff |")
    lines.append("|---|---:|---|---|---:|---:|---:|---:|")
    for name, stats in payload["static_recipe_summary"].items():
        css = "ok" if stats["has_embedded_birch_css"] or (stats["has_relative_css"] and stats["has_checker_css"]) else "missing"
        denied = ", ".join(stats["denied_classes"]) or "none"
        lines.append(
            f"| {name} | {stats['bytes']} | {denied} | {css} | {stats['bad_external_assets']} | "
            f"{stats['cards']} | {stats['numeric_tables']} | {stats['flow_steps']} | {stats['code_wrap_blocks']} |"
        )
    lines.append("")
    (REPORT_DIR / f"{RUN_SLUG}-run.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

#!/usr/bin/env python3
"""Build first-pass publication analysis data and README-ready SVG figures.

This script intentionally keeps the scoring transparent. It reads the packaged
Birch HTML benchmark records, consolidates model/artifact metrics, and writes:

  analysis/data/model-summary.json
  analysis/data/artifact-summary.json
  analysis/tables/model-summary.csv
  analysis/tables/artifact-summary.csv
  analysis/figures/quality-matrix.svg
  analysis/figures/quality-vs-efficiency.svg
  analysis/figures/efficiency-comparison.svg

The visual design is deliberately Tufte-ish: compact, direct labels, muted grids,
no decoration, and exact quantities in the data tables.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from statistics import median

EVALS = [
    "numeric-data",
    "code-review",
    "module-explainer",
    "implementation-plan",
    "benchmark-comparison",
]
VIEWPORTS = ["desktop", "mobile", "deep", "mobile-deep"]


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def rel(path: Path) -> str:
    """Return a browser/publication-friendly path relative to the repo root.

    Earlier drafts wrote absolute filesystem paths when build() used an absolute
    root. Those break static HTML image links. Keep all consolidated paths
    repository-relative.
    """
    p = Path(path)
    if p.is_absolute():
        for base in [Path.cwd(), Path(__file__).resolve().parents[1]]:
            try:
                return p.relative_to(base).as_posix()
            except Exception:
                pass
    return p.as_posix()


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def safe_sum(rows, key):
    return sum((r.get(key) or 0) for r in rows)


def pct_rank_lower_is_better(values):
    """Return mapping value -> 0..100 where low values score higher.

    Uses min/max normalization rather than rank so distances remain meaningful.
    If all values are equal, everyone receives 100.
    """
    vals = [v for v in values if v is not None and math.isfinite(v)]
    if not vals:
        return {}
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return {v: 100.0 for v in vals}
    return {v: 100.0 * (hi - v) / (hi - lo) for v in vals}


def eval_from_artifact_path(s: str) -> str | None:
    name = Path(s).name
    if name.endswith(".html"):
        name = name[:-5]
    return name if name in EVALS else None


def parse_vision_artifact_name(name: str) -> tuple[str | None, str | None]:
    """Parse e.g. numeric-data-mobile-deep__tile-02.png -> (numeric-data, mobile-deep)."""
    stem = Path(name).stem
    stem = stem.split("__tile-")[0]
    for ev in EVALS:
        prefix = ev + "-"
        if stem.startswith(prefix):
            vp = stem[len(prefix):]
            if vp in VIEWPORTS:
                return ev, vp
    return None, None


def load_generation_by_eval(run_json: Path):
    data = read_json(run_json, {}) or {}
    out = {}
    for g in data.get("generation", []) or []:
        ev = g.get("eval")
        if ev:
            out[ev] = g
    return out


def load_deterministic_counts(reports_dir: Path, label: str):
    """Return nested counts and detailed deterministic finding rows."""
    counts = defaultdict(lambda: defaultdict(lambda: {"failures": 0, "warnings": 0}))
    findings = []
    bytes_by_eval = {}

    for vp in VIEWPORTS:
        p = reports_dir / f"{label}-{vp}.json"
        if not p.exists():
            p = reports_dir / f"{label}-visionfill-{vp}.json"
        data = read_json(p, {}) or {}
        artifacts = data.get("artifacts", []) or []
        if p.exists() and len(artifacts) != len(EVALS):
            raise SystemExit(f"{p}: expected {len(EVALS)} artifacts, found {len(artifacts)}")
        for art in artifacts:
            ev = eval_from_artifact_path(art.get("artifact", ""))
            if not ev:
                continue
            stats = art.get("stats") or {}
            if isinstance(stats.get("bytes"), int):
                bytes_by_eval.setdefault(ev, stats["bytes"])
            for f in art.get("findings", []) or []:
                level = f.get("level")
                if level == "fail":
                    counts[ev][vp]["failures"] += 1
                elif level == "warn":
                    counts[ev][vp]["warnings"] += 1
                if level in {"fail", "warn"}:
                    findings.append({
                        "eval": ev,
                        "source": "deterministic",
                        "viewport": vp,
                        "level": level,
                        "name": f.get("name", ""),
                        "evidence": f.get("evidence", ""),
                        "report_path": rel(p),
                    })
    return counts, findings, bytes_by_eval


def load_vision_counts(reports_dir: Path):
    counts = defaultdict(lambda: {"failures": 0, "warnings": 0})
    findings = []
    p = reports_dir / "vision-findings.json"
    data = read_json(p, {}) or {}
    for art in data.get("artifacts", []) or []:
        ev, vp = parse_vision_artifact_name(art.get("artifact", ""))
        if not ev:
            continue
        for f in art.get("findings", []) or []:
            level = f.get("level")
            if level == "fail":
                counts[ev]["failures"] += 1
            elif level == "warn":
                counts[ev]["warnings"] += 1
            if level in {"fail", "warn"}:
                row = {
                    "eval": ev,
                    "source": "vlm",
                    "viewport": vp or "",
                    "level": level,
                    "name": f.get("name", ""),
                    "evidence": f.get("evidence", ""),
                    "screenshot_name": art.get("artifact", ""),
                    "report_path": rel(p),
                }
                if isinstance(f.get("bbox_px"), dict):
                    row["bbox_px"] = f["bbox_px"]
                findings.append(row)
    return counts, findings


def trace_count(reports_dir: Path, subdir: str) -> int:
    d = reports_dir / subdir
    return len(list(d.glob("*.json"))) if d.exists() else 0


def load_trace_usage(trace_path: Path) -> dict:
    """Extract per-prompt token/cache totals from a fast-agent trace.

    The run JSON already contains aggregate input/output/total token fields. Some
    cache details are only present inside messages[*].channels["fast-agent-usage"]
    as JSON text. We sum those usage events here. If a trace does not expose
    cache usage, these fields remain zero and token fields from the run JSON are
    still authoritative for the high-level report.
    """
    data = read_json(trace_path, {}) or {}
    usage_events = []
    for msg in data.get("messages", []) or []:
        channels = msg.get("channels") or {}
        for item in channels.get("fast-agent-usage", []) or []:
            text = item.get("text") if isinstance(item, dict) else None
            if not text:
                continue
            try:
                usage_events.append(json.loads(text))
            except Exception:
                continue

    out = {
        "usage_event_count": len(usage_events),
        "trace_input_tokens": 0,
        "trace_output_tokens": 0,
        "trace_total_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "cache_hit_tokens": 0,
        "total_cache_tokens": 0,
        "effective_input_tokens": 0,
        "display_input_tokens": 0,
        "current_context_tokens_last": 0,
    }
    for event in usage_events:
        turn = event.get("turn") or {}
        out["trace_input_tokens"] += int(turn.get("input_tokens") or 0)
        out["trace_output_tokens"] += int(turn.get("output_tokens") or 0)
        out["trace_total_tokens"] += int(turn.get("total_tokens") or 0)
        out["effective_input_tokens"] += int(turn.get("effective_input_tokens") or 0)
        out["display_input_tokens"] += int(turn.get("display_input_tokens") or 0)
        out["current_context_tokens_last"] = int(turn.get("current_context_tokens") or out["current_context_tokens_last"] or 0)
        cache = turn.get("cache_usage") or {}
        out["cache_read_tokens"] += int(cache.get("cache_read_tokens") or 0)
        out["cache_write_tokens"] += int(cache.get("cache_write_tokens") or 0)
        out["cache_hit_tokens"] += int(cache.get("cache_hit_tokens") or 0)
        out["total_cache_tokens"] += int(cache.get("total_cache_tokens") or 0)
    return out


def _tool_text(result: object) -> str:
    try:
        return json.dumps(result, ensure_ascii=False)
    except Exception:
        return str(result)


def _is_checker_run(command: str) -> bool:
    """Conservatively detect model-invoked checker executions.

    The older run JSON has self-check fields too, but those can overcount when a
    model writes prose/code mentioning the checker path. Here we require either
    a direct Python/uv invocation of check_birch_renderings.py, an import, or a
    subprocess-like Python heredoc that contains the checker path. Plain
    artifact writes that merely include the string are excluded.
    """
    stripped = command.strip()
    if not stripped:
        return False
    if "import check_birch_renderings" in stripped:
        return True
    if "check_birch_renderings.py" not in stripped:
        return False
    if re.match(r"^(cat|tee)\b", stripped):
        return False
    return bool(re.search(r"(^|[;&|]\s*)(uv\s+run\b[^;&|]*\s+)?python3?\b[^;&|]*check_birch_renderings\.py\b", stripped, re.S))


def _is_artifact_edit(command: str, eval_name: str) -> bool:
    artifact = f"{eval_name}.html"
    if artifact not in command:
        return False
    stripped = command.strip()
    if re.search(rf"\b(cat|tee)\s*>\s*[^;&|]*{re.escape(artifact)}\b", stripped):
        return True
    if re.search(rf"\b(cat|tee)\s+[^;&|]*\s*>\s*[^;&|]*{re.escape(artifact)}\b", stripped):
        return True
    edit_markers = ("write_text(", ".write_text", "sed -i", "perl -0pi", "Path(")
    return any(marker in stripped for marker in edit_markers) and any(
        marker in stripped for marker in ("write_text", "replace(", "sed -i", "perl -0pi")
    )


def _checker_failed(text: str) -> bool:
    if "process exit code was 1" in text or "process exit code was 2" in text:
        return True
    if re.search(r'"failures"\s*:\s*[1-9]\d*', text):
        return True
    if '"level": "fail"' in text or "'level': 'fail'" in text:
        return True
    return False


def _checker_succeeded(text: str) -> bool:
    if "process exit code was 0" in text:
        return True
    return bool(re.search(r'"failures"\s*:\s*0\b', text))


def load_trace_behavior(trace_path: Path, eval_name: str) -> dict:
    """Extract self-check and self-correction behavior from a fast-agent trace."""
    out = {
        "self_check_attempted": False,
        "self_check_ran": False,
        "self_check_succeeded": False,
        "self_check_runs": 0,
        "self_check_failed_runs": 0,
        "self_check_successful_runs": 0,
        "self_correction_edits": 0,
        "self_corrected_after_checker": False,
        "self_correction_verified": False,
        "assistant_turns": 0,
    }
    data = read_json(trace_path, {}) or {}
    pending: dict[str, dict] = {}
    saw_failed_checker = False
    saw_edit_after_failed_checker = False

    for msg in data.get("messages", []) or []:
        if msg.get("role") == "assistant":
            out["assistant_turns"] += 1
        tool_calls = msg.get("tool_calls") or {}
        if isinstance(tool_calls, dict):
            for call_id, call in tool_calls.items():
                params = call.get("params", {}) if isinstance(call, dict) else {}
                name = params.get("name")
                args = params.get("arguments", {}) if isinstance(params, dict) else {}
                if name != "execute":
                    if name == "read_text_file" and "check_birch_renderings.py" in str(args.get("path", "")):
                        out["self_check_attempted"] = True
                    continue
                command = str(args.get("command", ""))
                if "check_birch_renderings.py" in command or "import check_birch_renderings" in command:
                    out["self_check_attempted"] = True
                is_checker = _is_checker_run(command)
                is_edit = _is_artifact_edit(command, eval_name)
                if is_checker:
                    out["self_check_ran"] = True
                    out["self_check_runs"] += 1
                    pending[str(call_id)] = {"kind": "checker"}
                elif is_edit:
                    pending[str(call_id)] = {"kind": "edit"}
                    if saw_failed_checker:
                        saw_edit_after_failed_checker = True
                        out["self_corrected_after_checker"] = True
                        out["self_correction_edits"] += 1

        tool_results = msg.get("tool_results") or {}
        if isinstance(tool_results, dict):
            for call_id, result in tool_results.items():
                event = pending.pop(str(call_id), None)
                if not event or event.get("kind") != "checker":
                    continue
                text = _tool_text(result)
                failed = _checker_failed(text)
                succeeded = _checker_succeeded(text)
                if failed:
                    saw_failed_checker = True
                    out["self_check_failed_runs"] += 1
                if succeeded:
                    out["self_check_succeeded"] = True
                    out["self_check_successful_runs"] += 1
                    if saw_failed_checker:
                        out["self_correction_verified"] = True

    return out


def quality_score(det_fail_units, vlm_fail_units, det_warn_units, vlm_warn_units, missing_artifacts):
    """Transparent descriptive quality score, 0..100.

    Penalties are intentionally simple and documented in output metadata:
      - missing artifact: 20
      - unique deterministic failure unit: 6
      - unique VLM failure unit: 8
      - unique deterministic warning unit: 1
      - unique VLM warning unit: 1

    Finding units collapse repeated viewport sightings by ``(eval, finding name)``.
    This avoids charging four times for a single static contract failure seen in
    desktop, mobile, deep, and mobile-deep checker passes.
    """
    return clamp(100 - 20*missing_artifacts - 6*det_fail_units - 8*vlm_fail_units - det_warn_units - vlm_warn_units)


def finding_units(findings, *, level: str, eval_name: str | None = None) -> int:
    """Count distinct scoring units by eval and finding name."""
    return len({
        (f.get("eval"), f.get("name", ""))
        for f in findings
        if f.get("level") == level and (eval_name is None or f.get("eval") == eval_name)
    })


def has_finding(findings, *, level: str, name: str, eval_name: str) -> bool:
    return any(
        f.get("level") == level and f.get("name") == name and f.get("eval") == eval_name
        for f in findings
    )


def artifact_quality_score(row: dict, det_findings: list[dict], vlm_findings: list[dict]) -> tuple[float, str]:
    """Score one artifact opportunity, applying caps for missing/non-Birch renders."""
    if not row["artifact_present"]:
        return 0.0, "missing_artifact"

    score = quality_score(
        row["deterministic_failure_units"], row["vlm_failure_units"],
        row["deterministic_warning_units"], row["vlm_warning_units"],
        0,
    )
    ev = row["eval"]
    missing_birch_css = has_finding(det_findings, level="fail", name="uses_birch_system_css", eval_name=ev)
    missing_page_shell = has_finding(det_findings, level="fail", name="has_page_shell", eval_name=ev)
    visibly_unstyled = has_finding(vlm_findings, level="fail", name="vision_unstyled_render", eval_name=ev)

    cap_reason = ""
    if missing_birch_css and visibly_unstyled:
        score = min(score, 20.0)
        cap_reason = "missing_birch_css_and_visibly_unstyled"
    elif missing_birch_css:
        score = min(score, 35.0)
        cap_reason = "missing_birch_css"
    elif missing_page_shell:
        score = min(score, 50.0)
        cap_reason = "missing_page_shell"
    return score, cap_reason


def task_score(artifact_score_100: float) -> float:
    """Convert a 0..100 artifact score into one 20-point task contribution."""
    return artifact_score_100 / 5.0


def build(root: Path, suite_names: list[str] | None = None):
    model_rows = []
    artifact_rows = []
    finding_rows = []

    if suite_names:
        suites = [(name, root / "results" / name) for name in suite_names]
    else:
        default = ["original-11", "supplemental"]
        if (root / "results" / "clean-final" / "manifest.json").exists():
            default = ["clean-final"]
        suites = [(name, root / "results" / name) for name in default]

    for suite, base in suites:
        if not (base / "manifest.json").exists():
            print(f"warning: skipping missing suite {suite}: {base}")
            continue
        manifest = read_json(base / "manifest.json", {}) or {}
        for rec in manifest.get("records", []) or []:
            model = rec["model"]
            slug = rec["model_slug"]
            label = rec["label"]
            source_kind = rec.get("source_kind", "")
            mdir = base / "models" / slug
            reports = mdir / "reports"
            run_json = reports / f"{label}-run.json"
            gen_by_eval = load_generation_by_eval(run_json)
            det_counts, det_findings, bytes_by_eval = load_deterministic_counts(reports, label)
            vlm_counts, vlm_findings = load_vision_counts(reports)

            for f in det_findings + vlm_findings:
                f.update({"suite": suite, "model": model, "model_slug": slug, "source_kind": source_kind})
                finding_rows.append(f)

            for ev in EVALS:
                g = gen_by_eval.get(ev, {})
                trace_path = reports / "fast-agent-results" / f"{ev}.json"
                trace_usage = load_trace_usage(trace_path)
                trace_behavior = load_trace_behavior(trace_path, ev)
                row = {
                    "suite": suite,
                    "model": model,
                    "model_slug": slug,
                    "source_kind": source_kind,
                    "label": label,
                    "eval": ev,
                    "artifact_path": rel(mdir / "artifacts" / f"{ev}.html"),
                    "screenshot_desktop_path": rel(mdir / "reports" / "screenshots" / f"{ev}-desktop.png"),
                    "screenshot_mobile_path": rel(mdir / "reports" / "screenshots" / f"{ev}-mobile.png"),
                    "screenshot_deep_path": rel(mdir / "reports" / "screenshots" / f"{ev}-deep.png"),
                    "screenshot_mobile_deep_path": rel(mdir / "reports" / "screenshots" / f"{ev}-mobile-deep.png"),
                    "artifact_bytes": bytes_by_eval.get(ev) or ((mdir / "artifacts" / f"{ev}.html").stat().st_size if (mdir / "artifacts" / f"{ev}.html").exists() else 0),
                    "generation_ok": bool(g.get("ok")) if g else False,
                    "generation_duration_s": float(g.get("duration_s") or 0),
                    "input_tokens": int(g.get("input_tokens") or 0),
                    "output_tokens": int(g.get("output_tokens") or 0),
                    "total_tokens": int(g.get("total_tokens") or 0),
                    "billing_tokens": int(g.get("billing_tokens") or 0),
                    "reasoning_tokens": int(g.get("reasoning_tokens") or 0),
                    "tool_use_tokens": int(g.get("tool_use_tokens") or 0),
                    "cache_read_tokens": trace_usage["cache_read_tokens"],
                    "cache_write_tokens": trace_usage["cache_write_tokens"],
                    "cache_hit_tokens": trace_usage["cache_hit_tokens"],
                    "total_cache_tokens": trace_usage["total_cache_tokens"],
                    "effective_input_tokens": trace_usage["effective_input_tokens"],
                    "display_input_tokens": trace_usage["display_input_tokens"],
                    "usage_event_count": trace_usage["usage_event_count"],
                    "tool_calls": int(g.get("tool_calls") or 0),
                    "turn_count": int(g.get("turn_count") or 0),
                    "self_check_attempted": bool(trace_behavior["self_check_attempted"]),
                    "self_check_ran": bool(trace_behavior["self_check_ran"]),
                    "self_check_succeeded": bool(trace_behavior["self_check_succeeded"]),
                    "self_check_runs": int(trace_behavior["self_check_runs"]),
                    "self_check_failed_runs": int(trace_behavior["self_check_failed_runs"]),
                    "self_check_successful_runs": int(trace_behavior["self_check_successful_runs"]),
                    "self_correction_edits": int(trace_behavior["self_correction_edits"]),
                    "self_corrected_after_checker": bool(trace_behavior["self_corrected_after_checker"]),
                    "self_correction_verified": bool(trace_behavior["self_correction_verified"]),
                    "assistant_turns_trace": int(trace_behavior["assistant_turns"]),
                    "self_check_mode": g.get("self_check_mode", ""),
                    "self_check_evidence": g.get("self_check_evidence", ""),
                    "deterministic_failures": sum(det_counts[ev][vp]["failures"] for vp in VIEWPORTS),
                    "deterministic_warnings": sum(det_counts[ev][vp]["warnings"] for vp in VIEWPORTS),
                    "vlm_failures": vlm_counts[ev]["failures"],
                    "vlm_warnings": vlm_counts[ev]["warnings"],
                    "deterministic_failure_units": finding_units(det_findings, level="fail", eval_name=ev),
                    "deterministic_warning_units": finding_units(det_findings, level="warn", eval_name=ev),
                    "vlm_failure_units": finding_units(vlm_findings, level="fail", eval_name=ev),
                    "vlm_warning_units": finding_units(vlm_findings, level="warn", eval_name=ev),
                    "desktop_failures": det_counts[ev]["desktop"]["failures"],
                    "desktop_warnings": det_counts[ev]["desktop"]["warnings"],
                    "mobile_failures": det_counts[ev]["mobile"]["failures"],
                    "mobile_warnings": det_counts[ev]["mobile"]["warnings"],
                    "deep_failures": det_counts[ev]["deep"]["failures"],
                    "deep_warnings": det_counts[ev]["deep"]["warnings"],
                    "mobile_deep_failures": det_counts[ev]["mobile-deep"]["failures"],
                    "mobile_deep_warnings": det_counts[ev]["mobile-deep"]["warnings"],
                }
                row["artifact_present"] = row["artifact_bytes"] > 0
                artifact_score_100, cap_reason = artifact_quality_score(row, det_findings, vlm_findings)
                row["artifact_score_100"] = artifact_score_100
                row["task_score"] = round(task_score(artifact_score_100), 2)
                row["task_score_max"] = 20
                row["quality_score"] = artifact_score_100
                row["quality_cap_reason"] = cap_reason
                if row["deterministic_failures"] or row["vlm_failures"]:
                    row["quality_class"] = "fail"
                elif row["deterministic_warnings"] or row["vlm_warnings"]:
                    row["quality_class"] = "warn"
                elif row["artifact_present"]:
                    row["quality_class"] = "clean"
                else:
                    row["quality_class"] = "missing"
                artifact_rows.append(row)

            model_artifacts = [r for r in artifact_rows if r["model_slug"] == slug and r["suite"] == suite]
            missing = sum(1 for r in model_artifacts if not r["artifact_present"])
            model_row = {
                "suite": suite,
                "model": model,
                "model_slug": slug,
                "source_kind": source_kind,
                "label": label,
                "artifact_count": len([p for p in (mdir / "artifacts").glob("*.html")]) if (mdir / "artifacts").exists() else 0,
                "generation_ok": safe_sum(model_artifacts, "generation_ok"),
                "generation_total": len(EVALS),
                "artifact_present": safe_sum(model_artifacts, "artifact_present"),
                "generation_duration_s": round(safe_sum(model_artifacts, "generation_duration_s"), 3),
                "input_tokens": safe_sum(model_artifacts, "input_tokens"),
                "output_tokens": safe_sum(model_artifacts, "output_tokens"),
                "total_tokens": safe_sum(model_artifacts, "total_tokens"),
                "billing_tokens": safe_sum(model_artifacts, "billing_tokens"),
                "reasoning_tokens": safe_sum(model_artifacts, "reasoning_tokens"),
                "tool_use_tokens": safe_sum(model_artifacts, "tool_use_tokens"),
                "cache_read_tokens": safe_sum(model_artifacts, "cache_read_tokens"),
                "cache_write_tokens": safe_sum(model_artifacts, "cache_write_tokens"),
                "cache_hit_tokens": safe_sum(model_artifacts, "cache_hit_tokens"),
                "total_cache_tokens": safe_sum(model_artifacts, "total_cache_tokens"),
                "effective_input_tokens": safe_sum(model_artifacts, "effective_input_tokens"),
                "display_input_tokens": safe_sum(model_artifacts, "display_input_tokens"),
                "usage_event_count": safe_sum(model_artifacts, "usage_event_count"),
                "tool_calls": safe_sum(model_artifacts, "tool_calls"),
                "turn_count": safe_sum(model_artifacts, "turn_count"),
                "self_check_attempted": safe_sum(model_artifacts, "self_check_attempted"),
                "self_check_ran": safe_sum(model_artifacts, "self_check_ran"),
                "self_check_succeeded": safe_sum(model_artifacts, "self_check_succeeded"),
                "self_check_runs": safe_sum(model_artifacts, "self_check_runs"),
                "self_check_failed_runs": safe_sum(model_artifacts, "self_check_failed_runs"),
                "self_check_successful_runs": safe_sum(model_artifacts, "self_check_successful_runs"),
                "self_correction_edits": safe_sum(model_artifacts, "self_correction_edits"),
                "self_corrected_after_checker": safe_sum(model_artifacts, "self_corrected_after_checker"),
                "self_correction_verified": safe_sum(model_artifacts, "self_correction_verified"),
                "assistant_turns_trace": safe_sum(model_artifacts, "assistant_turns_trace"),
                "deterministic_failures": safe_sum(model_artifacts, "deterministic_failures"),
                "deterministic_warnings": safe_sum(model_artifacts, "deterministic_warnings"),
                "vlm_failures": safe_sum(model_artifacts, "vlm_failures"),
                "vlm_warnings": safe_sum(model_artifacts, "vlm_warnings"),
                "deterministic_failure_units": finding_units(det_findings, level="fail"),
                "deterministic_warning_units": finding_units(det_findings, level="warn"),
                "vlm_failure_units": finding_units(vlm_findings, level="fail"),
                "vlm_warning_units": finding_units(vlm_findings, level="warn"),
                "generation_trace_count": trace_count(reports, "fast-agent-results"),
                "vlm_trace_count": trace_count(reports, "fast-agent-vision-results"),
                "selected_record_path": rel(mdir),
            }
            model_row["quality_score"] = round(safe_sum(model_artifacts, "task_score"), 2)
            model_row["quality_score_basis"] = "sum_of_five_20_point_task_scores"
            model_row["missing_final_artifacts"] = missing
            model_rows.append(model_row)

    # Efficiency score: lower duration, tokens, and tool calls are better, each min/max-normalized.
    dur_scores = pct_rank_lower_is_better([r["generation_duration_s"] for r in model_rows])
    tok_scores = pct_rank_lower_is_better([r["total_tokens"] for r in model_rows])
    tool_scores = pct_rank_lower_is_better([r["tool_calls"] for r in model_rows])
    for r in model_rows:
        eff = 0.40 * dur_scores.get(r["generation_duration_s"], 0) + 0.40 * tok_scores.get(r["total_tokens"], 0) + 0.20 * tool_scores.get(r["tool_calls"], 0)
        r["efficiency_score"] = round(eff, 2)
        r["quality_efficiency_score"] = round(0.75 * r["quality_score"] + 0.25 * r["efficiency_score"], 2)

    model_rows.sort(key=lambda r: (-r["quality_efficiency_score"], -r["quality_score"], -r["efficiency_score"], r["model"]))
    for i, r in enumerate(model_rows, 1):
        r["rank_quality_efficiency"] = i

    return model_rows, artifact_rows, finding_rows


def write_json_csv(root: Path, model_rows, artifact_rows, finding_rows):
    (root / "analysis/data").mkdir(parents=True, exist_ok=True)
    (root / "analysis/tables").mkdir(parents=True, exist_ok=True)
    metadata = {
        "scoring": {
            "quality_score": "100-point sum over five equal 20-point tasks. Each task starts at 20 - 1.2*deterministic_failure_units - 1.6*vlm_failure_units - 0.2*deterministic_warning_units - 0.2*vlm_warning_units. Missing artifacts score 0/20. Artifacts missing valid Birch CSS are capped at 7/20, or 4/20 when VLM also reports vision_unstyled_render; artifacts missing .page are capped at 10/20. Units are distinct (eval, finding_name), so repeated viewport sightings of the same issue are not charged repeatedly.",
            "artifact_score_100": "Compatibility field for the same task score on a 0..100 per-artifact scale: 100 - 6*deterministic_failure_units - 8*vlm_failure_units - deterministic_warning_units - vlm_warning_units, with the equivalent caps 35/100, 20/100, and 50/100.",
            "efficiency_score": "0.40*duration_score + 0.40*token_score + 0.20*tool_call_score; each component is min/max normalized with lower-is-better",
            "quality_efficiency_score": "0.75*quality_score + 0.25*efficiency_score",
        },
        "notes": [
            "Scores are descriptive aids, not hidden ground truth.",
            "Leaderboard sorting should keep source_kind/suite labels visible.",
        ],
    }
    (root / "analysis/data/metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    for name, rows in [("model-summary", model_rows), ("artifact-summary", artifact_rows), ("finding-summary", finding_rows)]:
        (root / f"analysis/data/{name}.json").write_text(json.dumps(rows, indent=2) + "\n")
        if rows:
            fields = list(rows[0].keys())
            # Include any later keys too.
            for row in rows:
                for k in row.keys():
                    if k not in fields:
                        fields.append(k)
            with (root / f"analysis/tables/{name}.csv").open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)


def setup_matplotlib():
    import matplotlib as mpl
    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8,
        "axes.titlesize": 10,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "svg.fonttype": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
    })
    import matplotlib.pyplot as plt
    return plt


def make_figures(root: Path, model_rows, artifact_rows):
    plt = setup_matplotlib()
    out = root / "analysis/figures"
    out.mkdir(parents=True, exist_ok=True)

    # Sort by quality then efficiency for stable visual order.
    models = sorted(model_rows, key=lambda r: (-r["quality_score"], -r["efficiency_score"], r["model"]))
    model_slugs = [r["model_slug"] for r in models]
    model_labels = [r["model"] + (" †" if r["source_kind"] != "main-clean" else "") for r in models]
    by_model_eval = {(r["model_slug"], r["eval"]): r for r in artifact_rows}

    # Figure 1: quality matrix.
    fig_h = max(3.6, 0.29 * len(models) + 1.4)
    fig, ax = plt.subplots(figsize=(8.6, fig_h))
    ax.set_xlim(-0.7, len(EVALS) - 0.3)
    ax.set_ylim(-0.7, len(models) - 0.3)
    ax.invert_yaxis()
    ax.set_xticks(range(len(EVALS)), [e.replace("-", "\n") for e in EVALS])
    ax.set_yticks(range(len(models)), model_labels)
    ax.tick_params(axis="both", length=0)
    for y, slug in enumerate(model_slugs):
        for x, ev in enumerate(EVALS):
            r = by_model_eval.get((slug, ev), {})
            cls = r.get("quality_class", "missing")
            if cls == "fail":
                marker, color, size = "x", "#b2182b", 52
            elif cls == "warn":
                marker, color, size = "o", "#d99000", 30
            elif cls == "clean":
                marker, color, size = "o", "#333333", 18
            else:
                marker, color, size = "o", "#cccccc", 18
            ax.scatter([x], [y], marker=marker, c=color, s=size, linewidths=1.1)
            fail = (r.get("deterministic_failures") or 0) + (r.get("vlm_failures") or 0)
            warn = (r.get("deterministic_warnings") or 0) + (r.get("vlm_warnings") or 0)
            if fail:
                ax.text(x + 0.14, y, str(fail), va="center", ha="left", color="#b2182b", fontsize=6.5)
            elif warn:
                ax.text(x + 0.13, y, str(warn), va="center", ha="left", color="#8a6500", fontsize=6.2)
    ax.set_title("Artifact quality matrix — dot=clean, amber=warnings, red ×=failures")
    ax.text(-0.65, len(models) - 0.05, "† non-main-clean: permitted regeneration or supplemental", fontsize=6.5, color="#555")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(out / "quality-matrix.svg", bbox_inches="tight")
    plt.close(fig)

    # Figure 2: quality vs efficiency scatter.
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    colors = {"main-clean": "#333333", "permitted-regeneration": "#2b6cb0", "supplemental": "#777777"}
    for r in model_rows:
        ax.scatter(r["efficiency_score"], r["quality_score"], s=34, color=colors.get(r["source_kind"], "#333333"), alpha=0.9)
        ax.text(r["efficiency_score"] + 1.0, r["quality_score"] + 0.7, r["model"], fontsize=6.5, color="#222")
    ax.set_xlim(-3, 103)
    ax.set_ylim(-3, 103)
    ax.set_xlabel("Efficiency score: lower time/tokens/tool calls → higher")
    ax.set_ylabel("Quality score: fewer failures/warnings → higher")
    ax.set_title("Quality vs efficiency, with direct model labels")
    ax.grid(axis="both", color="#dddddd", linewidth=0.4)
    ax.text(0, -18, "Quality-efficiency score = 75% quality + 25% efficiency. Scores are descriptive, formula-based aids.", fontsize=7, color="#555")
    fig.tight_layout()
    fig.savefig(out / "quality-vs-efficiency.svg", bbox_inches="tight")
    plt.close(fig)

    # Figure 3: efficiency comparison as small aligned bars.
    ordered = sorted(model_rows, key=lambda r: (-r["quality_efficiency_score"], r["generation_duration_s"]))
    labels = [r["model"] + (" †" if r["source_kind"] != "main-clean" else "") for r in ordered]
    y = list(range(len(ordered)))
    fig_h = max(4.2, 0.32 * len(ordered) + 1.0)
    fig, axes = plt.subplots(1, 3, figsize=(9.2, fig_h), sharey=True)
    metrics = [
        ("generation_duration_s", "seconds", "#555555"),
        ("total_tokens", "tokens", "#555555"),
        ("tool_calls", "tool calls", "#555555"),
    ]
    for ax, (key, title, color) in zip(axes, metrics):
        vals = [r[key] for r in ordered]
        ax.barh(y, vals, color=color, height=0.55)
        ax.invert_yaxis()
        ax.set_title(title)
        ax.grid(axis="x", color="#dddddd", linewidth=0.4)
        ax.tick_params(axis="y", length=0)
        for yi, v in zip(y, vals):
            if key == "total_tokens":
                label = f"{v/1000:.0f}k"
            elif key == "generation_duration_s":
                label = f"{v:.0f}"
            else:
                label = str(v)
            ax.text(v, yi, "  " + label, va="center", fontsize=6.5, color="#222")
    axes[0].set_yticks(y, labels)
    axes[1].tick_params(labelleft=False)
    axes[2].tick_params(labelleft=False)
    fig.suptitle("Efficiency inputs by model — time, tokens, and tool calls", y=0.995, fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "efficiency-comparison.svg", bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repository root, default current directory")
    ap.add_argument("--suite", action="append", help="Result suite under results/ to include. Repeatable. Defaults to clean-final if present, else original-11 + supplemental.")
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    model_rows, artifact_rows, finding_rows = build(root, args.suite)
    write_json_csv(root, model_rows, artifact_rows, finding_rows)
    if not args.no_figures:
        make_figures(root, model_rows, artifact_rows)
    print(f"models: {len(model_rows)}")
    print(f"artifacts: {len(artifact_rows)}")
    print(f"findings: {len(finding_rows)}")
    print("wrote analysis/data, analysis/tables, analysis/figures")


if __name__ == "__main__":
    main()

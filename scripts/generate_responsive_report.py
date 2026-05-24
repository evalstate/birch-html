#!/usr/bin/env python3
"""Generate a cautious, responsive static HTML benchmark report.

Reads the first-pass consolidated files from analysis/data and emits
analysis/report.html. The report intentionally frames metrics as completion,
render-contract checks, VLM visual smoke findings, and efficiency -- not as an
overall model quality evaluation.
"""
from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analysis" / "data"
OUT = ROOT / "analysis" / "report.html"
EVALS = ["numeric-data", "code-review", "module-explainer", "implementation-plan", "benchmark-comparison"]


def read_json(name):
    return json.loads((DATA / name).read_text())


def esc(s):
    return html.escape(str(s), quote=True)


def fmt_int(n):
    try:
        return f"{int(n):,}"
    except Exception:
        return "0"


def fmt_s(n):
    try:
        return f"{float(n):,.0f}s"
    except Exception:
        return "0s"


def human_label(value):
    text = str(value or "").strip()
    if not text:
        return "Result bundle"
    if text.startswith("publication-final-plus-"):
        text = "publication-final"
    return " ".join(part.capitalize() for part in text.replace("_", "-").split("-") if part)


def completed_artifacts(row):
    return int(row.get("artifact_present", row.get("generation_ok", 0)) or 0)


def model_sort_key(row):
    return (
        -float(row.get("quality_score", 0)),
        -completed_artifacts(row),
        int(row.get("deterministic_failures", 0)),
        int(row.get("vlm_failures", 0)),
        int(row.get("deterministic_warnings", 0)),
        int(row.get("vlm_warnings", 0)),
        -float(row.get("efficiency_score", 0)),
        float(row.get("generation_duration_s", 0)),
        int(row.get("total_tokens", 0)),
        int(row.get("tool_calls", 0)),
    )


def comparison_button(label, a, b, prompt, viewport="deep"):
    return (
        f"<button class=\"link-button\" data-compare-a=\"{esc(a)}\" data-compare-b=\"{esc(b)}\" "
        f"data-compare-prompt=\"{esc(prompt)}\" data-compare-viewport=\"{esc(viewport)}\">"
        f"{esc(label)}</button>"
    )


def model_view_button(model_slug, prompt="numeric-data", viewport="deep"):
    return (
        f"<button class=\"link-button\" data-view-model=\"{esc(model_slug)}\" "
        f"data-view-prompt=\"{esc(prompt)}\" data-view-viewport=\"{esc(viewport)}\">view outputs</button>"
    )


def self_check_text(row):
    return fmt_int(row.get("self_check_runs", 0))


def headline_model_rows(models):
    rows = sorted(models, key=model_sort_key)
    out = []
    for i, r in enumerate(rows, 1):
        failures = (r.get("deterministic_failures") or 0) + (r.get("vlm_failures") or 0)
        out.append(f"""
          <tr>
            <td class="num" data-sort-value="{i}">{i}</td>
            <td data-sort-value="{esc(r['model'])}"><strong>{esc(r['model'])}</strong><br><span class="path">{esc(r.get('source_kind',''))}</span></td>
            <td class="num" data-sort-value="{float(r.get('quality_score', 0)):.3f}">{float(r.get('quality_score', 0)):.1f}</td>
            <td class="num" data-sort-value="{int(r.get('total_tokens', 0))}">{fmt_int(r.get('total_tokens', 0))}</td>
            <td class="num" data-sort-value="{float(r.get('generation_duration_s', 0)):.3f}">{fmt_s(r.get('generation_duration_s', 0))}</td>
            <td class="num" data-sort-value="{int(r.get('self_check_runs', 0) or 0)}">{self_check_text(r)}</td>
            <td class="num" data-sort-value="{int(failures)}">{fmt_int(failures)}</td>
            <td>{model_view_button(r['model_slug'])}</td>
          </tr>
        """)
    return "\n".join(out)


def model_rank_rows(models):
    rows = sorted(models, key=model_sort_key)
    out = []
    for i, r in enumerate(rows, 1):
        source = r.get("source_kind", "")
        badge = "" if source == "main-clean" else f" <span class='badge muted'>{esc(source)}</span>"
        render_findings = int(r.get("deterministic_failures",0)) + int(r.get("vlm_failures",0)) + int(r.get("deterministic_warnings",0)) + int(r.get("vlm_warnings",0))
        out.append(f"""
          <tr>
            <td class="num">{i}</td>
            <td><strong>{esc(r['model'])}</strong>{badge}<br><span class="path">{esc(r.get('suite',''))}</span></td>
            <td class="num">{completed_artifacts(r)}/{int(r.get('generation_total',5))}</td>
            <td class="num fail">{fmt_int(r.get('deterministic_failures',0))}</td>
            <td class="num warn">{fmt_int(r.get('deterministic_warnings',0))}</td>
            <td class="num fail">{fmt_int(r.get('vlm_failures',0))}</td>
            <td class="num warn">{fmt_int(r.get('vlm_warnings',0))}</td>
            <td class="num">{fmt_int(render_findings)}</td>
            <td class="num">{fmt_s(r.get('generation_duration_s',0))}</td>
            <td class="num">{fmt_int(r.get('total_tokens',0))}</td>
            <td class="num">{fmt_int(r.get('cache_hit_tokens',0) or r.get('total_cache_tokens',0))}</td>
            <td class="num">{fmt_int(r.get('tool_calls',0))}</td>
            <td class="num">{fmt_int(r.get('self_check_runs',0))}</td>
            <td class="num">{float(r.get('quality_score',0)):.1f}</td>
          </tr>
        """)
    return "\n".join(out)


def build_payload(models, artifacts, findings):
    finding_type_counts = Counter()
    finding_type_by_level = defaultdict(Counter)
    for f in findings:
        key = f.get("name") or "unknown"
        finding_type_counts[key] += 1
        finding_type_by_level[key][f.get("level") or ""] += 1
    top_finding_types = []
    for name, count in finding_type_counts.most_common(16):
        top_finding_types.append({
            "name": name,
            "count": count,
            "fail": finding_type_by_level[name].get("fail", 0),
            "warn": finding_type_by_level[name].get("warn", 0),
        })

    artifact_by_model_eval = {(a["model_slug"], a["eval"]): a for a in artifacts}
    model_order = sorted(models, key=lambda r: (
        -float(r.get("quality_score", 0)),
        -completed_artifacts(r),
        int(r.get("deterministic_failures", 0)),
        int(r.get("vlm_failures", 0)),
        int(r.get("deterministic_warnings", 0)),
        int(r.get("vlm_warnings", 0)),
        -float(r.get("efficiency_score", 0)),
        float(r.get("generation_duration_s", 0)),
    ))
    matrix = []
    for m in model_order:
        cells = []
        for ev in EVALS:
            a = artifact_by_model_eval.get((m["model_slug"], ev), {})
            failures = int(a.get("deterministic_failures",0)) + int(a.get("vlm_failures",0))
            warnings = int(a.get("deterministic_warnings",0)) + int(a.get("vlm_warnings",0))
            status = a.get("quality_class") or "missing"
            if status not in {"clean", "warn", "fail", "missing"}:
                status = "fail" if failures else ("warn" if warnings else ("clean" if a.get("generation_ok") else "missing"))
            cells.append({
                "eval": ev,
                "status": status,
                "failures": failures,
                "warnings": warnings,
                "deterministic_failures": int(a.get("deterministic_failures",0)),
                "deterministic_warnings": int(a.get("deterministic_warnings",0)),
                "vlm_failures": int(a.get("vlm_failures",0)),
                "vlm_warnings": int(a.get("vlm_warnings",0)),
                "task_score": float(a.get("task_score", 0)),
                "task_score_max": float(a.get("task_score_max", 20)),
                "quality_cap_reason": a.get("quality_cap_reason", ""),
                "duration": float(a.get("generation_duration_s",0)),
                "tokens": int(a.get("total_tokens",0)),
                "input_tokens": int(a.get("input_tokens",0)),
                "output_tokens": int(a.get("output_tokens",0)),
                "billing_tokens": int(a.get("billing_tokens",0)),
                "reasoning_tokens": int(a.get("reasoning_tokens",0)),
                "cache_hit_tokens": int(a.get("cache_hit_tokens",0)),
                "total_cache_tokens": int(a.get("total_cache_tokens",0)),
                "effective_input_tokens": int(a.get("effective_input_tokens",0)),
                "tool_calls": int(a.get("tool_calls",0)),
                "self_check_attempted": bool(a.get("self_check_attempted")),
                "self_check_ran": bool(a.get("self_check_ran")),
                "self_check_succeeded": bool(a.get("self_check_succeeded")),
                "self_check_runs": int(a.get("self_check_runs", 0)),
                "self_check_failed_runs": int(a.get("self_check_failed_runs", 0)),
                "self_check_successful_runs": int(a.get("self_check_successful_runs", 0)),
                "self_correction_edits": int(a.get("self_correction_edits", 0)),
                "self_corrected_after_checker": bool(a.get("self_corrected_after_checker")),
                "self_correction_verified": bool(a.get("self_correction_verified")),
                "assistant_turns_trace": int(a.get("assistant_turns_trace", 0)),
                "self_check_mode": a.get("self_check_mode", ""),
                "artifact_path": a.get("artifact_path", ""),
            })
        matrix.append({"model": m["model"], "model_slug": m["model_slug"], "source_kind": m.get("source_kind",""), "cells": cells})

    return {
        "models": models,
        "artifacts": artifacts,
        "findings": findings,
        "topFindingTypes": top_finding_types,
        "matrix": matrix,
        "evals": EVALS,
    }


def main():
    models = read_json("model-summary.json")
    artifacts = read_json("artifact-summary.json")
    findings = read_json("finding-summary.json")
    metadata = read_json("metadata.json") if (DATA / "metadata.json").exists() else {}

    payload = build_payload(models, artifacts, findings)
    payload_json = json.dumps(payload, separators=(",", ":"))

    total_models = len(models)
    total_artifacts = len(artifacts)
    det_fail = sum(int(m.get("deterministic_failures",0)) for m in models)
    det_warn = sum(int(m.get("deterministic_warnings",0)) for m in models)
    vlm_fail = sum(int(m.get("vlm_failures",0)) for m in models)
    vlm_warn = sum(int(m.get("vlm_warnings",0)) for m in models)
    total_seconds = sum(float(m.get("generation_duration_s",0)) for m in models)
    total_tokens = sum(int(m.get("total_tokens",0)) for m in models)
    total_tools = sum(int(m.get("tool_calls",0)) for m in models)
    total_checker_executes = sum(int(m.get("self_check_runs",0)) for m in models)
    suites = sorted({m.get("suite","") for m in models if m.get("suite")})
    source_kinds = sorted({m.get("source_kind","") for m in models if m.get("source_kind")})
    manifests = []
    for suite in suites:
        path = ROOT / "results" / suite / "manifest.json"
        if path.exists():
            try:
                manifests.append(json.loads(path.read_text()))
            except json.JSONDecodeError:
                pass
    label_suffixes = sorted({m.get("label_suffix", "") for m in manifests if m.get("label_suffix")})
    run_label = (
        f"{human_label(label_suffixes[0])} bundle"
        if len(label_suffixes) == 1 else
        "Packaged evidence bundle"
    )
    generation_traces = sum(int(m.get("generation_trace_count", 0)) for m in models)
    vlm_traces = sum(int(m.get("vlm_trace_count", 0)) for m in models)
    complete_models = sum(
        1 for m in models
        if completed_artifacts(m) == int(m.get("generation_total", 0)) and int(m.get("generation_total", 0)) > 0
    )
    suite_label = ", ".join(suites) or "analysis/data"
    run_note = (
        f"Generated from {suite_label}: {total_models} model records, "
        f"{total_artifacts} artifact rows, {generation_traces} generation traces, and "
        f"{vlm_traces} VLM traces. {complete_models}/{total_models} model records completed "
        "all expected artifacts; partial runs remain visible in the tables and matrix."
    )

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Birch HTML Benchmark — Completion, Render Checks, and Efficiency</title>
<style>
:root {{
  --color-ivory: #FAF9F5;
  --color-slate: #141413;
  --color-clay: #D97757;
  --color-clay-dark: #B85C3E;
  --color-oat: #E3DACC;
  --color-olive: #788C5D;
  --color-rust: #B04A3F;
  --color-sky: #6A8CAF;
  --color-white: #FFFFFF;
  --color-gray-50: #F7F5EE;
  --color-gray-100: #F0EEE6;
  --color-gray-150: #E8E4DA;
  --color-gray-200: #DED9CD;
  --color-gray-300: #D1CFC5;
  --color-gray-500: #87867F;
  --color-gray-700: #3D3D3A;
  --color-gray-800: #242421;
  --bg: var(--color-ivory);
  --panel: var(--color-white);
  --panel-2: var(--color-gray-50);
  --ink: var(--color-slate);
  --muted: var(--color-gray-500);
  --line: var(--color-gray-300);
  --soft: var(--color-gray-200);
  --fail: var(--color-rust);
  --warn: #C78E3F;
  --clean: var(--color-slate);
  --blue: var(--color-sky);
  --olive: var(--color-olive);
  --rust: var(--color-clay-dark);
  --accent: var(--color-clay);
  --accent-strong: var(--color-clay-dark);
  --shadow: rgba(20, 20, 19, .08);
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 15px/1.55 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
a {{ color: var(--blue); text-decoration-thickness: .08em; text-underline-offset: .18em; }}
.container {{ max-width: 1180px; margin: 0 auto; padding: 28px 18px 56px; }}
.hero {{ display: grid; grid-template-columns: 1.4fr .9fr; gap: 24px; align-items: end; border-bottom: 1px solid var(--line); padding-bottom: 22px; }}
.eyebrow {{ color: var(--rust); text-transform: uppercase; letter-spacing: .12em; font-size: 12px; font-weight: 700; margin-bottom: 10px; }}
h1 {{ font-family: Georgia, "Times New Roman", serif; font-size: clamp(32px, 5vw, 58px); line-height: .98; margin: 0 0 12px; letter-spacing: -0.045em; font-weight: 500; }}
.title-flourish {{ display: block; color: var(--accent); font-style: italic; font-weight: 500; letter-spacing: -0.065em; margin-left: .04em; }}
h2 {{ font-size: 22px; margin: 34px 0 12px; letter-spacing: -0.02em; }}
h3 {{ font-size: 16px; margin: 18px 0 8px; }}
p {{ margin: 0 0 12px; }}
.lede {{ font-size: 17px; color: var(--color-gray-700); max-width: 74ch; }}
.note {{ color: var(--muted); font-size: 13px; }}
.scope {{ background: color-mix(in srgb, var(--accent) 12%, var(--panel)); border-left: 3px solid var(--accent); padding: 12px 14px; margin-top: 14px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px,1fr)); gap: 10px; }}
.card {{ background: var(--panel); border: 1px solid var(--line); padding: 12px; box-shadow: 0 8px 24px var(--shadow); }}
.card .k {{ font-size: 23px; font-weight: 700; letter-spacing: -0.03em; }}
.card .l {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }}
.grid2 {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, .68fr); gap: 18px; align-items: start; }}
.summary-hero {{ display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 18px; align-items: start; }}
.summary-hero .chart {{ min-height: 520px; }}
.kpi-rail {{ display: grid; gap: 10px; position: sticky; top: 94px; }}
.kpi-card {{ background: var(--panel); border: 1px solid var(--line); padding: 13px; box-shadow: 0 8px 24px var(--shadow); }}
.kpi-card .k {{ font-size: 28px; line-height: 1; font-weight: 750; letter-spacing: -.04em; }}
.kpi-card .l {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .06em; margin-top: 4px; }}
.kpi-card .s {{ color: var(--muted); font-size: 12px; margin-top: 6px; }}
.callout-line {{ border-top: 1px solid var(--soft); padding-top: 10px; margin-top: 2px; color: var(--muted); font-size: 13px; }}
.panel {{ background: var(--panel); border: 1px solid var(--line); padding: 14px; margin: 12px 0; box-shadow: 0 8px 24px var(--shadow); }}
.chart {{ width: 100%; min-height: 330px; position: relative; }}
svg {{ display: block; width: 100%; height: auto; overflow: visible; }}
.axis text, .small {{ fill: var(--muted); font-size: 11px; }}
.gridline {{ stroke: var(--color-gray-200); stroke-width: 1; }}
.matrix-wrap {{ overflow-x: auto; border: 1px solid var(--line); background: var(--panel); box-shadow: 0 8px 24px var(--shadow); }}
.matrix {{ display: grid; min-width: 850px; grid-template-columns: 230px repeat(5, 1fr); align-items: stretch; }}
.mh, .mr, .mc {{ border-bottom: 1px solid var(--soft); padding: 8px 9px; min-height: 40px; display: flex; align-items: center; }}
.mh {{ color: var(--muted); font-size: 12px; font-weight: 650; }}
.mr {{ font-weight: 650; flex-direction: column; align-items: flex-start; justify-content: center; }}
.mr .src {{ display: block; color: var(--muted); font-weight: 400; font-size: 11px; }}
.mc {{ text-align: center; cursor: help; justify-content: center; }}
.status {{ display: inline-flex; justify-content: center; align-items: center; gap: 4px; min-width: 34px; min-height: 24px; padding: 2px 10px; border-radius: 999px; border: 1px solid transparent; font-weight: 700; font-size: 13px; line-height: 1.25; white-space: nowrap; }}
.status.clean {{ color: var(--clean); border-color: var(--color-gray-300); }}
.status.warn {{ color: #8a5700; background: color-mix(in srgb, var(--warn) 14%, var(--panel)); border-color: color-mix(in srgb, var(--warn) 40%, var(--panel)); }}
.status.fail {{ color: var(--fail); background: color-mix(in srgb, var(--fail) 10%, var(--panel)); border-color: color-mix(in srgb, var(--fail) 35%, var(--panel)); }}
.status.missing {{ color: var(--muted); background: var(--color-gray-100); border-color: var(--color-gray-200); }}
.badge {{ display: inline-block; padding: 1px 6px; border: 1px solid var(--line); border-radius: 999px; font-size: 11px; font-weight: 500; }}
.badge.muted {{ color: var(--muted); background: var(--color-gray-50); }}
table {{ border-collapse: collapse; width: 100%; background: var(--panel); }}
th, td {{ border-bottom: 1px solid var(--soft); padding: 7px 8px; text-align: left; vertical-align: top; }}
th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; font-weight: 650; position: sticky; top: 0; background: var(--panel); }}
th.sortable {{ cursor: pointer; user-select: none; }}
th.sortable::after {{ content: "↕"; color: var(--color-gray-500); margin-left: 5px; font-size: 10px; }}
th.sortable.asc::after {{ content: "↑"; color: var(--ink); }}
th.sortable.desc::after {{ content: "↓"; color: var(--ink); }}
td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.fail {{ color: var(--fail); }}
.warn {{ color: var(--warn); }}
.path {{ color: var(--muted); font-size: 12px; }}
.table-wrap {{ overflow-x: auto; border: 1px solid var(--line); margin-top: 10px; max-height: 620px; }}
.tooltip {{ position: fixed; pointer-events: none; background: #111; color: white; padding: 8px 10px; border-radius: 4px; font-size: 12px; line-height: 1.35; max-width: 300px; opacity: 0; transform: translate(10px,10px); transition: opacity .08s; z-index: 20; box-shadow: 0 6px 20px rgba(0,0,0,.18); }}
.tooltip.visible {{ opacity: .96; }}
.controls {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 8px 0 12px; }}
button {{ border: 1px solid var(--line); background: var(--panel); padding: 6px 10px; border-radius: 999px; cursor: pointer; color: var(--ink); }}
button.active {{ background: var(--ink); color: var(--color-ivory); border-color: var(--ink); }}
.link-button {{ border-radius: 3px; padding: 4px 8px; background: var(--panel); color: var(--blue); font: inherit; font-size: 12px; text-align: left; }}
.link-button:hover {{ border-color: var(--blue); }}
.comparison-list {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
.comparison-card {{ background: var(--panel); border: 1px solid var(--line); padding: 12px; box-shadow: 0 8px 24px var(--shadow); }}
.comparison-card p {{ color: var(--muted); font-size: 13px; margin: 6px 0 10px; }}
.vlm-example-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }}
.vlm-example-card {{ background: var(--panel); border: 1px solid var(--line); box-shadow: 0 8px 24px var(--shadow); min-width: 0; }}
.vlm-example-card h3 {{ margin: 0; padding: 9px 10px; border-bottom: 1px solid var(--soft); font-size: 13px; }}
.vlm-example-shot {{ height: 210px; overflow: auto; background: var(--color-gray-100); }}
.vlm-example-shot .shot-frame {{ width: 100%; }}
.vlm-example-meta {{ padding: 9px 10px; color: var(--muted); font-size: 12px; }}
.vlm-example-meta .status {{ white-space: normal; text-align: left; justify-content: flex-start; }}
.bar-cell {{ min-width: 135px; }}
.bar-track {{ height: 8px; background: var(--color-gray-100); margin-top: 4px; }}
.bar-fill {{ height: 8px; background: var(--accent); }}
.select-row {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: end; margin: 10px 0 14px; }}
.select-row label {{ display: grid; gap: 4px; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .05em; }}
select {{ min-width: 210px; padding: 7px 10px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); border-radius: 3px; }}
.compare {{ display: grid; grid-template-columns: 190px minmax(0, 1fr); gap: 14px; align-items: start; }}
.compare-controls {{ display: grid; grid-template-columns: 190px minmax(0, 1fr); gap: 14px; margin: 10px 0 14px; align-items: end; }}
.compare-selects {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)) 170px; gap: 12px; align-items: end; }}
.compare-selects label {{ display: grid; gap: 4px; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .05em; }}
.compare-selects select {{ width: 100%; min-width: 0; }}
.tabs-vertical {{ display: grid; gap: 7px; position: sticky; top: 12px; }}
.tab {{ width: 100%; text-align: left; border-radius: 0; border-left: 3px solid transparent; background: var(--panel-2); }}
.tab.active {{ background: var(--ink); color: var(--color-ivory); border-color: var(--accent); }}
.image-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
.image-card {{ background: var(--panel); border: 1px solid var(--line); min-width: 0; }}
.image-card h3 {{ margin: 0; padding: 9px 10px; border-bottom: 1px solid var(--soft); font-size: 14px; display:flex; justify-content:space-between; gap:8px; }}
.shot-wrap {{ max-height: 760px; overflow: auto; background: var(--color-gray-100); }}
.shot-frame {{ position: relative; display: block; width: 100%; }}
.shot-frame img {{ display: block; width: 100%; height: auto; background: var(--color-gray-100); }}
.bbox {{ position: absolute; border: 2px solid var(--fail); background: rgba(176,74,63,.10); box-shadow: 0 0 0 1px rgba(255,255,255,.75), 0 0 0 9999px rgba(0,0,0,.015); pointer-events: auto; }}
.bbox.warn {{ border-color: var(--warn); background: rgba(199,142,63,.12); }}
.viewer-status {{ color: var(--muted); font-size: 12px; padding: 8px 10px; border-top: 1px solid var(--soft); }}
.mini-link {{ font-weight: 400; font-size: 12px; }}
.footer {{ border-top: 1px solid var(--line); margin-top: 36px; padding-top: 18px; color: var(--muted); font-size: 13px; }}
.top-tabs {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin: 22px 0 20px; position: sticky; top: 0; z-index: 10; background: linear-gradient(var(--bg) 70%, rgba(247,242,232,0)); padding: 10px 0 14px; }}
.top-tab {{ border: 1px solid var(--line); background: var(--panel); padding: 13px 14px; border-radius: 0; text-align: left; box-shadow: 0 8px 20px var(--shadow); }}
.top-tab strong {{ display: block; font-size: 16px; letter-spacing: -.01em; }}
.top-tab span {{ display: block; color: var(--muted); font-size: 12px; margin-top: 2px; }}
.top-tab.active {{ background: var(--ink); color: var(--color-ivory); border-color: var(--ink); }}
.top-tab.active span {{ color: var(--color-gray-200); }}
.site-panel {{ display: none; }}
.site-panel.active {{ display: block; }}
@media (max-width: 850px) {{
  .hero, .grid2, .summary-hero {{ grid-template-columns: 1fr; }}
  .cards {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
  .compare {{ grid-template-columns: 1fr; }}
  .compare-controls {{ grid-template-columns: 1fr; }}
  .compare-selects {{ grid-template-columns: 1fr; }}
  .tabs-vertical {{ position: static; grid-template-columns: repeat(2,minmax(0,1fr)); }}
  .kpi-rail {{ position: static; grid-template-columns: repeat(2,minmax(0,1fr)); }}
  .comparison-list {{ grid-template-columns: 1fr; }}
  .vlm-example-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .top-tabs {{ grid-template-columns: 1fr; position: static; }}
  .container {{ padding-left: 12px; padding-right: 12px; }}
}}
@media (max-width: 520px) {{ .cards, .image-grid, .kpi-rail, .vlm-example-grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="container">
  <section class="hero">
    <div>
      <div class="eyebrow">Birch render evidence bundle · {esc(run_label)}</div>
      <h1>Birch Skill <span class="title-flourish">benchmark</span> report</h1>
      <p class="lede">A report for comparing what happened when multiple models received the same Birch HTML generation prompts under the same benchmark harness.</p>
      <div class="scope">
        <strong>Scope:</strong> this report summarizes completion, deterministic render-contract checks, screenshot-based VLM visual smoke findings, and generation efficiency. It does <strong>not</strong> grade the semantic correctness, analytical insight, factual completeness, or subjective usefulness of the generated reports.
      </div>
    </div>
    <div class="cards">
      <div class="card"><div class="k">{total_models}</div><div class="l">model records</div></div>
      <div class="card"><div class="k">{total_artifacts}</div><div class="l">artifact rows</div></div>
      <div class="card"><div class="k">{fmt_int(total_tokens)}</div><div class="l">total tokens</div></div>
      <div class="card"><div class="k">{fmt_s(total_seconds)}</div><div class="l">wall time</div></div>
      <div class="card"><div class="k">{fmt_int(det_fail + vlm_fail)}</div><div class="l">fail findings</div></div>
      <div class="card"><div class="k">{fmt_int(det_warn + vlm_warn)}</div><div class="l">warn findings</div></div>
    </div>
  </section>

  <section>
    <h2>How to read this report</h2>
    <p>The benchmark is best read as evidence, not as a single model-quality ranking. Raw counts are shown next to any derived index. The most important dimensions are: artifact completion, deterministic render-check failures/warnings, VLM screenshot smoke-review failures/warnings, and generation cost in seconds, tokens, and tool calls.</p>
    <p>Read more at the GitHub repository: <a href="https://github.com/evalstate/birch-html">https://github.com/evalstate/birch-html</a></p>
    <p class="note">{esc(run_note)}</p>
  </section>

  <nav class="top-tabs" aria-label="Report sections">
    <button class="top-tab active" data-site-tab="summary"><strong>Summary Reports</strong><span>overview charts, findings, efficiency</span></button>
    <button class="top-tab" data-site-tab="outputs"><strong>Outputs</strong><span>side-by-side screenshots and artifacts</span></button>
    <button class="top-tab" data-site-tab="details"><strong>Detailed Reports</strong><span>tables, raw counts, scoring caveats</span></button>
  </nav>

  <main>
  <div id="panel-summary" class="site-panel active">

  <section>
    <h2>Headline table: score, tokens, wall time</h2>
    <p class="note">A compact reader-first view: quality score, total generation tokens, total generation wall time, and failure count. Click column headers to sort. “View outputs” jumps to the screenshot/artifact viewer for that model.</p>
    <div class="table-wrap">
      <table id="headlineTable" class="sortable-table">
        <thead><tr><th class="num sortable" data-sort-type="number">#</th><th class="sortable" data-sort-type="text">model</th><th class="num sortable desc" data-sort-type="number">score</th><th class="num sortable" data-sort-type="number">tokens</th><th class="num sortable" data-sort-type="number">wall time</th><th class="num sortable" data-sort-type="number">checker runs</th><th class="num sortable" data-sort-type="number">failures</th><th>outputs</th></tr></thead>
        <tbody>{headline_model_rows(models)}</tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>Render findings vs generation cost</h2>
    <p class="note">Raw audit view. Each point is a model. The default x-axis is total tokens across all five prompts and the y-axis is total render findings: failures plus warnings. The zoom view hides extreme cost outliers and rescales to the visible models. Warnings are shown as findings, not errors. Lower-left is better.</p>
    <div class="summary-hero">
      <div class="panel">
        <div class="controls">
          <button data-x="total_tokens" class="active">tokens</button>
          <button data-x="generation_duration_s">seconds</button>
          <button data-x="tool_calls">tool calls</button>
          <span class="path" style="align-self:center;margin-left:8px;">view</span>
          <button data-domain="zoom" class="active">zoom</button>
          <button data-domain="full">full</button>
        </div>
        <div id="scatter" class="chart"></div>
      </div>
      <aside class="kpi-rail">
        <div class="kpi-card"><div class="k">{total_models}</div><div class="l">model records</div><div class="s">{total_artifacts} model × prompt artifact rows</div></div>
        <div class="kpi-card"><div class="k">{complete_models}/{total_models}</div><div class="l">complete records</div><div class="s">all five artifacts present</div></div>
        <div class="kpi-card"><div class="k">{fmt_int(det_fail + vlm_fail)}</div><div class="l">fail findings</div><div class="s">{fmt_int(det_fail)} deterministic · {fmt_int(vlm_fail)} VLM</div></div>
        <div class="kpi-card"><div class="k">{fmt_int(total_tokens)}</div><div class="l">total tokens</div><div class="s">summed across all records</div></div>
        <div class="kpi-card"><div class="k">{fmt_int(total_checker_executes)}</div><div class="l">checker runs</div><div class="s">model-invoked deterministic checker runs</div></div>
      </aside>
    </div>
  </section>

  <section>
    <h2>Efficiency comparison</h2>
    <p class="note">Raw generation cost inputs by model. Click column headers to sort.</p>
    <div id="efficiency" class="table-wrap"></div>
  </section>

  <section>
    <h2>VLM finding examples</h2>
    <p class="note">A few screenshot-backed visual smoke findings. Boxes are approximate VLM inspection overlays.</p>
    <div id="vlmExamples" class="vlm-example-grid"></div>
  </section>

  <section>
    <h2>Recommended publication comparisons</h2>
    <p class="note">A short set of pairings for readers who want to inspect the screenshot evidence behind the headline story.</p>
    <div class="comparison-list">
      <div class="comparison-card">
        <h3>Headline contenders</h3>
        <p>Two strong, efficient runs with small score differences.</p>
        {comparison_button("GPT-5.3 Codex vs GPT-5.5 · module explainer", "gpt-5-3-codex", "codexresponses-gpt-5-5", "module-explainer", "desktop")}
      </div>
      <div class="comparison-card">
        <h3>Perfect score, higher cost</h3>
        <p>Gemini Flash scores 100, but used much more token budget.</p>
        {comparison_button("Gemini Flash vs GPT-5.3 Codex · numeric data", "gemini35flash", "gpt-5-3-codex", "numeric-data", "desktop")}
      </div>
      <div class="comparison-card">
        <h3>Fair partial credit</h3>
        <p>Haiku has weak capped tasks, but this implementation-plan output earned real credit.</p>
        {comparison_button("Haiku vs GPT-5.3 Codex · implementation plan", "haiku45", "gpt-5-3-codex", "implementation-plan", "desktop")}
      </div>
      <div class="comparison-card">
        <h3>Birch CSS cap sanity check</h3>
        <p>Grok’s unstyled artifact makes the low capped score easy to audit.</p>
        {comparison_button("Grok vs GPT-5.3 Codex · module explainer", "grok-4-3", "gpt-5-3-codex", "module-explainer", "desktop")}
      </div>
    </div>
  </section>

  <section>
    <h2>Completion/render matrix</h2>
    <p class="note">Cells summarize render/check status for each model × prompt. Hover a cell for counts, the 20-point task score, cap reason if any, and generation metrics. A clean cell means no deterministic/VLM fail or warn findings were recorded; it does not mean the analysis content was semantically judged correct.</p>
    <div id="matrix" class="matrix-wrap"></div>
  </section>

  <section>
    <h2>Top finding types</h2>
    <p class="note">Most common deterministic/VLM finding names in the current evidence bundle.</p>
    <div id="findingTypes" class="panel"></div>
  </section>

  </div>
  <div id="panel-outputs" class="site-panel">

  <section>
    <h2>Side-by-side screenshot comparison</h2>
    <p class="note">Pick two model records, choose a viewport, then use the vertical prompt tabs to compare screenshots. The default is desktop deep so below-the-fold structure is visible first.</p>
    <div class="panel">
      <div class="compare-controls">
        <div></div>
        <div class="compare-selects">
          <label>Model A
            <select id="modelA"></select>
          </label>
          <label>Model B
            <select id="modelB"></select>
          </label>
          <label>Viewport
            <select id="viewportSelect">
              <option value="desktop">desktop</option>
              <option value="mobile">mobile</option>
              <option value="deep" selected>desktop deep</option>
              <option value="mobile-deep">mobile deep</option>
            </select>
          </label>
        </div>
      </div>
      <div class="compare">
        <div id="promptTabs" class="tabs-vertical"></div>
        <div id="imageCompare" class="image-grid"></div>
      </div>
    </div>
  </section>

  <section>
    <h2>Artifact-level output table</h2>
    <p class="note">Use this table to jump from aggregate findings to a generated artifact and see each task's 20-point score and cap reason.</p>
    <div id="artifactTable" class="table-wrap"></div>
  </section>

  </div>
  <div id="panel-details" class="site-panel">

  <section>
    <h2>Model summary table</h2>
    <p class="note">Default order is quality-first: five-task quality score, completed artifacts, deterministic failures, VLM failures, warnings, then efficiency. The score is a transparent sorting aid for Birch rendering compliance, not an overall model-quality grade.</p>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th class="num">#</th><th>model</th><th class="num">artifacts</th><th class="num">det fail</th><th class="num">det warn</th><th class="num">VLM fail</th><th class="num">VLM warn</th><th class="num">findings</th><th class="num">seconds</th><th class="num">tokens</th><th class="num">cached/hit</th><th class="num">tools</th><th class="num">checker runs</th><th class="num">quality score</th>
        </tr></thead>
        <tbody>{model_rank_rows(models)}</tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>Model checker execution count</h2>
    <p class="note">Counts below come from each model's own generation traces. This is the simple count of model `execute` tool calls that invoked the Birch deterministic checker. Harness-level checker passes are not counted here.</p>
    <div id="selfCheckTable" class="table-wrap"></div>
  </section>

  <section>
    <h2>Generated data files</h2>
    <p>The microsite is generated programmatically from consolidated JSON/CSV tables. Rebuild with:</p>
<pre class="panel"><code>uv run --with matplotlib python scripts/build_publication_analysis.py --suite publish
python3 scripts/generate_responsive_report.py</code></pre>
    <div class="table-wrap">
      <table>
        <thead><tr><th>file</th><th>purpose</th></tr></thead>
        <tbody>
          <tr><td><code>analysis/data/model-summary.json</code></td><td>model-level completion, render findings, token, time, and tool metrics</td></tr>
          <tr><td><code>analysis/data/artifact-summary.json</code></td><td>per-model × per-prompt metrics, including prompt-level token/cache breakdown</td></tr>
          <tr><td><code>analysis/data/finding-summary.json</code></td><td>deterministic and VLM finding rows</td></tr>
          <tr><td><code>analysis/tables/*.csv</code></td><td>CSV equivalents for audit, README tables, or external analysis</td></tr>
          <tr><td><code>analysis/report.html</code></td><td>this static microsite</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>Derived index caveat</h2>
    <p>The report includes a consolidated <code>quality_score</code>: a 100-point sum over five equal 20-point task scores. It is intentionally formula-based and limited to completion/render findings and Birch rendering contract compliance:</p>
    <pre class="panel"><code>{esc((metadata.get('scoring') or {}).get('quality_score', '100 - penalties for missing artifacts, render failures, VLM failures, render warnings, and VLM warnings'))}</code></pre>
    <p>Missing/fake Birch CSS caps a task because applying the Birch system stylesheet is the core benchmark requirement. A task can receive some credit for artifact presence and partial structure, but a fake or absent Birch stylesheet cannot score as a full Birch render. The combined quality/efficiency index is intentionally not used as the main public ranking in this draft. Raw dimensions remain visible so readers can make their own tradeoffs.</p>
  </section>

  </div>
  </main>

  <div class="footer">
    Generated from <code>analysis/data/*.json</code> and packaged <code>results/*/manifest.json</code> metadata. Raw dimensions remain visible so readers can inspect partial runs, render findings, traces, and efficiency tradeoffs directly.
  </div>
</div>
<div id="tooltip" class="tooltip"></div>
<script id="payload" type="application/json">{payload_json}</script>
<script>
const data = JSON.parse(document.getElementById('payload').textContent);
const tooltip = document.getElementById('tooltip');
function showTip(html, ev) {{ tooltip.innerHTML = html; tooltip.classList.add('visible'); moveTip(ev); }}
function moveTip(ev) {{ tooltip.style.left = Math.min(ev.clientX + 12, window.innerWidth - 330) + 'px'; tooltip.style.top = Math.min(ev.clientY + 12, window.innerHeight - 170) + 'px'; }}
function hideTip() {{ tooltip.classList.remove('visible'); }}
function n(x) {{ return Number(x || 0); }}
function fmt(x) {{ return Math.round(n(x)).toLocaleString(); }}
function statusGlyph(s) {{ return s === 'fail' ? '×' : s === 'warn' ? '○' : s === 'clean' ? '●' : '–'; }}
function totalFindings(m) {{ return n(m.deterministic_failures)+n(m.deterministic_warnings)+n(m.vlm_failures)+n(m.vlm_warnings); }}
function totalFailures(m) {{ return n(m.deterministic_failures)+n(m.vlm_failures); }}
function screenshotPath(artifactPath, evalName, viewport) {{
  if (!artifactPath) return '';
  return '../' + artifactPath.replace('/artifacts/' + evalName + '.html', '/reports/screenshots/' + evalName + '-' + viewport + '.png');
}}
function screenshotPathForArtifact(a, evalName, viewport) {{
  const key = viewport === 'mobile-deep' ? 'screenshot_mobile_deep_path' : 'screenshot_' + viewport.replace('-', '_') + '_path';
  const p = a && a[key] ? a[key] : screenshotPath((a && a.artifact_path) || '', evalName, viewport).replace(/^\\.\\.\\//, '');
  return p ? '../' + p.replace(/^\\.\\.\\//, '') : '';
}}
function artifactFor(modelSlug, evalName) {{
  return data.artifacts.find(a => a.model_slug === modelSlug && a.eval === evalName) || null;
}}
function findingsFor(modelSlug, evalName, viewport) {{
  return (data.findings || []).filter(f => {{
    if (f.model_slug !== modelSlug || f.eval !== evalName) return false;
    if (f.source === 'deterministic') return f.viewport === viewport;
    // VLM findings may be attached to a full screenshot or one of its deep
    // tiles; include same-viewport VLM findings for the inspected screenshot.
    return !f.viewport || f.viewport === viewport;
  }});
}}
function findingTip(modelName, evalName, viewport, fs) {{
  if (!fs.length) return `<strong>${{modelName}}</strong><br>${{evalName}} · ${{viewport}}<br>No fail/warn findings recorded for this inspected screenshot.`;
  const grouped = {{}};
  for (const f of fs) {{
    const key = `${{f.source}} · ${{f.level}}`;
    grouped[key] = grouped[key] || [];
    grouped[key].push(f.name || 'finding');
  }}
  let html = `<strong>${{modelName}}</strong><br>${{evalName}} · ${{viewport}}<br><br>`;
  for (const [k, names] of Object.entries(grouped)) {{
    const counts = {{}};
    names.forEach(n => counts[n] = (counts[n] || 0) + 1);
    html += `<strong>${{k}}</strong><br>` + Object.entries(counts).map(([n,c]) => `${{n}} ×${{c}}`).join('<br>') + '<br>';
  }}
  return html;
}}

function screenshotName(evalName, viewport) {{
  return evalName + '-' + viewport + '.png';
}}

function bboxFindingsFor(modelSlug, evalName, viewport) {{
  const shot = screenshotName(evalName, viewport);
  return (data.findings || []).filter(f =>
    f.model_slug === modelSlug &&
    f.eval === evalName &&
    f.source === 'vlm' &&
    f.screenshot_name === shot &&
    f.bbox_px &&
    n(f.bbox_px.width) > 0 &&
    n(f.bbox_px.height) > 0
  );
}}

function bboxOverlayHtml(fs) {{
  return fs.map((f, i) => {{
    const b = f.bbox_px || {{}};
    const left = n(b.x), top = n(b.y), width = n(b.width), height = n(b.height);
    const tip = `${{f.level || ''}} · ${{f.name || 'finding'}}<br>${{f.evidence || ''}}`.replaceAll('"','&quot;');
    return `<span class="bbox ${{f.level === 'warn' ? 'warn' : 'fail'}}" data-tip="${{tip}}" data-bbox-x="${{left}}" data-bbox-y="${{top}}" data-bbox-width="${{width}}" data-bbox-height="${{height}}" style="left:${{left}}px;top:${{top}}px;width:${{width}}px;height:${{height}}px;"></span>`;
  }}).join('');
}}

function renderMatrix() {{
  const host = document.getElementById('matrix');
  let html = `<div class="matrix"><div class="mh">model</div>`;
  for (const ev of data.evals) html += `<div class="mh">${{ev.replaceAll('-', '<br>')}}</div>`;
  for (const row of data.matrix) {{
    html += `<div class="mr">${{row.model}}<span class="src">${{row.source_kind}}</span></div>`;
    for (const c of row.cells) {{
      const title = `${{row.model}} / ${{c.eval}}`;
      const cap = c.quality_cap_reason ? `<br>cap: ${{c.quality_cap_reason}}` : '';
      const tip = `<strong>${{title}}</strong><br>status: ${{c.status}}<br>task score: ${{n(c.task_score).toFixed(1)}}/${{n(c.task_score_max).toFixed(0)}}${{cap}}<br>det: ${{c.deterministic_failures}} fail, ${{c.deterministic_warnings}} warn<br>VLM: ${{c.vlm_failures}} fail, ${{c.vlm_warnings}} warn<br>checker runs: ${{fmt(c.self_check_runs)}}${{c.self_check_mode ? '<br>mode: '+c.self_check_mode : ''}}<br><br><strong>This prompt only</strong><br>input: ${{fmt(c.input_tokens)}}<br>output: ${{fmt(c.output_tokens)}}<br>total: ${{fmt(c.tokens)}}<br>cached/hit: ${{fmt(n(c.cache_hit_tokens) || n(c.total_cache_tokens))}}<br>effective input: ${{fmt(c.effective_input_tokens)}}<br><br>seconds: ${{c.duration.toFixed(1)}}<br>tool calls: ${{c.tool_calls}}`;
      html += `<div class="mc" data-tip="${{tip.replaceAll('"','&quot;')}}"><span class="status ${{c.status}}">${{statusGlyph(c.status)}}${{c.failures ? ' '+c.failures : (c.warnings ? ' '+c.warnings : '')}}</span></div>`;
    }}
  }}
  html += `</div>`;
  host.innerHTML = html;
  host.querySelectorAll('[data-tip]').forEach(el => {{
    el.addEventListener('mousemove', e => showTip(el.dataset.tip, e));
    el.addEventListener('mouseleave', hideTip);
  }});
}}

function svgEl(name, attrs={{}}) {{
  const el = document.createElementNS('http://www.w3.org/2000/svg', name);
  Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k, v));
  return el;
}}
function text(svg, x, y, str, attrs={{}}) {{ const t=svgEl('text', {{x,y,...attrs}}); t.textContent=str; svg.appendChild(t); return t; }}
function line(svg, x1,y1,x2,y2, attrs={{}}) {{ const l=svgEl('line', {{x1,y1,x2,y2,...attrs}}); svg.appendChild(l); return l; }}

let xMetric = 'total_tokens';
let xDomainMode = 'zoom';

function artifactCount(m) {{ return n(m.artifact_present || m.generation_ok); }}
function provenanceText(m) {{ return `${{n(m.generation_ok)}}/${{n(m.generation_total)}}`; }}
function artifactText(m) {{ return `${{artifactCount(m)}}/${{n(m.generation_total)}}`; }}

function xDomain(rows, metric, mode) {{
  const xs = rows.map(r => n(r[metric]));
  const positive = xs.filter(v => v > 0);
  const minPositive = positive.length ? Math.min(...positive) : 1;
  const maxX = Math.max(...xs, 1);
  const sorted = [...positive].sort((a,b) => a-b);
  const q = p => sorted.length ? sorted[Math.min(sorted.length-1, Math.max(0, Math.floor((sorted.length-1)*p)))] : 1;
  let min = mode === 'zoom' ? Math.max(0, minPositive * 0.88) : 0;
  let max = mode === 'zoom' ? Math.max(q(.78), minPositive * 1.5) : maxX;
  if (mode === 'zoom' && metric === 'total_tokens') max = Math.min(max, 4_200_000);
  if (mode === 'zoom' && metric === 'generation_duration_s') max = Math.min(max, 1_400);
  if (mode === 'zoom' && metric === 'tool_calls') max = Math.min(max, 170);
  return {{min, max: Math.max(max, min + 1), maxObserved: maxX, minPositive}};
}}

function xLabelFor(metric, v) {{
  return metric === 'total_tokens' ? Math.round(v/1000).toLocaleString() + 'k' : Math.round(v).toLocaleString();
}}

function renderScatter() {{
  const host = document.getElementById('scatter'); host.innerHTML = '';
  const W = 980, H = 560, m = {{l:66,r:126,t:22,b:70}};
  const svg = svgEl('svg', {{viewBox:`0 0 ${{W}} ${{H}}`, role:'img'}});
  const allRows = data.models;
  const xs = allRows.map(r => n(r[xMetric]));
  const ysAll = allRows.map(totalFindings);
  const positiveXs = xs.filter(v => v > 0);
  const minPositiveX = positiveXs.length ? Math.min(...positiveXs) : 1;
  const maxX = Math.max(...xs, 1);
  const sortedXs = [...positiveXs].sort((a,b) => a-b);
  const q = p => sortedXs.length ? sortedXs[Math.min(sortedXs.length-1, Math.max(0, Math.floor((sortedXs.length-1)*p)))] : 1;
  let domainMin = xDomainMode === 'zoom' ? Math.max(0, minPositiveX * 0.88) : 0;
  let domainMax = xDomainMode === 'zoom' ? Math.max(q(.78), minPositiveX * 1.5) : maxX;
  // Keep the zoom domain honest: include most of the field but let extreme
  // token/time/tool outliers be marked at the right edge.
  if (xDomainMode === 'zoom' && xMetric === 'total_tokens') domainMax = Math.min(domainMax, 4_200_000);
  if (xDomainMode === 'zoom' && xMetric === 'generation_duration_s') domainMax = Math.min(domainMax, 1_400);
  if (xDomainMode === 'zoom' && xMetric === 'tool_calls') domainMax = Math.min(domainMax, 170);
  domainMax = Math.max(domainMax, domainMin + 1);
  const rows = xDomainMode === 'zoom' ? allRows.filter(r => n(r[xMetric]) <= domainMax) : allRows;
  const hidden = allRows.length - rows.length;
  const ys = rows.map(totalFindings);
  const maxY = Math.max(...ys, 1);
  const x = v => {{
    return m.l + (W-m.l-m.r) * ((v-domainMin)/(domainMax-domainMin));
  }};
  const xPlot = v => Math.max(m.l, Math.min(W-m.r, x(v)));
  const y = v => H-m.b - (H-m.t-m.b) * (v/maxY);
  const xLabel = v => xMetric === 'total_tokens' ? Math.round(v/1000).toLocaleString() + 'k' : Math.round(v).toLocaleString();
  for (let i=0;i<=4;i++) {{
    const yy = y(maxY*i/4); line(svg, m.l, yy, W-m.r, yy, {{class:'gridline'}});
    text(svg, m.l-12, yy+6, Math.round(maxY*i/4), {{'text-anchor':'end', class:'small', style:'font-size:16px;font-weight:650'}});
  }}
  const xTicks = [domainMin, domainMin + (domainMax-domainMin)*.25, domainMin + (domainMax-domainMin)*.5, domainMin + (domainMax-domainMin)*.75, domainMax];
  for (const val of xTicks) {{
    const xx = x(val);
    line(svg, xx, H-m.b, xx, H-m.b+5, {{stroke:'var(--color-gray-500)','stroke-width':1}});
    if (val > 0) line(svg, xx, m.t, xx, H-m.b, {{class:'gridline', opacity:.45}});
    text(svg, xx, H-m.b+25, xLabel(val), {{'text-anchor':'middle', class:'small', style:'font-size:15px;font-weight:650'}});
  }}
  line(svg, m.l, H-m.b, W-m.r, H-m.b, {{stroke:'var(--color-gray-500)','stroke-width':1}});
  line(svg, m.l, m.t, m.l, H-m.b, {{stroke:'var(--color-gray-500)','stroke-width':1}});
  text(svg, (m.l + W - m.r)/2, H-10, xMetric === 'generation_duration_s' ? 'generation seconds' : xMetric === 'total_tokens' ? 'total tokens' : 'tool calls', {{'text-anchor':'middle', class:'small', style:'font-size:18px;font-weight:750'}});
  text(svg, 18, H/2, 'fail + warn findings', {{'text-anchor':'middle', class:'small', style:'font-size:18px;font-weight:750', transform:`rotate(-90 18 ${{H/2}})`}});
  if (hidden) text(svg, W-m.r, m.t+16, `zoom hides ${{hidden}} cost outlier${{hidden === 1 ? '' : 's'}} · switch to full`, {{'text-anchor':'end', class:'small', style:'font-size:12px;font-weight:650'}});
  const labels = [];
  for (const r of rows) {{
    const rawX = n(r[xMetric]);
    const outRight = rawX > domainMax;
    const outLeft = rawX < domainMin;
    const cx=xPlot(rawX), cy=y(totalFindings(r));
    const c=svgEl('circle', {{cx, cy, r: totalFailures(r) ? 7.2 : 6.0, fill: totalFailures(r) ? 'var(--fail)' : 'var(--ink)', opacity:.92}});
    c.addEventListener('mousemove', e => showTip(`<strong>${{r.model}}</strong><br>findings: ${{totalFindings(r)}} (${{totalFailures(r)}} failures)<br><br><strong>All 5 prompts, summed</strong><br>input: ${{fmt(r.input_tokens)}}<br>output: ${{fmt(r.output_tokens)}}<br>total: ${{fmt(r.total_tokens)}}<br>cached/hit: ${{fmt(n(r.cache_hit_tokens) || n(r.total_cache_tokens))}}<br>effective input: ${{fmt(r.effective_input_tokens)}}<br><br>seconds: ${{n(r.generation_duration_s).toFixed(1)}}<br>tool calls: ${{r.tool_calls}}`, e));
    c.addEventListener('mouseleave', hideTip);
    svg.appendChild(c);
    if (outRight) {{
      line(svg, W-m.r-18, cy, W-m.r-4, cy, {{stroke:'var(--accent-strong)','stroke-width':1.5}});
      const arrow = svgEl('path', {{d:`M ${{W-m.r-4}} ${{cy}} l -5 -4 m 5 4 l -5 4`, fill:'none', stroke:'var(--accent-strong)', 'stroke-width':1.5}});
      svg.appendChild(arrow);
    }}
    const anchor = (cx > W - m.r - 160 || outRight) ? 'end' : 'start';
    const tx = anchor === 'end' ? cx - 10 : cx + 10;
    const suffix = outRight ? ` → ${{xLabel(rawX)}}` : '';
    labels.push({{model:r.model + suffix, cx, cy, x:tx, y:cy+4, anchor, w:Math.max(44, (r.model.length + suffix.length)*7.2), h:16}});
  }}
  function bbox(l) {{
    const left = l.anchor === 'end' ? l.x - l.w : l.x;
    return {{left, right:left+l.w, top:l.y-l.h+3, bottom:l.y+4}};
  }}
  function overlaps(a,b) {{
    const A=bbox(a), B=bbox(b);
    return !(A.right < B.left || B.right < A.left || A.bottom < B.top || B.bottom < A.top);
  }}
  // Greedy collision pass. Prefer moving labels upward, which works well for
  // the baseline cluster of failure-free models. Keep labels inside the plot.
  labels.sort((a,b) => b.y - a.y || a.x - b.x);
  for (let pass=0; pass<6; pass++) {{
    for (let i=0; i<labels.length; i++) {{
      for (let j=0; j<i; j++) {{
        if (overlaps(labels[i], labels[j])) {{
          labels[i].y = labels[j].y - 18;
        }}
      }}
      labels[i].y = Math.max(m.t + 14, Math.min(H - m.b - 8, labels[i].y));
    }}
  }}
  for (const l of labels) {{
    if (Math.abs(l.y - (l.cy+4)) > 6) {{
      line(svg, l.cx, l.cy, l.anchor === 'end' ? l.x+2 : l.x-2, l.y-4, {{stroke:'var(--color-gray-300)','stroke-width':.8}});
    }}
    text(svg, l.x, l.y, l.model, {{class:'small', 'text-anchor': l.anchor, style:'font-size:12.5px;font-weight:600'}});
  }}
  host.appendChild(svg);
}}

document.querySelectorAll('button[data-x]').forEach(btn => btn.addEventListener('click', () => {{
  document.querySelectorAll('button[data-x]').forEach(b => b.classList.remove('active'));
  btn.classList.add('active'); xMetric = btn.dataset.x; renderScatter();
}}));
document.querySelectorAll('button[data-domain]').forEach(btn => btn.addEventListener('click', () => {{
  document.querySelectorAll('button[data-domain]').forEach(b => b.classList.remove('active'));
  btn.classList.add('active'); xDomainMode = btn.dataset.domain; renderScatter();
}}));
function renderFindingTypes() {{
  const host = document.getElementById('findingTypes');
  const max = Math.max(...data.topFindingTypes.map(d => d.count), 1);
  let html = '';
  for (const d of data.topFindingTypes) {{
    html += `<div style="display:grid;grid-template-columns:minmax(150px,1fr) 2fr 48px;gap:8px;align-items:center;margin:5px 0;">
      <div class="path">${{d.name}}</div>
      <div style="height:8px;background:var(--color-gray-100);"><div style="height:8px;width:${{100*d.count/max}}%;background:var(--accent);"></div></div>
      <div class="num">${{d.count}}</div>
    </div>`;
  }}
  host.innerHTML = html;
}}

function renderVlmExamples() {{
  const host = document.getElementById('vlmExamples');
  if (!host) return;
  const seen = new Set();
  const examples = (data.findings || [])
    .filter(f => f.source === 'vlm' && f.bbox_px && n(f.bbox_px.width) > 0 && n(f.bbox_px.height) > 0)
    .sort((a,b) => (a.level === 'fail' ? 0 : 1) - (b.level === 'fail' ? 0 : 1) || n(a.bbox_px.width) * n(a.bbox_px.height) - n(b.bbox_px.width) * n(b.bbox_px.height))
    .filter(f => {{
      const key = `${{f.model_slug}}/${{f.eval}}/${{f.name}}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    }})
    .slice(0, 4);
  host.innerHTML = examples.map(f => {{
    const a = artifactFor(f.model_slug, f.eval) || {{}};
    const viewport = f.viewport || (f.screenshot_name || '').replace(`${{f.eval}}-`, '').replace(/\\.png$/, '') || 'deep';
    const src = screenshotPathForArtifact(a, f.eval, viewport);
    const tip = `${{f.level || ''}} · ${{f.name || 'finding'}}<br>${{f.evidence || ''}}`.replaceAll('"','&quot;');
    const shot = src
      ? `<div class="shot-frame"><img src="${{src}}" alt="${{f.model}} ${{f.eval}} ${{viewport}} VLM finding screenshot" loading="lazy" onload="sizeShotFrame(this)" onerror="this.closest('.vlm-example-shot').innerHTML='<div class=&quot;viewer-status&quot;>Image failed to load.</div>'">${{bboxOverlayHtml([f])}}</div>`
      : `<div class="viewer-status">No screenshot path available.</div>`;
    const evidence = String(f.evidence || '').slice(0, 180);
    return `<article class="vlm-example-card">
      <h3>${{f.model}} · ${{f.eval}}</h3>
      <div class="vlm-example-shot">${{shot}}</div>
      <div class="vlm-example-meta"><span class="status ${{f.level === 'warn' ? 'warn' : 'fail'}}" data-tip="${{tip}}">${{statusGlyph(f.level)}} ${{f.name || 'finding'}}</span><br>${{viewport}}${{evidence ? ' · '+evidence+(String(f.evidence || '').length > 180 ? '…' : '') : ''}}</div>
    </article>`;
  }}).join('');
  host.querySelectorAll('[data-tip]').forEach(el => {{
    el.addEventListener('mousemove', e => showTip(el.dataset.tip, e));
    el.addEventListener('mouseleave', hideTip);
  }});
}}

let selectedPrompt = data.evals[0];
function setupCompareControls() {{
  const models = [...data.models].sort((a,b) => a.model.localeCompare(b.model));
  const options = models.map(m => `<option value="${{m.model_slug}}">${{m.model}}${{m.source_kind !== 'main-clean' ? ' · '+m.source_kind : ''}}</option>`).join('');
  const a = document.getElementById('modelA');
  const b = document.getElementById('modelB');
  a.innerHTML = options;
  b.innerHTML = options;
  const preferredA = data.models.find(m => m.model === 'codexresponses.gpt-5.5') || data.models[0];
  const preferredB = data.models.find(m => m.model === 'gpt-5.3-codex') || data.models[1] || data.models[0];
  if (preferredA) a.value = preferredA.model_slug;
  if (preferredB) b.value = preferredB.model_slug;
  const viewport = document.getElementById('viewportSelect');
  if (viewport) viewport.value = 'deep';
  a.addEventListener('change', renderImageCompare);
  b.addEventListener('change', renderImageCompare);
  viewport.addEventListener('change', renderImageCompare);
  renderPromptTabs();
  renderImageCompare();
}}
function renderPromptTabs() {{
  const host = document.getElementById('promptTabs');
  host.innerHTML = data.evals.map(ev => `<button class="tab ${{ev === selectedPrompt ? 'active' : ''}}" data-prompt="${{ev}}">${{ev.replaceAll('-', ' ')}}</button>`).join('');
  host.querySelectorAll('[data-prompt]').forEach(btn => btn.addEventListener('click', () => {{
    selectedPrompt = btn.dataset.prompt;
    renderPromptTabs();
    renderImageCompare();
  }}));
}}
function renderImageCard(slot, modelSlug, evalName, viewport) {{
  const model = data.models.find(m => m.model_slug === modelSlug) || {{}};
  const a = artifactFor(modelSlug, evalName) || {{}};
  const src = screenshotPathForArtifact(a, evalName, viewport);
  const fs = findingsFor(modelSlug, evalName, viewport);
  const bfs = bboxFindingsFor(modelSlug, evalName, viewport);
  const failures = fs.filter(f => f.level === 'fail').length;
  const warnings = fs.filter(f => f.level === 'warn').length;
  const status = a.quality_class || (!a.generation_ok ? 'missing' : failures ? 'fail' : warnings ? 'warn' : 'clean');
  const tip = findingTip(model.model || modelSlug, evalName, viewport, fs).replaceAll('"','&quot;');
  const badge = `<span class="status ${{status}}" data-tip="${{tip}}">${{statusGlyph(status)}}${{failures ? ' '+failures : warnings ? ' '+warnings : ''}}</span>`;
  const artifactLink = a.artifact_path ? `<a class="mini-link" href="../${{a.artifact_path}}" target="_blank" rel="noopener noreferrer">open HTML</a>` : '';
  return `<div class="image-card">
    <h3><span>${{slot}} · ${{model.model || modelSlug}}</span> ${{badge}}</h3>
    <div class="shot-wrap">${{src ? `<div class="shot-frame"><img src="${{src}}" alt="${{model.model || modelSlug}} ${{evalName}} ${{viewport}} screenshot" loading="lazy" onload="sizeShotFrame(this)" onerror="this.closest('.shot-wrap').innerHTML='<div class=&quot;viewer-status&quot;>Image failed to load.<br><a href=&quot;${{src}}&quot; target=&quot;_blank&quot; rel=&quot;noopener noreferrer&quot;>${{src}}</a></div>'">${{bboxOverlayHtml(bfs)}}</div>` : `<div class="viewer-status">No screenshot path available.</div>`}}</div>
    <div class="viewer-status">${{evalName}} · ${{viewport}} · task ${{n(a.task_score).toFixed(1)}}/20${{a.quality_cap_reason ? ' · cap '+a.quality_cap_reason : ''}} · det ${{a.deterministic_failures || 0}}F/${{a.deterministic_warnings || 0}}W · VLM ${{a.vlm_failures || 0}}F/${{a.vlm_warnings || 0}}W${{bfs.length ? ' · boxes '+bfs.length : ''}} · checker runs ${{fmt(a.self_check_runs)}} · tokens ${{fmt(a.total_tokens)}} · <a href="${{src}}" target="_blank" rel="noopener noreferrer">open PNG</a> · ${{artifactLink}}</div>
  </div>`;
}}

function sizeShotFrame(img) {{
  const frame = img.closest('.shot-frame');
  if (!frame || !img.naturalWidth || !img.naturalHeight) return;
  frame.style.aspectRatio = `${{img.naturalWidth}} / ${{img.naturalHeight}}`;
  const scaleX = img.clientWidth / img.naturalWidth;
  const scaleY = img.clientHeight / img.naturalHeight;
  frame.querySelectorAll('.bbox').forEach(box => {{
    const left = parseFloat(box.dataset.bboxX || box.style.left || '0');
    const top = parseFloat(box.dataset.bboxY || box.style.top || '0');
    const width = parseFloat(box.dataset.bboxWidth || box.style.width || '0');
    const height = parseFloat(box.dataset.bboxHeight || box.style.height || '0');
    box.style.left = (left * scaleX) + 'px';
    box.style.top = (top * scaleY) + 'px';
    box.style.width = (width * scaleX) + 'px';
    box.style.height = (height * scaleY) + 'px';
  }});
  const swatch = img.closest('.vlm-example-shot');
  const firstBox = frame.querySelector('.bbox');
  if (swatch && firstBox) {{
    requestAnimationFrame(() => {{
      swatch.scrollLeft = Math.max(0, firstBox.offsetLeft + firstBox.offsetWidth / 2 - swatch.clientWidth / 2);
      swatch.scrollTop = Math.max(0, firstBox.offsetTop + firstBox.offsetHeight / 2 - swatch.clientHeight / 2);
    }});
  }}
  frame.querySelectorAll('[data-tip]').forEach(el => {{
    el.addEventListener('mousemove', e => showTip(el.dataset.tip, e));
    el.addEventListener('mouseleave', hideTip);
  }});
}}
function renderImageCompare() {{
  const modelA = document.getElementById('modelA').value;
  const modelB = document.getElementById('modelB').value;
  const viewport = document.getElementById('viewportSelect').value;
  document.getElementById('imageCompare').innerHTML =
    renderImageCard('A', modelA, selectedPrompt, viewport) +
    renderImageCard('B', modelB, selectedPrompt, viewport);
  document.querySelectorAll('#imageCompare [data-tip]').forEach(el => {{
    el.addEventListener('mousemove', e => showTip(el.dataset.tip, e));
    el.addEventListener('mouseleave', hideTip);
  }});
}}

function activateSiteTab(tab) {{
  document.querySelectorAll('[data-site-tab]').forEach(b => b.classList.toggle('active', b.dataset.siteTab === tab));
  document.querySelectorAll('.site-panel').forEach(panel => panel.classList.toggle('active', panel.id === 'panel-' + tab));
}}

function jumpToCompare(modelA, modelB, prompt, viewport) {{
  activateSiteTab('outputs');
  if (modelA && document.getElementById('modelA')) document.getElementById('modelA').value = modelA;
  if (modelB && document.getElementById('modelB')) document.getElementById('modelB').value = modelB;
  if (viewport && document.getElementById('viewportSelect')) document.getElementById('viewportSelect').value = viewport;
  if (prompt) selectedPrompt = prompt;
  renderPromptTabs();
  renderImageCompare();
  window.scrollTo({{top: document.getElementById('panel-outputs').offsetTop - 78, behavior: 'smooth'}});
}}

function setupJumpLinks() {{
  const reference = (data.models.find(m => m.model === 'gpt-5.3-codex') || data.models[0] || {{}}).model_slug;
  document.querySelectorAll('[data-compare-a]').forEach(btn => btn.addEventListener('click', () => {{
    jumpToCompare(btn.dataset.compareA, btn.dataset.compareB, btn.dataset.comparePrompt, btn.dataset.compareViewport || 'deep');
  }}));
  document.querySelectorAll('[data-view-model]').forEach(btn => btn.addEventListener('click', () => {{
    const model = btn.dataset.viewModel;
    const other = model === reference ? ((data.models.find(m => m.model === 'codexresponses.gpt-5.5') || data.models[1] || {{}}).model_slug) : reference;
    jumpToCompare(model, other, btn.dataset.viewPrompt || 'numeric-data', btn.dataset.viewViewport || 'deep');
  }}));
}}

function renderEfficiency() {{
  const host = document.getElementById('efficiency'); host.innerHTML='';
  const rows = [...data.models].sort((a,b) => n(a.generation_duration_s)-n(b.generation_duration_s));
  const metrics=[['generation_duration_s','seconds'],['total_tokens','tokens'],['tool_calls','tool calls']];
  const maxes = Object.fromEntries(metrics.map(([k]) => [k, Math.max(...rows.map(r=>n(r[k])),1)]));
  let html = `<table class="sortable-table"><thead><tr>
    <th class="sortable" data-sort-type="text">model</th>
    <th class="num sortable asc" data-sort-type="number">seconds</th>
    <th class="num sortable" data-sort-type="number">tokens</th>
    <th class="num sortable" data-sort-type="number">tool calls</th>
    <th class="num sortable" data-sort-type="number">checker runs</th>
  </tr></thead><tbody>`;
  for (const r of rows) {{
    const cell = (key, value, label) => `<td class="num bar-cell" data-sort-value="${{n(value)}}">${{label}}<div class="bar-track"><div class="bar-fill" style="width:${{Math.max(1, 100*n(value)/maxes[key])}}%"></div></div></td>`;
    html += `<tr>
      <td data-sort-value="${{r.model}}"><strong>${{r.model}}</strong><br><span class="path">${{r.source_kind || ''}}</span></td>
      ${{cell('generation_duration_s', r.generation_duration_s, n(r.generation_duration_s).toFixed(1))}}
      ${{cell('total_tokens', r.total_tokens, fmt(r.total_tokens))}}
      ${{cell('tool_calls', r.tool_calls, fmt(r.tool_calls))}}
      <td class="num" data-sort-value="${{n(r.self_check_runs)}}">${{fmt(r.self_check_runs)}}</td>
    </tr>`;
  }}
  host.innerHTML = html + `</tbody></table>`;
}}

function renderArtifactTable() {{
  const rows = [...data.artifacts].sort((a,b) => (n(b.deterministic_failures)+n(b.vlm_failures)) - (n(a.deterministic_failures)+n(a.vlm_failures)) || (n(b.deterministic_warnings)+n(b.vlm_warnings)) - (n(a.deterministic_warnings)+n(a.vlm_warnings)));
  let html = `<table><thead><tr><th>model</th><th>artifact</th><th>status</th><th class="num">task</th><th>cap</th><th class="num">det fail</th><th class="num">det warn</th><th class="num">VLM fail</th><th class="num">VLM warn</th><th class="num">checker runs</th><th class="num">seconds</th><th class="num">input</th><th class="num">output</th><th class="num">total</th><th class="num">cached/hit</th><th class="num">tools</th><th>artifact</th></tr></thead><tbody>`;
  for (const r of rows) {{
    const failures=n(r.deterministic_failures)+n(r.vlm_failures), warnings=n(r.deterministic_warnings)+n(r.vlm_warnings);
    const status = r.quality_class || (!r.generation_ok ? 'missing' : failures ? 'fail' : warnings ? 'warn' : 'clean');
    html += `<tr><td>${{r.model}}<br><span class="path">${{r.source_kind}}</span></td><td>${{r.eval}}</td><td><span class="status ${{status}}">${{statusGlyph(status)}}${{failures ? ' '+failures : warnings ? ' '+warnings : ''}}</span></td><td class="num">${{n(r.task_score).toFixed(1)}}/20</td><td><span class="path">${{r.quality_cap_reason || ''}}</span></td><td class="num fail">${{r.deterministic_failures}}</td><td class="num warn">${{r.deterministic_warnings}}</td><td class="num fail">${{r.vlm_failures}}</td><td class="num warn">${{r.vlm_warnings}}</td><td class="num"><span title="${{r.self_check_mode || ''}}">${{fmt(r.self_check_runs)}}</span></td><td class="num">${{n(r.generation_duration_s).toFixed(1)}}</td><td class="num">${{fmt(r.input_tokens)}}</td><td class="num">${{fmt(r.output_tokens)}}</td><td class="num">${{fmt(r.total_tokens)}}</td><td class="num">${{fmt(n(r.cache_hit_tokens) || n(r.total_cache_tokens))}}</td><td class="num">${{r.tool_calls}}</td><td><a href="../${{r.artifact_path}}">open</a></td></tr>`;
  }}
  html += `</tbody></table>`;
  document.getElementById('artifactTable').innerHTML = html;
}}

function renderSelfCheckTable() {{
  const rows = [...data.models].sort((a,b) => n(b.self_check_runs)-n(a.self_check_runs) || a.model.localeCompare(b.model));
  let html = `<table><thead><tr><th>model</th><th class="num">checker runs</th><th class="num">tasks checked</th><th class="num">gen tasks</th></tr></thead><tbody>`;
  for (const r of rows) {{
    const total = n(r.generation_total) || 5;
    html += `<tr><td><strong>${{r.model}}</strong><br><span class="path">${{r.source_kind || ''}}</span></td><td class="num">${{fmt(r.self_check_runs)}}</td><td class="num">${{n(r.self_check_ran)}}/${{total}}</td><td class="num">${{n(r.generation_ok)}}/${{total}}</td></tr>`;
  }}
  html += `</tbody></table>`;
  document.getElementById('selfCheckTable').innerHTML = html;
}}

function setupSortableTables() {{
  document.querySelectorAll('table.sortable-table').forEach(table => {{
    const tbody = table.tBodies[0];
    table.querySelectorAll('th.sortable').forEach((th, col) => {{
      th.addEventListener('click', () => {{
        const type = th.dataset.sortType || 'text';
        const desc = !th.classList.contains('desc');
        table.querySelectorAll('th.sortable').forEach(h => h.classList.remove('asc', 'desc'));
        th.classList.add(desc ? 'desc' : 'asc');
        const rows = Array.from(tbody.rows);
        rows.sort((a, b) => {{
          const av = a.cells[col]?.dataset.sortValue ?? a.cells[col]?.textContent ?? '';
          const bv = b.cells[col]?.dataset.sortValue ?? b.cells[col]?.textContent ?? '';
          const cmp = type === 'number'
            ? (Number(av) || 0) - (Number(bv) || 0)
            : String(av).localeCompare(String(bv));
          return desc ? -cmp : cmp;
        }});
        rows.forEach(row => tbody.appendChild(row));
      }});
    }});
  }});
}}

function setupSiteTabs() {{
  document.querySelectorAll('[data-site-tab]').forEach(btn => btn.addEventListener('click', () => {{
    const tab = btn.dataset.siteTab;
    activateSiteTab(tab);
    window.scrollTo({{top: document.querySelector('.top-tabs').offsetTop - 8, behavior: 'smooth'}});
  }}));
}}

setupSiteTabs(); renderMatrix(); renderScatter(); renderFindingTypes(); renderVlmExamples(); setupCompareControls(); setupJumpLinks(); renderEfficiency(); renderArtifactTable(); renderSelfCheckTable(); setupSortableTables();
window.addEventListener('resize', () => {{
  // Re-render screenshot cards so optional bbox overlays are recalculated for
  // the current displayed image width. SVG viewBox handles charts.
  if (document.getElementById('panel-outputs').classList.contains('active')) renderImageCompare();
}});
</script>
</body>
</html>
"""
    OUT.write_text(html_doc)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

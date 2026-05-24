#!/usr/bin/env python3
"""Package eval run records into results/clean-final.

This creates the same publication layout consumed by build_publication_analysis.py:
results/clean-final/manifest.json and results/clean-final/models/<slug>/{artifacts,reports,prompts,logs}.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json, re, shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWPORTS = ['desktop','mobile','deep','mobile-deep']

MODEL_NAMES = {
    'codexresponses-gpt-5-5': 'codexresponses.gpt-5.5',
    'codexresponses-gpt-5-4-mini': 'codexresponses.gpt-5.4-mini',
    'codexspark': 'codexspark',
    'opus47': 'opus47',
    'haiku45': 'haiku45',
    'gemini35flash': 'gemini35flash',
    'grok-4-3': 'grok-4.3',
    'kimi': 'kimi',
    'deepseek': 'deepseek',
    'minimax27': 'minimax27',
    'gpt-5-3-codex': 'gpt-5.3-codex',
    'glm51': 'glm51',
    'sonnet46': 'sonnet46',
}

PUBLISH_RUN_SLUG_ALIASES = {
    # Treat the last Kimi retry as the canonical Kimi record for publication.
    'kimi-finaltry': 'kimi',
    # Promote better final retries as the canonical model records.
    'opus47-finaltry': 'opus47',
    'deepseek-finaltry': 'deepseek',
}

PUBLISH_RUN_EXCLUDE_SLUGS = {
    # Superseded by kimi-finaltry.
    'kimi',
    'kimi-k26-together',
    # Superseded by promoted final retries.
    'opus47',
    'deepseek',
    # Retried but not better than the base record.
    'codexspark-finaltry',
    # Tie with the base record; keep the original publish-run record.
    'codexresponses-gpt-5-5-finaltry',
}

def read_json(p):
    return json.loads(p.read_text()) if p.exists() else {}

def copytree(src, dst):
    if dst.exists(): shutil.rmtree(dst)
    if src.exists(): shutil.copytree(src, dst)

def copyfiles(src_dir, dst_dir, pattern):
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_dir.exists():
        for p in src_dir.glob(pattern):
            if p.is_file(): shutil.copy2(p, dst_dir / p.name)

def det_summary(reports_dir, label):
    out = {}
    total_f = total_w = 0
    for vp in VIEWPORTS:
        p = reports_dir / f'{label}-{vp}.json'
        if not p.exists():
            p = reports_dir / f'{label}-visionfill-{vp}.json'
        d = read_json(p)
        s = d.get('summary') or {}
        out[vp] = {
            'artifacts': s.get('artifacts', 0),
            'pairs': s.get('pairs', 0),
            'failures': s.get('failures', 0),
            'warnings': s.get('warnings', 0),
            'notes': s.get('notes', 0),
        }
        total_f += int(s.get('failures') or 0)
        total_w += int(s.get('warnings') or 0)
    return out, total_f, total_w

def vision_counts(reports_dir):
    d = read_json(reports_dir / 'vision-findings.json')
    c = Counter()
    for art in d.get('artifacts', []) or []:
        for f in art.get('findings', []) or []:
            lvl = f.get('level')
            if lvl: c[lvl] += 1
    return dict(c)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--label-suffix",
        default="final-run",
        help="Run label suffix to package, e.g. final-run or publish-run.",
    )
    ap.add_argument(
        "--suite",
        default="clean-final",
        help="Output suite under results/, e.g. clean-final or publish-20260524.",
    )
    ap.add_argument(
        "--description",
        help="Manifest description. Defaults to a description derived from --label-suffix.",
    )
    args = ap.parse_args()
    suffix = args.label_suffix.strip("-")
    suite = args.suite.strip("/")
    out = ROOT / 'results' / suite

    if out.exists(): shutil.rmtree(out)
    (out / 'models').mkdir(parents=True)
    records = []
    run_jsons = sorted((ROOT / 'eval-runs' / 'reports').glob(f'skill-with-shell-*-{suffix}/*-run.json'))
    for run_json in run_jsons:
        label = run_json.parent.name
        m = re.match(rf'skill-with-shell-(.+)-{re.escape(suffix)}$', label)
        if not m: continue
        raw_slug = m.group(1)
        if suffix == 'publish-run' and raw_slug in PUBLISH_RUN_EXCLUDE_SLUGS:
            continue
        slug = PUBLISH_RUN_SLUG_ALIASES.get(raw_slug, raw_slug) if suffix == 'publish-run' else raw_slug
        model = MODEL_NAMES.get(slug, slug)
        src_artifacts = ROOT / 'eval-runs' / label
        src_reports = ROOT / 'eval-runs' / 'reports' / label
        src_prompts = ROOT / 'eval-runs' / 'prompts' / label
        src_logs = ROOT / 'eval-runs' / 'logs'
        dst = out / 'models' / slug
        copytree(src_artifacts, dst / 'artifacts')
        copytree(src_reports, dst / 'reports')
        copytree(src_prompts, dst / 'prompts')
        # logs are flat and label-prefixed; copy matching files if present.
        (dst / 'logs').mkdir(parents=True, exist_ok=True)
        for p in src_logs.glob(f'*{label}*'):
            if p.is_file(): shutil.copy2(p, dst / 'logs' / p.name)
        run = read_json(run_json)
        gen = run.get('generation', []) or []
        artifacts = {p.name: f'eval-runs/{label}/{p.name}' for p in sorted(src_artifacts.glob('*.html'))}
        viewport_summary, det_f, det_w = det_summary(src_reports, label)
        vc = vision_counts(src_reports)
        records.append({
            'model': model,
            'model_slug': slug,
            'label': label,
            'source_kind': 'clean-final',
            'artifact_count': len(artifacts),
            'artifacts': artifacts,
            'generation_ok': sum(1 for g in gen if g.get('ok')),
            'generation_total': len(gen),
            'deterministic_failures': det_f,
            'deterministic_warnings': det_w,
            'viewport_summary': viewport_summary,
            'vision_findings_present': (src_reports / 'vision-findings.json').exists(),
            'vision_counts': vc,
            'publication_paths': {
                'artifacts': f'results/{suite}/models/{slug}/artifacts',
                'reports': f'results/{suite}/models/{slug}/reports',
                'prompts': f'results/{suite}/models/{slug}/prompts',
                'logs': f'results/{suite}/models/{slug}/logs',
            }
        })
    manifest = {
        'created_at': dt.date.today().isoformat(),
        'description': args.description or f'Clean final run packaged from eval-runs/*-{suffix} records. Includes generation and VLM fast-agent traces where available.',
        'label_suffix': suffix,
        'records': records,
    }
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (out / 'README.md').write_text(f'# {suite} results\n\nPackaged {len(records)} model records from `eval-runs/*-{suffix}`.\n')
    print(f'packaged {len(records)} records into {out.relative_to(ROOT)}')

if __name__ == '__main__': main()

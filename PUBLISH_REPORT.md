# Birch HTML benchmark: final publishable report

**Live browser:** <https://evalstate-birch-html.hf.space/analysis/report.html>  
**Packaged evidence:** `results/publish/`  
**Generated:** 2026-05-24  
**Scope:** 13 model runs × 5 Birch HTML artifact tasks.

## Executive summary

This final publication report is built from the fresh **`publication-final`** run with a promoted clean **GPT-5.5** experimental rerun replacing its earlier publication-final record. It includes dynamic deep screenshots capped at 6000px, strengthened VLM diagram review, optional VLM bounding boxes, a report viewer that defaults to desktop-deep screenshots, and model checker-execute counts from generation traces.

The highest raw quality scores are now shared by **codexresponses.gpt-5.5**, **opus47**, **sonnet46**, and **gemini35flash** at **100.0**. The strongest combined quality/efficiency score is **codexresponses.gpt-5.5**.

## Headline results

- **13** model records packaged.
- **65** final artifacts packaged.
- **52 / 65** generation tasks passed immediate provenance validation.
- **186** consolidated finding rows.
- **55** VLM findings include `bbox_px` for report overlays.
- All 13 model records have VLM review with `vision_rc=0` in the final run status.
- GPT-5.5 was promoted from `opus-gpt55-deepseek-experiment-20260524-164522`; the corresponding experimental opus/deepseek records were not promoted. It is displayed as `clean-final` in report tables for simplicity.
- A post-audit verified every packaged model has 20 canonical VLM entries and 5 saved VLM traces.

## How to read the scores

Each model gets five 20-point task opportunities for a 100-point quality score. Scores are formula-based render/compliance aids, not semantic quality judgments.

```text
task_score = 20
- 1.2 * deterministic_failure_units
- 1.6 * VLM_failure_units
- 0.2 * deterministic_warning_units
- 0.2 * VLM_warning_units
```

Caps: missing artifact 0/20; missing/fake Birch CSS max 7/20; missing/fake Birch CSS plus visibly unstyled max 4/20; missing page shell max 10/20.

## Quality-first model summary

| Rank | Model | Quality | Combined | Gen | Det units F/W | VLM units F/W | Tokens | Seconds |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | codexresponses.gpt-5.5 | 100.0 | 96.86 | 5/5 | 0/0 | 0/0 | 797,947 | 670.5 |
| 2 | opus47 | 100.0 | 93.67 | 5/5 | 0/0 | 0/0 | 2,041,367 | 872.9 |
| 3 | gemini35flash | 100.0 | 83.80 | 5/5 | 0/0 | 0/0 | 8,127,743 | 774.4 |
| 4 | sonnet46 | 100.0 | 81.65 | 5/5 | 0/0 | 0/0 | 5,035,097 | 2303.8 |
| 5 | codexresponses.gpt-5.4-mini | 99.8 | 89.84 | 5/5 | 0/1 | 0/0 | 2,887,707 | 1155.8 |
| 6 | glm51 | 96.8 | 92.71 | 5/5 | 1/0 | 1/2 | 1,610,470 | 767.4 |
| 7 | gpt-5.3-codex | 94.4 | 93.45 | 5/5 | 3/1 | 1/1 | 1,288,812 | 372.5 |
| 8 | deepseek | 84.0 | 78.54 | 4/5 | 3/1 | 2/0 | 2,612,700 | 1242.4 |
| 9 | kimi | 83.8 | 75.65 | 4/5 | 2/0 | 3/2 | 2,670,489 | 1764.6 |
| 10 | haiku45 | 83.0 | 86.17 | 3/5 | 7/3 | 1/2 | 949,404 | 370.2 |
| 11 | codexspark | 72.2 | 65.01 | 3/5 | 4/2 | 2/0 | 7,185,820 | 363.5 |
| 12 | grok-4.3 | 58.0 | 68.50 | 2/5 | 4/0 | 4/1 | 599,552 | 284.3 |
| 13 | minimax27 | 58.0 | 63.37 | 1/5 | 7/1 | 1/1 | 1,326,533 | 1039.9 |

## Combined quality/efficiency model summary

| Rank | Model | Quality | Combined | Gen | Det units F/W | VLM units F/W | Tokens | Seconds |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | codexresponses.gpt-5.5 | 100.0 | 96.86 | 5/5 | 0/0 | 0/0 | 797,947 | 670.5 |
| 2 | opus47 | 100.0 | 93.67 | 5/5 | 0/0 | 0/0 | 2,041,367 | 872.9 |
| 3 | gpt-5.3-codex | 94.4 | 93.45 | 5/5 | 3/1 | 1/1 | 1,288,812 | 372.5 |
| 4 | glm51 | 96.8 | 92.71 | 5/5 | 1/0 | 1/2 | 1,610,470 | 767.4 |
| 5 | codexresponses.gpt-5.4-mini | 99.8 | 89.84 | 5/5 | 0/1 | 0/0 | 2,887,707 | 1155.8 |
| 6 | haiku45 | 83.0 | 86.17 | 3/5 | 7/3 | 1/2 | 949,404 | 370.2 |
| 7 | gemini35flash | 100.0 | 83.80 | 5/5 | 0/0 | 0/0 | 8,127,743 | 774.4 |
| 8 | sonnet46 | 100.0 | 81.65 | 5/5 | 0/0 | 0/0 | 5,035,097 | 2303.8 |
| 9 | deepseek | 84.0 | 78.54 | 4/5 | 3/1 | 2/0 | 2,612,700 | 1242.4 |
| 10 | kimi | 83.8 | 75.65 | 4/5 | 2/0 | 3/2 | 2,670,489 | 1764.6 |
| 11 | grok-4.3 | 58.0 | 68.50 | 2/5 | 4/0 | 4/1 | 599,552 | 284.3 |
| 12 | codexspark | 72.2 | 65.01 | 3/5 | 4/2 | 2/0 | 7,185,820 | 363.5 |
| 13 | minimax27 | 58.0 | 63.37 | 1/5 | 7/1 | 1/1 | 1,326,533 | 1039.9 |

## Model checker execution count

Counts below are from model generation traces, not harness checker passes. This is the simple count of model `execute` tool calls that invoked the deterministic checker. Across all tasks: **92** checker runs across **47/65** tasks.

| Model | Checker runs | Tasks checked | Gen |
|---|---:|---:|---:|
| codexresponses.gpt-5.4-mini | 13 | 5/5 | 5/5 |
| gemini35flash | 13 | 5/5 | 5/5 |
| sonnet46 | 11 | 5/5 | 5/5 |
| opus47 | 10 | 5/5 | 5/5 |
| codexresponses.gpt-5.5 | 9 | 5/5 | 5/5 |
| deepseek | 8 | 4/5 | 4/5 |
| kimi | 7 | 4/5 | 4/5 |
| glm51 | 6 | 5/5 | 5/5 |
| codexspark | 5 | 2/5 | 3/5 |
| gpt-5.3-codex | 5 | 3/5 | 5/5 |
| minimax27 | 3 | 2/5 | 1/5 |
| haiku45 | 2 | 2/5 | 3/5 |
| grok-4.3 | 0 | 0/5 | 2/5 |

## Capped tasks

| Model | Task | Task score | Cap reason |
|---|---|---:|---|
| codexspark | code-review | 7.0 | `missing_birch_css` |
| codexspark | numeric-data | 7.0 | `missing_birch_css` |
| deepseek | module-explainer | 4.0 | `missing_birch_css_and_visibly_unstyled` |
| grok-4.3 | benchmark-comparison | 7.0 | `missing_birch_css` |
| grok-4.3 | implementation-plan | 4.0 | `missing_birch_css_and_visibly_unstyled` |
| grok-4.3 | module-explainer | 7.0 | `missing_birch_css` |
| haiku45 | numeric-data | 7.0 | `missing_birch_css` |
| kimi | module-explainer | 4.0 | `missing_birch_css_and_visibly_unstyled` |
| minimax27 | benchmark-comparison | 7.0 | `missing_birch_css` |
| minimax27 | implementation-plan | 7.0 | `missing_birch_css` |
| minimax27 | module-explainer | 4.0 | `missing_birch_css_and_visibly_unstyled` |

## Evidence bundle

- `results/publish/manifest.json`
- `results/publish/models/<slug>/artifacts/*.html`
- `results/publish/models/<slug>/reports/*`
- `analysis/report.html`
- `analysis/data/*.json`
- `analysis/tables/*.csv`

## Caveats

- This is an artifact generation and Birch rendering-compliance benchmark, not a general intelligence benchmark.
- Generation provenance is retained separately from final artifact presence.
- Some rows use `visionfill` checker report names because generation/check exited nonzero but artifacts existed and were render-reviewed uniformly.
- Deep screenshots are dynamically measured but capped at 6000px; some long mobile pages are clipped at that cap.
- VLM bounding boxes are approximate and used for inspection overlays, not scoring.
- The `gpt-5.3-codex module-explainer` VLM issue was added from a targeted diagram audit after the broad pass missed it.
- Kimi's saved VLM traces initially included four generic `desktop.png`/`mobile.png` code-review labels; these were empty findings, but have now been normalized to `code-review-*` names so coverage audits are exact.

## Rebuild

```bash
uv run --with matplotlib python scripts/build_publication_analysis.py --suite publish
python3 scripts/generate_responsive_report.py
```

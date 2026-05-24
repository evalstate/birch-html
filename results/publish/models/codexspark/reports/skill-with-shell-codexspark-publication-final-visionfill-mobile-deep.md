# Birch rendering check

Checks rendered Birch artifacts for contract and visual smoke failures.

## Summary

- Mode: **artifact**
- Artifacts: **5**
- Pairs/checks: **5**
- Failures: **4**
- Warnings: **1**
- Notes: **5**

## `eval-runs/skill-with-shell-codexspark-publication-final/numeric-data.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/numeric-data-mobile-deep.png`
- Size: `[390, 2756]`
- Palette close fraction: `0.9364`
- Background fraction: `0.7933`
- Non-background fraction: `0.2067`
- Blackish fraction: `0.0`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| fail | `uses_birch_system_css` | stylesheet links: []; embedded=True; embedded_bytes=7510 |
| pass | `has_page_shell` | .page found |
| pass | `uses_layout_primitives` | layout primitive count is healthy |
| pass | `uses_semantic_components` | semantic component count is healthy |
| pass | `no_unknown_css_vars` | all CSS variables are defined in Birch system or local CSS |
| pass | `no_patch_markers` | no accidental patch marker lines |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/numeric-data-mobile-deep.png at [390, 2756] |
| fail | `layout_overflow` | section.section.stack > div.section-rail > div.stack > article.panel.chart-panel.stack > p.chart-caption overX=0 overY=0 offRight=202; div.section-rail > div.stack > article.panel.stack > div.section-head > h2 overX=0 overY=0 offRight=202; main.page.stack > section.section.stack > div.section-rail > aside.panel.stack > h2 overX=0 overY=0 offRight=202; div.section-rail > aside.panel.stack > div.metric-list > div.metric-row > span.caption overX=0 overY=0 offRight=40; div.section-rail > aside.panel.stack > div.metric-list > div.metric-row > code overX=0 overY=0 offRight=202 |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `metric_alignment` | metric meters align within each metric-list |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-codexspark-publication-final/code-review.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/code-review-mobile-deep.png`
- Size: `[390, 2413]`
- Palette close fraction: `0.8289`
- Background fraction: `0.6687`
- Non-background fraction: `0.3313`
- Blackish fraction: `0.0`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| fail | `uses_birch_system_css` | stylesheet links: []; embedded=True; embedded_bytes=20 |
| pass | `has_page_shell` | .page found |
| pass | `uses_layout_primitives` | layout primitive count is healthy |
| pass | `uses_semantic_components` | semantic component count is healthy |
| pass | `no_unknown_css_vars` | all CSS variables are defined in Birch system or local CSS |
| pass | `no_patch_markers` | no accidental patch marker lines |
| fail | `grid_list_item_children` | grid-based insight/takeaway list items should wrap content in one child; examples: build_chart_brief.py : data loading, per-artifact line-chart construction, table/ranking r | run_eval.py : end-to-end regeneration + 4 viewport checker invocations. | check_candle_renderings.py : contract checks, list/metric/timeline parser additions, and r |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/code-review-mobile-deep.png at [390, 2413] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-codexspark-publication-final/module-explainer.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/module-explainer-mobile-deep.png`
- Size: `[390, 5285]`
- Palette close fraction: `0.8522`
- Background fraction: `0.7113`
- Non-background fraction: `0.2887`
- Blackish fraction: `0.0`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| pass | `uses_birch_system_css` | embeds or links Birch system CSS |
| pass | `has_page_shell` | .page found |
| pass | `uses_layout_primitives` | layout primitive count is healthy |
| pass | `uses_semantic_components` | semantic component count is healthy |
| pass | `no_unknown_css_vars` | all CSS variables are defined in Birch system or local CSS |
| pass | `no_patch_markers` | no accidental patch marker lines |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/module-explainer-mobile-deep.png at [390, 5285] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| warn | `split_rail_heading_alignment` | Artifact mode payload ↔ Pair mode additions delta=681.8px |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-codexspark-publication-final/implementation-plan.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/implementation-plan-mobile-deep.png`
- Size: `[390, 6000]`
- Palette close fraction: `0.905`
- Background fraction: `0.7605`
- Non-background fraction: `0.2395`
- Blackish fraction: `0.0`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| pass | `uses_birch_system_css` | embeds or links Birch system CSS |
| pass | `has_page_shell` | .page found |
| pass | `uses_layout_primitives` | layout primitive count is healthy |
| pass | `uses_semantic_components` | semantic component count is healthy |
| pass | `no_unknown_css_vars` | all CSS variables are defined in Birch system or local CSS |
| pass | `no_patch_markers` | no accidental patch marker lines |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/implementation-plan-mobile-deep.png at [390, 6000] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-codexspark-publication-final/benchmark-comparison.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/benchmark-comparison-mobile-deep.png`
- Size: `[390, 6000]`
- Palette close fraction: `0.9258`
- Background fraction: `0.8179`
- Non-background fraction: `0.1821`
- Blackish fraction: `0.0006`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| pass | `uses_birch_system_css` | embeds or links Birch system CSS |
| pass | `has_page_shell` | .page found |
| pass | `uses_layout_primitives` | layout primitive count is healthy |
| pass | `uses_semantic_components` | semantic component count is healthy |
| pass | `no_unknown_css_vars` | all CSS variables are defined in Birch system or local CSS |
| pass | `no_patch_markers` | no accidental patch marker lines |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-codexspark-publication-final/screenshots/benchmark-comparison-mobile-deep.png at [390, 6000] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

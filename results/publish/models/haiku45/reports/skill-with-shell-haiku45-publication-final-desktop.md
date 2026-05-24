# Birch rendering check

Checks rendered Birch artifacts for contract and visual smoke failures.

## Summary

- Mode: **artifact**
- Artifacts: **5**
- Pairs/checks: **5**
- Failures: **6**
- Warnings: **3**
- Notes: **6**

## `eval-runs/skill-with-shell-haiku45-publication-final/numeric-data.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/numeric-data-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9215`
- Background fraction: `0.8866`
- Non-background fraction: `0.1134`
- Blackish fraction: `0.0`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| fail | `uses_birch_system_css` | stylesheet links: []; embedded=False; embedded_bytes=0 |
| fail | `has_page_shell` | candidate should use .page as the outer shell |
| warn | `uses_layout_primitives` | too few Birch layout primitives; LLM layout may be brittle |
| warn | `uses_semantic_components` | too few semantic components; likely still page-specific CSS |
| pass | `no_unknown_css_vars` | all CSS variables are defined in Birch system or local CSS |
| pass | `no_patch_markers` | no accidental patch marker lines |
| warn | `local_css_size` | 9565 bytes of local CSS; consider moving recurring patterns into birch-system.css |
| fail | `no_birch_gradients` | Birch artifacts use flat token surfaces; page-local gradient backgrounds are not allowed |
| note | `local_literal_colors` | literal colors outside canonical palette: #1a1a1a, #2d8f5f, #5a5a5a, #8a8a8a, #a86c2d, #e8f5f1, #efefef, #f5f5f5 |
| fail | `metric_row_contract` | .metric-row must be caption + .meter + code; examples: Timeline 99.0% | Design System 98.0% | Component Variants 96.0% |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/numeric-data-desktop.png at [1365, 900] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-haiku45-publication-final/code-review.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/code-review-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9415`
- Background fraction: `0.7699`
- Non-background fraction: `0.2301`
- Blackish fraction: `0.0005`

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
| fail | `no_patch_markers` | found line beginning with + |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/code-review-desktop.png at [1365, 900] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-haiku45-publication-final/module-explainer.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/module-explainer-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9452`
- Background fraction: `0.8769`
- Non-background fraction: `0.1231`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/module-explainer-desktop.png at [1365, 900] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-haiku45-publication-final/implementation-plan.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/implementation-plan-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9382`
- Background fraction: `0.8662`
- Non-background fraction: `0.1338`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/implementation-plan-desktop.png at [1365, 900] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-haiku45-publication-final/benchmark-comparison.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/benchmark-comparison-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9723`
- Background fraction: `0.9319`
- Non-background fraction: `0.0681`
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
| fail | `metric_row_contract` | .metric-row must be caption + .meter + code; examples: vs. Seed A +0.048 | vs. Seed A −3 | Failures 0 | vs. Seed A +18.7% |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/benchmark-comparison-desktop.png at [1365, 900] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

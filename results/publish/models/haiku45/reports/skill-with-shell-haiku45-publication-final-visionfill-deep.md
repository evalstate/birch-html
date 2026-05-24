# Birch rendering check

Checks rendered Birch artifacts for contract and visual smoke failures.

## Summary

- Mode: **artifact**
- Artifacts: **5**
- Pairs/checks: **5**
- Failures: **7**
- Warnings: **3**
- Notes: **6**

## `eval-runs/skill-with-shell-haiku45-publication-final/numeric-data.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/numeric-data-deep.png`
- Size: `[1365, 2020]`
- Palette close fraction: `0.9518`
- Background fraction: `0.9226`
- Non-background fraction: `0.0774`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/numeric-data-deep.png at [1365, 2020] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `metric_alignment` | metric meters align within each metric-list |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-haiku45-publication-final/code-review.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/code-review-deep.png`
- Size: `[1365, 6000]`
- Palette close fraction: `0.9479`
- Background fraction: `0.7492`
- Non-background fraction: `0.2508`
- Blackish fraction: `0.0011`

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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/code-review-deep.png at [1365, 6000] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-haiku45-publication-final/module-explainer.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/module-explainer-deep.png`
- Size: `[1365, 4150]`
- Palette close fraction: `0.9304`
- Background fraction: `0.86`
- Non-background fraction: `0.14`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/module-explainer-deep.png at [1365, 4150] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-haiku45-publication-final/implementation-plan.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/implementation-plan-deep.png`
- Size: `[1365, 6000]`
- Palette close fraction: `0.9545`
- Background fraction: `0.883`
- Non-background fraction: `0.117`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/implementation-plan-deep.png at [1365, 6000] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-haiku45-publication-final/benchmark-comparison.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/benchmark-comparison-deep.png`
- Size: `[1365, 5805]`
- Palette close fraction: `0.8101`
- Background fraction: `0.7314`
- Non-background fraction: `0.2686`
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
| fail | `no_unknown_css_vars` | undefined CSS vars: --color-amber-700, --color-blue-50, --color-green-50, --color-green-700, --color-red-700 |
| pass | `no_patch_markers` | no accidental patch marker lines |
| warn | `local_css_size` | 11985 bytes of local CSS; consider moving recurring patterns into birch-system.css |
| fail | `no_birch_gradients` | Birch artifacts use flat token surfaces; page-local gradient backgrounds are not allowed |
| note | `local_literal_colors` | literal colors outside canonical palette: #059669, #0f172a, #10b981, #1d4ed8, #1e293b, #2563eb, #334155, #3b82f6 |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-haiku45-publication-final/screenshots/benchmark-comparison-deep.png at [1365, 5805] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

# Birch rendering check

Checks rendered Birch artifacts for contract and visual smoke failures.

## Summary

- Mode: **artifact**
- Artifacts: **5**
- Pairs/checks: **5**
- Failures: **6**
- Warnings: **1**
- Notes: **6**

## `eval-runs/skill-with-shell-minimax27-publication-final/numeric-data.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/numeric-data-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9537`
- Background fraction: `0.8924`
- Non-background fraction: `0.1076`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/numeric-data-desktop.png at [1365, 900] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-minimax27-publication-final/code-review.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/code-review-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9102`
- Background fraction: `0.8451`
- Non-background fraction: `0.1549`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/code-review-desktop.png at [1365, 900] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-minimax27-publication-final/module-explainer.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/module-explainer-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9278`
- Background fraction: `0.8648`
- Non-background fraction: `0.1352`
- Blackish fraction: `0.0`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| fail | `uses_birch_system_css` | stylesheet links: ['../styles/birch-system.css']; embedded=False; embedded_bytes=0 |
| pass | `has_page_shell` | .page found |
| pass | `uses_layout_primitives` | layout primitive count is healthy |
| pass | `uses_semantic_components` | semantic component count is healthy |
| pass | `no_unknown_css_vars` | all CSS variables are defined in Birch system or local CSS |
| pass | `no_patch_markers` | no accidental patch marker lines |
| note | `local_literal_colors` | literal colors outside canonical palette: #E8E6DC |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/module-explainer-desktop.png at [1365, 900] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-minimax27-publication-final/implementation-plan.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/implementation-plan-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9489`
- Background fraction: `0.9063`
- Non-background fraction: `0.0937`
- Blackish fraction: `0.0`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| fail | `uses_birch_system_css` | stylesheet links: []; embedded=True; embedded_bytes=6271 |
| pass | `has_page_shell` | .page found |
| warn | `uses_layout_primitives` | too few Birch layout primitives; LLM layout may be brittle |
| pass | `uses_semantic_components` | semantic component count is healthy |
| fail | `no_unknown_css_vars` | undefined CSS vars: --size-sm, --size-xs |
| pass | `no_patch_markers` | no accidental patch marker lines |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/implementation-plan-desktop.png at [1365, 900] |
| fail | `layout_overflow` | section > div.auto-grid > article.card > ol.flow-list > li.flow-step overX=3 overY=0 offRight=0 |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-minimax27-publication-final/benchmark-comparison.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/benchmark-comparison-desktop.png`
- Size: `[1365, 900]`
- Palette close fraction: `0.9149`
- Background fraction: `0.8653`
- Non-background fraction: `0.1347`
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
| fail | `grid_list_item_children` | grid-based insight/takeaway list items should wrap content in one child; examples: Token comparability: Provider token schemas differ; cached, reasoning, and effective token | Checker limitations: Checker warnings are mechanical contract signals, not a complete huma | Screenshot validation: Same:same screenshot pairs validate geometry and rendering contract | Wall time noise: Wall time includes model latency and harness overhead; small differences  |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/benchmark-comparison-desktop.png at [1365, 900] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

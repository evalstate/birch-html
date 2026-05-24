# Birch rendering check

Checks rendered Birch artifacts for contract and visual smoke failures.

## Summary

- Mode: **artifact**
- Artifacts: **5**
- Pairs/checks: **5**
- Failures: **3**
- Warnings: **0**
- Notes: **5**

## `eval-runs/skill-with-shell-glm51-publication-final/numeric-data.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/numeric-data-mobile-deep.png`
- Size: `[390, 3149]`
- Palette close fraction: `0.9289`
- Background fraction: `0.8108`
- Non-background fraction: `0.1892`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/numeric-data-mobile-deep.png at [390, 3149] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `metric_alignment` | metric meters align within each metric-list |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-glm51-publication-final/code-review.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/code-review-mobile-deep.png`
- Size: `[390, 6000]`
- Palette close fraction: `0.8591`
- Background fraction: `0.7314`
- Non-background fraction: `0.2686`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/code-review-mobile-deep.png at [390, 6000] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-glm51-publication-final/module-explainer.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/module-explainer-mobile-deep.png`
- Size: `[390, 6000]`
- Palette close fraction: `0.8443`
- Background fraction: `0.7026`
- Non-background fraction: `0.2974`
- Blackish fraction: `0.0077`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| fail | `uses_birch_system_css` | stylesheet links: []; embedded=True; embedded_bytes=22 |
| pass | `has_page_shell` | .page found |
| pass | `uses_layout_primitives` | layout primitive count is healthy |
| pass | `uses_semantic_components` | semantic component count is healthy |
| pass | `no_unknown_css_vars` | all CSS variables are defined in Birch system or local CSS |
| pass | `no_patch_markers` | no accidental patch marker lines |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/module-explainer-mobile-deep.png at [390, 6000] |
| fail | `layout_overflow` | section.section.stack > div.split > div.stack > div.card.stack > pre.code-block overX=24 overY=0 offRight=0; section.section.stack > div.split > div.stack > div.card.stack > pre.code-block overX=24 overY=0 offRight=0; section.section.stack > div.split > div.stack > div.card.stack > pre.code-block overX=24 overY=0 offRight=0; section.section.stack > div.split > div.stack > div.card.stack > pre.code-block overX=40 overY=0 offRight=0 |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `metric_alignment` | metric meters align within each metric-list |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-glm51-publication-final/implementation-plan.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/implementation-plan-mobile-deep.png`
- Size: `[390, 6000]`
- Palette close fraction: `0.9089`
- Background fraction: `0.7615`
- Non-background fraction: `0.2385`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/implementation-plan-mobile-deep.png at [390, 6000] |
| fail | `layout_overflow` | table.numeric-table > tbody > tr > td.metric > code overX=0 overY=0 offRight=297; table.numeric-table > tbody > tr > td.metric > code overX=0 overY=0 offRight=462; table.numeric-table > tbody > tr > td.metric > code overX=0 overY=0 offRight=149; table.numeric-table > tbody > tr > td.metric > code overX=0 overY=0 offRight=140; table.numeric-table > tbody > tr > td.metric > code overX=0 overY=0 offRight=140 |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-glm51-publication-final/benchmark-comparison.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/benchmark-comparison-mobile-deep.png`
- Size: `[390, 6000]`
- Palette close fraction: `0.9466`
- Background fraction: `0.8542`
- Non-background fraction: `0.1458`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-glm51-publication-final/screenshots/benchmark-comparison-mobile-deep.png at [390, 6000] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

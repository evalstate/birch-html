# Birch rendering check

Checks rendered Birch artifacts for contract and visual smoke failures.

## Summary

- Mode: **artifact**
- Artifacts: **5**
- Pairs/checks: **5**
- Failures: **8**
- Warnings: **4**
- Notes: **6**

## `eval-runs/skill-with-shell-minimax27-publication-final/numeric-data.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/numeric-data-mobile-deep.png`
- Size: `[390, 1692]`
- Palette close fraction: `0.9458`
- Background fraction: `0.7504`
- Non-background fraction: `0.2496`
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
| warn | `local_css_size` | 10616 bytes of local CSS; consider moving recurring patterns into birch-system.css |
| note | `local_literal_colors` | literal colors outside canonical palette: #B85C3E, #C78E3F, #DED9CD, #E8E4DA, #F7F5EE |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/numeric-data-mobile-deep.png at [390, 1692] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-minimax27-publication-final/code-review.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/code-review-mobile-deep.png`
- Size: `[390, 5477]`
- Palette close fraction: `0.8836`
- Background fraction: `0.7181`
- Non-background fraction: `0.2819`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/code-review-mobile-deep.png at [390, 5477] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-minimax27-publication-final/module-explainer.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/module-explainer-mobile-deep.png`
- Size: `[390, 6000]`
- Palette close fraction: `0.8294`
- Background fraction: `0.6765`
- Non-background fraction: `0.3235`
- Blackish fraction: `0.0041`

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
| warn | `local_css_size` | 4485 bytes of local CSS; consider moving recurring patterns into birch-system.css |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/module-explainer-mobile-deep.png at [390, 6000] |
| fail | `layout_overflow` | table.ext-table > tbody > tr > td > code overX=0 overY=0 offRight=114; table.ext-table > tbody > tr > td > code overX=0 overY=0 offRight=37; table.ext-table > tbody > tr > td > code overX=0 overY=0 offRight=18; table.ext-table > tbody > tr > td > code overX=0 overY=0 offRight=75; table.ext-table > tbody > tr > td > code overX=0 overY=0 offRight=12 |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-minimax27-publication-final/implementation-plan.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/implementation-plan-mobile-deep.png`
- Size: `[390, 5193]`
- Palette close fraction: `0.8539`
- Background fraction: `0.7235`
- Non-background fraction: `0.2765`
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
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/implementation-plan-mobile-deep.png at [390, 5193] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

## `eval-runs/skill-with-shell-minimax27-publication-final/benchmark-comparison.html`

### Screenshot metrics

- Screenshot: `eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/benchmark-comparison-mobile-deep.png`
- Size: `[390, 3243]`
- Palette close fraction: `0.8372`
- Background fraction: `0.6972`
- Non-background fraction: `0.3028`
- Blackish fraction: `0.0001`

### Findings

| level | check | evidence |
|---|---|---|
| pass | `doctype` | doctype present |
| pass | `viewport` | viewport meta present |
| fail | `uses_birch_system_css` | stylesheet links: []; embedded=True; embedded_bytes=20 |
| pass | `has_page_shell` | .page found |
| pass | `uses_layout_primitives` | layout primitive count is healthy |
| pass | `uses_semantic_components` | semantic component count is healthy |
| fail | `no_unknown_css_vars` | undefined CSS vars: --fg-muted |
| pass | `no_patch_markers` | no accidental patch marker lines |
| fail | `grid_list_item_children` | grid-based insight/takeaway list items should wrap content in one child; examples: numeric-data: Candidate chart is clearer but uses more SVG text; worth the +0.040 gain. | code-review: No mechanical regression; inspect finding severity wording manually before co | module-explainer: Runtime path improved; mobile flow caption remains dense — future improv | implementation-plan: Largest single gain (+0.088); no checker regression. |
| note | `screenshot_capture` | captured eval-runs/reports/skill-with-shell-minimax27-publication-final/screenshots/benchmark-comparison-mobile-deep.png at [390, 3243] |
| pass | `layout_overflow` | no visible text/content overflow detected |
| pass | `container_text_overflow` | text stays within its card/panel containers |
| pass | `stat_card_squeeze` | KPI/stat cards have enough horizontal space |
| pass | `timeline_geometry` | timeline markers/content stay within expected geometry |
| pass | `numeric_header_alignment` | numeric table headers align with right-aligned numeric columns |
| pass | `code_wrap_underfill` | wrapped code/diff blocks use available container width |
| pass | `pathological_text_wrapping` | prose/list text uses available container width |

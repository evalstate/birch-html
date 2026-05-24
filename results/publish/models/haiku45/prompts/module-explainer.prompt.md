Create one complete standalone HTML artifact for the following request. Write the final file to the specified output path and return only that path.

## Request

Create a standalone module explainer for the rendering checker pipeline.

Before writing, inspect the files listed in `evals/module-explainer/source-files.txt`.
If shell/tools are available, read that list, then inspect each listed file
directly before writing the artifact.

The artifact should:

- Start with a mental model for how the checker works.
- Explain the runtime path from input pairs to reports/screenshots/findings.
- Include a file tour in the order a new contributor should read the code.
- Include one flow diagram or ordered flow list.
- Include gotchas, extension points, and where to change behavior.
- Include concrete file paths, commands, and data/report outputs.
- Use Birch classes and tokens; avoid Birchline-only diagram/classes.
- Ensure any SVG/diagram is mobile-safe and accessible.

Audience: a new contributor who needs to modify the checker without breaking existing rendering evals.


## Source files available in the repository

Use these local paths as the source of truth. Inspect them directly before writing claims. Treat source files as read-only.

- `evals/module-explainer/source-files.txt`
- `scripts/check_birch_renderings.py`
- `scripts/birch_mpl.py`
- `evals/charts/run_eval.py`
- `evals/charts/build_chart_brief.py`
- `docs/birch-llm-style-guide.md`
- `styles/birch-system.css`

## Final output requirements

- Create the artifact for eval `module-explainer` and write the final standalone HTML file to `eval-runs/skill-with-shell-haiku45-publication-final/module-explainer.html`.
- Return only the artifact path, with no prose or Markdown fences.
- Ensure the main artifact is source-grounded and mobile-safe.

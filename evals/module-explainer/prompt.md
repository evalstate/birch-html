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

# Code review rubric

Score each category 1–5.

1. **Findings-first structure** — high-impact findings or explicit no-findings state appears first.
2. **Diff grounding** — cites changed files, functions, behavior, and concrete evidence from the diff.
3. **Severity clarity** — severity/risk labels are visible and meaningful.
4. **Reviewer usefulness** — includes actionable fixes, checklist, and residual risk.
5. **Birch contract** — uses `.card`, `.badge`, `.diff`, `.diff-row`, `.code-block`, `.callout`, `.checklist`, `.plain-list`; avoids Birchline-only classes.
6. **Visual/readability quality** — compact, scannable, no decorative dashboard drift, mobile safe.

Fail conditions: invented facts, burying blocking issues, no file references, external assets, unknown Birch/Birchline class leakage.

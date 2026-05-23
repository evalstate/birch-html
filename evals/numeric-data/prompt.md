Create a standalone numeric-data analysis from the local CSV file
`evals/numeric-data/source.csv`.

Inspect the CSV directly and compute the headline numbers from the file. Useful
values include latest-week pass rates, overflow counts, week-over-week change,
best/worst artifact, and the trend across weeks.

The artifact should:

- Start with a compact hero stating the key finding.
- Show evidence in the first desktop viewport.
- Include a KPI strip with 3–4 headline numbers.
- Include one ranking/progress visual using Birch metric rows.
- Include one plotted SVG chart for the weekly trend.
- Include an exact numeric table near the chart.
- Use Python or another local calculation path when helpful to compute exact
  values. The final artifact must still be one standalone HTML document with an
  inline SVG chart.
- Include a short source/caveat note.
- Use Birch classes and tokens; avoid hard-coded colors in page CSS.
- Do not use external JavaScript chart libraries.
- The chart must be readable on mobile without horizontal scrolling.

Audience: engineering/product leads deciding whether the new rendering checker is stable enough to adopt.

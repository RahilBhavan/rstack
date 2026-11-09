# Output format

Default: **one self-contained HTML file** (or HTML artifact) that works on screen and prints
cleanly. Only produce Word, PDF, or Markdown when the user names that format. Pick once and
stay with it: rebuilding the same guide in a second format doubles the work.

## Layout
- Light background, one readable sans-serif font, 16px body, max width ~800px, generous
  line spacing. Clear h2 per topic, h3 per subsection. No emoji, no decorative icons.
- A table of contents with anchor links at the top.
- Each answer directly under its question, hidden in `<details><summary>Show answer</summary>…</details>`
  so the student retrieves before checking.
- Print stylesheet: `@media print { details { display:block } details > summary { display:none } }`
  plus `break-inside: avoid` on questions, so the printout shows answers in place and
  questions don't split across pages. If the user prints the exam without answers, offer a
  version with the details removed.

## Math
- Use KaTeX with auto-render from a CDN (`katex.min.css`, `katex.min.js`, `auto-render.min.js`)
  with `\(...\)` for inline and `\[...\]` for display math. Don't use `$` delimiters:
  economics material is full of dollar amounts, which `$` delimiters turn into broken math.
- After writing, check every expression: balanced delimiters, no stray `\` commands outside
  math, no CSS that resets `.katex` styles. If you can render the file (browser, headless
  screenshot), do it and confirm no raw TeX is visible before delivering. Broken math
  showing as raw code has happened repeatedly and wastes a turn each time.
- If the environment can't load KaTeX, fall back to Unicode math (x², β̂₁, ≤, →, ×, √).
- In chat replies (not files), write math in plain Unicode, not LaTeX.

## Graphs
- Inline SVG (or Chart.js from a CDN for data-heavy plots). Label axes and curves directly.
  Economics diagrams: show the shift with the original curve faded and the new one solid,
  and label the equilibrium points.
- Verify each graph matches the claim in the text (direction of shift, intercepts, slope sign).

## Size
One HTML file is the default. Split into numbered files (one per lecture group, same
styling) only when a single file would exceed one response; that rule wins over the
one-file default. Never stop mid-way to ask whether to continue.

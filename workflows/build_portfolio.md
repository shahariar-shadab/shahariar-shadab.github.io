# Workflow: build and preview the portfolio

**Objective:** regenerate `docs/` from the content and template, and check it in a browser before anything is published.

## Inputs
- `content/site.json`: all copy and numbers
- `site/template.html`: layout, styles, scripts
- `.env`: only `PUBLIC_*` keys are read (email, LinkedIn, GitHub username, Formspree ID, domain)
- The newest PDF in `content/resume/`

## Steps
1. If `.venv/` is missing, run `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
2. Build with `.venv/bin/python tools/build_site.py`. The build prints what it made, the form mode (`formspree` or `mailto`) and the site URL.
3. Preview by serving `docs/` (`python3 -m http.server 8000 -d docs`), or use the `portfolio` entry in `.claude/launch.json`. Open http://localhost:8000.
4. Check:
   - Desktop and 375px mobile, with no horizontal scroll (`document.documentElement.scrollWidth === innerWidth`).
   - No console errors.
   - Every `#anchor` link resolves. `resume.pdf`, `favicon.svg` and `og.png` all return 200.
   - `resume.pdf` starts with the name header, not the blank cover page.
   - `grep -c PHONE docs/index.html` returns 0, so no private values were built in.
   - **Both themes:** toggle with the sun/moon button and check each one. Clear `localStorage.theme`, set the system or browser to light, and reload: the page should come up light, with no `data-theme` attribute on `<html>`.
   - **Contrast:** every text colour must reach at least 4.5:1, or 3:1 for text that is 24px+ (or 18.66px+ bold), in both themes. Run `tools/contrast_audit.js` in the page (paste it into the console). It checks both themes and must report 0 failures. Baseline on 2026-10-14: 187 elements, 0 failures. The lowest ratios were 4.79 (dark, section numbers) and 3.61 (light, the large "agents." headline).

## Edge cases / learnings
- The light theme's tokens are written twice in `site/template.html`: once inside `@media (prefers-color-scheme: light)` and once for `:root[data-theme="light"]`. Edit both, or the toggle and the automatic mode will drift apart.
- In light mode, never use Sky Glow, Signal Amber or Slate Blue for text; they fail contrast on light backgrounds. Use the theme tokens instead.
- In the Claude browser pane, clicking an element by its `ref` once fired the toggle twice. A normal mouse click fires it once. That's a tool quirk, not a site bug.
- **Never edit `docs/` by hand.** The next build overwrites it.
- A `{{placeholder}}` in the template with no value stops the build with an error. Add the value in `build_site.py`'s `values` dict.
- The page's wording is escaped HTML. To add a link inside copy, add a new field and render it in `build_site.py`; don't put raw HTML in `site.json`.
- `og.png` is cropped from `brand_assets/LinkedIn banner.png` using macOS `sips`. On a machine without `sips` the step is skipped, and the previous `og.png` is kept.
- In the Claude desktop browser pane, programmatic `scrollTo` can be reset while the pane is resizing. Wait a moment and retry. This doesn't happen in real browsers.
- Reduced motion: with `prefers-reduced-motion: reduce` (or no JS), the `motion` class is never added, so all content shows immediately.

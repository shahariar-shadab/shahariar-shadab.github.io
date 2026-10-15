# Agent Instructions — SHAH Portfolio

This project is Shahariar "Shah" Shadab's personal portfolio website: a static site linked from the resume so hiring managers for **Data / BI Analyst** roles can see the work behind the bullet points. Positioning: *Data Analyst → Automation & Agents* ("From SQL to agents.").

It uses the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution.

- **Workflows** (`workflows/`): Markdown SOPs — objective, inputs, tools, outputs, edge cases.
- **Agent** (you): read the relevant workflow, run tools in order, handle failures, ask when unsure.
- **Tools** (`tools/`): Python scripts that do the actual work. Run them with `.venv/bin/python`.

## Workflows

| Task | Workflow |
| --- | --- |
| Build and preview the site locally | `workflows/build_portfolio.md` |
| Resume changed — refresh the site content | `workflows/update_from_resume.md` |
| Publish to GitHub Pages / connect the custom domain | `workflows/deploy_github_pages.md` |

## How the site is made

```
content/site.json  ─┐
site/template.html ─┼─► tools/build_site.py ─► docs/   (GitHub Pages serves main:/docs)
.env (PUBLIC_* only)┘        └─ newest PDF in content/resume/ ─► docs/resume.pdf (cover page dropped)
```

- **Never hand-edit `docs/`** — it is generated. Change `content/site.json` or `site/template.html`, then rebuild.
- `content/site.json` is the single source for all words and numbers on the page.
- `site/template.html` holds layout, styles and scripts. Placeholders are `{{name}}`; repeated blocks are rendered in `build_site.py`.

## Rules

1. **Honesty.** Only publish claims and numbers that are on the resume or that Shah has confirmed in chat or in `content/INFO_NEEDED.md`. "Agents" is positioning (where the work is heading) until a real agent project is confirmed. Never invent metrics to fill a card.
2. **Confidentiality.** Employer work (NYC DOHMH especially) is described in general terms: no student/school-level data, internal file names, or screenshots of real dashboards.
3. **Personal data.** Private values live only in `.env` (gitignored). Only keys starting with `PUBLIC_` are ever read by the build, and they become public on the website. Never write a non-`PUBLIC_` value into `docs/`, `content/`, commits or chat. The phone number is not published.
4. **Brand.** Follow `brand_assets/Brand Guidelines.png` (summary below). `brand_assets/Portfolio hero.png` is the reference for the hero and case-study cards.
5. **Ask before** pushing to GitHub, buying/registering anything, creating accounts, or overwriting a workflow.
6. **Keep this file current.** When a decision is made or something is learned, update the relevant section here or in the workflow.

## Brand summary (SHAH Visual Identity v1.0, Oct 2026)

| Token | Hex | Use |
| --- | --- | --- |
| Midnight | `#071426` | page background |
| Deep Navy | `#0E2441` | cards, panels |
| Cobalt | `#1747B8` | depth, gradients |
| Volt Blue | `#2F7CFF` | primary buttons, key accents |
| Sky Glow | `#7DCBFF` | highlights, icons, metrics, logo dots |
| Slate Blue | `#8FA9C9` | secondary text |
| Mist | `#DCE8F7` | body text on dark |
| Signal Amber | `#FFB43B` | accent — **one per view** (human review, contact CTA) |

- Type: **Sora** (400/600/800) headlines & body; **IBM Plex Mono** (400/500) labels, data, captions — uppercase, letter-spaced.
- Logo: the S-mark (rounded stroke with two Sky Glow end dots) + "SHAH". Blue outer glow on dark backgrounds only. Clearspace = half the mark's height.
- Icons: 24px grid, 1.75px rounded stroke, Sky Glow on dark.
- Buttons: primary Volt Blue pill with glow; secondary outlined pill; amber accent max once per view.
- Background: dot grid + soft radial blue glow top-right.

### Light / dark themes
Dark is the default and the brand's signature look (LinkedIn banner, og.png, favicon stay dark). The site also has a
light theme: it follows the visitor's system setting, and a sun/moon toggle in the nav overrides it (saved in
`localStorage.theme`). Components use **theme tokens** (`--bg`, `--text`, `--accent`, `--human`, …) defined in
`site/template.html` — never brand hex values directly. The light token block exists twice (auto + forced); keep both
copies identical (the build workflow checks this).

Light-mode colour roles (contrast on `#F4F8FD`):
| Role | Light value | Why |
| --- | --- | --- |
| Text / headings | `#1C2B44` / Midnight | 13.3:1 / 17.3:1 |
| Secondary text | `#4A5D78` | Slate Blue fails on light (2.4:1) |
| Links, labels, metrics | Cobalt `#1747B8` | Sky Glow fails on light (1.8:1) |
| "Human review" text/icon | `#8A5400` | Signal Amber fails as text on light (1.8:1) |
| Headline accent ("agents.") | Volt Blue | large text only (3.6:1) |
| Buttons | Volt / Amber fills with Midnight text | 4.8:1 / 10.4:1 |
| Logo | Midnight S + Volt dots, no glow | brand "light background" variant |

## File structure

```
CLAUDE.md                this file
.env / .env.example      private values (gitignored) / committed template
requirements.txt         Python deps for tools/ (installed into .venv/)
content/
  INFO_NEEDED.md         open questions for Shah — check before writing new claims (LOCAL ONLY, gitignored)
  resume/                resume PDFs; the newest file is the source of truth (LOCAL ONLY, gitignored)
  site.json              all site copy and numbers
site/template.html       page template
tools/                   extract_resume.py, build_site.py
workflows/               SOPs (see table above)
docs/                    GENERATED website — published by GitHub Pages
brand_assets/            approved logo, guidelines, banner, hero mockup (read-only; LOCAL ONLY, gitignored)
.tmp/                    disposable intermediates (resume text, previews)
```

## Status / decisions log

- 2026-10-14 — Project started. Design = SHAH brand (not the InstaLanding editorial style). Hosting = GitHub Pages from `main:/docs`. Extras wanted: Formspree contact form, low-cost custom domain (Shah buys it). No photo; logo mark instead. Resume download offered without the blank cover page.
- Case studies 01–04 come from the resume. A past AI newsletter pipeline may become case study 05 if Shah confirms (see INFO_NEEDED.md).
- 2026-10-14 — First build done and verified (desktop + 375px mobile, no console errors, no overflow). Contact form runs in `mailto` mode until `PUBLIC_FORMSPREE_ID` is set. Not yet pushed — waiting on GitHub username.
- 2026-10-14 — Added light theme (auto from system setting + nav toggle) for visitors who find dark pages hard to read. Contrast audit: 0 failures in either theme across 187 text elements.
- 2026-10-14 — Git set up: repo-local identity from `.env` (`GIT_NAME`/`GIT_EMAIL`, a GitHub noreply address; global config untouched). GitHub user `shahariar-shadab`; target repo `shahariar-shadab.github.io` (site URL https://shahariar-shadab.github.io/). The whole repo is public, so personal notes stay out: `content/INFO_NEEDED.md` is gitignored.
- 2026-10-14 — Repo kept lean at Shah's request: `brand_assets/` and the source resume PDFs are gitignored (local only). The committed site uses the generated `docs/og.png` and `docs/resume.pdf`, so a fresh clone can't rebuild those two without the local files — that's intended.
- 2026-10-14 — **LIVE at https://shahariar-shadab.github.io/** (GitHub Pages, `main` → `/docs`; went live ~20s after saving). Shah pushes from VS Code (Source Control → Sync/Publish, GitHub browser sign-in); no credentials are stored for the CLI. Live checks passed: desktop + mobile, dark + light (auto), resume/og/favicon 200, no console errors.
- Shah has public GitHub repos `Tableau-Data-Analytics-Projects` and `MySQL-Data-Analytics-Projects` — candidates to link from case studies / a projects section (ask first).
- Known: the resume PDF shows a placeholder phone `0000000`; the downloadable `docs/resume.pdf` inherits it until Shah exports a fixed resume.

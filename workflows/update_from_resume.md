# Workflow: update the site from a new resume

**Objective:** when Shah updates the resume, bring the site's content in line with it, without inventing anything.

## Inputs
- A new PDF dropped into `content/resume/`. The newest file by modified time wins. Older versions can stay, or be moved out if Shah prefers.
- The current `content/site.json`.
- `content/INFO_NEEDED.md`, for confirmed extra details.

## Steps
1. Extract the text with `.venv/bin/python tools/extract_resume.py`, which writes `.tmp/resume.txt` and reports which cover pages it will drop.
2. Diff the content. Compare `.tmp/resume.txt` with `content/site.json` and list for Shah:
   - new or ended roles and changed dates
   - new, changed or removed metrics
   - new skills and certifications
   - a changed headline, summary or contact details
3. Propose the edits to `site.json` in chat, grouped by section, and wait for a yes on anything that changes a claim or a number.
4. Apply the approved edits to `content/site.json`. Keep the case-study structure (problem / approach / validation / result). If a metric disappeared from the resume, remove it from the site as well.
5. Rebuild and check, following `workflows/build_portfolio.md`. The new `docs/resume.pdf` comes from the new file automatically.
6. Commit with a message like `Update content from resume (<month year>)`. Push only when Shah says so.
7. Log the update in `CLAUDE.md` → *Status / decisions log*.

## Rules
- Honesty rule (see `CLAUDE.md`): every number on the site must be on the resume or confirmed by Shah.
- Contact details on the site come from `.env` (`PUBLIC_*`), not from the resume text. If the resume's email or LinkedIn changed, update `.env`.
- If the resume shows a placeholder phone such as `0000000`, mention it to Shah. The site never shows a phone number, but the downloadable PDF would.

## Edge cases / learnings
- A page counts as a cover page when it has fewer than 200 characters of text (`COVER_PAGE_MAX_CHARS` in `extract_resume.py`). A real one-page resume is never dropped. If every page is short, all of them are kept.
- Some PDF exports run words together (e.g. "ATS-OptimizedResume"). Read the extracted text with that in mind, and check against the PDF itself when something looks off.

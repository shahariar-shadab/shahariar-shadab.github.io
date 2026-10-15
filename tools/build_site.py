"""Build the portfolio into docs/ (served by GitHub Pages from main:/docs).

Inputs
  content/site.json      all copy and numbers
  site/template.html     layout, styles, scripts ({{placeholders}})
  .env                   ONLY keys starting with PUBLIC_ are read — they become public on the site
  content/resume/*.pdf   newest file → docs/resume.pdf with cover pages removed
  brand_assets/LinkedIn banner.png → docs/og.png (social preview, via macOS `sips`)

Outputs  docs/index.html, docs/resume.pdf, docs/favicon.svg, docs/og.png, docs/.nojekyll, docs/CNAME (if domain)

Usage:  .venv/bin/python tools/build_site.py
"""
from datetime import date
from html import escape
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys

from pypdf import PdfReader, PdfWriter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_resume import content_pages, newest_resume  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BANNER = ROOT / "brand_assets" / "LinkedIn banner.png"

# ---------------------------------------------------------------- icons
# 24px grid, 1.75px rounded stroke (brand iconography). Colour comes from CSS currentColor.
ICON_PATHS = {
    "bolt": '<path d="M13 2.5 4.5 13.5h6.5l-1 8 8.5-11h-6.5l1-8z"/>',
    "chart": '<path d="M4 20h16M7 16.5v-5M12 16.5v-9M17 16.5V10"/>',
    "shield": '<path d="M12 3 5 5.8v5.4c0 4.4 2.9 8.3 7 9.8 4.1-1.5 7-5.4 7-9.8V5.8L12 3z"/>',
    "layers": '<path d="m12 3 9 4.5-9 4.5-9-4.5L12 3z"/><path d="m3 12 9 4.5 9-4.5"/><path d="m3 16.5 9 4.5 9-4.5"/>',
    "chat": '<path d="M5 4.5h14a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H10l-5 4v-4.5A1.5 1.5 0 0 1 3.5 15V6A1.5 1.5 0 0 1 5 4.5z"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.4-4.4"/>',
    "download": '<path d="M12 4v11M7 10.5l5 5 5-5M5 20h14"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "mail": '<rect x="3.5" y="5.5" width="17" height="13" rx="2"/><path d="m4 7 8 6 8-6"/>',
    "link": '<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/>',
    "code": '<path d="m8.5 8-4 4 4 4M15.5 8l4 4-4 4"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "moon": '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
}


def icon(name: str, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON_PATHS[name]}</svg>')


# The S-mark, recreated from brand_assets/logo.png: rounded stroke + two end dots.
# Colours come from CSS (.logo-s / .logo-dot → theme tokens): white + Sky Glow on dark,
# Midnight + Volt Blue on light (the brand's "light background" variant). Attributes are the dark fallback.
S_PATH = "M30 8H16a8 8 0 0 0 0 16h8a8 8 0 0 1 0 16H10"
LOGO_SVG = (
    '<svg viewBox="2 1 36 46" aria-hidden="true">'
    f'<path class="logo-s" d="{S_PATH}" fill="none" stroke="#fff" stroke-width="7.5" stroke-linejoin="round"/>'
    '<circle class="logo-dot" cx="30" cy="8" r="5.2" fill="#7DCBFF"/>'
    '<circle class="logo-dot" cx="10" cy="40" r="5.2" fill="#7DCBFF"/></svg>'
)
FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
    '<rect width="48" height="48" rx="11" fill="#071426"/>'
    f'<g transform="translate(4 0.5)"><path d="{S_PATH}" fill="none" stroke="#fff" stroke-width="7.5" stroke-linejoin="round"/>'
    '<circle cx="30" cy="8" r="5.2" fill="#7DCBFF"/><circle cx="10" cy="40" r="5.2" fill="#7DCBFF"/></g></svg>\n'
)


# ---------------------------------------------------------------- inputs
def read_public_env() -> dict:
    """Read PUBLIC_* keys from .env. Anything else in .env is ignored on purpose."""
    env = {}
    path = ROOT / ".env"
    if not path.exists():
        print("note: no .env found — building with defaults (copy .env.example to .env)")
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("PUBLIC_"):
            env[key] = value.strip().strip('"').strip("'")
    return env


def e(text) -> str:
    return escape(str(text), quote=True)


# ---------------------------------------------------------------- fragments
def pipeline_steps(steps) -> str:
    out = []
    for i, s in enumerate(steps, 1):
        cls = ' class="is-accent"' if s.get("accent") else ""
        out.append(
            f'          <li{cls}><span class="dot" aria-hidden="true"></span><div>'
            f'<p class="step__label">{i:02d} · {e(s["label"])}</p>'
            f'<p class="step__text">{e(s["text"])}</p></div></li>')
    return "\n".join(out)


def impact(items) -> str:
    return "\n".join(
        f'        <li class="rv"><p class="value">{e(i["value"])}</p><p class="label">{e(i["label"])}</p></li>'
        for i in items)


def tags(items) -> str:
    return '<ul class="tags">' + "".join(f"<li>{e(t)}</li>" for t in items) + "</ul>"


def case_studies(cases) -> str:
    out = []
    for n, c in enumerate(cases, 1):
        out.append(f"""        <article class="case rv">
          <p class="case__kicker">Case study {n:02d} <span>· {e(c["org"])}</span></p>
          <h3>{e(c["title"])}</h3>
          <p class="case__metric">{e(c["metric"])}</p>
          <p class="case__summary">{e(c["summary"])}</p>
          {tags(c["tools"])}
          <details>
            <summary>{icon("plus")}Read the case study</summary>
            <dl>
              <div><dt>Problem</dt><dd>{e(c["problem"])}</dd></div>
              <div><dt>Approach</dt><dd>{e(c["approach"])}</dd></div>
              <div><dt>How I checked it</dt><dd>{e(c["validation"])}</dd></div>
              <div><dt>Result</dt><dd class="result">{e(c["result"])}</dd></div>
            </dl>
          </details>
        </article>""")
    return "\n".join(out)


def pillars(items) -> str:
    out = []
    for p in items:
        cls = "pillar rv is-accent" if p.get("accent") else "pillar rv"
        out.append(f'        <article class="{cls}"><div class="icon-tile">{icon(p["icon"])}</div>'
                   f'<h3>{e(p["title"])}</h3><p>{e(p["text"])}</p></article>')
    return "\n".join(out)


def experience(items) -> str:
    out = []
    for x in items:
        points = "".join(f"<li>{e(p)}</li>" for p in x["points"])
        out.append(f'        <li class="rv"><p class="dates">{e(x["dates"])}</p><div>'
                   f'<h3>{e(x["org"])}</h3><p class="role">{e(x["role"])}</p><ul>{points}</ul></div></li>')
    return "\n".join(out)


def skills(groups) -> str:
    return "\n".join(
        f'        <article class="skill rv"><div class="skill__head"><div class="icon-tile">{icon(g["icon"])}</div>'
        f'<h3>{e(g["group"])}</h3></div>{tags(g["items"])}</article>'
        for g in groups)


def education(items) -> str:
    return "\n".join(
        f'            <li><strong>{e(x["school"])}</strong><span>{e(x["degree"])} · {e(x["dates"])}</span></li>'
        for x in items)


def certifications(items) -> str:
    out = []
    for c in items:
        meta = " · ".join(v for v in (c["issuer"], c.get("year", "")) if v)
        out.append(f'            <li><strong>{e(c["name"])}</strong><span>{e(meta)}</span></li>')
    return "\n".join(out)


def contact_links(env: dict) -> str:
    links = []
    if env.get("PUBLIC_EMAIL"):
        links.append((f'mailto:{env["PUBLIC_EMAIL"]}', "mail", env["PUBLIC_EMAIL"], False))
    if env.get("PUBLIC_LINKEDIN"):
        shown = re.sub(r"^https?://(www\.)?", "", env["PUBLIC_LINKEDIN"]).rstrip("/")
        links.append((env["PUBLIC_LINKEDIN"], "link", shown, True))
    if env.get("PUBLIC_GITHUB_USERNAME"):
        u = env["PUBLIC_GITHUB_USERNAME"]
        links.append((f"https://github.com/{u}", "code", f"github.com/{u}", True))
    links.append(("resume.pdf", "download", "Download resume (PDF)", False))
    out = []
    for href, ic, label, external in links:
        ext = ' target="_blank" rel="noopener"' if external else ""
        dl = " download" if href == "resume.pdf" else ""
        out.append(f'            <a href="{e(href)}"{ext}{dl}>{icon(ic)}{e(label)}</a>')
    return "\n".join(out)


# ---------------------------------------------------------------- assets
def build_resume() -> None:
    src = newest_resume()
    reader = PdfReader(src)
    keep = content_pages(reader)
    writer = PdfWriter()
    for i in keep:
        writer.add_page(reader.pages[i])
    writer.add_metadata({"/Title": "Shahariar Shadab — Resume", "/Author": "Shahariar Shadab"})
    with (DOCS / "resume.pdf").open("wb") as f:
        writer.write(f)
    print(f"resume.pdf  ← {src.name} (kept pages {[i + 1 for i in keep]} of {len(reader.pages)})")


def build_og_image() -> None:
    """1200x630 social preview cropped from the LinkedIn banner (macOS sips). Skipped if unavailable."""
    out = DOCS / "og.png"
    if not BANNER.exists() or not shutil.which("sips"):
        print("og.png      skipped (no banner or no sips)")
        return
    # Banner is 3168x792; take a 1508x792 window around the headline (≈1.9:1), then scale to 1200x630.
    tmp = ROOT / ".tmp" / "og_crop.png"
    tmp.parent.mkdir(exist_ok=True)
    shutil.copy(BANNER, tmp)
    run = lambda *a: subprocess.run(["sips", *a, str(tmp)], check=True, capture_output=True)
    run("--cropToHeightWidth", "792", "1508", "--cropOffset", "0", "1000")
    run("--resampleHeightWidth", "630", "1200")
    shutil.copy(tmp, out)
    print("og.png      ← LinkedIn banner (1200x630)")


# ---------------------------------------------------------------- main
def main() -> None:
    site = json.loads((ROOT / "content" / "site.json").read_text())
    env = read_public_env()
    template = (ROOT / "site" / "template.html").read_text()
    DOCS.mkdir(exist_ok=True)

    domain = env.get("PUBLIC_DOMAIN", "")
    user = env.get("PUBLIC_GITHUB_USERNAME", "")
    base = f"https://{domain}/" if domain else (f"https://{user}.github.io/" if user else "")
    email = env.get("PUBLIC_EMAIL", "")
    formspree = env.get("PUBLIC_FORMSPREE_ID", "")

    m, h, c = site["meta"], site["hero"], site["contact"]
    values = {
        "title": e(m["title"]),
        "description": e(m["description"]),
        "name": e(m["name"]),
        "canonical_tag": f'<link rel="canonical" href="{e(base)}">' if base else "",
        "og_image": e(base + "og.png") if base else "og.png",
        "logo_svg": LOGO_SVG,
        "icon_download": icon("download"),
        "icon_sun": icon("sun", "i-sun"),
        "icon_moon": icon("moon", "i-moon"),
        "hero_eyebrow": e(h["eyebrow"]),
        "hero_headline_lead": e(h["headline_lead"]),
        "hero_headline_accent": e(h["headline_accent"]),
        "hero_intro": e(h["intro"]),
        "hero_status": e(h["status"]),
        "pipeline_caption": e(site["pipeline"]["caption"]),
        "pipeline_steps": pipeline_steps(site["pipeline"]["steps"]),
        "impact": impact(site["impact"]),
        "case_studies": case_studies(site["case_studies"]),
        "case_study_note": e(site["case_study_note"]),
        "pillars": pillars(site["pillars"]),
        "experience": experience(site["experience"]),
        "skills": skills(site["skills"]),
        "education": education(site["education"]),
        "certifications": certifications(site["certifications"]),
        "contact_heading": e(c["heading"]),
        "contact_text": e(c["text"]),
        "contact_links": contact_links(env),
        "form_action": e(f"https://formspree.io/f/{formspree}" if formspree else f"mailto:{email}"),
        "form_mode": "formspree" if formspree else "mailto",
        "email": e(email),
        "year": str(date.today().year),
    }

    def fill(match):
        key = match.group(1)
        if key not in values:
            sys.exit(f"template placeholder {{{{{key}}}}} has no value")
        return values[key]

    html = re.sub(r"\{\{(\w+)\}\}", fill, template)
    (DOCS / "index.html").write_text(html)
    print(f"index.html  ({len(html) // 1024} KB)")

    (DOCS / "favicon.svg").write_text(FAVICON_SVG)
    (DOCS / ".nojekyll").write_text("")
    cname = DOCS / "CNAME"
    if domain:
        cname.write_text(domain + "\n")
        print(f"CNAME       {domain}")
    elif cname.exists():
        cname.unlink()

    build_resume()
    build_og_image()
    print(f"\nBuilt → {DOCS.relative_to(ROOT)}/  "
          f"(form: {values['form_mode']}, url: {base or 'not set — add PUBLIC_GITHUB_USERNAME or PUBLIC_DOMAIN'})")


if __name__ == "__main__":
    main()

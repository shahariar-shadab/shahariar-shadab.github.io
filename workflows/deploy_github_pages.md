# Workflow: publish to GitHub Pages (+ custom domain)

**Objective:** put the site online at a stable URL to use on the resume and LinkedIn.
**Ask Shah before every push.** Pushing publishes everything in `docs/`.

## One-time setup
1. **Repository name**
   - `<username>.github.io` (recommended): the site lives at `https://<username>.github.io/`, the cleanest URL.
   - Any other name (e.g. `portfolio`): the site lives at `https://<username>.github.io/portfolio/`. That works too, but the canonical and OG URLs in `build_site.py` assume the root, so set `PUBLIC_DOMAIN` or adjust them.
2. Shah creates the empty repository on github.com: **New repository**, public, no README.
3. Shah fills in `PUBLIC_GITHUB_USERNAME`, `GIT_NAME` and `GIT_EMAIL` in `.env` (section 1). Then:
   - Set the commit identity **for this repo only**, never globally: `git config user.name "$GIT_NAME"` and `git config user.email "$GIT_EMAIL"`, with the values read from `.env`. Don't print the email in chat.
   - Rebuild (`tools/build_site.py`) so the canonical URL and the OG image URL use the real address.
4. Connect and push:
   ```bash
   git remote add origin https://github.com/<username>/<repo>.git
   git branch -M main
   git push -u origin main
   ```
   Without the GitHub CLI, the first push asks Shah to sign in through the browser (Git Credential Manager) or with a personal access token. Shah enters the credentials; Claude never does. VS Code's Source Control panel → **Publish Branch** is an easier alternative.
5. On GitHub: repo **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs` → Save**.
6. Wait 1–2 minutes, open the URL, and run the checks from `build_portfolio.md` against the live site.

## Custom domain (after Shah buys one)
1. Set `PUBLIC_DOMAIN=yourdomain.com` in `.env`, rebuild (this writes `docs/CNAME`), commit and push.
2. At the registrar's DNS settings:
   - Four `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - (optional IPv6) `AAAA` records for `@` → `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`
   - `CNAME` for `www` → `<username>.github.io`
   - On Cloudflare, set these records to **DNS only** (grey cloud) until GitHub has issued the certificate.
3. GitHub **Settings → Pages → Custom domain** shows the domain from `CNAME`. Once the DNS check passes, tick **Enforce HTTPS**. The certificate can take up to about an hour.
4. Recommended: **Settings → Pages → Verify domain** (add the TXT record GitHub shows), which stops others from claiming the domain.
5. Security hardening (Cloudflare, all records DNS only):
   - **DNSSEC:** DNS → Settings → Enable DNSSEC. Cloudflare Registrar adds the DS record automatically.
   - **No-email domain protection:** TXT `@` = `v=spf1 -all`, and TXT `_dmarc` = `v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s`. Remove these if email is ever set up on the domain.
6. Verify with these checks:
   - `dig +short <domain> A @1.1.1.1` returns the 4 GitHub IPs. Cloudflare IPs (104.x / 172.x) mean the proxy is still orange.
   - `curl -sI https://<domain>` returns 200.
   - `www` and `<user>.github.io` return a 301 to the domain.
   - `openssl s_client -connect <domain>:443 -servername <domain>` shows a Let's Encrypt certificate for the apex and `www`.
   - `dig +short <domain> DS` shows the DNSSEC record, and the SPF/DMARC TXT records resolve.

## Every later update
Build → check locally → commit → (Shah says go) → `git push`. Pages redeploys automatically in about a minute.

## Edge cases / learnings
- Cloudflare creates every new DNS record as **proxied (orange cloud)** by default. Switch each one to **DNS only** before saving, or GitHub can't see the records and won't issue the certificate.
- With the records grey, the Let's Encrypt certificate (apex + `www`) arrived quickly (2026-10-16). Until **Enforce HTTPS** is ticked, `http://` serves the page without redirecting, and the github.io link forwards to `http://` rather than `https://`.
- `docs/.nojekyll` is written by the build so GitHub serves files as-is (no Jekyll processing).
- If Pages shows a 404 right after enabling it, wait a couple of minutes. Then check that the branch and folder are `main` and `/docs`.
- Don't commit `.env`. `.gitignore` covers it; confirm with `git check-ignore .env`.

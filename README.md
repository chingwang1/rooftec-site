# Rooftec local SEO site

Static multi-page roofing site built for **local rankings** (Rank & Rent / service-area SEO style).

## Host on GitHub Pages (free)

This folder is already a **git** repo with an initial commit on `main`.

### 1. Log in to GitHub (one time)

In PowerShell:

```powershell
gh auth login
```

Choose: **GitHub.com** → **HTTPS** → **Login with a web browser**.

### 2. Create the repo and push

```powershell
cd $env:USERPROFILE\Desktop\rooftec-site
gh repo create rooftec-site --public --source=. --remote=origin --push
```

If the repo already exists empty on GitHub:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/rooftec-site.git
git push -u origin main
```

### 3. Turn on GitHub Pages

**Browser:** repo → **Settings** → **Pages** → Deploy from branch → **`main`** / **`/` (root)** → Save.

**Or CLI** (after push):

```powershell
gh api -X POST repos/:owner/rooftec-site/pages -f build_type=legacy -f source[branch]=main -f source[path]=/
```

### 4. Live URL

```
https://YOUR_GITHUB_USERNAME.github.io/rooftec-site/
```

Relative links work with project Pages. After you know the real URL, update `canonical` tags and `sitemap.xml` / `robots.txt` to match.

### Update later

```powershell
cd $env:USERPROFILE\Desktop\rooftec-site
git add .
git commit -m "Update site content"
git push
```

---

## Open locally

Open `index.html` in your browser, or:

```
cd Desktop\rooftec-site
npx --yes serve .
```

## Structure (SEO)

| Page type | Purpose |
|-----------|---------|
| Home | Primary geo + brand terms (Colorbond roofing SEQ) |
| **One service per page** | Service + region intent (repairs, replacement, gutters…) |
| **Area pages** | City modifiers (Brisbane, Sunshine Coast, GC/Tweed) |
| About / Contact | Trust + conversions + NAP |

Each service page includes: who needs it, **common examples**, process, cost ranges, FAQs, internal links.

## Before go-live / custom domain

1. Replace phone `1300 000 000`, email, domain `rooftec.example`
2. Add QBCC licence, ABN, real address if public
3. Point canonical URLs + sitemap to your real domain
4. Optional: GitHub Pages → **Custom domain** (e.g. `www.yourroofing.com.au`)
5. Create Google Business Profile matching NAP
6. Submit sitemap in Search Console

## Video themes applied

From Rank & Rent / local SEO practice:

- Service silos (one main keyword focus per URL)
- Location in titles & H1s
- Area pages for map-pack style relevance
- Internal links service ↔ suburb pages
- Schema on home, services, areas
- FAQ blocks for long-tail queries

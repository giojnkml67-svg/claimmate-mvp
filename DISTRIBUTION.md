# VA ClaimMate — Distribution & Growth Playbook

This document is a step-by-step guide to getting VA ClaimMate in front of the veterans
who need it. Work through the sections in order — hosting first, then organic community,
then SEO. Do not skip to paid advertising until the app is stable and you have at least
20–30 real users giving you feedback.

---

## Step 1 — Hosting (do this first)

### Option A: Railway (Recommended — easiest, free tier available)

1. Push the repo to GitHub (main branch).
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub Repo.
3. Select `claimmate-mvp`.
4. Add environment variables in the Railway dashboard:
   - `GOOGLE_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY` (anon/publishable key only — never service_role)
5. Railway auto-detects the `Dockerfile` and deploys.
6. Under Settings → Domains: add a custom domain (e.g. `vaclaimmate.com`).
7. Copy the public URL and update every `YOUR-APP-URL-HERE` in `docs/index.html`.

### Option B: Render (also free tier, Docker support)

1. [render.com](https://render.com) → New → Web Service → Connect GitHub repo.
2. Runtime: Docker. Set the same three environment variables above.
3. Free tier sleeps after 15 minutes of inactivity — upgrade to Starter ($7/mo) for
   always-on if you expect real traffic.

### Option C: Fly.io (best for global latency)

```bash
fly launch                # follow prompts, choose a region near your users
fly secrets set GOOGLE_API_KEY=... SUPABASE_URL=... SUPABASE_KEY=...
fly deploy
fly domains add vaclaimmate.com
```

### Option D: Streamlit Community Cloud (zero-cost, simplest)

1. [share.streamlit.io](https://share.streamlit.io) → New App → GitHub repo.
2. Set secrets in the "Secrets" section of the app settings (TOML format):
   ```toml
   GOOGLE_API_KEY = "..."
   SUPABASE_URL   = "..."
   SUPABASE_KEY   = "..."
   ```
3. Custom domains require a paid Streamlit for Teams plan.
4. Free tier limits: 1 app per account, sleeps after inactivity.

### Domain & SSL

- Register a domain at Namecheap or Google Domains (~$12/yr).
  Suggested names: `vaclaimmate.com`, `claimmate.io`, `veclaimhelp.com`
- All platforms above provide free TLS/SSL automatically.

---

## Step 2 — GitHub Pages landing page

After merging to `main`, GitHub Actions will deploy `docs/` to GitHub Pages automatically.

**Enable it once:**
1. Repo Settings → Pages → Source: **GitHub Actions**.
2. The `pages.yml` workflow handles the rest on every push.
3. Update `YOUR-DOMAIN-HERE` in `docs/index.html` to your actual domain.
4. Point your domain's DNS CNAME record to `<username>.github.io`.

The landing page ranks in Google. The app URL is a separate service.

---

## Step 3 — Reddit (highest ROI, free, immediate)

Reddit has hundreds of thousands of veterans actively asking VA claims questions.

### Subreddits to target

| Subreddit | Members | Best content type |
|-----------|---------|-------------------|
| r/VeteransBenefits | 130k+ | Tool share, answering questions |
| r/Veterans | 500k+ | General veteran interest, tool share |
| r/Military | 500k+ | Broader audience, lighter touch |
| r/PTSD | 200k+ | PTSD claim specifics |
| r/ArmyVeterans, r/NavyVets, r/AirForce, r/USMC | 50–150k each | Branch-specific |
| r/disability | 100k+ | General disability claims overlap |

### How to post without getting flagged as spam

**Don't** post "Check out my tool!" — mods will remove it.

**Do** this instead:

1. **Answer 5–10 existing questions in the subreddit first** (using your app to research
   accurate answers). Build credibility as a helpful member.

2. **Post a value-first thread:**
   ```
   Title: "38 CFR rating criteria for [PTSD / sleep apnea / lumbar strain] — exactly what
   symptoms earn each percentage (compiled for the community)"
   
   Body: [Paste the actual 38 CFR criteria from VA ClaimMate's database in plain text]
   
   Last paragraph: "I built a free tool that shows these criteria for your specific
   conditions automatically and also helps with the C&P exam prep, combined rating
   calculator, and statement builder. Happy to share if it's useful."
   ```

3. **Respond to questions** like "what does my C&P exam look for?" or "how is the
   combined rating calculated?" with real, thorough answers, then mention the tool
   naturally at the end.

4. **Post timing:** Tuesday–Thursday, 8–10 AM ET (peak US veteran traffic).

### Sample thread titles that perform well

- "The VA combined rating formula explained (with a free calculator)"  
- "38 CFR criteria for PTSD ratings — what the examiner is actually looking for"
- "Secondary conditions veterans miss: diabetes → neuropathy → ED (all separately ratable)"
- "C&P exam prep for sleep apnea — exactly what you need to know"
- "Presumptive conditions by service era — no nexus letter needed for these"

---

## Step 4 — VSO Partnerships

Veterans Service Organizations are the biggest referral channel if you can get in.

### Organizations to contact

| Organization | Website | Contact approach |
|---|---|---|
| DAV (Disabled American Veterans) | dav.org | Email national communications |
| VFW (Veterans of Foreign Wars) | vfw.org | Chapter service officers |
| AMVETS | amvets.org | National HQ communications |
| American Legion | legion.org | Email adjutant |
| Iraq and Afghanistan Veterans (IAVA) | iava.org | Very tech-friendly, email directly |
| Student Veterans of America | studentveterans.org | Good for younger vets |
| Veterans of Modern Warfare (VMW) | vmwusa.org | Grassroots, approachable |

### Email template to VSO contacts

```
Subject: Free VA claim preparation tool — would like your feedback

Hi [Name],

I'm a veteran who built VA ClaimMate (vaclaimmate.com), a free tool that helps
veterans prepare stronger VA disability claims. It includes:

- 38 CFR rating criteria lookup for 16+ common conditions
- Combined-rating calculator with step-by-step breakdown
- Monthly compensation estimator (official Dec 2025 rates)
- C&P exam preparation and DBQ finder
- AI lay statement builder tuned to 38 CFR thresholds
- Presumptive condition matcher for all major eras

I'd love to get feedback from service officers and, if useful, make it available
to veterans you work with. Happy to set up a brief call or send a walkthrough.

[Your name / contact]
```

---

## Step 5 — SEO content strategy

The landing page at `docs/` targets high-intent searches. To accelerate ranking:

### Quick wins (do these in the first month)

1. **Update all `YOUR-DOMAIN-HERE` placeholders** in `docs/index.html` with the real URL.
2. **Submit to Google Search Console** — add the landing page URL and request indexing.
3. **Submit sitemap** — add `docs/sitemap.xml` (see below) and submit it.
4. **Get one backlink** — post a link on your Reddit account bio, GitHub profile,
   or LinkedIn. Backlinks from Reddit count.

### Add a sitemap

Create `docs/sitemap.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://YOUR-DOMAIN-HERE/</loc>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

### Target keywords (already in the landing page)

| Primary keyword | Monthly searches (est.) | Competition |
|---|---|---|
| VA disability claim tool | 2,400 | Low |
| VA combined rating calculator | 4,400 | Medium |
| VA disability compensation estimator | 1,600 | Low |
| 38 CFR rating criteria | 1,200 | Low |
| C&P exam preparation | 2,900 | Low |
| presumptive conditions VA | 3,600 | Low |
| VA rating for PTSD | 8,100 | Medium |
| VA rating for sleep apnea | 5,400 | Medium |

### Content ideas that rank and build trust

Each of these can be a Reddit post AND a future blog page:
- "How the VA combined rating formula actually works (with examples)"
- "Presumptive conditions by service era: complete 2025 list"
- "PTSD VA rating: what symptoms earn 30%, 50%, 70%, 100%"
- "Secondary conditions for diabetes veterans (each is separately ratable)"
- "What to say at your C&P exam: tips by condition"

---

## Step 6 — Other free distribution channels

### Facebook veteran groups
- Search "VA disability claims" on Facebook — several groups have 50k–200k members
- Same approach as Reddit: answer questions first, mention tool naturally

### LinkedIn
- Post to your network with hashtags: #veteranbenefits #VAdisability #militarytransition
- Tag VA-adjacent accounts: Hire Heroes USA, American Corporate Partners, etc.

### Twitter/X
- @VetBenefits, @IAVA, @DAVHq — mention or reply to their posts
- Hashtags: #Veterans #VADisability #VeteranBenefits #BurnPit #PACTAct

### Veteran-focused newsletters
- Task & Purpose, Military Times — both have submission forms for tools/resources
- Coffee or Die Magazine

### Google Business Profile
- Create a free Google Business Profile for the app (category: "Software Company")
- Even without a physical address, this can help local SEO

---

## Step 7 — Track what's working

Set up free Google Analytics (GA4) on the landing page:

```html
<!-- Add to <head> in docs/index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

Watch these metrics:
- **Landing page → App clicks** (primary conversion)
- **Top traffic sources** (Reddit? Google? Direct?)
- **Top landing page** by search query (Google Search Console)
- **Bounce rate** (if >80%, improve the CTA or hero copy)

---

## Disclaimer

VA ClaimMate is an educational tool, not a VSO, attorney, or legal aid service.
Never promise veterans guaranteed outcomes. All marketing copy must reflect that
this tool prepares veterans to work with accredited VSOs — it does not replace them.

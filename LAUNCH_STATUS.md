# VA ClaimMate — Launch Status

## Live URLs
- **App:** https://claimmate-mvp-working1.streamlit.app
- **Domain:** https://vaclaimmate.com (redirects to app)
- **Landing page:** https://giojnkml67-svg.github.io/claimmate-mvp (GitHub Pages)

## What's Built

### App Features
- 10-tab Streamlit app (Profile, Presumptive Conditions, Evidence Upload, Symptom Mapper,
  38 CFR Criteria & C&P Prep, Statement Builder, Rating Calculator, Saved Claims & Export,
  VA Chat, Privacy & Data)
- AI powered by Google Gemini 2.0 Flash
- Supabase auth + Row-Level Security (veterans can only see their own data)
- Password reset flow (Forgot password → email link → set new password)
- Brand logo (navy shield, gold stars + checkmark) on login, app header, landing page

### Monetization (Stripe)
- **Free tier:** All static tools + 3 free AI generations
- **Pro — $9.99/mo:** Unlimited AI, PDF export, plain-text export
- Promo code **FIRST10** — 100% off first month, limited to 10 redemptions
- Stripe Checkout with promo code field enabled

### Infrastructure
- Docker + start.sh for Railway/Render/Fly.io deployment
- GitHub Actions CI (27 tests run on every push)
- GitHub Pages auto-deploy for landing page on push to main

## Secrets Required (Streamlit Cloud → Settings → Secrets)
```toml
GOOGLE_API_KEY    = "..."   # Google Gemini API key
SUPABASE_URL      = "..."   # https://YOUR-PROJECT.supabase.co
SUPABASE_KEY      = "..."   # Anon/publishable key ONLY — never service_role
STRIPE_SECRET_KEY = "..."   # sk_live_...
STRIPE_PRICE_ID   = "price_1Tjo9MLcfshOQiisITfsEv8m"
```

## Supabase Setup Required
1. Run `schema.sql` in Supabase SQL Editor
2. Authentication → URL Configuration → add `https://claimmate-mvp-working1.streamlit.app`
   to Redirect URLs (required for password reset emails)
3. Authentication → Users → resume/unpause VA-ClaimMate project if paused

## Stripe Setup
- Product: VA Claimmate Pro — $9.99/mo
- Price ID: price_1Tjo9MLcfshOQiisITfsEv8m
- Coupon: FIRST10 (100% off once, 0/10 redeemed as of launch)

## Promotion Plan
- Facebook veteran groups: "VA Claims Insider Community", "VA Disability Help Group"
- TikTok/YouTube Shorts: combined rating math explainer → show calculator
- LinkedIn: tag DAV, IAVA, Hire Heroes USA
- Offer FIRST10 code for honest feedback from first 10 users

## Key Files
| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit app (~2700 lines) |
| `cfr_data.py` | 38 CFR Part 4 data for 16 conditions |
| `va_rates.py` | VA compensation rates (Dec 2025, 2.8% COLA) |
| `schema.sql` | Supabase table + RLS policies |
| `docs/index.html` | SEO landing page |
| `docs/styles.css` | Landing page styles |
| `docs/logo.svg` | Brand logo |
| `assets/logo.svg` | Brand logo (source) |
| `Dockerfile` + `start.sh` | Docker deployment |
| `DISTRIBUTION.md` | Full growth playbook |
| `PRIVACY.md` | Privacy policy |
| `.streamlit/config.toml` | Theme (navy/gold) |
| `.github/workflows/ci.yml` | CI — runs pytest on every push |
| `.github/workflows/pages.yml` | Auto-deploy landing page to GitHub Pages |

## Legal Note
VA ClaimMate is an educational tool. Under 38 U.S.C. § 5901 only VA-accredited
persons may charge for claims assistance. The app charges for software features
(AI generation, document export) — not claims representation. Verify with a
lawyer before scaling paid users.

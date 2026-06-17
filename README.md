# VA ClaimMate

An AI-assisted web app that helps U.S. veterans prepare stronger VA disability
claims — profile and service history, presumptive-condition matching, evidence
summaries, symptom-to-condition mapping, lay/buddy statements, a combined-rating
calculator with a **monthly compensation estimator**, a claim-readiness score,
PDF/text export, and an educational Q&A chat.

> ⚠️ VA ClaimMate is an educational tool. It is **not** affiliated with the U.S.
> Department of Veterans Affairs and does **not** provide legal advice. Always
> review your claim with a VA-accredited VSO, attorney, or claims agent before
> submitting.

## Tech stack

- **Streamlit** (UI) · **Google Gemini** (AI) · **Supabase/Postgres** (auth + storage) · **ReportLab** (PDF)

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create the database schema (required for security)**

   In your Supabase project's SQL Editor, run [`schema.sql`](schema.sql). This
   creates the `claimmate_state` table and enables **Row-Level Security** so each
   veteran can only ever access their own data.

3. **Configure secrets** in `.streamlit/secrets.toml` (never commit this file):
   ```toml
   GOOGLE_API_KEY = "your-gemini-api-key"
   SUPABASE_URL   = "https://YOUR-PROJECT.supabase.co"
   SUPABASE_KEY   = "your-supabase-ANON-key"   # anon/publishable key ONLY
   ```

   > 🔒 Use the **anon / publishable** key — never the `service_role` key, which
   > bypasses Row-Level Security and must not ship in an app.

4. **Run**
   ```bash
   streamlit run app.py
   ```

## Tests

```bash
pip install -r requirements-dev.txt
pytest                     # or: python tests/test_va_rates.py
```

## Privacy & data

See [`PRIVACY.md`](PRIVACY.md). Veterans can export or permanently delete their
data (and their account) from the in-app **Privacy & Data** tab.

## Compensation rates

Monthly payment estimates use official VA rates effective **December 1, 2025**
(2.8% COLA), kept in [`va_rates.py`](va_rates.py) for easy annual updates. Always
verify exact amounts at
[va.gov](https://www.va.gov/disability/compensation-rates/veteran-rates/).

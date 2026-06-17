# VA ClaimMate — Privacy & Data Policy

_Last updated: December 2025_

VA ClaimMate is a free, educational tool that helps veterans organize and
prepare materials for a VA disability claim. **It is not affiliated with the
U.S. Department of Veterans Affairs (VA) and does not provide legal advice.**

This document explains, in plain language, what the app stores and how your
information is protected. It is a starting point — have it reviewed by a
qualified attorney before you rely on it publicly.

## What we store

When you create an account and use the app, we store the information you
enter so you can return to it later, including:

- Your account email (handled by our authentication provider, Supabase).
- Your service profile (name, branch, service dates, era, VA file number).
- The conditions you are claiming and any notes you add.
- Text extracted from medical or service documents you upload, plus your
  notes about them.
- AI-generated drafts you create (statements, summaries) and your rating
  inputs.

**Uploaded files themselves are not stored.** The app extracts text in
memory to help you build a summary; the original file is not saved to our
servers.

## Where it is stored and who can see it

- Your data is stored in a Supabase (PostgreSQL) database.
- **Row-Level Security is enforced at the database level** (see
  `schema.sql`). Each account can only ever read or write its own row, even
  in the event of an application bug.
- We do not sell your data or use it for advertising.

## AI processing

Features like the symptom mapper, evidence summary, statement builder, and
chat send the relevant text you provide to a third-party AI provider
(Google Gemini) to generate suggestions. **AI output can be incomplete or
incorrect** — always verify it with a VA-accredited Veterans Service
Organization (VSO), attorney, or claims agent, and against official sources
like [VA.gov](https://www.va.gov) and 38 CFR.

Do not paste information you are not comfortable sending to an AI service.

## Your control over your data

- **Export:** download your full packet as a PDF or text file at any time
  (Tab 7).
- **Delete your data:** the "Privacy & Data" tab lets you permanently delete
  everything stored for your account.
- **Delete your account:** you can delete your entire account (login + data)
  from the same tab if the `delete_my_account` function in `schema.sql` is
  installed.

## Security practices

- Use the Supabase **anon/publishable** key in the app — never the
  `service_role` key, which bypasses Row-Level Security.
- All traffic to Supabase and the AI provider is over HTTPS.
- Keep API keys in Streamlit secrets, never in source control.

## Contact

Questions about your data? Open an issue in the project repository or contact
the maintainer listed there.

---

_This tool helps you prepare; it does not submit claims and does not
guarantee any outcome. Always review your claim with a VA-accredited VSO,
attorney, or claims agent before submitting._

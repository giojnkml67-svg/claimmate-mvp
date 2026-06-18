#!/bin/sh
# Inject runtime secrets from environment variables into Streamlit secrets.toml.
# Deploy platforms (Railway, Render, Fly.io, Cloud Run) pass secrets as env vars;
# this translates them to the format Streamlit expects at startup.

set -e

mkdir -p .streamlit

cat > .streamlit/secrets.toml << EOF
GOOGLE_API_KEY       = "${GOOGLE_API_KEY:-}"
SUPABASE_URL         = "${SUPABASE_URL:-}"
SUPABASE_KEY         = "${SUPABASE_KEY:-}"
STRIPE_SECRET_KEY    = "${STRIPE_SECRET_KEY:-}"
STRIPE_PRICE_ID      = "${STRIPE_PRICE_ID:-}"
EOF

exec streamlit run app.py \
    --server.port="${PORT:-8501}" \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false

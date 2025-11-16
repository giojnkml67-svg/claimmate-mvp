import os
import io
import json
from datetime import datetime

import streamlit as st
from openai import OpenAI
from supabase import create_client
from PyPDF2 import PdfReader

from docx import Document

# ---------------------------------------------------------
# Streamlit setup
# ---------------------------------------------------------
st.set_page_config(page_title="VA ClaimMate MVP", layout="wide")

# ---------------------------------------------------------
# OpenAI client
# ---------------------------------------------------------
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------------------------
# Supabase client (new official SDK)
# ---------------------------------------------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase configuration missing in Streamlit secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

STATE_TABLE = "claimmate_state"


# ---------------------------------------------------------
# Default state for new users
# ---------------------------------------------------------
def default_state():
    return {
        "veteran_profile": {},
        "issues": [],
        "symptom_note": "",
        "symptom_mappings": [],
        "documents": [],
        "evidence_summary": "",
        "claims": [],
        "notes": "",
    }


# ---------------------------------------------------------
# Supabase authentication
# ---------------------------------------------------------
def sign_up(email, password):
    try:
        return supabase.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def sign_in(email, password):
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass
    st.session_state.clear()
    st.experimental_rerun()


def current_user():
    return st.session_state.get("user")


# ---------------------------------------------------------
# Load and save per-user JSON state
# ---------------------------------------------------------
def load_state(user_id):
    try:
        res = supabase.table(STATE_TABLE).select("state").eq("user_id", user_id).execute()
        rows = res.data

        if rows:
            state = rows[0]["state"]
        else:
            state = default_state()
            supabase.table(STATE_TABLE).insert({"user_id": user_id, "state": state}).execute()

        base = default_state()
        for key in base:
            if key not in state:
                state[key] = base[key]

        return state

    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return default_state()


def save_state(user_id, state):
    try:
        supabase.table(STATE_TABLE).upsert(
            {"user_id": user_id, "state": state},
            on_conflict="user_id",
        ).execute()
    except Exception as e:
        st.error(f"Error saving data: {e}")


def get_state():
    user = current_user()
    if not user:
        return None

    if "app_state" not in st.session_state:
        st.session_state.app_state = load_state(user["id"])

    return st.session_state.app_state


def persist_state():
    user = current_user()
    if user and "app_state" in st.session_state:
        save_state(user["id"], st.session_state.app_state)


# ---------------------------------------------------------
# File extraction
# ---------------------------------------------------------
def extract_text(content, mime, name):
    text = ""

    if mime == "application/pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            return "\n".join(pages)
        except:
            return ""

    if mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except:
            return ""

    try:
        return content.decode("utf-8", errors="ignore")
    except:
        return ""


# ---------------------------------------------------------
# GPT helper
# ---------------------------------------------------------
def ask_gpt(system_prompt, user_prompt, model="gpt-4o-mini", temp=0.25):
    try:
        result = client.chat.completions.create(
            model=model,
            temperature=temp,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return result.choices[0].message.content
    except Exception as e:
        st.error(f"Model error: {e}")
        return ""


# ---------------------------------------------------------
# Symptom mapper
# ---------------------------------------------------------
def map_symptoms(text):
    system_prompt = (
        "You support veterans building VA disability claims. "
        "Return JSON only. Format: "
        '[{"condition":"","icd10":"","body_system":"","va_rating_hint":"","rationale":""}]'
    )

    user_prompt = (
        "Symptoms from the veteran:\n"
        f"{text}\n\n"
        "Suggest diagnostic labels with ICD-10 codes, rating hints, and rationale."
    )

    raw = ask_gpt(system_prompt, user_prompt)

    try:
        parsed = json.loads(raw)
        return parsed, raw
    except:
        return [], raw


# ---------------------------------------------------------
# Build personal statement
# ---------------------------------------------------------
def build_statement(state, title, focus_conditions):
    prof = state.get("veteran_profile", {})
    issues = state.get("issues", [])
    mappings = state.get("symptom_mappings", [])
    summary = state.get("evidence_summary", "")

    selected = [
        m for m in mappings
        if m.get("condition") in focus_conditions
    ]

    sys = (
        "You write VA disability lay statements. "
        "Use first person, plain language, detailed daily impact, onsets, progression, "
        "functional loss, and how conditions relate to service. 600 to 900 words."
    )

    usr = f"""
Claim title:
{title}

Profile:
{json.dumps(prof, indent=2)}

Issues:
{json.dumps(issues, indent=2)}

Conditions:
{json.dumps(selected, indent=2)}

Evidence summary:
{summary}

Write the statement.
"""

    return ask_gpt(sys, usr, temp=0.35)


# ---------------------------------------------------------
# Chat context builder
# ---------------------------------------------------------
def chat_context(state):
    prof = state.get("veteran_profile", {})
    issues = state.get("issues", [])
    summary = state.get("evidence_summary", "")
    docs = state.get("documents", [])

    snippets = []
    for d in docs:
        t = d.get("text") or ""
        if t:
            snippets.append(f"{d['name']}:\n{t[:800]}")

    out = []

    if prof:
        out.append("Profile:\n" + json.dumps(prof, indent=2))
    if issues:
        out.append("Issues:\n" + json.dumps(issues, indent=2))
    if summary:
        out.append("Evidence summary:\n" + summary)
    if snippets:
        out.append("Record snippets:\n" + "\n\n".join(snippets))

    return "\n\n".join(out)


# ---------------------------------------------------------
# Login / Signup screen
# ---------------------------------------------------------
def auth_screen():
    st.title("VA ClaimMate MVP")
    st.write("Sign up or log in with your email and password.")

    mode = st.radio("Select mode", ["Log in", "Sign up"], horizontal=True)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if mode == "Log in":
        if st.button("Log in"):
            res = sign_in(email, password)
            if res and res.user:
                st.session_state.user = {"id": res.user.id, "email": email}
                st.experimental_rerun()

    else:
        if st.button("Sign up"):
            res = sign_up(email, password)
            if res and res.user:
                st.success("Account created. You can now log in.")
            else:
                st.error("Sign up failed.")


# ---------------------------------------------------------
# Main app UI
# ---------------------------------------------------------
def app_ui():
    state = get_state()

    st.title("VA ClaimMate MVP")

    if st.button("Logout"):
        logout()

    tabs = st.tabs([
        "Profile",
        "Upload Evidence",
        "Symptom Mapper",
        "Statement Builder",
        "Saved Claims",
        "VA Claim Chat"
    ])

    # -----------------------------------------------------
    # 1. Profile
    # -----------------------------------------------------
    with tabs[0]:
        st.subheader("Service Profile")

        prof = state["veteran_profile"]

        prof["full_name"] = st.text_input("Full name", prof.get("full_name", ""))
        prof["branch"] = st.text_input("Branch", prof.get("branch", ""))
        prof["service_dates"] = st.text_input("Service dates", prof.get("service_dates", ""))
        prof["deployment_locations"] = st.text_area("Deployments", prof.get("deployment_locations", ""))
        prof["mos_duties"] = st.text_area("Duties / MOS", prof.get("mos_duties", ""))
        prof["other_notes"] = st.text_area("Other notes", prof.get("other_notes", ""))

        state["veteran_profile"] = prof

        st.markdown("### Claimed Issues")
        raw = "\n".join([i["label"] for i in state["issues"]])
        updated = st.text_area("One issue per line", raw)

        issues = []
        for line in updated.splitlines():
            line = line.strip()
            if line:
                issues.append({"label": line})
        state["issues"] = issues

    # -----------------------------------------------------
    # 2. Upload evidence
    # -----------------------------------------------------
    with tabs[1]:
        st.subheader("Upload Evidence")

        uploads = st.file_uploader("Upload files", type=["pdf", "txt", "docx"], accept_multiple_files=True)

        if uploads:
            for file in uploads:
                content = file.getvalue()
                mime = file.type
                name = file.name
                size = len(content)

                doc_id = f"{name}:{size}"
                if doc_id in [d["id"] for d in state["documents"]]:
                    continue

                text = extract_text(content, mime, name)

                state["documents"].append({
                    "id": doc_id,
                    "name": name,
                    "mime": mime,
                    "size": size,
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "text": text,
                })

        for d in state["documents"]:
            with st.expander(f"{d['name']} ({d['mime']})"):
                st.text_area("Preview", (d["text"] or "")[:1200], height=200)

        st.markdown("### Evidence Summary")

        current = state.get("evidence_summary", "")

        if st.button("Generate summary"):
            joined = []
            for d in state["documents"]:
                if d.get("text"):
                    joined.append(d["text"])
            blob = "\n\n".join(joined)[:15000]

            if blob:
                sys = (
                    "You summarize medical records for VA disability claims. "
                    "Identify diagnoses, functional impacts, and service connections."
                )
                usr = f"Summarize these records:\n{blob}"
                summary = ask_gpt(sys, usr)
                state["evidence_summary"] = summary
                current = summary

        state["evidence_summary"] = st.text_area("Editable summary", current, height=240)

    # -----------------------------------------------------
    # 3. Symptom mapper
    # -----------------------------------------------------
    with tabs[2]:
        st.subheader("Symptom Mapper")

        note = st.text_area("Describe symptoms", state.get("symptom_note", ""), height=200)
        state["symptom_note"] = note

        if st.button("Analyze symptoms"):
            if note.strip():
                mappings, raw = map_symptoms(note)
                if mappings:
                    state["symptom_mappings"] = mappings
                else:
                    st.text(raw)

        if state["symptom_mappings"]:
            st.write("Suggested conditions:")
            st.json(state["symptom_mappings"])

    # -----------------------------------------------------
    # 4. Statement Builder
    # -----------------------------------------------------
    with tabs[3]:
        st.subheader("Statement Builder")

        mappings = state["symptom_mappings"]
        conditions = [m["condition"] for m in mappings if m.get("condition")]

        title_guess = ", ".join(conditions[:3]) if conditions else ""
        title = st.text_input("Title", title_guess)

        focus = st.multiselect("Select conditions for this statement", conditions, default=conditions)

        if st.button("Generate Statement"):
            if title.strip():
                text = build_statement(state, title, focus)
                st.session_state["latest_statement"] = text

        current = st.session_state.get("latest_statement", "")
        edited = st.text_area("Statement", current, height=250)
        st.session_state["latest_statement"] = edited

        if st.button("Save Statement"):
            if edited.strip():
                state["claims"].append({
                    "id": f"claim_{int(datetime.utcnow().timestamp())}",
                    "title": title,
                    "body": edited,
                    "created_at": datetime.utcnow().isoformat(),
                })
                st.success("Saved")

    # -----------------------------------------------------
    # 5. Saved Claims
    # -----------------------------------------------------
    with tabs[4]:
        st.subheader("Saved Claims")

        for c in state["claims"]:
            with st.expander(f"{c['title']} - {c['created_at']}"):
                st.text_area("Text", c["body"], height=200)

        all_text = []

        all_text.append("VA ClaimMate Packet\n")
        all_text.append("Generated " + datetime.utcnow().isoformat() + "\n\n")

        all_text.append("Profile:\n" + json.dumps(state["veteran_profile"], indent=2))
        all_text.append("\nIssues:\n" + json.dumps(state["issues"], indent=2))
        all_text.append("\nSummary:\n" + state.get("evidence_summary", ""))

        all_text.append("\n\nStatements:")
        for c in state["claims"]:
            all_text.append(f"\n\n---\n{c['title']}\n{c['body']}")

        packet = "\n".join(all_text)

        st.download_button(
            label="Download full claim packet",
            data=packet,
            file_name="claimmate_packet.txt",
            mime="text/plain"
        )

    # -----------------------------------------------------
    # 6. Chat
    # -----------------------------------------------------
    with tabs[5]:
        st.subheader("General VA Claim Chat")

        if "chat" not in st.session_state:
            st.session_state.chat = []

        for msg in st.session_state.chat:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_msg = st.chat_input("Ask a question")
        if user_msg:
            st.session_state.chat.append({"role": "user", "content": user_msg})

            context = chat_context(state)

            sys = (
                "You assist veterans with general VA claim guidance. "
                "No legal advice. Use provided context when helpful."
            )

            usr = f"Context:\n{context}\n\nQuestion:\n{user_msg}"

            reply = ask_gpt(sys, usr)
            st.session_state.chat.append({"role": "assistant", "content": reply})

            with st.chat_message("assistant"):
                st.write(reply)

    persist_state()


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
def main():
    if not current_user():
        auth_screen()
    else:
        app_ui()


if __name__ == "__main__":
    main()


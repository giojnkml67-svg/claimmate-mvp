import os
import io
import json
from datetime import datetime

import streamlit as st
from openai import OpenAI
from supabase import create_client
from PyPDF2 import PdfReader
from docx import Document

st.set_page_config(page_title="VA ClaimMate MVP", layout="wide")

# ------------------- OpenAI -------------------
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------- Supabase -------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase configuration missing in Streamlit secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
STATE_TABLE = "claimmate_state"


# ------------------- Default per-user state -------------------
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


# ------------------- Auth helpers -------------------
def sign_up(email, password):
    try:
        return supabase.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        st.error(f"Sign up error: {e}")
        return None


def sign_in(email, password):
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        st.error(f"Sign in error: {e}")
        return None


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.clear()
    st.rerun()


def current_user():
    return st.session_state.get("user")


# ------------------- State load/save -------------------
def load_state(user_id: str):
    try:
        res = supabase.table(STATE_TABLE).select("state").eq("user_id", user_id).execute()
        rows = res.data or []
        if rows:
            state = rows[0]["state"]
        else:
            state = default_state()
            supabase.table(STATE_TABLE).insert({"user_id": user_id, "state": state}).execute()

        base = default_state()
        for k in base:
            if k not in state:
                state[k] = base[k]
        return state
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return default_state()


def save_state(user_id: str, state: dict):
    try:
        base = default_state()
        for k in base:
            if k not in state:
                state[k] = base[k]

        supabase.table(STATE_TABLE).upsert(
            {"user_id": user_id, "state": state},
            on_conflict="user_id",
        ).execute()
    except Exception as e:
        st.error(f"Error saving user data: {e}")


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


# ------------------- File extraction -------------------
def extract_text(content: bytes, mime: str, name: str) -> str:
    if mime == "application/pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
        except Exception:
            return ""

    if mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""

    try:
        return content.decode("utf-8", errors="ignore")
    except Exception:
        return ""


# ------------------- GPT helper -------------------
def ask_gpt(system_prompt, user_prompt, model="gpt-4o-mini", temp=0.25):
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=temp,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content
    except Exception as e:
        st.error(f"Model error: {e}")
        return ""


# ------------------- Symptom mapper -------------------
def map_symptoms(text: str):
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

    raw = ask_gpt(system_prompt, user_prompt, temp=0.2)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed, raw
        return [], raw
    except Exception:
        return [], raw


# ------------------- Statement builder -------------------
def build_statement(state, title, focus_conditions):
    prof = state.get("veteran_profile", {})
    issues = state.get("issues", [])
    mappings = state.get("symptom_mappings", [])
    summary = state.get("evidence_summary", "")

    selected = [m for m in mappings if m.get("condition") in focus_conditions]

    system_prompt = (
        "You write VA disability lay statements. "
        "Use first person, plain language, detailed daily impact, onset, progression, "
        "functional loss, and how conditions relate to service. Target 600–900 words."
    )

    user_prompt = f"""
Claim title:
{title}

Profile:
{json.dumps(prof, indent=2)}

Issues:
{json.dumps(issues, indent=2)}

Selected conditions:
{json.dumps(selected, indent=2)}

Evidence summary:
{summary}

Write the statement.
"""

    return ask_gpt(system_prompt, user_prompt, temp=0.35)


# ------------------- Chat context -------------------
def chat_context(state):
    prof = state.get("veteran_profile", {})
    issues = state.get("issues", [])
    summary = state.get("evidence_summary", "")
    docs = state.get("documents", [])

    snippets = []
    for d in docs:
        txt = d.get("text") or ""
        if txt:
            snippets.append(f"{d['name']}:\n{txt[:800]}")

    parts = []
    if prof:
        parts.append("Profile:\n" + json.dumps(prof, indent=2))
    if issues:
        parts.append("Issues:\n" + json.dumps(issues, indent=2))
    if summary:
        parts.append("Evidence summary:\n" + summary)
    if snippets:
        parts.append("Record snippets:\n" + "\n\n".join(snippets))

    return "\n\n".join(parts)


# ------------------- Auth screen -------------------
def auth_screen():
    st.title("VA ClaimMate MVP")
    st.caption("Secure login")

    mode = st.radio("Mode", ["Log in", "Sign up"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if mode == "Log in":
        if st.button("Log in"):
            res = sign_in(email, password)
            if res and res.user:
                st.session_state.user = {"id": res.user.id, "email": email}
                st.rerun()
            else:
                st.error("Login failed.")
    else:
        if st.button("Sign up"):
            res = sign_up(email, password)
            if res and res.user:
                st.success("Account created. You can now log in.")
            else:
                st.error("Sign up failed.")


# ------------------- Main UI -------------------
def app_ui():
    state = get_state()
    if state is None:
        st.error("Could not load user data.")
        return

    st.title("VA ClaimMate MVP")

    top_col1, top_col2 = st.columns([4, 1])
    with top_col2:
        if st.button("Logout"):
            logout()

    tabs = st.tabs([
        "Profile",
        "Upload Evidence",
        "Symptom Mapper",
        "Statement Builder",
        "Saved Claims",
        "VA Claim Chat",
    ])

    # Profile tab
    with tabs[0]:
        st.subheader("Service profile and claimed issues")

        prof = state["veteran_profile"]

        prof["full_name"] = st.text_input("Full name", prof.get("full_name", ""))
        prof["branch"] = st.text_input("Branch", prof.get("branch", ""))
        prof["service_dates"] = st.text_input("Service dates", prof.get("service_dates", ""))
        prof["deployment_locations"] = st.text_area("Deployments", prof.get("deployment_locations", ""))
        prof["mos_duties"] = st.text_area("Duties / MOS", prof.get("mos_duties", ""))
        prof["other_notes"] = st.text_area("Other notes", prof.get("other_notes", ""))

        state["veteran_profile"] = prof

        st.markdown("### Claimed issues")
        raw = "\n".join(i["label"] for i in state["issues"])
        updated = st.text_area("One issue per line", raw)

        issues = []
        for line in updated.splitlines():
            label = line.strip()
            if label:
                issues.append({"label": label})
        state["issues"] = issues

    # Upload Evidence tab
    with tabs[1]:
        st.subheader("Upload medical records and evidence")

        uploads = st.file_uploader("Upload files", type=["pdf", "txt", "docx"], accept_multiple_files=True)

        if uploads:
            for up in uploads:
                content = up.getvalue()
                mime = up.type
                name = up.name
                size = len(content)

                doc_id = f"{name}:{size}"
                if doc_id in [d["id"] for d in state["documents"]]:
                    continue

                text = extract_text(content, mime, name)
                state["documents"].append(
                    {
                        "id": doc_id,
                        "name": name,
                        "mime": mime,
                        "size": size,
                        "uploaded_at": datetime.utcnow().isoformat() + "Z",
                        "text": text,
                    }
                )

        if state["documents"]:
            for d in state["documents"]:
                with st.expander(f"{d['name']} ({d['mime']})"):
                    st.text_area("Preview", (d.get("text") or "")[:1200], height=200)

        st.markdown("### Combined evidence summary")

        current = state.get("evidence_summary", "")

        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Build or refresh summary"):
                all_texts = [d.get("text") or "" for d in state["documents"] if d.get("text")]
                blob = "\n\n".join(all_texts)[:15000]
                if blob:
                    sys = (
                        "You summarize medical records for VA disability claims. "
                        "Focus on diagnoses, functional impact, and service connection hints."
                    )
                    usr = f"Summarize these records for a VA claim:\n{blob}"
                    summary = ask_gpt(sys, usr)
                    state["evidence_summary"] = summary
                    current = summary
        with col_b:
            st.caption("Use the button to let the model scan uploaded records and draft a structured summary.")

        state["evidence_summary"] = st.text_area("Editable summary", current, height=220)

    # Symptom Mapper tab
    with tabs[2]:
        st.subheader("Symptom to condition mapper")

        note = st.text_area("Describe symptoms and history", state.get("symptom_note", ""), height=220)
        state["symptom_note"] = note

        if st.button("Analyze symptoms and suggest conditions"):
            if note.strip():
                mappings, raw = map_symptoms(note)
                if mappings:
                    state["symptom_mappings"] = mappings
                else:
                    st.warning("Could not parse JSON from model. Raw output below.")
                    st.text_area("Raw model output", raw, height=200)

        if state["symptom_mappings"]:
            st.write("Suggested conditions and VA hints:")
            st.json(state["symptom_mappings"])

    # Statement Builder tab
    with tabs[3]:
        st.subheader("Personal statement builder")

        mappings = state["symptom_mappings"]
        conditions = [m.get("condition") for m in mappings if m.get("condition")]

        if conditions:
            default_title = ", ".join(conditions[:3])
        else:
            default_title = ""

        title = st.text_input("Statement title", default_title)

        focus = st.multiselect("Conditions to focus on", conditions, default=conditions)

        if "latest_statement" not in st.session_state:
            st.session_state.latest_statement = ""

        if st.button("Generate statement"):
            if title.strip():
                text = build_statement(state, title, focus)
                st.session_state.latest_statement = text

        edited = st.text_area(
            "Statement text (editable)",
            st.session_state.latest_statement,
            height=260,
        )
        st.session_state.latest_statement = edited

        if st.button("Save statement"):
            if edited.strip():
                state["claims"].append(
                    {
                        "id": f"claim_{int(datetime.utcnow().timestamp())}",
                        "title": title or "VA claim statement",
                        "body": edited,
                        "created_at": datetime.utcnow().isoformat() + "Z",
                    }
                )
                st.success("Statement saved to Claims tab.")

    # Saved Claims tab
    with tabs[4]:
        st.subheader("Saved claims dashboard and export")

        if not state["claims"]:
            st.info("No saved statements yet.")
        else:
            for c in state["claims"]:
                with st.expander(f"{c['title']} (created {c['created_at']})"):
                    st.text_area("Text", c["body"], height=220)

        parts = []
        parts.append("VA ClaimMate Claim Packet")
        parts.append(f"Generated: {datetime.utcnow().isoformat()}Z")
        parts.append("")

        parts.append("Profile:")
        parts.append(json.dumps(state["veteran_profile"], indent=2))
        parts.append("")

        parts.append("Issues:")
        parts.append(json.dumps(state["issues"], indent=2))
        parts.append("")

        parts.append("Evidence summary:")
        parts.append(state.get("evidence_summary", ""))
        parts.append("")

        parts.append("Statements:")
        for c in state["claims"]:
            parts.append("")
            parts.append(f"Title: {c['title']}")
            parts.append(c["body"])

        packet = "\n".join(parts)

        st.download_button(
            label="Download full claim packet as .txt",
            data=packet,
            file_name="va_claimmate_packet.txt",
            mime="text/plain",
        )

    # VA Claim Chat tab
    with tabs[5]:
        st.subheader("General VA claim chat")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_msg = st.chat_input("Ask a VA claim question")
        if user_msg:
            st.session_state.chat_history.append({"role": "user", "content": user_msg})

            context = chat_context(state)

            sys = (
                "You are a VA claims education assistant. "
                "Explain concepts and preparation steps. No legal advice, no promises."
            )
            usr = f"Context for this veteran:\n{context}\n\nQuestion:\n{user_msg}"

            reply = ask_gpt(sys, usr, temp=0.35)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

            with st.chat_message("assistant"):
                st.write(reply)

    persist_state()


# ------------------- Entry point -------------------
def main():
    if not current_user():
        auth_screen()
    else:
        app_ui()


if __name__ == "__main__":
    main()

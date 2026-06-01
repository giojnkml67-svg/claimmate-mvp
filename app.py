import os
import io
import json
from datetime import datetime

import pandas as pd
import streamlit as st
import google.generativeai as genai
from supabase import create_client
from PyPDF2 import PdfReader
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)

st.set_page_config(page_title="VA ClaimMate", layout="wide")

# ── API clients ────────────────────────────────────────────────────────────
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
genai.configure(api_key=GOOGLE_API_KEY)

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase configuration missing. Set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
STATE_TABLE = "claimmate_state"

# ── Presumptive conditions data (no API needed) ────────────────────────────
PRESUMPTIVE_CONDITIONS = {
    "agent_orange": {
        "era_label": "Agent Orange / Vietnam Era",
        "description": (
            "Veterans who served in Vietnam, the Korean DMZ (Apr 1, 1968–Aug 31, 1971), "
            "or Thailand military bases (Jan 9, 1962–May 7, 1975). VA presumes service "
            "connection — no nexus letter required."
        ),
        "date_range": ("1962-01-09", "1975-05-07"),
        "profile_era_match": ["Vietnam (1961–1975)", "Korea DMZ (1968–1971)"],
        "conditions": [
            {"name": "AL Amyloidosis",                                       "icd10": "E85.0",  "typical_rating": "At least 10%"},
            {"name": "Bladder Cancer",                                        "icd10": "C67.9",  "typical_rating": "100% active; 10% post-tx"},
            {"name": "Chronic B-Cell Leukemia",                               "icd10": "C91.1",  "typical_rating": "100% active"},
            {"name": "Chloracne",                                              "icd10": "L70.8",  "typical_rating": "10%–30%"},
            {"name": "Diabetes Mellitus Type 2",                               "icd10": "E11.9",  "typical_rating": "10%–60%"},
            {"name": "Hodgkin's Disease",                                       "icd10": "C81.9",  "typical_rating": "100% active"},
            {"name": "Hypertension",                                            "icd10": "I10",    "typical_rating": "10%–60%"},
            {"name": "Hypothyroidism",                                          "icd10": "E03.9",  "typical_rating": "10%–30%"},
            {"name": "Ischemic Heart Disease",                                  "icd10": "I25.9",  "typical_rating": "10%–100%"},
            {"name": "Monoclonal Gammopathy (MGUS)",                           "icd10": "D47.2",  "typical_rating": "10%"},
            {"name": "Multiple Myeloma",                                        "icd10": "C90.0",  "typical_rating": "100%"},
            {"name": "Non-Hodgkin's Lymphoma",                                  "icd10": "C85.9",  "typical_rating": "100% active"},
            {"name": "Parkinson's Disease",                                     "icd10": "G20",    "typical_rating": "30%–100%"},
            {"name": "Parkinsonism",                                             "icd10": "G21.9",  "typical_rating": "30%–100%"},
            {"name": "Peripheral Neuropathy (early onset)",                     "icd10": "G62.9",  "typical_rating": "10%–20%"},
            {"name": "Porphyria Cutanea Tarda",                                 "icd10": "E80.1",  "typical_rating": "10%"},
            {"name": "Prostate Cancer",                                          "icd10": "C61",    "typical_rating": "100% active; 10% post-tx"},
            {"name": "Respiratory Cancers (lung, bronchus, larynx, trachea)",  "icd10": "C34.9",  "typical_rating": "100% active"},
            {"name": "Soft Tissue Sarcoma",                                     "icd10": "C49.9",  "typical_rating": "100% active"},
        ],
    },
    "gulf_war": {
        "era_label": "Gulf War Syndrome / Undiagnosed Illness",
        "description": (
            "Veterans who served in Southwest Asia (Iraq, Kuwait, Saudi Arabia, Bahrain, "
            "Qatar, UAE, Oman, Afghanistan, Yemen, Djibouti, Jordan, Egypt, Turkey, Syria, "
            "Lebanon) on or after Aug 2, 1990. Chronic undiagnosed illnesses and Medically "
            "Unexplained Chronic Multisymptom Illness (MUCMI) are presumptive."
        ),
        "date_range": ("1990-08-02", None),
        "profile_era_match": "Gulf War / SW Asia (1990–present)",
        "conditions": [
            {"name": "Chronic Fatigue Syndrome",                              "icd10": "G93.3",  "typical_rating": "10%–100%"},
            {"name": "Fibromyalgia",                                           "icd10": "M79.3",  "typical_rating": "10%–40%"},
            {"name": "Functional Gastrointestinal Disorders (IBS, etc.)",    "icd10": "K58.9",  "typical_rating": "10%–30%"},
            {"name": "Gulf War Undiagnosed Illness (neurological)",           "icd10": "G93.3",  "typical_rating": "10%–100%"},
            {"name": "Gulf War Undiagnosed Illness (musculoskeletal)",        "icd10": "M79.3",  "typical_rating": "Rated by symptoms"},
            {"name": "Gulf War Undiagnosed Illness (skin)",                   "icd10": "L98.9",  "typical_rating": "Rated by symptoms"},
            {"name": "Brucellosis",                                            "icd10": "A23.9",  "typical_rating": "Rated by symptoms"},
            {"name": "Campylobacter jejuni",                                   "icd10": "A04.5",  "typical_rating": "Rated by symptoms"},
            {"name": "Coxiella burnetii (Q Fever)",                           "icd10": "A78",    "typical_rating": "Rated by symptoms"},
            {"name": "Mycobacterium tuberculosis",                             "icd10": "A15.9",  "typical_rating": "Rated by symptoms"},
            {"name": "Visceral Leishmaniasis",                                 "icd10": "B55.0",  "typical_rating": "Rated by symptoms"},
            {"name": "West Nile Virus (neurological residuals)",               "icd10": "A92.31", "typical_rating": "Rated by residual symptoms"},
        ],
    },
    "pact_act": {
        "era_label": "PACT Act / Burn Pits (Post-9/11)",
        "description": (
            "The PACT Act (2022) extends presumptive service connection to veterans exposed "
            "to airborne hazards or burn pits in covered locations on or after Aug 2, 1990. "
            "Post-9/11 (2001–present) veterans are covered regardless of documented "
            "burn pit exposure."
        ),
        "date_range": ("2001-09-11", None),
        "profile_era_match": "Post-9/11 / GWOT (2001–present)",
        "conditions": [
            {"name": "Constrictive or Obliterative Bronchiolitis",           "icd10": "J44.1",  "typical_rating": "10%–100%"},
            {"name": "Head or Neck Cancer (any type)",                        "icd10": "C76.0",  "typical_rating": "100% active"},
            {"name": "Respiratory Cancer (lung, bronchus)",                   "icd10": "C34.9",  "typical_rating": "100% active"},
            {"name": "Gastrointestinal Cancer",                               "icd10": "C26.9",  "typical_rating": "100% active"},
            {"name": "Reproductive Cancer",                                    "icd10": "C57.9",  "typical_rating": "100% active"},
            {"name": "Kidney Cancer",                                          "icd10": "C64",    "typical_rating": "100% active"},
            {"name": "Melanoma",                                                "icd10": "C43.9",  "typical_rating": "100% active"},
            {"name": "Glioblastoma",                                            "icd10": "C71.9",  "typical_rating": "100%"},
            {"name": "Pancreatobiliary Cancer",                                "icd10": "C25.9",  "typical_rating": "100% active"},
            {"name": "Squamous Cell Carcinoma of Head/Neck",                  "icd10": "C06.9",  "typical_rating": "100% active"},
            {"name": "Any Rare Cancer per VA Rare Cancer list",               "icd10": "Various","typical_rating": "100% active"},
        ],
    },
    "camp_lejeune": {
        "era_label": "Camp Lejeune Contaminated Water",
        "description": (
            "Veterans and family members who lived or worked at Camp Lejeune or MCAS New "
            "River, NC for at least 30 cumulative days between Aug 1, 1953 and Dec 31, 1987. "
            "Caused by TCE, PCE, benzene, and vinyl chloride in the base water supply."
        ),
        "date_range": ("1953-08-01", "1987-12-31"),
        "profile_era_match": "Camp Lejeune (served Aug 1953–Dec 1987)",
        "conditions": [
            {"name": "Bladder Cancer",                                  "icd10": "C67.9",  "typical_rating": "100% active; 10% post-tx"},
            {"name": "Breast Cancer",                                    "icd10": "C50.9",  "typical_rating": "100% active"},
            {"name": "Esophageal Cancer",                                "icd10": "C15.9",  "typical_rating": "100% active"},
            {"name": "Hepatic Steatosis (non-alcoholic fatty liver)",   "icd10": "K76.0",  "typical_rating": "10%–30%"},
            {"name": "Kidney Cancer",                                    "icd10": "C64",    "typical_rating": "100% active"},
            {"name": "Leukemia",                                         "icd10": "C95.9",  "typical_rating": "100% active"},
            {"name": "Lung Cancer",                                      "icd10": "C34.9",  "typical_rating": "100% active"},
            {"name": "Multiple Myeloma",                                 "icd10": "C90.0",  "typical_rating": "100%"},
            {"name": "Myelodysplastic Syndrome",                        "icd10": "D46.9",  "typical_rating": "100% active"},
            {"name": "Neurobehavioral Effects",                         "icd10": "F09",    "typical_rating": "Rated by severity"},
            {"name": "Non-Hodgkin's Lymphoma",                          "icd10": "C85.9",  "typical_rating": "100% active"},
            {"name": "Renal Toxicity",                                   "icd10": "N17.9",  "typical_rating": "Rated by severity"},
            {"name": "Scleroderma",                                      "icd10": "M34.9",  "typical_rating": "Rated by severity"},
        ],
    },
    "radiation": {
        "era_label": "Radiation Exposure (Radiogenic Diseases)",
        "description": (
            "Veterans who participated in atmospheric nuclear tests, were POWs in "
            "Hiroshima/Nagasaki, served in Hiroshima/Nagasaki during occupation "
            "(Aug 6, 1945–Jul 1, 1946), or participated in Enewetak Atoll cleanup "
            "(1977–1980) or Palomares/Thule operations."
        ),
        "date_range": ("1945-08-06", None),
        "profile_era_match": "Radiation exposure",
        "conditions": [
            {"name": "All forms of Leukemia (except CLL)",   "icd10": "C91.9", "typical_rating": "100% active"},
            {"name": "Thyroid Cancer",                        "icd10": "C73",   "typical_rating": "100% active; 30% post-tx"},
            {"name": "Breast Cancer",                         "icd10": "C50.9", "typical_rating": "100% active"},
            {"name": "Lung Cancer",                           "icd10": "C34.9", "typical_rating": "100% active"},
            {"name": "Bone Cancer",                           "icd10": "C40.9", "typical_rating": "100% active"},
            {"name": "Liver Cancer (primary)",                "icd10": "C22.9", "typical_rating": "100% active"},
            {"name": "Stomach Cancer",                        "icd10": "C16.9", "typical_rating": "100% active"},
            {"name": "Colon Cancer",                          "icd10": "C18.9", "typical_rating": "100% active"},
            {"name": "Non-Hodgkin's Lymphoma",                "icd10": "C85.9", "typical_rating": "100% active"},
            {"name": "Posterior Subcapsular Cataracts",       "icd10": "H26.1", "typical_rating": "10%–30%"},
            {"name": "Urinary Bladder Cancer",                "icd10": "C67.9", "typical_rating": "100% active"},
            {"name": "Salivary Gland Cancer",                 "icd10": "C08.9", "typical_rating": "100% active"},
        ],
    },
}

SERVICE_ERAS = [
    "Vietnam (1961–1975)",
    "Korea DMZ (1968–1971)",
    "Gulf War / SW Asia (1990–present)",
    "Post-9/11 / GWOT (2001–present)",
    "Cold War",
    "Camp Lejeune (served Aug 1953–Dec 1987)",
    "Radiation exposure",
    "Korean War (1950–1953)",
    "World War II (1941–1945)",
    "Other",
]

# ── Default state ──────────────────────────────────────────────────────────
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
        "presumptive_matches": [],
        "buddy_statements": [],
        "rating_inputs": [],
        "va_file_number": "",
    }


# ── Auth helpers ───────────────────────────────────────────────────────────
def sign_up(email, password):
    try:
        return supabase.auth.sign_up({"email": email, "password": password})
    except Exception:
        return None


def sign_in(email, password):
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception:
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


# ── State load/save ────────────────────────────────────────────────────────
def load_state(user_id: str):
    try:
        res = supabase.table(STATE_TABLE).select("state").eq("user_id", user_id).execute()
        rows = res.data or []
        state = (rows[0]["state"] if rows else None) or {}
        if not rows:
            supabase.table(STATE_TABLE).insert({"user_id": user_id, "state": state}).execute()
        base = default_state()
        for k in base:
            if k not in state:
                state[k] = base[k]
        return state
    except Exception:
        st.error("Error loading your data. Please refresh the page.")
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
    except Exception:
        st.error("Error saving your data. Please try again.")


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


# ── File extraction ────────────────────────────────────────────────────────
def extract_text(content: bytes, mime: str, name: str) -> str:
    if mime == "application/pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)[:10000]
        except Exception:
            return ""
    if mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)[:10000]
        except Exception:
            return ""
    try:
        return content.decode("utf-8", errors="ignore")[:10000]
    except Exception:
        return ""


# ── Gemini helper ──────────────────────────────────────────────────────────
def ask_ai(system_prompt, user_prompt, model="gemini-2.0-flash", temp=0.25):
    try:
        m = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
        )
        response = m.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(temperature=temp),
        )
        return response.text
    except Exception as e:
        st.error(f"Model error: {e}")
        return ""


# ── Symptom mapper ─────────────────────────────────────────────────────────
def map_symptoms(text: str):
    system_prompt = (
        "You support veterans building VA disability claims. "
        "Return JSON only. Format: "
        '[{"condition":"","icd10":"","body_system":"","va_rating_hint":"","rationale":""}] '
        "Do not add any text outside the JSON array."
    )
    user_prompt = (
        f"Symptoms from the veteran:\n{text}\n\n"
        "Suggest diagnostic labels with ICD-10 codes, VA rating hints, and rationale. "
        "Include Gulf War or toxic exposure links where relevant."
    )
    raw = ask_ai(system_prompt, user_prompt, temp=0.2)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed, raw
        return [], raw
    except Exception:
        return [], raw


# ── Personal statement builder ─────────────────────────────────────────────
def build_statement(state, title, focus_conditions):
    prof = state.get("veteran_profile", {})
    issues = state.get("issues", [])
    mappings = state.get("symptom_mappings", [])
    summary = state.get("evidence_summary", "")
    presumptive = state.get("presumptive_matches", [])

    selected_mappings = [m for m in mappings if m.get("condition") in focus_conditions]
    presumptive_str = ""
    if presumptive:
        lines = [f"- {m['condition']} ({m['era_label']})" for m in presumptive]
        presumptive_str = "Presumptive conditions:\n" + "\n".join(lines)

    system_prompt = (
        "You write VA disability lay statements for veterans. "
        "Use first person, plain language, and detailed daily functional impact. "
        "Cover onset, progression, daily limitations, work impact, sleep, mental health, "
        "flare patterns, and connection to service. Target 600–900 words."
    )
    user_prompt = f"""Claim title: {title}

Profile:
{json.dumps(prof, indent=2)}

Claimed issues:
{json.dumps(issues, indent=2)}

Selected conditions and VA hints:
{json.dumps(selected_mappings, indent=2)}

{presumptive_str}

Evidence summary:
{summary}

Write a lay statement in first person. End with a short paragraph affirming the statement is true to the best of the veteran's knowledge."""

    return ask_ai(system_prompt, user_prompt, temp=0.35)


# ── Buddy statement templates (no API) ─────────────────────────────────────
def buddy_statement_fellow_veteran(prof: dict, conditions: list) -> str:
    name = prof.get("full_name", "[Veteran Name]")
    branch = prof.get("branch", "[Branch]")
    service_dates = prof.get("service_dates", "[Service Dates]")
    cond_str = ", ".join(conditions) if conditions else "[listed conditions]"
    return f"""BUDDY STATEMENT — FELLOW VETERAN
VA Form 21-10210 (Lay/Witness Statement)
Date: {datetime.utcnow().strftime("%B %d, %Y")}

To Whom It May Concern:

My name is [YOUR FULL NAME]. I am a [YOUR BRANCH] veteran who served alongside {name} during [DESCRIBE SHARED SERVICE PERIOD OR LOCATION]. I provide this statement in support of {name}'s VA disability claim for {cond_str}.

I personally witnessed {name}'s condition(s) during and/or after our shared service. Specifically, I observed:
[Describe what you witnessed — symptoms, limitations, behavior changes. Be specific with dates and locations if possible.]

During our time in {branch} ({service_dates}), I observed the following events or conditions that I believe are directly related to {name}'s current disability:
[Describe any relevant incidents, exposures, or working conditions you both experienced.]

Since leaving service, I have remained in contact with {name} and have observed the following:
[Describe current functional impact — what they can and cannot do, how their condition affects daily life, work, and relationships.]

I provide this statement freely and voluntarily. I understand it may be used in support of a VA disability claim. I affirm that the information above is true and accurate to the best of my knowledge.

Respectfully,

[YOUR FULL NAME]
[YOUR ADDRESS]
[CITY, STATE, ZIP]
[YOUR PHONE NUMBER]
[YOUR EMAIL]
[YOUR VA FILE NUMBER, if applicable]
[DATE SIGNED]
"""


def buddy_statement_family_member(prof: dict, conditions: list) -> str:
    name = prof.get("full_name", "[Veteran Name]")
    branch = prof.get("branch", "[Branch]")
    cond_str = ", ".join(conditions) if conditions else "[listed conditions]"
    return f"""BUDDY STATEMENT — FAMILY MEMBER OR SPOUSE
VA Form 21-10210 (Lay/Witness Statement)
Date: {datetime.utcnow().strftime("%B %d, %Y")}

To Whom It May Concern:

My name is [YOUR FULL NAME] and I am the [RELATIONSHIP — spouse / parent / sibling / adult child] of {name}, a {branch} veteran. I submit this statement in support of {name}'s VA disability claim for {cond_str}.

I have known {name} for [HOW LONG] and have lived with or been in close contact with them since [DATE]. I am in a unique position to describe the direct impact of their service-connected condition(s) on their daily life, our household, and our relationship.

Before {name}'s military service, I observed they were:
[Describe what the veteran was like before service — personality, physical ability, social life, energy level, work capacity.]

After {name}'s service, I noticed the following changes:
[Describe specific changes — sleep problems, mood changes, physical limitations, pain, avoidance behaviors, medication use, etc.]

On a typical day, I observe the following:
[Walk through a realistic daily routine — what the veteran struggles to do, what you help with, what they have given up. Include specifics: stairs, driving, cooking, childcare, work, social activities.]

The impact on our family has been:
[Describe caregiver burden, relationship strain, financial impact, safety concerns, emotional toll.]

I have personally witnessed the following medical events or treatments:
[List relevant observations — ER visits, pain flares, hospitalizations, therapy, medication management.]

I affirm this statement is true and complete to the best of my knowledge. I provide it freely in support of {name}'s claim.

Respectfully,

[YOUR FULL NAME]
[YOUR RELATIONSHIP TO THE VETERAN]
[YOUR ADDRESS]
[YOUR PHONE NUMBER]
[YOUR EMAIL]
[DATE SIGNED]
"""


def buddy_statement_employer(prof: dict, conditions: list) -> str:
    name = prof.get("full_name", "[Veteran Name]")
    cond_str = ", ".join(conditions) if conditions else "[listed conditions]"
    return f"""BUDDY STATEMENT — EMPLOYER OR COWORKER
VA Form 21-10210 (Lay/Witness Statement)
Date: {datetime.utcnow().strftime("%B %d, %Y")}

To Whom It May Concern:

My name is [YOUR FULL NAME] and I am the [TITLE — employer / supervisor / coworker] of {name}. I have known {name} professionally since [DATE] at [COMPANY/ORGANIZATION]. I provide this statement in support of {name}'s VA disability claim for {cond_str}.

In my professional capacity, I have observed the following limitations related to {name}'s condition(s):

Attendance and scheduling:
[Describe missed days, late arrivals, early departures, need for schedule accommodations, frequent medical appointments.]

Physical limitations at work:
[Describe tasks {name} cannot perform or struggles with — standing, lifting, sitting, operating equipment, use of stairs, etc.]

Cognitive or behavioral observations (if applicable):
[Concentration difficulties, memory issues, need for repeated instructions, social withdrawal, anxiety-related behaviors.]

Accommodations made:
[Describe any workplace accommodations — modified duties, reduced hours, ergonomic equipment, remote work, assistance from coworkers.]

Changes I have observed over time:
[Describe any progression or fluctuation in {name}'s limitations since you began working together.]

I affirm this statement is accurate to the best of my professional knowledge and provide it voluntarily.

Respectfully,

[YOUR FULL NAME]
[YOUR TITLE]
[YOUR COMPANY/ORGANIZATION]
[YOUR ADDRESS]
[YOUR PHONE NUMBER]
[YOUR EMAIL]
[DATE SIGNED]
"""


# ── VA Combined Rating Calculator ──────────────────────────────────────────
def calculate_va_combined_rating(ratings: list) -> dict:
    if not ratings:
        return {"sorted_ratings": [], "steps": ["No ratings entered."],
                "combined_exact": 0.0, "combined_rounded": 0, "display_rating": 0}

    valid = sorted([r for r in ratings if 0 <= r <= 100], reverse=True)
    if not valid:
        return {"sorted_ratings": [], "steps": ["No valid ratings (must be 0–100)."],
                "combined_exact": 0.0, "combined_rounded": 0, "display_rating": 0}

    steps = []
    remaining = 100.0
    combined = 0.0
    steps.append("Start: 100% whole person (0% disabled, 100% remaining).")

    for i, r in enumerate(valid):
        added = (r / 100.0) * remaining
        combined += added
        remaining -= added
        steps.append(
            f"Step {i+1}: Apply {r}% to {remaining + added:.1f}% remaining "
            f"→ adds {added:.2f}%. Running total: {combined:.2f}% disabled, {remaining:.2f}% remaining."
        )

    # VA uses integer ones digit for rounding (not decimal)
    ones_digit = int(combined) % 10
    if ones_digit < 5:
        rounded = (int(combined) // 10) * 10
    else:
        rounded = (int(combined) // 10 + 1) * 10
    rounded = min(rounded, 100)

    steps.append(f"Combined (exact): {combined:.2f}%  →  Rounded to nearest 10: {rounded}%")

    if (rounded >= 70 and valid[0] >= 40) or valid[0] >= 60:
        steps.append(
            f"With a {rounded}% combined rating and a single rating of {valid[0]}%, "
            "you may qualify for TDIU (Total Disability Individual Unemployability) "
            "if your conditions prevent substantially gainful employment "
            "(38 CFR 4.16a: one disability ≥60%, or combined ≥70% with one ≥40%). "
            "See VA Form 21-8940."
        )

    return {
        "sorted_ratings": valid,
        "steps": steps,
        "combined_exact": round(combined, 2),
        "combined_rounded": rounded,
        "display_rating": rounded,
    }


# ── Chat context builder ───────────────────────────────────────────────────
def chat_context(state):
    prof = state.get("veteran_profile", {})
    issues = state.get("issues", [])
    summary = state.get("evidence_summary", "")
    docs = state.get("documents", [])
    presumptive = state.get("presumptive_matches", [])

    parts = []
    bits = []
    if prof.get("branch"):
        bits.append(f"Branch: {prof.get('branch')}")
    if prof.get("service_dates"):
        bits.append(f"Service: {prof.get('service_dates')}")
    if prof.get("deployment_locations"):
        bits.append(f"Deployments: {prof.get('deployment_locations')}")
    if bits:
        parts.append("Profile:\n" + "\n".join(bits))

    if issues:
        parts.append("Claimed issues:\n- " + "\n- ".join(i["label"] for i in issues if i.get("label")))

    if presumptive:
        plines = [f"- {m['condition']} ({m['era_label']}, ICD-10 {m['icd10']})" for m in presumptive]
        parts.append("Presumptive condition matches:\n" + "\n".join(plines))

    if summary:
        parts.append("Evidence summary:\n" + summary)

    snippets = []
    for d in docs[:3]:
        txt = d.get("text") or ""
        if txt:
            snippets.append(f"{d['name']}:\n{txt[:800]}")
    if snippets:
        parts.append("Record snippets:\n" + "\n\n".join(snippets))

    return "\n\n".join(parts)


# ── TXT packet builder ─────────────────────────────────────────────────────
def build_txt_packet(state: dict) -> str:
    prof = state.get("veteran_profile", {})
    lines = []
    lines.append("VA ClaimMate — Claim Packet")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    lines.append("")

    lines.append("VETERAN PROFILE")
    lines.append("-" * 30)
    for k, v in prof.items():
        if v:
            lines.append(f"{k}: {', '.join(v) if isinstance(v, list) else v}")
    lines.append("")

    lines.append("CLAIMED ISSUES")
    lines.append("-" * 30)
    for i in state.get("issues", []):
        if i.get("label"):
            lines.append(f"- {i['label']}")
    if not state.get("issues"):
        lines.append("None recorded.")
    lines.append("")

    lines.append("PRESUMPTIVE CONDITIONS")
    lines.append("-" * 30)
    for m in state.get("presumptive_matches", []):
        lines.append(f"- {m['condition']} | {m['era_label']} | ICD-10 {m['icd10']} | Rating: {m['typical_rating']}")
    if not state.get("presumptive_matches"):
        lines.append("None selected.")
    lines.append("")

    lines.append("SYMPTOM-TO-CONDITION MAPPINGS (selected)")
    lines.append("-" * 30)
    selected_m = [m for m in state.get("symptom_mappings", []) if m.get("selected_for_claim")]
    for m in selected_m:
        lines.append(f"- {m.get('condition')} | ICD-10 {m.get('icd10')} | {m.get('va_rating_hint')}")
    if not selected_m:
        lines.append("None selected.")
    lines.append("")

    lines.append("EVIDENCE SUMMARY")
    lines.append("-" * 30)
    lines.append(state.get("evidence_summary", "Not prepared."))
    lines.append("")

    lines.append("PERSONAL STATEMENTS")
    lines.append("-" * 30)
    for c in state.get("claims", []):
        lines.append(f"\nTitle: {c.get('title')}")
        lines.append(f"Created: {c.get('created_at')}")
        lines.append("")
        lines.append(c.get("body", ""))
        lines.append("")

    lines.append("BUDDY / LAY STATEMENT TEMPLATES")
    lines.append("-" * 30)
    for bs in state.get("buddy_statements", []):
        lines.append(f"\nType: {bs.get('type')}")
        lines.append(f"Created: {bs.get('created_at')}")
        lines.append("")
        lines.append(bs.get("body", ""))
        lines.append("")

    return "\n".join(lines)


# ── PDF packet generator ───────────────────────────────────────────────────
def generate_pdf_packet(state: dict) -> bytes:
    buf = io.BytesIO()
    prof = state.get("veteran_profile", {})

    doc_obj = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=0.75 * inch,
        title="VA ClaimMate Claim Packet",
    )

    styles = getSampleStyleSheet()
    s_title = ParagraphStyle(
        "ClaimTitle", parent=styles["Title"],
        fontSize=22, spaceAfter=10,
        textColor=colors.HexColor("#1a237e"),
    )
    s_h1 = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=14, spaceAfter=6, spaceBefore=14,
        textColor=colors.HexColor("#1a237e"),
    )
    s_h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=12, spaceAfter=4, spaceBefore=10,
        textColor=colors.HexColor("#283593"),
    )
    s_body = styles["Normal"]
    s_small = ParagraphStyle(
        "Small", parent=styles["Normal"],
        fontSize=8, textColor=colors.gray, spaceAfter=4,
    )

    story = []

    # Cover page
    story.append(Spacer(1, 1.2 * inch))
    story.append(Paragraph("VA Disability Claim Packet", s_title))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a237e")))
    story.append(Spacer(1, 0.25 * inch))

    cover_data = [
        ["Veteran Name:", prof.get("full_name", "Not provided")],
        ["VA File Number:", prof.get("va_file_number", "Not provided")],
        ["Branch of Service:", prof.get("branch", "Not provided")],
        ["Service Dates:", prof.get("service_dates", "Not provided")],
        ["Discharge Type:", prof.get("discharge_type", "Not provided")],
        ["Service Era(s):", ", ".join(prof.get("era", [])) or "Not provided"],
        ["Date Generated:", datetime.utcnow().strftime("%B %d, %Y")],
    ]
    ct = Table(cover_data, colWidths=[2 * inch, 4.3 * inch])
    ct.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1a237e")),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(
        "DISCLAIMER: This document was prepared using VA ClaimMate, an AI-assisted claim "
        "preparation tool. It is not legal advice and is not affiliated with the U.S. "
        "Department of Veterans Affairs. Review all content with a VA-accredited attorney, "
        "claims agent, or Veterans Service Organization (VSO) before submission.",
        s_small,
    ))
    story.append(PageBreak())

    def section(title):
        story.append(Paragraph(title, s_h1))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c5cae9")))
        story.append(Spacer(1, 0.1 * inch))

    def table_block(headers, rows, col_widths):
        if not rows:
            story.append(Paragraph("None recorded.", s_body))
            return
        data = [headers] + rows
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e8eaf6")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c5cae9")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)

    # Section 1: Profile
    section("Section 1 — Veteran Profile & Service History")
    profile_fields = [
        ("Full Name", prof.get("full_name")),
        ("VA File Number", prof.get("va_file_number")),
        ("Branch of Service", prof.get("branch")),
        ("Service Dates", prof.get("service_dates")),
        ("Discharge Type", prof.get("discharge_type")),
        ("Service Era(s)", ", ".join(prof.get("era", []))),
        ("Deployment Locations", prof.get("deployment_locations")),
        ("MOS / Duties", prof.get("mos_duties")),
        ("Additional Notes", prof.get("other_notes")),
    ]
    for label, value in profile_fields:
        if value:
            story.append(Paragraph(f"<b>{label}:</b> {value}", s_body))
            story.append(Spacer(1, 0.05 * inch))

    # Section 2: Claimed issues
    story.append(Spacer(1, 0.15 * inch))
    section("Section 2 — Claimed Issues")
    issues = state.get("issues", [])
    if issues:
        for i, issue in enumerate(issues, 1):
            story.append(Paragraph(f"{i}. {issue.get('label', '')}", s_body))
    else:
        story.append(Paragraph("No issues recorded.", s_body))

    # Section 3: Presumptive conditions
    story.append(Spacer(1, 0.15 * inch))
    section("Section 3 — Presumptive Condition Matches")
    presump = state.get("presumptive_matches", [])
    table_block(
        ["Era", "Condition", "ICD-10", "Typical Rating"],
        [[m.get("era_label", ""), m.get("condition", ""), m.get("icd10", ""), m.get("typical_rating", "")]
         for m in presump],
        [1.7 * inch, 2.2 * inch, 0.85 * inch, 1.35 * inch],
    )

    # Section 4: Symptom mappings
    story.append(Spacer(1, 0.15 * inch))
    section("Section 4 — Symptom-to-Condition Mappings")
    selected_m = [m for m in state.get("symptom_mappings", []) if m.get("selected_for_claim")]
    table_block(
        ["Condition", "ICD-10", "Body System", "VA Rating Hint"],
        [[m.get("condition", ""), m.get("icd10", ""), m.get("body_system", ""), m.get("va_rating_hint", "")]
         for m in selected_m],
        [2 * inch, 0.9 * inch, 1.4 * inch, 1.8 * inch],
    )

    # Section 5: Evidence
    story.append(Spacer(1, 0.15 * inch))
    section("Section 5 — Evidence Summary")
    ev = state.get("evidence_summary", "")
    if ev:
        story.append(Paragraph(ev.replace("\n", "<br/>"), s_body))
    else:
        story.append(Paragraph("No evidence summary prepared.", s_body))

    docs = state.get("documents", [])
    if docs:
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("<b>Documents uploaded:</b>", s_body))
        for d in docs:
            notes = d.get("notes", "")
            note_str = f" — {notes}" if notes else ""
            story.append(Paragraph(f"• {d.get('name')} ({d.get('mime')}){note_str}", s_body))

    # Section 6: Personal statements
    claims = state.get("claims", [])
    if claims:
        story.append(PageBreak())
        section("Section 6 — Personal Statements")
        for c in claims:
            story.append(Paragraph(f"<b>{c.get('title', 'VA Claim Statement')}</b>", s_h2))
            story.append(Paragraph(f"Created: {c.get('created_at', '')}", s_small))
            story.append(Spacer(1, 0.06 * inch))
            story.append(Paragraph(c.get("body", "").replace("\n", "<br/>"), s_body))
            story.append(Spacer(1, 0.2 * inch))

    # Section 7: Buddy statements
    buddy_stmts = state.get("buddy_statements", [])
    if buddy_stmts:
        story.append(PageBreak())
        section("Section 7 — Supporting / Buddy Statement Templates")
        story.append(Paragraph(
            "These templates have been pre-filled with the veteran's information. "
            "Bracketed sections must be completed by the person providing the statement.",
            s_small,
        ))
        story.append(Spacer(1, 0.1 * inch))
        for bs in buddy_stmts:
            story.append(Paragraph(f"<b>{bs.get('type', 'Buddy Statement')}</b>", s_h2))
            story.append(Paragraph(bs.get("body", "").replace("\n", "<br/>"), s_body))
            story.append(Spacer(1, 0.2 * inch))

    doc_obj.build(story)
    return buf.getvalue()


# ── AUTH SCREEN ────────────────────────────────────────────────────────────
def auth_screen():
    st.title("VA ClaimMate")
    st.caption("Your step-by-step companion for stronger VA disability claim preparation.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Log in")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log in", type="primary"):
            res = sign_in(email, password)
            if res and res.user:
                st.session_state.user = {"id": res.user.id, "email": email}
                st.rerun()
            else:
                st.error("Login failed. Check your email and password.")

    with col2:
        st.subheader("Create account")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password (8+ characters)", type="password", key="reg_pass")
        if st.button("Sign up"):
            if len(reg_pass) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                res = sign_up(reg_email, reg_pass)
                if res and res.user:
                    if res.session:
                        st.success("Account created. You can now log in.")
                    else:
                        st.success("Account created. Check your email to confirm your address, then log in.")
                else:
                    st.error("Sign up failed. Please try again.")

    st.markdown("---")
    st.caption(
        "VA ClaimMate is an AI-assisted claim preparation tool. "
        "It is not affiliated with the U.S. Department of Veterans Affairs and does not provide legal advice. "
        "Always review your claim with a VA-accredited VSO, attorney, or claims agent before submitting."
    )


# ── TAB 1: Profile & Service ───────────────────────────────────────────────
def tab_profile(state, tabs):
    with tabs[0]:
        st.subheader("Step 1 — Veteran Profile & Service History")
        st.caption("Fill in your service background. Other tabs use this information to personalize your claim materials.")

        prof = state.get("veteran_profile", {})
        discharge_options = [
            "", "Honorable", "General Under Honorable Conditions",
            "Other Than Honorable (OTH)", "Bad Conduct", "Dishonorable", "Entry Level Separation",
        ]

        col1, col2 = st.columns(2)
        with col1:
            prof["full_name"] = st.text_input("Full name", prof.get("full_name", ""))
            prof["va_file_number"] = st.text_input("VA File Number (C-File #)", prof.get("va_file_number", ""))
            prof["branch"] = st.text_input("Branch of service", prof.get("branch", ""))
            prof["service_dates"] = st.text_input(
                "Service dates (e.g. 1990-01 to 1998-06)", prof.get("service_dates", "")
            )
            current_discharge = prof.get("discharge_type", "")
            discharge_idx = discharge_options.index(current_discharge) if current_discharge in discharge_options else 0
            prof["discharge_type"] = st.selectbox("Discharge type", discharge_options, index=discharge_idx)

        with col2:
            current_eras = [e for e in prof.get("era", []) if e in SERVICE_ERAS]
            prof["era"] = st.multiselect(
                "Service era(s) — drives Presumptive Conditions tab",
                SERVICE_ERAS,
                default=current_eras,
            )
            prof["deployment_locations"] = st.text_area(
                "Deployment locations / bases", prof.get("deployment_locations", ""), height=80
            )
            prof["mos_duties"] = st.text_area(
                "Duties, MOS/AFSC, and role details", prof.get("mos_duties", ""), height=80
            )
            prof["other_notes"] = st.text_area(
                "Other background notes for the rating", prof.get("other_notes", ""), height=80
            )

        state["veteran_profile"] = prof

        st.markdown("---")
        st.markdown("#### Claimed issues list")
        st.caption(
            "List each condition you are claiming, one per line. "
            "Examples: PTSD, lumbar strain, tinnitus, hypertension, sleep apnea."
        )
        raw = "\n".join(i["label"] for i in state.get("issues", []) if i.get("label"))
        updated = st.text_area("One issue per line", raw, height=120)

        new_issues = []
        for line in updated.splitlines():
            label = line.strip()
            if label:
                new_issues.append({"label": label})
        state["issues"] = new_issues


# ── TAB 2: Presumptive Conditions ─────────────────────────────────────────
def tab_presumptive(state, tabs):
    with tabs[1]:
        st.subheader("Step 2 — Presumptive Conditions Checker")
        st.caption(
            "No AI needed here. This tool matches your service era to VA presumptive conditions — "
            "disabilities VA presumes were caused by your service without requiring a nexus letter. "
            "Set your era in Tab 1 to see automatic matches."
        )

        prof = state.get("veteran_profile", {})
        eras_served = prof.get("era", [])
        def _era_matches(group_match, eras):
            if isinstance(group_match, list):
                return any(m in eras for m in group_match)
            return group_match in eras

        matched_groups = [key for key, g in PRESUMPTIVE_CONDITIONS.items()
                          if _era_matches(g["profile_era_match"], eras_served)]

        if not eras_served:
            st.info("Add your service era(s) in the Profile tab to see your presumptive matches automatically.")
        elif not matched_groups:
            st.info("No automatic matches for your selected era(s). You can still review all categories below.")
        else:
            st.success(
                f"Based on your service era, {len(matched_groups)} exposure group(s) may apply to you. "
                "Matched groups are expanded below."
            )

        for key, group in PRESUMPTIVE_CONDITIONS.items():
            era_match = _era_matches(group["profile_era_match"], eras_served)
            label = ("✓ MATCH — " if era_match else "") + group["era_label"]

            with st.expander(label, expanded=era_match):
                st.markdown(f"**{group['description']}**")
                end_date = group["date_range"][1] or "present"
                st.caption(f"Covered period: {group['date_range'][0]} to {end_date}")
                st.markdown("---")

                rows = [
                    {"Condition": c["name"], "ICD-10": c["icd10"], "Typical VA Rating": c["typical_rating"]}
                    for c in group["conditions"]
                ]
                st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

                condition_names = [c["name"] for c in group["conditions"]]
                existing_selected = [
                    m["condition"] for m in state.get("presumptive_matches", [])
                    if m.get("group") == key and m["condition"] in condition_names
                ]
                selected = st.multiselect(
                    "Select conditions that apply to you",
                    condition_names,
                    default=existing_selected,
                    key=f"presump_{key}",
                )

                state["presumptive_matches"] = [
                    m for m in state.get("presumptive_matches", []) if m.get("group") != key
                ]
                for cname in selected:
                    cdata = next(c for c in group["conditions"] if c["name"] == cname)
                    state["presumptive_matches"].append({
                        "group": key,
                        "era_label": group["era_label"],
                        "condition": cname,
                        "icd10": cdata["icd10"],
                        "typical_rating": cdata["typical_rating"],
                    })

        if state.get("presumptive_matches"):
            st.markdown("---")
            st.markdown("### Your selected presumptive conditions")
            match_rows = [
                {"Era": m["era_label"], "Condition": m["condition"],
                 "ICD-10": m["icd10"], "Typical Rating": m["typical_rating"]}
                for m in state["presumptive_matches"]
            ]
            st.dataframe(pd.DataFrame(match_rows), hide_index=True, use_container_width=True)
            st.success(
                f"{len(state['presumptive_matches'])} presumptive condition(s) selected. "
                "These are included in your PDF export and VA Claims Chat context."
            )

            if st.button("Add all selected presumptive conditions to issues list"):
                existing_labels = {i["label"] for i in state.get("issues", [])}
                added = 0
                for m in state["presumptive_matches"]:
                    if m["condition"] not in existing_labels:
                        state["issues"].append({"label": m["condition"]})
                        added += 1
                if added:
                    st.success(f"Added {added} condition(s) to your issues list.")
                else:
                    st.info("All selected conditions are already in your issues list.")


# ── TAB 3: Upload Evidence ─────────────────────────────────────────────────
def tab_evidence(state, tabs):
    with tabs[2]:
        st.subheader("Step 3 — Upload Medical Records & Evidence")
        st.caption(
            "Upload VA records, C&P exams, DBQs, STRs, or private records (PDF, DOCX, or TXT). "
            "The app extracts text to help build your evidence summary."
        )

        uploads = st.file_uploader(
            "Select one or more files",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
        )

        if uploads:
            for up in uploads:
                content = up.getvalue()
                doc_id = f"{up.name}:{len(content)}"
                if doc_id in [d["id"] for d in state["documents"]]:
                    continue
                text = extract_text(content, up.type, up.name)
                state["documents"].append({
                    "id": doc_id,
                    "name": up.name,
                    "mime": up.type,
                    "size": len(content),
                    "uploaded_at": datetime.utcnow().isoformat() + "Z",
                    "text": text,
                    "notes": "",
                })

        if state["documents"]:
            st.markdown("#### Uploaded documents")
            for idx, doc in enumerate(state["documents"]):
                with st.expander(f"{doc['name']} ({doc['mime']}, {doc['size']:,} bytes)"):
                    doc["notes"] = st.text_area(
                        "Notes about this document (what it proves, its relevance to your claim)",
                        value=doc.get("notes", ""),
                        key=f"doc_notes_{idx}",
                        height=60,
                    )
                    sample = (doc.get("text") or "")[:1200]
                    if sample:
                        st.text_area("First part of extracted text", sample, height=140, key=f"doc_preview_{idx}")
                    else:
                        st.info("No text extracted from this file.")

        st.markdown("---")
        st.markdown("#### Combined evidence summary")

        current = state.get("evidence_summary", "")
        col_a, col_b = st.columns([1, 2])
        with col_a:
            if st.button("Build or refresh summary"):
                all_texts = [d.get("text") or "" for d in state["documents"] if d.get("text")]
                blob = "\n\n".join(all_texts)[:15000]
                if blob:
                    with st.spinner("Analyzing records..."):
                        sys = (
                            "You summarize medical records for VA disability claims. "
                            "Write a structured summary covering diagnoses, key findings, "
                            "functional limitations, and any references to service or exposures."
                        )
                        usr = f"Summarize these records for use in a VA disability claim:\n\n{blob}"
                        current = ask_ai(sys, usr)
                        state["evidence_summary"] = current
                else:
                    st.warning("No uploaded documents with extractable text yet.")
        with col_b:
            st.caption(
                "Click to let the AI scan your uploaded records and draft a structured summary. "
                "You can edit the result below."
            )

        state["evidence_summary"] = st.text_area("Evidence summary (editable)", current, height=220)


# ── TAB 4: Symptom Mapper ──────────────────────────────────────────────────
def tab_symptom_mapper(state, tabs):
    with tabs[3]:
        st.subheader("Step 4 — Symptom to Condition Mapper")
        st.caption(
            "Describe your symptoms in your own words. The AI suggests diagnostic labels "
            "with ICD-10 codes and VA rating hints. Select the ones that apply to your claim."
        )

        note = st.text_area(
            "Describe your symptoms, flare patterns, and any relevant service exposures",
            state.get("symptom_note", ""),
            height=180,
        )
        state["symptom_note"] = note

        if st.button("Analyze symptoms and suggest conditions"):
            if note.strip():
                with st.spinner("Analyzing symptoms..."):
                    mappings, raw = map_symptoms(note[:5000])
                if mappings:
                    state["symptom_mappings"] = mappings
                    st.success(f"Found {len(mappings)} potential condition(s). Select the ones that apply.")
                else:
                    st.warning("Could not parse the AI response as JSON. Raw output shown below.")
                    st.text_area("Raw model output", raw, height=160)
            else:
                st.warning("Describe your symptoms before analyzing.")

        if state["symptom_mappings"]:
            st.markdown("---")
            st.markdown("#### Suggested conditions — select those that apply to your claim")

            all_names = [m.get("condition", "") for m in state["symptom_mappings"] if m.get("condition")]
            preselected = [
                m.get("condition") for m in state["symptom_mappings"]
                if m.get("selected_for_claim") and m.get("condition")
            ]

            selected = st.multiselect(
                "Check all conditions to include in your claim",
                all_names,
                default=preselected,
            )
            for m in state["symptom_mappings"]:
                m["selected_for_claim"] = m.get("condition") in selected

            rows = [
                {
                    "Condition": m.get("condition"),
                    "ICD-10": m.get("icd10"),
                    "Body System": m.get("body_system"),
                    "VA Rating Hint": m.get("va_rating_hint"),
                    "Rationale": m.get("rationale"),
                    "For Claim": "✓" if m.get("selected_for_claim") else "",
                }
                for m in state["symptom_mappings"]
            ]
            if rows:
                st.dataframe(rows, hide_index=True, use_container_width=True)

            if st.button("Add selected conditions to issues list"):
                existing_labels = {i["label"] for i in state.get("issues", [])}
                added = 0
                for m in state["symptom_mappings"]:
                    if m.get("selected_for_claim") and m.get("condition") not in existing_labels:
                        state["issues"].append({"label": m["condition"]})
                        added += 1
                if added:
                    st.success(f"Added {added} condition(s) to your issues list.")
                else:
                    st.info("All selected conditions are already in your issues list.")


# ── TAB 5: Statement Builder ───────────────────────────────────────────────
def tab_statement_builder(state, tabs):
    with tabs[4]:
        st.subheader("Step 5 — Statement Builder")

        # Personal statement section
        st.markdown("### Personal Statement (Lay Statement)")
        st.caption(
            "A lay statement in your own words describing how your service caused or worsened "
            "your conditions and how they affect your daily life. This is one of the most "
            "important documents you can submit with your claim."
        )

        mappings = state.get("symptom_mappings", [])
        all_conditions = [m.get("condition") for m in mappings if m.get("condition")]
        for m in state.get("presumptive_matches", []):
            if m["condition"] not in all_conditions:
                all_conditions.append(m["condition"])

        default_title = ""
        if all_conditions:
            default_title = ", ".join(all_conditions[:3])
        elif state.get("issues"):
            default_title = ", ".join(i["label"] for i in state["issues"][:3] if i.get("label"))

        title = st.text_input(
            "Statement title / claim focus",
            default_title,
            placeholder="e.g. PTSD, Lumbar Strain, and Gulf War Respiratory Illness",
        )

        selected_conditions = [
            m.get("condition") for m in mappings
            if m.get("selected_for_claim") and m.get("condition")
        ]
        focus = st.multiselect(
            "Conditions to focus on in this statement",
            all_conditions,
            default=selected_conditions,
        )

        if "latest_statement" not in st.session_state:
            st.session_state.latest_statement = ""

        if st.button("Generate personal statement", type="primary"):
            if title.strip():
                with st.spinner("Drafting your statement..."):
                    text = build_statement(state, title, focus)
                st.session_state.latest_statement = text
            else:
                st.warning("Enter a title or focus before generating.")

        edited = st.text_area(
            "Statement (editable — make it sound like your own voice)",
            st.session_state.latest_statement,
            height=300,
        )
        st.session_state.latest_statement = edited

        if st.button("Save statement to claim packet"):
            if edited.strip():
                state["claims"].append({
                    "id": f"stmt_{int(datetime.utcnow().timestamp())}",
                    "title": title or "VA Claim Statement",
                    "body": edited,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                })
                st.success("Statement saved. Review it in the Saved Claims & Export tab.")
            else:
                st.warning("Nothing to save — write or generate a statement first.")

        # Buddy statement section
        st.markdown("---")
        st.markdown("### Buddy / Lay Statement Templates")
        st.caption(
            "Statements from people who know you — a fellow veteran, family member, or employer — "
            "can significantly strengthen your claim. Select a template type, generate it, "
            "then give it to that person to complete the bracketed sections and sign."
        )

        template_type = st.selectbox(
            "Select template type",
            ["Fellow Veteran (VA Form 21-10210)", "Family Member / Spouse", "Employer / Coworker"],
        )

        conditions_for_template = [
            m.get("condition") for m in mappings if m.get("selected_for_claim") and m.get("condition")
        ]
        for m in state.get("presumptive_matches", []):
            if m["condition"] not in conditions_for_template:
                conditions_for_template.append(m["condition"])

        if st.button("Generate template"):
            prof = state.get("veteran_profile", {})
            if "Fellow Veteran" in template_type:
                tmpl = buddy_statement_fellow_veteran(prof, conditions_for_template)
            elif "Family" in template_type:
                tmpl = buddy_statement_family_member(prof, conditions_for_template)
            else:
                tmpl = buddy_statement_employer(prof, conditions_for_template)
            st.session_state["buddy_template"] = tmpl

        buddy_text = st.text_area(
            "Template (copy and send to your supporter — they fill in the [bracketed] sections and sign)",
            value=st.session_state.get("buddy_template", ""),
            height=320,
        )
        st.session_state["buddy_template"] = buddy_text

        col_save, col_dl = st.columns(2)
        with col_save:
            if st.button("Save template to claim packet"):
                if buddy_text.strip():
                    state["buddy_statements"].append({
                        "id": f"buddy_{int(datetime.utcnow().timestamp())}",
                        "type": template_type,
                        "body": buddy_text,
                        "created_at": datetime.utcnow().isoformat() + "Z",
                    })
                    st.success("Template saved to claim packet.")
                else:
                    st.warning("Generate a template first.")
        with col_dl:
            if buddy_text.strip():
                st.download_button(
                    "Download template as .txt",
                    data=buddy_text,
                    file_name=f"buddy_statement_{template_type.split('(')[0].strip().replace('/', '_').replace(' ', '_')}.txt",
                    mime="text/plain",
                )


# ── TAB 6: Rating Calculator ───────────────────────────────────────────────
def tab_rating_calculator(state, tabs):
    with tabs[5]:
        st.subheader("Step 6 — VA Combined Rating Calculator")
        st.caption(
            "The VA does NOT add percentages. It uses the 'whole person' method — each disability "
            "is applied to the remaining non-disabled portion. Enter your individual ratings to see "
            "the combined result."
        )

        st.info(
            "Results are estimates. Your final rating may differ based on bilateral factor "
            "adjustments or TDIU eligibility. Always verify with your VSO."
        )

        col_input, col_ref = st.columns([3, 2])

        with col_input:
            st.markdown("#### Enter individual disability ratings")
            st.caption("One number per line (just the percentage — no % symbol needed).")
            ratings_text = st.text_area(
                "Ratings",
                value="\n".join(str(r) for r in state.get("rating_inputs", [])),
                height=180,
                placeholder="50\n30\n20\n10",
                label_visibility="collapsed",
            )

        with col_ref:
            st.markdown("#### Common ratings reference")
            st.markdown("""
| Condition | Typical |
|-----------|---------|
| Tinnitus | 10% |
| Knee (mild) | 10% |
| Knee (moderate) | 20% |
| Lumbar strain | 10%–20% |
| Sleep Apnea w/ CPAP | 50% |
| PTSD (mild) | 30% |
| PTSD (moderate) | 50%–70% |
| Diabetes T2 | 20%–60% |
| Hypertension | 10%–60% |
| Hearing loss | 0%–100% |
""")

        parsed_ratings = []
        for line in ratings_text.splitlines():
            try:
                val = int(line.strip().replace("%", ""))
                if 0 <= val <= 100:
                    parsed_ratings.append(val)
            except ValueError:
                pass

        state["rating_inputs"] = parsed_ratings

        if st.button("Calculate combined rating", type="primary"):
            if not parsed_ratings:
                st.warning("Enter at least one rating above.")
            else:
                result = calculate_va_combined_rating(parsed_ratings)

                st.markdown("---")
                st.markdown("#### Results")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Conditions entered", len(result["sorted_ratings"]))
                with col_b:
                    st.metric("Combined (exact)", f"{result['combined_exact']}%")
                with col_c:
                    highest = max(result["sorted_ratings"], default=0)
                    delta = result["display_rating"] - highest
                    st.metric(
                        "VA Will Likely Rate At",
                        f"{result['display_rating']}%",
                        delta=f"+{delta}% above highest single" if delta > 0 else "Same as highest single",
                    )

                st.markdown("#### Step-by-step calculation")
                for step in result["steps"]:
                    st.write(f"• {step}")

                st.markdown("---")
                st.markdown("#### What does this rating mean?")
                rating = result["display_rating"]
                if rating == 0:
                    st.write("A 0% rating means VA recognizes the condition but it is non-compensable — no monthly payment.")
                elif rating < 10:
                    st.write(f"A {rating}% rating is non-compensable — VA acknowledges the condition but pays no monthly compensation.")
                elif rating < 30:
                    st.write(f"A {rating}% rating is compensable. Check current VA compensation rate tables for your monthly amount.")
                elif rating < 50:
                    st.write(f"A {rating}% rating qualifies you for VA compensation and healthcare benefits.")
                elif rating < 70:
                    st.write(
                        f"A {rating}% rating qualifies you for significant VA benefits. "
                        "At 50%+, veterans typically qualify for VA healthcare at Priority Group 1."
                    )
                elif rating < 100:
                    st.write(
                        f"A {rating}% combined rating is substantial. "
                        "If your conditions prevent substantially gainful employment, "
                        "you may qualify for **TDIU** (Total Disability Individual Unemployability) — "
                        "paid at the 100% rate. Ask your VSO about VA Form 21-8940."
                    )
                else:
                    st.write(
                        "A 100% rating provides maximum monthly compensation and full VA healthcare benefits."
                    )

                st.markdown(
                    "*Bilateral factor: If you have the same disability on both sides of your body "
                    "(e.g., both knees, both shoulders), VA adds a 10% bilateral adjustment before "
                    "the combined calculation. Add that adjustment manually to your inputs if applicable.*"
                )


# ── TAB 7: Saved Claims & Export ───────────────────────────────────────────
def tab_saved_claims(state, tabs):
    with tabs[6]:
        st.subheader("Step 7 — Saved Claims & Export")
        st.caption(
            "Review your saved statements and export your complete claim packet as a "
            "professionally formatted PDF or plain text file."
        )

        # Personal statements
        claims = state.get("claims", [])
        st.markdown("### Personal Statements")
        if not claims:
            st.info("No personal statements saved yet. Use the Statement Builder tab to generate and save.")
        else:
            remove_ids = []
            for c in claims:
                with st.expander(f"{c.get('title', 'Statement')} — {c.get('created_at', '')}"):
                    st.text_area("Text", c.get("body", ""), height=200, key=f"claim_{c.get('id')}")
                    if st.button("Remove this statement", key=f"rm_{c.get('id')}"):
                        remove_ids.append(c.get("id"))
            if remove_ids:
                state["claims"] = [c for c in claims if c.get("id") not in remove_ids]
                st.rerun()

        # Buddy statements
        buddy_stmts = state.get("buddy_statements", [])
        if buddy_stmts:
            st.markdown("### Buddy / Supporting Statement Templates")
            remove_buddy_ids = []
            for bs in buddy_stmts:
                with st.expander(f"{bs.get('type', 'Buddy Statement')} — {bs.get('created_at', '')}"):
                    st.text_area("Text", bs.get("body", ""), height=200, key=f"buddy_{bs.get('id')}")
                    if st.button("Remove this template", key=f"rmb_{bs.get('id')}"):
                        remove_buddy_ids.append(bs.get("id"))
            if remove_buddy_ids:
                state["buddy_statements"] = [b for b in buddy_stmts if b.get("id") not in remove_buddy_ids]
                st.rerun()

        # Export
        st.markdown("---")
        st.markdown("### Export Complete Claim Packet")
        st.caption(
            "The PDF includes your profile, presumptive conditions, symptom mappings, "
            "evidence summary, personal statements, and buddy statement templates — "
            "everything organized and ready to review with your VSO."
        )

        col_pdf, col_txt = st.columns(2)

        with col_pdf:
            if st.button("Generate PDF packet", type="primary"):
                with st.spinner("Building PDF..."):
                    try:
                        pdf_bytes = generate_pdf_packet(state)
                        prof = state.get("veteran_profile", {})
                        name_slug = (prof.get("full_name") or "veteran").replace(" ", "_").lower()
                        date_slug = datetime.utcnow().strftime("%Y%m%d")
                        st.download_button(
                            label="Download PDF claim packet",
                            data=pdf_bytes,
                            file_name=f"va_claimmate_{name_slug}_{date_slug}.pdf",
                            mime="application/pdf",
                            key="pdf_dl",
                        )
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")

        with col_txt:
            packet_txt = build_txt_packet(state)
            st.download_button(
                label="Download as plain text (.txt)",
                data=packet_txt,
                file_name="va_claimmate_packet.txt",
                mime="text/plain",
            )


# ── TAB 8: VA Claims Chat ──────────────────────────────────────────────────
def tab_chat(state, tabs):
    with tabs[7]:
        st.subheader("Step 8 — VA Claims Chat")
        st.caption(
            "Ask questions about your claim, VA rating criteria, evidence requirements, "
            "or next steps. The assistant uses your profile, conditions, and evidence as context. "
            "This is education only — not legal advice. Consult a VSO or accredited attorney "
            "for guidance on your specific claim."
        )

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_msg = st.chat_input("Ask a VA claim question...")
        if user_msg:
            st.session_state.chat_history.append({"role": "user", "content": user_msg})

            context = chat_context(state)
            sys = (
                "You are a VA claims education assistant. Help veterans understand VA concepts, "
                "rating criteria, evidence requirements, and how to prepare stronger claims. "
                "Do not provide legal advice and do not promise specific outcomes. "
                "If relevant, mention the veteran's specific conditions or service details from context. "
                "Suggest consulting a VSO or accredited attorney for specific claim decisions."
            )
            usr = f"Context for this veteran:\n{context}\n\nQuestion:\n{user_msg}"
            reply = ask_ai(sys, usr, temp=0.35)

            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.write(reply)

        if st.session_state.get("chat_history"):
            if st.button("Clear chat history"):
                st.session_state.chat_history = []
                st.rerun()


# ── MAIN APP UI ────────────────────────────────────────────────────────────
def app_ui():
    state = get_state()
    if state is None:
        st.error("Could not load user data.")
        return

    st.title("VA ClaimMate")

    top_col1, top_col2 = st.columns([5, 1])
    with top_col2:
        user = current_user()
        if user:
            st.caption(f"{user.get('email', '')}")
        if st.button("Logout"):
            logout()

    tabs = st.tabs([
        "1. Profile & Service",
        "2. Presumptive Conditions",
        "3. Upload Evidence",
        "4. Symptom Mapper",
        "5. Statement Builder",
        "6. Rating Calculator",
        "7. Saved Claims & Export",
        "8. VA Claims Chat",
    ])

    tab_profile(state, tabs)
    tab_presumptive(state, tabs)
    tab_evidence(state, tabs)
    tab_symptom_mapper(state, tabs)
    tab_statement_builder(state, tabs)
    tab_rating_calculator(state, tabs)
    tab_saved_claims(state, tabs)
    tab_chat(state, tabs)

    persist_state()


# ── ENTRY POINT ────────────────────────────────────────────────────────────
def main():
    if not current_user():
        auth_screen()
    else:
        app_ui()


if __name__ == "__main__":
    main()

"""
38 CFR Part 4 rating criteria for the most commonly claimed VA disabilities.

Data is simplified for educational display. Official criteria are in Title 38 Code of Federal
Regulations Part 4 (Schedule for Rating Disabilities). Always verify current criteria at
https://www.ecfr.gov/current/title-38/chapter-I/part-4 and with a VSO or accredited attorney.

Each entry contains:
  full_name         — official VA condition name
  diagnostic_code   — VA Schedule diagnostic code(s)
  cfr_ref           — 38 CFR citation
  rating_criteria   — dict {percentage: description_string}
  key_evidence      — list of what to gather before a C&P exam
  cp_tips           — exam-day tips specific to this condition
  dbq_form          — name of the Disability Benefits Questionnaire (DBQ) form
  secondary_conditions — list of conditions commonly rated as secondary to this one
"""

CONDITIONS_38CFR: dict = {
    "PTSD": {
        "full_name": "Post-Traumatic Stress Disorder",
        "diagnostic_code": "9411",
        "cfr_ref": "38 CFR §4.130, DC 9411",
        "rating_criteria": {
            100: (
                "Total occupational and social impairment due to such symptoms as: gross impairment "
                "in thought processes or communication; persistent delusions or hallucinations; "
                "grossly inappropriate behavior; persistent danger of hurting self or others; "
                "intermittent inability to perform activities of daily living; disorientation to "
                "time or place; memory loss for names of close relatives, own occupation, or own name."
            ),
            70: (
                "Occupational and social impairment with deficiencies in most areas (work, school, "
                "family relations, judgment, thinking, or mood) due to: suicidal ideation; "
                "obsessional rituals interfering with routine activities; near-continuous panic or "
                "depression affecting independent functioning; chronic sleep impairment; mild memory loss."
            ),
            50: (
                "Occupational and social impairment with reduced reliability and productivity due to: "
                "flattened affect; circumstantial or stereotyped speech; panic attacks more than once "
                "a week; difficulty understanding complex commands; impaired short- and long-term "
                "memory; disturbances of motivation and mood; difficulty maintaining work/social relationships."
            ),
            30: (
                "Occupational and social impairment with occasional decrease in work efficiency and "
                "intermittent inability to perform occupational tasks, due to: depressed mood, "
                "anxiety, suspiciousness, panic attacks weekly or less, chronic sleep impairment, "
                "mild memory loss. Generally functioning satisfactorily with routine behavior."
            ),
            10: (
                "Mild or transient symptoms decreasing work efficiency only during periods of "
                "significant stress; or symptoms controlled by continuous medication."
            ),
            0: "Formal diagnosis but symptoms not severe enough to interfere with functioning.",
        },
        "key_evidence": [
            "DSM-5 PTSD diagnosis from a mental health provider",
            "PTSD PCL-5 (Checklist for DSM-5) score — higher scores support higher ratings",
            "GAF score from treating clinician (lower GAF supports higher rating)",
            "Written or verbal documentation of occupational impairment: missed work, "
            "performance issues, disciplinary actions, terminations",
            "Social impact records: isolation, relationship breakdown, loss of hobbies",
            "Sleep study or sleep-medication records if applicable",
            "Stressor statement (VA Form 21-0781) describing the in-service trauma",
            "Buddy statements describing behavioral changes before vs. after service",
        ],
        "cp_tips": [
            "Describe your WORST days and most impaired periods — not your average day",
            "Bring a written list of ALL symptoms: nightmares, hypervigilance, avoidance, irritability, flashbacks",
            "Report every occupational impact: missed days, conflicts with supervisors, job losses",
            "Describe relationship impacts: divorce, estrangement, social withdrawal",
            "List ALL medications and any side effects that impair functioning",
            "If you have suicidal ideation — even passive — disclose it; it factors into the rating",
            "The examiner will ask about your worst week in the past month — prepare specific examples",
            "Be honest and thorough; understating symptoms is the #1 reason veterans get undertrated",
        ],
        "dbq_form": "PTSD DBQ (Mental Disorders DBQ)",
        "secondary_conditions": [
            "Major Depressive Disorder (secondary to PTSD)",
            "Generalized Anxiety Disorder (secondary to PTSD)",
            "Sleep Apnea (secondary to PTSD)",
            "Alcohol Use Disorder (secondary to PTSD)",
            "Chronic Pain Syndrome (secondary to PTSD)",
            "Irritable Bowel Syndrome (secondary to PTSD)",
            "Hypertension (secondary to PTSD)",
            "Erectile Dysfunction (secondary to PTSD / SSRIs)",
            "Migraines (secondary to PTSD)",
        ],
    },
    "Lumbar Strain / Low Back Pain": {
        "full_name": "Lumbosacral or Cervical Strain",
        "diagnostic_code": "5237",
        "cfr_ref": "38 CFR §4.71a, DC 5237",
        "rating_criteria": {
            40: "Unfavorable ankylosis of the entire thoracolumbar spine.",
            20: (
                "Forward flexion of the thoracolumbar spine 30° or less; or, "
                "favorable ankylosis of the entire thoracolumbar spine."
            ),
            10: (
                "Forward flexion greater than 30° but not greater than 60°; or, combined range of "
                "motion not greater than 120°; or, muscle spasm/guarding causing abnormal gait or "
                "abnormal spinal contour; or, vertebral body fracture with ≥50% height loss."
            ),
            0: (
                "Forward flexion greater than 60° but not greater than 85°; or, combined range of "
                "motion greater than 120° but not greater than 235°; or, muscle spasm, guarding, or "
                "localized tenderness not causing abnormal gait; or, vertebral fracture with <50% height loss."
            ),
        },
        "key_evidence": [
            "Range-of-motion measurements (goniometer) from a treating provider — flexion is the key number",
            "MRI or X-ray showing disc pathology, degeneration, stenosis, or fracture",
            "Physical therapy notes documenting functional limitations",
            "Records of incapacitating episodes (physician-ordered bedrest) — adds 10–20% on top",
            "All treating-provider records (VA and private)",
            "Functional description: activities limited by pain (bending, lifting, prolonged sitting/standing)",
            "Buddy statements describing before-vs.-after service comparison",
        ],
        "cp_tips": [
            "Do NOT warm up or stretch before the exam — cold ROM is what gets measured",
            "Report pain at end-range of motion — examiners must note this",
            "Report flare patterns: frequency, duration, and what triggers them",
            "Incapacitating episodes (forced bedrest ordered by MD) earn an extra 10–20% — document dates",
            "Radiculopathy (pain/numbness shooting into the leg) is a SEPARATE ratable condition — mention it",
            "Bring a list of all medications, injections, and procedures tried",
            "Bring imaging reports and any surgical records",
        ],
        "dbq_form": "Spine (Thoracolumbar Spine) Conditions DBQ",
        "secondary_conditions": [
            "Radiculopathy — left lower extremity (secondary to lumbar strain)",
            "Radiculopathy — right lower extremity (secondary to lumbar strain)",
            "Erectile Dysfunction (secondary to lumbar radiculopathy)",
            "Bladder/Bowel Dysfunction (secondary to lumbar — file separately)",
            "Depression/Anxiety (secondary to chronic lumbar pain)",
            "Hip Condition secondary to altered gait from lumbar",
        ],
    },
    "Cervical Strain / Neck Pain": {
        "full_name": "Cervical Strain",
        "diagnostic_code": "5237",
        "cfr_ref": "38 CFR §4.71a, DC 5237 (cervical)",
        "rating_criteria": {
            40: "Unfavorable ankylosis of the entire cervical spine.",
            30: "Favorable ankylosis of the entire cervical spine.",
            20: (
                "Forward flexion of the cervical spine 15° or less; or, "
                "combined range of motion not greater than 30°."
            ),
            10: (
                "Forward flexion greater than 15° but not greater than 30°; or, combined range of motion "
                "not greater than 170°; or, muscle spasm/guarding causing abnormal gait or spinal contour; "
                "or, vertebral fracture with ≥50% height loss."
            ),
            0: (
                "Forward flexion greater than 30° but not greater than 40°; or, combined range of motion "
                "not greater than 170°; or, muscle spasm/guarding not causing abnormal gait; "
                "or, vertebral fracture with <50% height loss."
            ),
        },
        "key_evidence": [
            "Goniometer ROM measurements (flexion, extension, lateral bending, rotation)",
            "MRI or X-ray showing disc pathology, degeneration, or fracture",
            "Physical therapy notes documenting functional limitations",
            "Documentation of the in-service incident that caused the neck injury",
            "Records of radiculopathy symptoms (arm/hand numbness or weakness)",
        ],
        "cp_tips": [
            "Do NOT warm up or stretch before the exam — measure cold ROM",
            "Report pain at end-range of motion",
            "Radiculopathy into arms/hands is a SEPARATE ratable condition — mention it explicitly",
            "Bring all imaging and PT records",
            "Report activities limited: turning head while driving, overhead work, prolonged computer use",
            "Report incapacitating episodes (bedrest ordered by MD) for extra credit",
        ],
        "dbq_form": "Spine (Cervical Spine) Conditions DBQ",
        "secondary_conditions": [
            "Radiculopathy — left upper extremity (secondary to cervical strain)",
            "Radiculopathy — right upper extremity (secondary to cervical strain)",
            "Headaches/Migraines (secondary to cervical strain)",
            "Depression/Anxiety (secondary to chronic cervical pain)",
        ],
    },
    "Knee (Limitation of Flexion)": {
        "full_name": "Limitation of Flexion, Knee",
        "diagnostic_code": "5260",
        "cfr_ref": "38 CFR §4.71a, DC 5260",
        "rating_criteria": {
            30: "Flexion limited to 15°.",
            20: "Flexion limited to 30°.",
            10: "Flexion limited to 45°.",
            0: "Flexion limited to 60°.",
        },
        "key_evidence": [
            "Goniometer ROM measurements from a provider (flexion is the key number)",
            "MRI showing meniscus tears, ACL/PCL injury, or articular damage",
            "X-ray showing joint space narrowing, bone spurs, or degenerative changes",
            "Physical therapy notes documenting functional limitation",
            "In-service injury report, line-of-duty determination, or STR noting the knee injury",
            "Records of all surgeries, injections, or procedures",
        ],
        "cp_tips": [
            "Do NOT warm up before the exam — exam measures your baseline cold ROM",
            "Report pain on movement and the exact ROM at which pain starts",
            "Instability (giving way), locking, or recurrent swelling are rated under separate codes — mention each",
            "Bilateral knees = a SEPARATE rating for each knee plus a possible bilateral factor",
            "Bring all imaging and surgical records",
            "Report ALL functional impacts: stairs, kneeling, crouching, prolonged walking",
        ],
        "dbq_form": "Knee and Lower Leg Conditions DBQ",
        "secondary_conditions": [
            "Hip Condition secondary to altered gait from knee",
            "Lower Back Pain secondary to altered gait from knee",
            "Depression/Anxiety (secondary to chronic knee pain)",
        ],
    },
    "Sleep Apnea": {
        "full_name": "Sleep Apnea Syndromes",
        "diagnostic_code": "6847",
        "cfr_ref": "38 CFR §4.97, DC 6847",
        "rating_criteria": {
            100: (
                "Chronic respiratory failure with carbon dioxide retention or cor pulmonale; "
                "or requires tracheostomy."
            ),
            50: "Requires use of a breathing assistance device such as a CPAP or BiPAP machine.",
            30: "Persistent daytime hypersomnolence.",
            0: "Asymptomatic but with documented sleep disorder breathing.",
        },
        "key_evidence": [
            "Polysomnogram (in-lab sleep study) or home sleep test with AHI score",
            "CPAP/BiPAP prescription letter — if prescribed, the standard rating is 50%",
            "Compliance report from CPAP machine (usage data / events per hour)",
            "Sleep specialist or primary care note confirming diagnosis and treatment plan",
            "Documentation of daytime symptoms: excessive sleepiness, cognitive fog, non-restorative sleep",
            "Nexus letter if claiming secondary to PTSD, TBI, or another service-connected condition",
        ],
        "cp_tips": [
            "A CPAP prescription is the key piece of evidence — if you have one, the standard rating is 50%",
            "Bring the prescription letter and sleep study report to the exam",
            "Report all daytime symptoms: fatigue, falling asleep while driving, cognitive fog",
            "If secondary to PTSD, the examiner needs a nexus letter from your treating provider",
            "Bring your CPAP machine data report showing usage and event rate",
        ],
        "dbq_form": "Sleep Apnea DBQ",
        "secondary_conditions": [
            "Hypertension (secondary to sleep apnea)",
            "Atrial Fibrillation (secondary to sleep apnea)",
            "Depression (secondary to sleep apnea)",
            "Ischemic Heart Disease (secondary to sleep apnea)",
            "Cognitive Impairment (secondary to sleep apnea)",
        ],
    },
    "Tinnitus": {
        "full_name": "Tinnitus",
        "diagnostic_code": "6260",
        "cfr_ref": "38 CFR §4.87, DC 6260",
        "rating_criteria": {
            10: (
                "Recurrent tinnitus. (10% is the ONLY compensable rating level for tinnitus — "
                "this is the ceiling under DC 6260.)"
            ),
        },
        "key_evidence": [
            "Audiologist or ENT diagnosis of tinnitus",
            "Documentation of in-service noise exposure (MOS/AFSC, weapons qualification, aircraft, machinery)",
            "Current audiological evaluation confirming tinnitus",
            "Buddy statements from fellow veterans about shared noise exposure",
        ],
        "cp_tips": [
            "Tinnitus is almost always rated 10% — that is the only compensable level",
            "Describe the character: constant vs. intermittent, pitch, bilateral vs. unilateral",
            "Report ALL functional impacts: sleep disruption, concentration difficulty, tinnitus-related anxiety",
            "Document noise-exposure details: weapons fired, aircraft maintained, vehicle noise",
            "Make sure tinnitus is listed as a SEPARATE claimed condition from hearing loss",
        ],
        "dbq_form": "Hearing Loss and Tinnitus DBQ",
        "secondary_conditions": [],
    },
    "Hearing Loss": {
        "full_name": "Hearing Loss",
        "diagnostic_code": "6100",
        "cfr_ref": "38 CFR §4.85–4.87, DC 6100",
        "rating_criteria": {
            100: "Pure tone average greater than 100 dB in both ears, or speech recognition 0% in both ears.",
            80: "Severe-to-profound loss — determined by VA Table VI / Table VIA (bilateral evaluation).",
            60: "Severe loss — per VA Table VI / Table VIA.",
            40: "Moderately severe loss — per VA Table VI / Table VIA.",
            20: "Moderate loss — per VA Table VI / Table VIA.",
            10: "Mild loss — per VA Table VI / Table VIA.",
            0: "Any hearing loss not meeting the threshold for a compensable rating.",
        },
        "key_evidence": [
            "VA-standard audiological exam performed by a state-licensed audiologist",
            "Pure Tone Averages (PTA) at 500, 1000, 2000, 3000, and 4000 Hz for both ears",
            "Speech Discrimination (Recognition) score as a percentage for both ears",
            "Documentation of in-service noise exposure",
            "Service records showing MOS/duties involving noise exposure",
            "Buddy statements about shared in-service noise exposure",
        ],
        "cp_tips": [
            "The rating is determined by a VA-standard audiogram — both PTA and speech discrimination matter",
            "Speech discrimination score determines which column in VA's rating table applies",
            "Report ALL functional impacts: mishearing conversations, TV volume, phone calls at work",
            "File tinnitus as a SEPARATE condition — it gets a separate 10% rating",
            "Bilateral hearing loss uses VA's combined bilateral table — report findings for BOTH ears",
        ],
        "dbq_form": "Hearing Loss and Tinnitus DBQ",
        "secondary_conditions": [
            "Tinnitus (secondary to noise-induced hearing loss — file separately)",
            "Depression/Anxiety (secondary to hearing loss)",
        ],
    },
    "Hypertension": {
        "full_name": "Hypertension",
        "diagnostic_code": "7101",
        "cfr_ref": "38 CFR §4.104, DC 7101",
        "rating_criteria": {
            60: "Diastolic pressure predominantly 130 or more.",
            40: "Diastolic pressure predominantly 120 or more.",
            20: (
                "Diastolic pressure predominantly 110 or more; "
                "or systolic pressure predominantly 200 or more."
            ),
            10: (
                "Diastolic pressure predominantly 100 or more; "
                "or systolic pressure predominantly 160 or more; "
                "or history of diastolic predominantly 100+ requiring continuous medication for control."
            ),
        },
        "key_evidence": [
            "Blood pressure readings from multiple visits (average/trend matters more than one reading)",
            "Current list of all antihypertensive medications and dosages",
            "Records documenting diastolic/systolic readings over time",
            "Agent Orange exposure documentation if Vietnam/Korea DMZ era (hypertension is presumptive)",
            "Nexus letter if secondary to PTSD, sleep apnea, obesity, or service-related stress",
        ],
        "cp_tips": [
            "Do NOT take extra blood pressure medication before the exam",
            "Bring a log of home BP readings (morning and evening readings over several weeks)",
            "The examiner will measure your BP on exam day — your actual reading matters",
            "List ALL medications and any side effects (fatigue, dizziness, erectile dysfunction)",
            "Agent Orange veterans: hypertension is PRESUMPTIVE — no nexus letter required",
            "If secondary to PTSD or sleep apnea, bring a nexus letter from your treating doctor",
        ],
        "dbq_form": "Hypertension DBQ",
        "secondary_conditions": [
            "Ischemic Heart Disease (secondary to hypertension)",
            "Chronic Kidney Disease / CKD (secondary to hypertension)",
            "Erectile Dysfunction (secondary to hypertension or antihypertensive medications)",
            "Stroke Residuals (secondary to hypertension)",
        ],
    },
    "Diabetes Mellitus Type 2": {
        "full_name": "Diabetes Mellitus",
        "diagnostic_code": "7913",
        "cfr_ref": "38 CFR §4.119, DC 7913",
        "rating_criteria": {
            100: (
                "More than one daily insulin injection, restricted diet, and regulated activities; "
                "with ketoacidosis or hypoglycemic reactions requiring ≥3 hospitalizations/year; "
                "or voluminous urinary output; or progressive weight and strength loss."
            ),
            60: (
                "Insulin, restricted diet, and regulated activities with 1–2 hospitalizations/year "
                "for ketoacidosis or hypoglycemia; or twice-daily insulin with EITHER restricted diet "
                "OR regulated activities."
            ),
            40: "Requires insulin AND restricted diet; or oral hypoglycemic agent AND restricted diet.",
            20: "Manageable by restricted diet only.",
            10: "Restricted diet only, with no more than occasional episodes of ketoacidosis or hypoglycemia.",
        },
        "key_evidence": [
            "HbA1c readings and trends",
            "Current medication list: insulin type, dose, frequency (number of daily injections matters)",
            "Documentation of physician-prescribed dietary restrictions",
            "Hospitalization records for DKA or hypoglycemia if applicable",
            "For Agent Orange veterans: DM Type 2 is presumptive — no nexus letter required",
            "Documentation of medication side effects",
        ],
        "cp_tips": [
            "Bring your medication list with exact insulin doses and injection frequency",
            "The number of daily insulin injections directly drives the rating — be precise",
            "Report ALL symptoms: frequent urination, blurred vision, neuropathy, slow wound healing",
            "Report dietary restrictions your doctor prescribed and how strictly you follow them",
            "Agent Orange veterans: DM Type 2 is PRESUMPTIVE — no nexus required",
            "DM leads to many secondary conditions — file each one separately",
        ],
        "dbq_form": "Diabetes Mellitus DBQ",
        "secondary_conditions": [
            "Peripheral Neuropathy — bilateral lower extremities (secondary to DM)",
            "Peripheral Neuropathy — bilateral upper extremities (secondary to DM)",
            "Erectile Dysfunction (secondary to DM)",
            "Diabetic Retinopathy / Vision Loss (secondary to DM)",
            "Chronic Kidney Disease / Nephropathy (secondary to DM)",
            "Peripheral Vascular Disease (secondary to DM)",
            "Ischemic Heart Disease (secondary to DM)",
        ],
    },
    "Ischemic Heart Disease": {
        "full_name": "Arteriosclerotic / Ischemic Heart Disease",
        "diagnostic_code": "7005",
        "cfr_ref": "38 CFR §4.104, DC 7005",
        "rating_criteria": {
            100: (
                "Chronic congestive heart failure; or workload ≤3 METs results in dyspnea, fatigue, "
                "angina, dizziness, or syncope; or left ventricular ejection fraction (EF) < 30%."
            ),
            60: (
                "More than one episode of acute congestive heart failure in the past year; or workload "
                ">3 METs but ≤5 METs causes symptoms; or EF 30–50%."
            ),
            30: (
                "Workload >5 METs but ≤7 METs causes dyspnea, fatigue, angina, dizziness, or syncope; "
                "or EF > 50%."
            ),
            10: (
                "Workload >7 METs but ≤10 METs causes symptoms; "
                "or continuous medication required."
            ),
        },
        "key_evidence": [
            "Echocardiogram with ejection fraction measurement — EF drives the rating",
            "Stress test (METs capacity) — this directly determines the rating level",
            "Cardiac catheterization or coronary angiography results",
            "List of all cardiac medications and dosages",
            "History of cardiac events: MI, stents, bypass surgery",
            "Agent Orange exposure documentation (IHD is presumptive for AO-exposed veterans)",
        ],
        "cp_tips": [
            "Ejection fraction and METs capacity are the primary rating drivers — bring all test results",
            "EF < 30% → 100%; EF 30–50% → 60%; EF > 50% → depends on exertional METs capacity",
            "Report ALL exertional symptoms: how far can you walk before chest pain/fatigue starts?",
            "Agent Orange veterans: IHD is PRESUMPTIVE — no nexus letter required",
            "Bring ALL cardiac test results: echo, stress test, cath, EKG",
            "Report medications and any dose adjustments or recent changes",
        ],
        "dbq_form": "Ischemic Heart Disease (IHD) DBQ",
        "secondary_conditions": [
            "Heart Failure (secondary to IHD)",
            "Arrhythmia (secondary to IHD)",
            "Depression/Anxiety (secondary to IHD)",
            "Erectile Dysfunction (secondary to IHD or cardiac medications)",
        ],
    },
    "Depression / Major Depressive Disorder": {
        "full_name": "Major Depressive Disorder",
        "diagnostic_code": "9434",
        "cfr_ref": "38 CFR §4.130, DC 9434",
        "rating_criteria": {
            100: "Total occupational and social impairment (same General Rating Formula as PTSD 100%).",
            70: "Occupational and social impairment with deficiencies in most areas (same as PTSD 70%).",
            50: "Occupational and social impairment with reduced reliability and productivity (PTSD 50%).",
            30: "Occasional decrease in work efficiency and intermittent inability to perform tasks (PTSD 30%).",
            10: "Mild or transient symptoms, or symptoms controlled by medication (PTSD 10%).",
            0: "Formally diagnosed but not severe enough to interfere with occupational/social functioning.",
        },
        "key_evidence": [
            "DSM-5 MDD diagnosis from a mental health provider",
            "PHQ-9 scores (document baseline and trend — scores ≥15 indicate severe depression)",
            "GAF score from treating clinician",
            "Documentation of occupational impairment: missed work, disciplinary actions, terminations",
            "Medication list (antidepressants, dosages, any changes)",
            "Hospitalization or crisis-intervention records if applicable",
            "Buddy statements about behavioral and functional changes since service",
        ],
        "cp_tips": [
            "Uses the same rating formula as PTSD — occupational and social impairment drives the rating",
            "Describe your WORST days and most impaired episodes — not just average days",
            "Report ALL occupational impacts: attendance, productivity, job losses",
            "Report social isolation, loss of relationships, inability to enjoy former activities",
            "PHQ-9 ≥15 = severe depression — bring recent scores",
            "Report suicidal ideation (even passive) if present — it is factored into the rating",
        ],
        "dbq_form": "Mental Disorders (other than PTSD and Eating Disorders) DBQ",
        "secondary_conditions": [
            "Anxiety Disorder (secondary to MDD)",
            "Insomnia (secondary to MDD)",
            "Alcohol Use Disorder (secondary to MDD)",
        ],
    },
    "Migraines": {
        "full_name": "Migraines / Headaches",
        "diagnostic_code": "8100",
        "cfr_ref": "38 CFR §4.124a, DC 8100",
        "rating_criteria": {
            50: (
                "Very frequent completely prostrating and prolonged attacks "
                "productive of severe economic inadaptability."
            ),
            30: (
                "Characteristic prostrating attacks occurring on average "
                "once a month over the last several months."
            ),
            10: (
                "Characteristic prostrating attacks averaging once in 2 months "
                "over the last several months."
            ),
            0: "Less frequent attacks.",
        },
        "key_evidence": [
            "Diagnosis from a neurologist or primary care provider",
            "Headache diary (dates, duration, severity, whether prostrating) for 3–6 months",
            "List of all preventive and abortive medications (Sumatriptan, Topamax, Botox, etc.)",
            "Documentation of work absences or missed activities due to migraines",
            "ER visits or urgent care records for migraine treatment",
            "In-service records: head trauma, TBI, or PTSD connection to headaches",
        ],
        "cp_tips": [
            "FREQUENCY and PROSTRATION are the key rating drivers — track them carefully",
            "Keep a headache diary for 3–6 months before the exam — bring it",
            "'Prostrating' means completely bedridden, unable to perform ANY activities, requiring darkness and quiet",
            "Document work impacts: missed days, early departures, performance warnings",
            "Report ALL medications and their effectiveness",
            "If secondary to TBI or PTSD, bring a nexus letter",
            "Report aura, nausea/vomiting, photophobia — these help characterize severity",
        ],
        "dbq_form": "Headaches (including Migraine Headaches) DBQ",
        "secondary_conditions": [
            "Depression/Anxiety (secondary to chronic migraines)",
        ],
    },
    "GERD / Acid Reflux": {
        "full_name": "Hiatal Hernia / GERD",
        "diagnostic_code": "7346",
        "cfr_ref": "38 CFR §4.114, DC 7346",
        "rating_criteria": {
            60: (
                "Symptoms of pain, vomiting, material weight loss, and hematemesis or melena "
                "with moderate anemia; or other symptom combinations productive of severe impairment of health."
            ),
            30: (
                "Persistently recurrent epigastric distress with dysphagia, pyrosis, and regurgitation, "
                "accompanied by substernal or arm/shoulder pain, productive of considerable impairment of health."
            ),
            10: "Two or more of the 30% symptoms at lesser severity.",
        },
        "key_evidence": [
            "Diagnosis from gastroenterologist or primary care",
            "Upper endoscopy (EGD) results if available (shows esophagitis, Barrett's, etc.)",
            "List of all medications (PPIs, H2 blockers, antacids) and dosages",
            "Documentation of physician-prescribed dietary restrictions",
            "Weight-loss records if significant weight loss has occurred",
            "Frequency and severity of symptoms: heartburn, regurgitation, dysphagia, chest pain",
        ],
        "cp_tips": [
            "Describe ALL symptoms: heartburn frequency, regurgitation, difficulty swallowing",
            "Report chest/arm/shoulder pain — this can elevate the rating",
            "Document dietary restrictions your doctor prescribed",
            "Report sleep disruption (nocturnal regurgitation, needing to elevate head of bed)",
            "If secondary to NSAIDs used for service-connected musculoskeletal pain, note that connection",
            "Report any history of Barrett's esophagus or esophagitis found on endoscopy",
        ],
        "dbq_form": "Esophageal Conditions (including GERD) DBQ",
        "secondary_conditions": [
            "Sleep Disturbance (secondary to GERD)",
            "Depression/Anxiety (secondary to chronic GERD)",
        ],
    },
    "TBI (Traumatic Brain Injury)": {
        "full_name": "Residuals of Traumatic Brain Injury",
        "diagnostic_code": "8045",
        "cfr_ref": "38 CFR §4.124a, DC 8045",
        "rating_criteria": {
            100: (
                "Total disability — assigned when Schedule criteria for all TBI residuals combined do not "
                "adequately reflect total functional impairment (§4.16)."
            ),
            70: (
                "Three or more cognitive impairment symptoms at Level 3 (§4.124a Table II) OR "
                "emotional/behavioral symptoms at Level 3 (Table III)."
            ),
            50: "Three or more cognitive or emotional/behavioral symptoms at moderate severity.",
            30: "One or two cognitive or emotional/behavioral symptoms at mild-to-moderate levels.",
            10: "Subjective symptoms that don't interfere with routine work and social activities.",
            0: "Purely subjective complaints with no objective findings.",
        },
        "key_evidence": [
            "Documentation of the TBI event: in-service medical record, line-of-duty determination",
            "Neuropsychological testing results",
            "Brain MRI or CT scan results",
            "Neurology or neuropsychiatry evaluation",
            "Comprehensive list of ALL residual symptoms: memory, cognition, headaches, mood, sleep, balance",
            "Documentation of how each residual impairs daily and occupational functioning",
        ],
        "cp_tips": [
            "TBI is rated on its RESIDUALS — you must document every residual symptom separately",
            "Common residuals: migraines, cognitive deficits, vestibular/balance problems, mood disorders",
            "Each residual can be rated SEPARATELY — list every symptom you experience",
            "Bring neuropsychological test results and all brain imaging reports",
            "PTSD and TBI often co-occur — both should be claimed and rated separately",
            "Sleep disturbance, chronic pain, and depression secondary to TBI are all separately ratable",
        ],
        "dbq_form": "Traumatic Brain Injury (TBI) Residuals DBQ",
        "secondary_conditions": [
            "Migraines (secondary to TBI)",
            "PTSD (secondary to or concurrent with TBI)",
            "Depression (secondary to TBI)",
            "Sleep Apnea (secondary to TBI)",
            "Seizure Disorder (secondary to TBI)",
            "Vestibular/Balance Disorder (secondary to TBI)",
            "Cognitive Disorder (secondary to TBI)",
        ],
    },
    "Peripheral Neuropathy": {
        "full_name": "Peripheral Neuropathy",
        "diagnostic_code": "8520",
        "cfr_ref": "38 CFR §4.124a, DC 8520–8530",
        "rating_criteria": {
            80: "Complete paralysis — foot drops; no active movement below knee; knee flexion weak or lost.",
            60: (
                "Incomplete paralysis, severe — persistent limb disability; severe constant pain; "
                "marked muscular atrophy; foot drop."
            ),
            40: "Incomplete paralysis, moderately severe.",
            20: "Incomplete paralysis, moderate.",
            10: "Incomplete paralysis, mild.",
        },
        "key_evidence": [
            "Nerve conduction velocity (NCV) study or EMG results",
            "Neurologist or podiatrist documentation",
            "Detailed symptom description: burning, tingling, numbness, weakness in each extremity",
            "Functional limitations: difficulty walking, using stairs, balance problems, falls",
            "Nexus letter connecting neuropathy to the primary condition (diabetes, AO, chemical exposure)",
        ],
        "cp_tips": [
            "Bilateral neuropathy = SEPARATE rating for each affected extremity (left leg, right leg, etc.)",
            "Report ALL sensory symptoms: burning, tingling, numbness, electrical sensations",
            "Report motor symptoms: weakness, foot drop, balance problems, falls",
            "If secondary to diabetes or Agent Orange presumptive, bring nexus documentation",
            "NCV/EMG test results are very helpful — bring them",
            "Upper-extremity and lower-extremity neuropathy are rated separately",
        ],
        "dbq_form": "Peripheral Nerves Conditions DBQ",
        "secondary_conditions": [
            "Depression/Anxiety (secondary to chronic neuropathic pain)",
            "Sleep Disturbance (secondary to neuropathic pain)",
            "Falls / Balance Disorder (secondary to neuropathy)",
        ],
    },
    "Erectile Dysfunction": {
        "full_name": "Deformity of Penis with Loss of Erectile Power",
        "diagnostic_code": "7522",
        "cfr_ref": "38 CFR §4.115b, DC 7522",
        "rating_criteria": {
            0: (
                "Non-compensable rating of 0%. HOWEVER: veterans with service-connected ED are "
                "entitled to Special Monthly Compensation (SMC) at the 'K rate' "
                "(approximately $118–125/month on top of regular compensation) for loss of use of "
                "a creative organ. This is separate from the combined-disability rating."
            ),
        },
        "key_evidence": [
            "Treating provider's diagnosis of erectile dysfunction",
            "Nexus letter connecting ED to the primary service-connected condition",
            "Common primary conditions: PTSD, DM, peripheral neuropathy, hypertension, "
            "lumbar radiculopathy, TBI, or medications (beta-blockers, SSRIs, diuretics)",
            "Documentation of medications that cause ED as a side effect",
        ],
        "cp_tips": [
            "ED is rated 0% BUT qualifies for Special Monthly Compensation (SMC-K)",
            "SMC-K adds ~$118–125/month ON TOP of your regular compensation — always file for it",
            "The nexus letter is critical — your doctor must connect ED to the service-connected condition",
            "Common nexus conditions: PTSD, DM, peripheral neuropathy, lumbar radiculopathy",
            "Even if only one SC condition causes ED, you are entitled to SMC-K",
        ],
        "dbq_form": "Male Reproductive System Conditions DBQ",
        "secondary_conditions": [],
    },
}

# ── Alias lookup ────────────────────────────────────────────────────────────
# Maps common veteran-entered terms to keys in CONDITIONS_38CFR.
CONDITION_ALIASES: dict[str, str] = {
    "ptsd": "PTSD",
    "post traumatic stress": "PTSD",
    "post-traumatic stress": "PTSD",
    "post-traumatic stress disorder": "PTSD",
    "back pain": "Lumbar Strain / Low Back Pain",
    "lower back": "Lumbar Strain / Low Back Pain",
    "lumbar": "Lumbar Strain / Low Back Pain",
    "lumbosacral": "Lumbar Strain / Low Back Pain",
    "low back pain": "Lumbar Strain / Low Back Pain",
    "lumbar strain": "Lumbar Strain / Low Back Pain",
    "neck pain": "Cervical Strain / Neck Pain",
    "cervical": "Cervical Strain / Neck Pain",
    "cervical strain": "Cervical Strain / Neck Pain",
    "sleep apnea": "Sleep Apnea",
    "osa": "Sleep Apnea",
    "obstructive sleep apnea": "Sleep Apnea",
    "tinnitus": "Tinnitus",
    "ringing in ears": "Tinnitus",
    "ringing ears": "Tinnitus",
    "hearing loss": "Hearing Loss",
    "hearing": "Hearing Loss",
    "hypertension": "Hypertension",
    "high blood pressure": "Hypertension",
    "htn": "Hypertension",
    "diabetes": "Diabetes Mellitus Type 2",
    "diabetes mellitus": "Diabetes Mellitus Type 2",
    "dm type 2": "Diabetes Mellitus Type 2",
    "type 2 diabetes": "Diabetes Mellitus Type 2",
    "dm2": "Diabetes Mellitus Type 2",
    "knee": "Knee (Limitation of Flexion)",
    "knee pain": "Knee (Limitation of Flexion)",
    "knee condition": "Knee (Limitation of Flexion)",
    "ischemic heart disease": "Ischemic Heart Disease",
    "ihd": "Ischemic Heart Disease",
    "coronary artery disease": "Ischemic Heart Disease",
    "cad": "Ischemic Heart Disease",
    "depression": "Depression / Major Depressive Disorder",
    "major depressive disorder": "Depression / Major Depressive Disorder",
    "mdd": "Depression / Major Depressive Disorder",
    "migraines": "Migraines",
    "migraine": "Migraines",
    "headaches": "Migraines",
    "headache": "Migraines",
    "gerd": "GERD / Acid Reflux",
    "acid reflux": "GERD / Acid Reflux",
    "heartburn": "GERD / Acid Reflux",
    "reflux": "GERD / Acid Reflux",
    "tbi": "TBI (Traumatic Brain Injury)",
    "traumatic brain injury": "TBI (Traumatic Brain Injury)",
    "brain injury": "TBI (Traumatic Brain Injury)",
    "neuropathy": "Peripheral Neuropathy",
    "peripheral neuropathy": "Peripheral Neuropathy",
    "ed": "Erectile Dysfunction",
    "erectile dysfunction": "Erectile Dysfunction",
}


def lookup_condition(query: str) -> dict | None:
    """Return the CFR entry for a condition name or alias. Case-insensitive.

    Tries in order: exact key match, alias match, substring key match,
    substring alias match. Returns None if nothing matches.
    """
    q = query.lower().strip()
    for key in CONDITIONS_38CFR:
        if key.lower() == q:
            return CONDITIONS_38CFR[key]
    if q in CONDITION_ALIASES:
        return CONDITIONS_38CFR[CONDITION_ALIASES[q]]
    for key in CONDITIONS_38CFR:
        if q in key.lower():
            return CONDITIONS_38CFR[key]
    for alias, key in CONDITION_ALIASES.items():
        if q in alias:
            return CONDITIONS_38CFR[key]
    return None


def find_matching_conditions(condition_list: list) -> list:
    """Return [(original_name, cfr_data), ...] for every condition that matches the database.

    Deduplicates by full_name so the same condition mapped via different aliases
    appears only once.
    """
    results = []
    seen: set = set()
    for cond in condition_list:
        data = lookup_condition(cond)
        if data and data["full_name"] not in seen:
            results.append((cond, data))
            seen.add(data["full_name"])
    return results

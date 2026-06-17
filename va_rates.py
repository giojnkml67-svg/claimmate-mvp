"""VA disability compensation rate tables and estimator.

Rates effective December 1, 2025 (2.8% COLA), the amounts payable
throughout 2026. Source: U.S. Department of Veterans Affairs,
https://www.va.gov/disability/compensation-rates/veteran-rates/

These figures are kept in one place so they are easy to verify and to
update each December when the new COLA takes effect. To update for a new
year, replace the dollar values below and bump RATES_EFFECTIVE.

The VA does NOT add disability percentages together — see
``calculate_va_combined_rating`` in app.py for the "whole person" combine.
This module converts an already-combined rating into an estimated monthly
payment, including additional amounts for a spouse, dependent children,
and dependent parents.

Accuracy note: every column below is anchored to published VA values.
The VA pays a slightly higher amount for the FIRST dependent child under
18 than for each additional child. To avoid shipping unverified numbers,
this estimator applies the published "each additional child under 18"
amount to every child under 18, so estimates for veterans claiming
children may be a few dollars conservative. The result is always labeled
an estimate and links to the official VA calculator for exact figures.
"""

RATES_EFFECTIVE = "December 1, 2025"
VA_RATES_URL = "https://www.va.gov/disability/compensation-rates/veteran-rates/"

# Ratings under 30% pay a flat amount; dependents do not increase it.
FLAT_RATES = {
    0: 0.00,
    10: 180.42,
    20: 356.66,
}

# Basic monthly rate for a veteran alone (no dependents), 30%–100%.
BASE_ALONE = {
    30: 552.47,
    40: 795.84,
    50: 1132.90,
    60: 1435.02,
    70: 1808.45,
    80: 2102.15,
    90: 2362.30,
    100: 3938.58,
}

# Added amount for a spouse (no Aid & Attendance).
ADD_SPOUSE = {
    30: 65.00,
    40: 87.00,
    50: 109.00,
    60: 131.00,
    70: 153.00,
    80: 175.00,
    90: 197.00,
    100: 219.59,
}

# Added amount per dependent parent (the VA allows up to two).
ADD_PER_PARENT = {
    30: 52.00,
    40: 70.00,
    50: 88.00,
    60: 105.00,
    70: 123.00,
    80: 140.00,
    90: 158.00,
    100: 176.24,
}

# Added amount per child under age 18.
ADD_CHILD_UNDER_18 = {
    30: 32.00,
    40: 43.00,
    50: 54.00,
    60: 65.00,
    70: 75.87,
    80: 86.40,
    90: 97.99,
    100: 109.11,
}

# Added amount per child over 18 in a qualifying school program.
ADD_CHILD_IN_SCHOOL = {
    30: 105.00,
    40: 140.00,
    50: 176.00,
    60: 211.00,
    70: 246.00,
    80: 281.00,
    90: 317.00,
    100: 352.45,
}

# Added amount when a spouse qualifies for Aid & Attendance.
ADD_SPOUSE_AID_ATTENDANCE = {
    30: 61.00,
    40: 81.00,
    50: 101.00,
    60: 121.00,
    70: 141.00,
    80: 161.00,
    90: 181.00,
    100: 201.41,
}

VALID_RATINGS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def snap_to_rating(rating) -> int:
    """Snap any number to the nearest valid VA rating step (0–100 by 10s)."""
    try:
        r = float(rating)
    except (TypeError, ValueError):
        return 0
    r = max(0, min(100, r))
    # Nearest valid rating; on an exact tie (e.g. 75) round up.
    return min(VALID_RATINGS, key=lambda v: (abs(v - r), -v))


def estimate_monthly_compensation(
    rating,
    spouse: bool = False,
    children_under_18: int = 0,
    children_in_school: int = 0,
    dependent_parents: int = 0,
    spouse_aid_attendance: bool = False,
) -> dict:
    """Estimate the monthly VA disability payment for a combined rating.

    Returns a dict with the total and an itemized breakdown so the figure
    can be shown transparently.
    """
    r = snap_to_rating(rating)
    children_under_18 = max(0, int(children_under_18 or 0))
    children_in_school = max(0, int(children_in_school or 0))
    dependent_parents = max(0, min(2, int(dependent_parents or 0)))

    breakdown = []

    if r < 30:
        total = FLAT_RATES.get(r, 0.00)
        if r == 0:
            note = "A 0% rating is recognized but non-compensable (no monthly payment)."
        else:
            note = (
                f"At {r}%, the VA pays a flat rate. Dependents do not increase "
                "compensation until you reach 30%."
            )
        breakdown.append((f"Base rate at {r}%", total))
        return {
            "rating": r,
            "total": round(total, 2),
            "breakdown": breakdown,
            "note": note,
            "effective": RATES_EFFECTIVE,
        }

    base = BASE_ALONE[r]
    total = base
    breakdown.append((f"Base rate at {r}% (veteran alone)", base))

    if spouse:
        amt = ADD_SPOUSE[r]
        total += amt
        breakdown.append(("Spouse", amt))
        if spouse_aid_attendance:
            aa = ADD_SPOUSE_AID_ATTENDANCE[r]
            total += aa
            breakdown.append(("Spouse Aid & Attendance", aa))

    if dependent_parents:
        amt = ADD_PER_PARENT[r] * dependent_parents
        total += amt
        label = "Dependent parent" + ("s" if dependent_parents > 1 else "")
        breakdown.append((f"{label} ({dependent_parents})", amt))

    if children_under_18:
        amt = ADD_CHILD_UNDER_18[r] * children_under_18
        total += amt
        breakdown.append((f"Children under 18 ({children_under_18})", amt))

    if children_in_school:
        amt = ADD_CHILD_IN_SCHOOL[r] * children_in_school
        total += amt
        breakdown.append((f"Children 18+ in school ({children_in_school})", amt))

    return {
        "rating": r,
        "total": round(total, 2),
        "breakdown": breakdown,
        "note": "",
        "effective": RATES_EFFECTIVE,
    }


def rate_overview() -> list:
    """A simple veteran-alone vs. with-spouse snapshot across all ratings."""
    rows = []
    for r in VALID_RATINGS:
        if r == 0:
            continue
        alone = estimate_monthly_compensation(r)["total"]
        with_spouse = estimate_monthly_compensation(r, spouse=True)["total"]
        rows.append({"rating": r, "alone": alone, "with_spouse": with_spouse})
    return rows

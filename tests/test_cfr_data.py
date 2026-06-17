"""Tests for cfr_data: 38 CFR criteria lookup and secondary-condition data."""

import cfr_data


def test_all_conditions_have_required_keys():
    required = {"full_name", "diagnostic_code", "cfr_ref", "rating_criteria",
                "key_evidence", "cp_tips", "dbq_form", "secondary_conditions"}
    for name, entry in cfr_data.CONDITIONS_38CFR.items():
        missing = required - entry.keys()
        assert not missing, f"{name} is missing keys: {missing}"


def test_rating_criteria_percentages_valid():
    for name, entry in cfr_data.CONDITIONS_38CFR.items():
        for pct in entry["rating_criteria"]:
            assert isinstance(pct, int), f"{name}: rating key {pct!r} is not int"
            assert 0 <= pct <= 100, f"{name}: rating {pct} out of 0–100 range"


def test_lookup_exact_key():
    result = cfr_data.lookup_condition("PTSD")
    assert result is not None
    assert result["diagnostic_code"] == "9411"


def test_lookup_case_insensitive():
    assert cfr_data.lookup_condition("ptsd") is not None
    assert cfr_data.lookup_condition("PTSD") is not None
    assert cfr_data.lookup_condition("Ptsd") is not None


def test_lookup_alias():
    result = cfr_data.lookup_condition("back pain")
    assert result is not None
    assert "Lumbosacral" in result["full_name"]


def test_lookup_alias_diabetes():
    result = cfr_data.lookup_condition("diabetes")
    assert result is not None
    assert result["diagnostic_code"] == "7913"


def test_lookup_partial_key():
    result = cfr_data.lookup_condition("sleep apnea")
    assert result is not None
    assert result["diagnostic_code"] == "6847"


def test_lookup_no_match():
    result = cfr_data.lookup_condition("xyznotacondition")
    assert result is None


def test_find_matching_conditions_deduplicates():
    # "ptsd" and "PTSD" and "post traumatic stress" all point to the same entry.
    matches = cfr_data.find_matching_conditions(["ptsd", "PTSD", "post traumatic stress"])
    assert len(matches) == 1


def test_find_matching_conditions_multiple():
    matches = cfr_data.find_matching_conditions(["tinnitus", "hypertension", "xyz_unknown"])
    names = [m[0] for m in matches]
    assert "tinnitus" in names
    assert "hypertension" in names
    assert "xyz_unknown" not in names
    assert len(matches) == 2


def test_secondary_conditions_are_lists():
    for name, entry in cfr_data.CONDITIONS_38CFR.items():
        assert isinstance(entry["secondary_conditions"], list), (
            f"{name}: secondary_conditions must be a list"
        )


def test_known_secondary_conditions():
    ptsd = cfr_data.CONDITIONS_38CFR["PTSD"]
    sc_lower = [s.lower() for s in ptsd["secondary_conditions"]]
    assert any("sleep apnea" in s for s in sc_lower)
    assert any("depressive" in s or "depression" in s for s in sc_lower)

    dm = cfr_data.CONDITIONS_38CFR["Diabetes Mellitus Type 2"]
    sc_lower_dm = [s.lower() for s in dm["secondary_conditions"]]
    assert any("neuropathy" in s for s in sc_lower_dm)
    assert any("erectile" in s for s in sc_lower_dm)


def test_erectile_dysfunction_smk_note_present():
    ed = cfr_data.CONDITIONS_38CFR["Erectile Dysfunction"]
    criteria_text = " ".join(ed["rating_criteria"].values()).lower()
    assert "smc" in criteria_text or "special monthly" in criteria_text


def test_ptsd_100_criteria_mentions_hallucinations():
    ptsd = cfr_data.CONDITIONS_38CFR["PTSD"]
    assert "hallucinations" in ptsd["rating_criteria"][100].lower()


def test_sleep_apnea_50_mentions_cpap():
    sa = cfr_data.CONDITIONS_38CFR["Sleep Apnea"]
    assert "cpap" in sa["rating_criteria"][50].lower() or "breathing assistance" in sa["rating_criteria"][50].lower()


def test_all_cp_tips_are_nonempty_strings():
    for name, entry in cfr_data.CONDITIONS_38CFR.items():
        for tip in entry["cp_tips"]:
            assert isinstance(tip, str) and tip.strip(), f"{name}: empty CP tip found"

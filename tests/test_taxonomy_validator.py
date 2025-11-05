import os
import json
import pytest


TAX_PATH = os.path.join(os.getcwd(), "local_inference",
                        "emotional_taxonomy.json")


def load_taxonomy(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def assert_msg(cond, msg):
    assert cond, msg


def test_canonical_taxonomy_schema():
    """
    Validate a canonical emotional taxonomy file against the project's expectations.

    The test is intentionally skipped when no `local_inference/emotional_taxonomy.json`
    file is present; place the canonical file there (or point CI to it) to run validation.
    """
    if not os.path.exists(TAX_PATH):
        pytest.skip(
            f"No canonical taxonomy found at {TAX_PATH}; skipping validator")

    tax = load_taxonomy(TAX_PATH)

    # Root structure
    assert_msg(isinstance(tax, dict),
               "taxonomy must be a JSON object at the root")
    assert_msg("emotional_tags" in tax and isinstance(tax["emotional_tags"], list),
               "root must contain 'emotional_tags' as an array of tag objects")
    assert_msg("escalation_tiers" in tax and isinstance(tax["escalation_tiers"], dict),
               "root must contain 'escalation_tiers' as an object")

    escalation_keys = set(tax["escalation_tiers"].keys())
    allowed_tiers = {"tier_1", "tier_2", "tier_3"}
    # All escalation tier keys must be subset of allowed tiers
    assert_msg(escalation_keys.issubset(allowed_tiers),
               f"escalation_tiers keys must be subset of {allowed_tiers}; found: {escalation_keys}")

    # Validate emotional_tags array
    canonical_tags = []
    for idx, tag_obj in enumerate(tax["emotional_tags"]):
        assert_msg(isinstance(tag_obj, dict),
                   f"each emotional tag must be an object (index {idx})")

        # Required field: canonical_tag (string)
        ct = tag_obj.get("canonical_tag")
        assert_msg(isinstance(ct, str) and ct.strip(),
                   f"tag at index {idx} missing or invalid 'canonical_tag'")
        canonical_tags.append(ct)

        # tier must be present and valid
        tier = tag_obj.get("tier")
        assert_msg(isinstance(tier, str) and tier in allowed_tiers,
                   f"tag '{ct}' has invalid 'tier' value: {tier}")
        # ensure tier exists in escalation_tiers
        assert_msg(tier in tax["escalation_tiers"],
                   f"tag '{ct}' references unknown tier '{tier}' not present in escalation_tiers")

        # synonyms if present must be list of strings and not duplicate canonical tags
        syns = tag_obj.get("synonyms", [])
        if syns is not None:
            assert_msg(isinstance(syns, list),
                       f"'synonyms' for tag '{ct}' must be a list if present")
            for s in syns:
                assert_msg(isinstance(s, str),
                           f"each synonym for '{ct}' must be a string")

        # editorial_flags if present must be list of strings
        eflags = tag_obj.get("editorial_flags", [])
        if eflags is not None:
            assert_msg(isinstance(eflags, list),
                       f"'editorial_flags' for '{ct}' must be a list if present")
            for ef in eflags:
                assert_msg(isinstance(ef, str),
                           f"editorial_flag '{ef}' for '{ct}' must be a string")

        # Optional: tone_sensitive requires description
        if isinstance(eflags, list) and "tone_sensitive" in eflags:
            desc = tag_obj.get("description")
            assert_msg(isinstance(desc, str) and desc.strip(),
                       f"tag '{ct}' marked 'tone_sensitive' must include a non-empty 'description'")

        # Optional: cluster_sensitive requires tier_2 membership
        if isinstance(eflags, list) and "cluster_sensitive" in eflags:
            assert_msg(tier == "tier_2",
                       f"tag '{ct}' marked 'cluster_sensitive' must be assigned to 'tier_2' (found '{tier}')")

    # All canonical_tag values must be unique
    duplicates = [t for t in canonical_tags if canonical_tags.count(t) > 1]
    assert_msg(len(duplicates) == 0,
               f"duplicate canonical_tag values found: {set(duplicates)}")

    # Ensure synonyms do not duplicate canonical tags
    all_syns = []
    for tag_obj in tax["emotional_tags"]:
        for s in tag_obj.get("synonyms", []) or []:
            all_syns.append(s)
            assert_msg(s not in canonical_tags,
                       f"synonym '{s}' duplicates an existing canonical_tag")

    # Ensure escalation_tiers reference canonical tags only (if tiers are lists of tag names)
    for tier_key, tier_list in tax["escalation_tiers"].items():
        if isinstance(tier_list, list):
            for t in tier_list:
                assert_msg(t in canonical_tags,
                           f"escalation_tiers['{tier_key}'] contains unknown tag '{t}' not listed in emotional_tags")

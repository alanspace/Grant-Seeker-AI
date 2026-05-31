"""
Filter Accuracy Test Suite
===========================

Tests apply_filters_to_results() with concrete, deterministic grant fixtures.
No API calls required — all data is hardcoded.

Run with:
    python -m pytest tests/test_filter_accuracy.py -v
Or for detailed output:
    python -m pytest tests/test_filter_accuracy.py -v -s
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from backend.filters import apply_filters_to_results

# ============================================================================
# GRANT FIXTURES
# A representative sample covering all filter dimensions.
# ============================================================================

GRANTS = [
    # --- Women-led grants ---
    {
        "id": 1,
        "title": "Women Entrepreneurship Fund",
        "funder": "ISED Canada",
        "amount": "$50,000",
        "funding_nature": "Non-repayable Grant",
        "geography": "National (Federal Canada-wide)",
        "founder_demographics": ["Women-led", "Female founders"],
        "description": "Funding for women-owned businesses in Canada.",
    },
    {
        "id": 2,
        "title": "Female Innovators Program",
        "funder": "FedDev Ontario",
        "amount": "$10,000 - $25,000",
        "funding_nature": "Grant",
        "geography": "Ontario",
        "founder_demographics": ["female entrepreneurs"],
        "description": "Supports female-led startups in Ontario.",
    },

    # --- Indigenous-led grants ---
    {
        "id": 3,
        "title": "Indigenous Business Development Grant",
        "funder": "Indigenous Services Canada",
        "amount": "$100,000",
        "funding_nature": "Grant",
        "geography": "National (Federal Canada-wide)",
        "founder_demographics": ["Indigenous", "First Nations", "Inuit", "Métis"],
        "description": "Supports Indigenous-owned enterprises across Canada.",
    },
    {
        "id": 4,
        "title": "Aboriginal Tourism Fund",
        "funder": "Canadian Tourism Commission",
        "amount": "$30,000 - $75,000",
        "funding_nature": "Contribution",
        "geography": "British Columbia",
        "founder_demographics": ["Aboriginal", "Indigenous communities"],
        "description": "Supports tourism businesses led by Aboriginal peoples.",
    },

    # --- Youth-led grants ---
    {
        "id": 5,
        "title": "Youth Employment Strategy",
        "funder": "Employment and Social Development Canada",
        "amount": "$15,000",
        "funding_nature": "Grant",
        "geography": "National (Federal Canada-wide)",
        "founder_demographics": ["Youth (under 30)", "Young entrepreneurs"],
        "description": "Helps young Canadians gain work experience.",
    },

    # --- No demographics (general grants) ---
    {
        "id": 6,
        "title": "Clean Technology Research Grant",
        "funder": "Natural Resources Canada",
        "amount": "$500,000",
        "funding_nature": "Non-repayable Grant",
        "geography": "National (Federal Canada-wide)",
        "founder_demographics": [],
        "description": "Funding for clean energy R&D projects.",
    },
    {
        "id": 7,
        "title": "Export Market Development Fund",
        "funder": "Trade Commissioner Service",
        "amount": "$5,000 - $50,000",
        "funding_nature": "Repayable Loan",
        "geography": "National (Federal Canada-wide)",
        "founder_demographics": [],
        "description": "Helps Canadian businesses expand into export markets.",
    },

    # --- Provincial grants ---
    {
        "id": 8,
        "title": "Ontario Small Business Grant",
        "funder": "Ontario Ministry of Economic Development",
        "amount": "$20,000",
        "funding_nature": "Grant",
        "geography": "Ontario",
        "founder_demographics": [],
        "description": "Supports small businesses in Ontario.",
    },
    {
        "id": 9,
        "title": "BC Innovation Fund",
        "funder": "BC Ministry of Jobs",
        "amount": "$75,000 - $200,000",
        "funding_nature": "Grant",
        "geography": "British Columbia",
        "founder_demographics": ["Women-led"],
        "description": "Supports innovative businesses in British Columbia.",
    },

    # --- Tax credit ---
    {
        "id": 10,
        "title": "Scientific Research Tax Credit (SR&ED)",
        "funder": "Canada Revenue Agency",
        "amount": "15-35% of R&D costs",
        "funding_nature": "Tax Credit",
        "geography": "National (Federal Canada-wide)",
        "founder_demographics": [],
        "description": "Tax incentive for Canadian companies conducting R&D.",
    },

    # --- Large grant ---
    {
        "id": 11,
        "title": "Strategic Innovation Fund",
        "funder": "Innovation, Science and Economic Development Canada",
        "amount": "$10,000,000",
        "funding_nature": "Contribution",
        "geography": "National (Federal Canada-wide)",
        "founder_demographics": [],
        "description": "Large-scale support for transformative innovation projects.",
    },

    # --- Unspecified amount ---
    {
        "id": 12,
        "title": "Community Foundation Grant",
        "funder": "Community Foundations of Canada",
        "amount": "Not specified",
        "funding_nature": "Grant",
        "geography": "National (Federal Canada-wide)",
        "founder_demographics": ["Women-led"],
        "description": "Community-driven projects supporting Canadian communities.",
    },
]

NO_FILTER = {
    'demographic_focus': [],
    'funding_min': None,
    'funding_max': None,
    'funding_types': [],
    'geographic_scope': '',
    'applicant_type': '',
    'project_stage': '',
}


def make_filter(**kwargs):
    """Build a filter dict with defaults for all unset keys."""
    f = dict(NO_FILTER)
    f.update(kwargs)
    return f


def ids(grants):
    return sorted(g['id'] for g in grants)


# ============================================================================
# DEMOGRAPHIC FILTER TESTS
# ============================================================================

def test_no_filters_returns_all():
    """No filters → all grants returned."""
    result = apply_filters_to_results(GRANTS, NO_FILTER)
    assert len(result) == len(GRANTS), f"Expected {len(GRANTS)}, got {len(result)}"


def test_women_filter_returns_only_women_grants():
    """Women filter → women-tagged grants + untagged (open-to-all) grants; explicit non-women excluded."""
    f = make_filter(demographic_focus=["Women-led / Female Founders"])
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = set(g['id'] for g in result)
    # Must include: women-tagged (1, 2, 9, 12) + untagged general grants (6, 7, 8, 10, 11)
    assert {1, 2, 9, 12}.issubset(returned_ids), "Women-tagged grants must be included"
    assert {6, 7, 8, 10, 11}.issubset(returned_ids), "Untagged general grants must pass through"
    # Must exclude: exclusively Indigenous-tagged grant 3, exclusively Youth-tagged grant 5
    assert 3 not in returned_ids, "Indigenous-only grant should be excluded"
    assert 5 not in returned_ids, "Youth-only grant should be excluded"


def test_indigenous_filter_matches_various_terms():
    """Indigenous filter → indigenous-tagged + untagged grants; women/youth-only excluded."""
    f = make_filter(demographic_focus=["Indigenous-led (First Nations, Inuit, Métis)"])
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = set(g['id'] for g in result)
    # Grants 3 and 4 are indigenous/aboriginal → must be included
    assert 3 in returned_ids, "Indigenous grant 3 must be included"
    assert 4 in returned_ids, "Aboriginal grant 4 must be included"
    # Untagged general grants → pass through
    assert {6, 7, 8, 10, 11}.issubset(returned_ids), "Untagged general grants must pass through"
    # Women-only and youth-only grants must be excluded
    assert 1 not in returned_ids, "Women-only grant 1 should be excluded"
    assert 5 not in returned_ids, "Youth-only grant 5 should be excluded"


def test_youth_filter():
    """Youth filter → youth-tagged + untagged grants; women/indigenous-only excluded."""
    f = make_filter(demographic_focus=["Youth-led (Under 30)"])
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = set(g['id'] for g in result)
    assert 5 in returned_ids, "Youth-tagged grant 5 must be included"
    assert {6, 7, 8, 10, 11}.issubset(returned_ids), "Untagged grants must pass through"
    assert 1 not in returned_ids, "Women-only grant 1 should be excluded"
    assert 3 not in returned_ids, "Indigenous-only grant 3 should be excluded"


def test_multi_demographic_or_logic():
    """Multiple demographics → OR logic; untagged general grants also pass through."""
    f = make_filter(demographic_focus=["Women-led / Female Founders", "Youth-led (Under 30)"])
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = set(g['id'] for g in result)
    # Women-tagged (1, 2, 9, 12) and youth-tagged (5) must be included
    assert {1, 2, 5, 9, 12}.issubset(returned_ids), "Women + youth grants must be included"
    # Untagged general grants must pass through
    assert {6, 7, 8, 10, 11}.issubset(returned_ids), "Untagged grants must pass through"
    # Indigenous-only grant must be excluded (explicitly tagged, no overlap)
    assert 3 not in returned_ids, "Indigenous-only grant should be excluded"


def test_demographic_filter_passes_untagged_grants():
    """Grants with no demographics field are treated as 'open to all' and pass through."""
    f = make_filter(demographic_focus=["Women-led / Female Founders"])
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = set(g['id'] for g in result)
    # Grants 6, 7, 8, 10, 11 have no demographics — treated as open to all, must pass through.
    no_demo_ids = {6, 7, 8, 10, 11}
    assert no_demo_ids.issubset(returned_ids), f"General grants should pass demographic filter: {no_demo_ids - returned_ids} missing"
    # Women-tagged grants (1, 2, 9, 12) must be included
    assert {1, 2, 9, 12}.issubset(returned_ids), "Women-tagged grants must be included"
    # Explicitly non-matching demographic tags must be excluded
    assert 3 not in returned_ids, "Indigenous-only grant 3 should be excluded"
    assert 5 not in returned_ids, "Youth-only grant 5 should be excluded"


# ============================================================================
# FUNDING AMOUNT FILTER TESTS
# ============================================================================

def test_funding_min_excludes_small_grants():
    """Min $50,000 → excludes grants whose max offered amount is below threshold."""
    f = make_filter(funding_min=50000)
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 5 ($15,000) and grant 8 ($20,000) must be excluded
    assert 5 not in returned_ids, "Grant 5 ($15k) should be filtered out"
    assert 8 not in returned_ids, "Grant 8 ($20k) should be filtered out"
    # Grant 6 ($500,000) must be included
    assert 6 in returned_ids, "Grant 6 ($500k) should be included"
    # Grant 12 has "Not specified" amount — excluded when min is set
    assert 12 not in returned_ids, "Grant 12 (unspecified amount) should be excluded when min is set"


def test_funding_max_excludes_large_grants():
    """Max $50,000 → excludes grants whose minimum offered amount exceeds threshold."""
    f = make_filter(funding_max=50000)
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 11 ($10M) must be excluded
    assert 11 not in returned_ids, "Grant 11 ($10M) should be filtered out with max=$50k"
    # Grant 6 ($500k) must be excluded
    assert 6 not in returned_ids, "Grant 6 ($500k) should be filtered out with max=$50k"
    # Grant 5 ($15k) must be included
    assert 5 in returned_ids, "Grant 5 ($15k) should be included within max=$50k"


def test_funding_range_filter():
    """Range $20k–$100k → only grants whose amounts overlap with this range."""
    f = make_filter(funding_min=20000, funding_max=100000)
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 5 ($15k) — max=$15k < min=$20k → excluded
    assert 5 not in returned_ids, "Grant 5 ($15k) below range"
    # Grant 11 ($10M) — min=$10M > max=$100k → excluded
    assert 11 not in returned_ids, "Grant 11 ($10M) above range"
    # Grant 1 ($50k) — overlaps → included
    assert 1 in returned_ids, "Grant 1 ($50k) within range"
    # Grant 3 ($100k) — exactly at max → included
    assert 3 in returned_ids, "Grant 3 ($100k) at upper boundary"


def test_unspecified_amount_excluded_when_min_set():
    """Grant with 'Not specified' amount is excluded if user sets a minimum."""
    f = make_filter(funding_min=1000)
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    assert 12 not in returned_ids, "Unspecified-amount grant should be excluded when min is set"


def test_unspecified_amount_passes_when_only_max_set():
    """Grant with 'Not specified' amount passes if only a max is set (no min)."""
    f = make_filter(funding_max=500000)
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    assert 12 in returned_ids, "Unspecified-amount grant should pass when only max is set"


# ============================================================================
# FUNDING TYPE FILTER TESTS
# ============================================================================

def test_grant_type_excludes_loans():
    """Non-repayable Grant filter → excludes loans."""
    f = make_filter(funding_types=["Non-repayable Grant"])
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 7 is a "Repayable Loan" and must be excluded
    assert 7 not in returned_ids, "Repayable Loan should be excluded when Grant filter is active"


def test_grant_type_includes_contributions():
    """Non-repayable Grant filter → includes 'Contribution' and 'Fund' types (common Canadian naming)."""
    f = make_filter(funding_types=["Non-repayable Grant"])
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 4 is a "Contribution" — treated as grant-like
    assert 4 in returned_ids, "Contribution should be accepted as grant-like"
    # Grant 11 is a "Contribution" — also accepted
    assert 11 in returned_ids, "Contribution should be accepted as grant-like"


def test_loan_type_filter():
    """Repayable Loan filter → only returns loans."""
    f = make_filter(funding_types=["Repayable Loan / Contribution"])
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 7 is the only explicit loan
    assert 7 in returned_ids, "Loan grant should appear"
    # Pure grants should be excluded
    assert 1 not in returned_ids, "Grant type should not appear in loan filter"


def test_tax_credit_filter():
    """Tax Credit filter → returns tax credit grants only."""
    f = make_filter(funding_types=["Tax Credit"])
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    assert 10 in returned_ids, "SR&ED tax credit should be returned"
    assert 1 not in returned_ids, "Regular grant should not appear in tax credit filter"


# ============================================================================
# GEOGRAPHY FILTER TESTS
# ============================================================================

def test_ontario_filter():
    """Ontario filter → only Ontario and federal (Canada-wide) grants."""
    f = make_filter(geographic_scope="Ontario")
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 8 is Ontario-specific
    assert 8 in returned_ids, "Ontario grant should be included"
    # Grant 2 is Ontario-specific
    assert 2 in returned_ids, "Ontario grant should be included"
    # Grant 4 is BC-only — must be excluded
    assert 4 not in returned_ids, "BC grant should be excluded for Ontario filter"
    # Grant 9 is BC-only — must be excluded
    assert 9 not in returned_ids, "BC grant should be excluded for Ontario filter"


def test_bc_filter():
    """BC filter → only BC and federal grants."""
    f = make_filter(geographic_scope="British Columbia")
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    assert 4 in returned_ids, "BC grant should be included"
    assert 9 in returned_ids, "BC grant should be included"
    assert 8 not in returned_ids, "Ontario grant should be excluded for BC filter"
    assert 2 not in returned_ids, "Ontario grant should be excluded for BC filter"


# ============================================================================
# COMBINED FILTER TESTS
# ============================================================================

def test_women_plus_ontario():
    """Women-led + Ontario → only women grants in Ontario or Canada-wide."""
    f = make_filter(
        demographic_focus=["Women-led / Female Founders"],
        geographic_scope="Ontario"
    )
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 2: female, Ontario → included
    assert 2 in returned_ids
    # Grant 1: women, Canada-wide → included (canada in geography)
    assert 1 in returned_ids
    # Grant 9: women, BC → excluded
    assert 9 not in returned_ids


def test_women_plus_grant_type():
    """Women-led + Non-repayable Grant → women grants AND general grants, no loans."""
    f = make_filter(
        demographic_focus=["Women-led / Female Founders"],
        funding_types=["Non-repayable Grant"]
    )
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grants with non-matching explicit demographic tags must be excluded
    # Grant 3 is explicitly Indigenous-only → excluded
    assert 3 not in returned_ids, "Indigenous-only grant should be excluded by Women filter"
    # No loans should slip through
    for g in result:
        assert 'loan' not in g.get('funding_nature', '').lower(), \
            f"Grant {g['id']} '{g['title']}' is a loan but passed grant type filter"


def test_amount_range_plus_indigenous():
    """Indigenous + $30k–$150k range."""
    f = make_filter(
        demographic_focus=["Indigenous-led (First Nations, Inuit, Métis)"],
        funding_min=30000,
        funding_max=150000
    )
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 3: Indigenous, $100k → within range, included
    assert 3 in returned_ids
    # Grant 4: Indigenous/Aboriginal, $30k-$75k → within range, included
    assert 4 in returned_ids


def test_empty_results_input():
    """Empty input always returns empty list regardless of filters."""
    f = make_filter(demographic_focus=["Women-led / Female Founders"])
    result = apply_filters_to_results([], f)
    assert result == []


def test_none_filter_returns_all():
    """None filter dict → returns all grants unchanged."""
    result = apply_filters_to_results(GRANTS, None)
    assert len(result) == len(GRANTS)


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_filter_is_strict_and_logic():
    """All active filters must match — AND logic across filter types."""
    f = make_filter(
        demographic_focus=["Women-led / Female Founders"],
        funding_types=["Non-repayable Grant"],
        geographic_scope="British Columbia",
        funding_min=50000
    )
    result = apply_filters_to_results(GRANTS, f)
    returned_ids = {g['id'] for g in result}
    # Grant 9: women-led, Grant type, BC, $75k-$200k → all conditions met
    assert 9 in returned_ids, "Grant 9 should pass all four filters"
    # Grant 1: women-led, Grant type, Canada-wide, $50k — passes if 'canada' in geography
    # Grant 2: Ontario — excluded by BC geo filter
    assert 2 not in returned_ids, "Grant 2 (Ontario) should be excluded by BC filter"


def test_national_filter_includes_federal_geography():
    """National filter should accept grants with geography='Federal' (not just 'Canada')."""
    test_grants = [
        {"id": 101, "title": "Federal Youth Loan", "funder": "Government",
         "amount": "$50,000", "funding_nature": "Repayable Loan",
         "geography": "Federal", "founder_demographics": ["Youth"], "description": ""},
        {"id": 102, "title": "Pan-Canadian Innovation", "funder": "Government",
         "amount": "$100,000", "funding_nature": "Grant",
         "geography": "Pan-Canadian", "founder_demographics": [], "description": ""},
        {"id": 103, "title": "Ontario-Only Program", "funder": "Province",
         "amount": "$20,000", "funding_nature": "Grant",
         "geography": "Ontario", "founder_demographics": [], "description": ""},
    ]
    f = make_filter(geographic_scope="National (Federal Canada-wide)")
    result = apply_filters_to_results(test_grants, f)
    returned_ids = {g['id'] for g in result}
    assert 101 in returned_ids, "'Federal' geography should pass National filter"
    assert 102 in returned_ids, "'Pan-Canadian' geography should pass National filter"
    assert 103 not in returned_ids, "Province-only grant should be excluded by National filter"


def test_provincial_filter_includes_national_grants():
    """Provincial filter should still include national/federal grants."""
    test_grants = [
        {"id": 201, "title": "Alberta Local Grant", "funder": "Province",
         "amount": "$25,000", "funding_nature": "Grant",
         "geography": "Alberta", "founder_demographics": [], "description": ""},
        {"id": 202, "title": "Federal Business Loan", "funder": "Government",
         "amount": "$75,000", "funding_nature": "Repayable Loan",
         "geography": "Canada", "founder_demographics": [], "description": ""},
        {"id": 203, "title": "BC-Only Fund", "funder": "Province",
         "amount": "$30,000", "funding_nature": "Grant",
         "geography": "British Columbia", "founder_demographics": [], "description": ""},
    ]
    f = make_filter(geographic_scope="Alberta")
    result = apply_filters_to_results(test_grants, f)
    returned_ids = {g['id'] for g in result}
    assert 201 in returned_ids, "Alberta grant should be included"
    assert 202 in returned_ids, "National/federal grant should be included for any province"
    assert 203 not in returned_ids, "BC grant should be excluded for Alberta filter"


def test_case_insensitive_demographic_matching():
    """Demographics matching should be case-insensitive."""
    f = make_filter(demographic_focus=["Women-led / Female Founders"])
    # Inject a grant with uppercase WOMEN
    test_grants = [{
        "id": 99,
        "title": "WOMEN Startup Fund",
        "funder": "Test",
        "amount": "$10,000",
        "funding_nature": "Grant",
        "geography": "Canada",
        "founder_demographics": ["WOMEN entrepreneurs"],
        "description": "Uppercase demographic test",
    }]
    result = apply_filters_to_results(test_grants, f)
    assert len(result) == 1, "Should match uppercase WOMEN demographic"


def test_partial_word_match_in_demographics():
    """'female' substring in 'female innovators' should match Women filter."""
    test_grants = [{
        "id": 99,
        "title": "Female Innovators",
        "funder": "Test",
        "amount": "$10,000",
        "funding_nature": "Grant",
        "geography": "Canada",
        "founder_demographics": ["female innovators in STEM"],
        "description": "Partial match test",
    }]
    f = make_filter(demographic_focus=["Women-led / Female Founders"])
    result = apply_filters_to_results(test_grants, f)
    assert len(result) == 1, "Should match 'female' substring in demographics"

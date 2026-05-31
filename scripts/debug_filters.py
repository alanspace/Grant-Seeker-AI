"""
Diagnose filter behaviour for the UI scenario:
  keyword = 'quantum computing'
  demographic = Youth-led
  funding_type = Repayable Loan
  geography = National
  applicant_type = Startup
  project_stage = R&D
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from backend.filters import apply_filters_to_results

FILTERS = {
    'demographic_focus': ['Youth-led (Under 30)'],
    'funding_min': None,
    'funding_max': None,
    'funding_types': ['Repayable Loan / Contribution'],
    'geographic_scope': 'National (Federal Canada-wide)',
    'applicant_type': 'For-profit / Startup',
    'project_stage': 'Early Stage / R&D',
}

# 12 representative grants — cover all the ways the backend might return data
GRANTS = [
    {
        "id": 1, "title": "BDC Young Entrepreneurs Loan",
        "founder_demographics": ["Youth (under 30)", "Young entrepreneurs"],
        "funding_nature": "Repayable Loan",
        "geography": "National (Federal Canada-wide)",
        "amount": "$50,000",
        "description": "BDC offers repayable loans for young Canadian startups.",
    },
    {
        "id": 2, "title": "Canada Student Loan Bursary",
        "founder_demographics": ["Youth", "Students"],
        "funding_nature": "Repayable Loan",
        "geography": "Canada",                     # <-- shorter form
        "amount": "$15,000",
        "description": "Federal student loan assistance for youth under 30.",
    },
    {
        "id": 3, "title": "NSERC Research Grant",
        "founder_demographics": [],                 # no demographics
        "funding_nature": "Non-repayable Grant",
        "geography": "National (Federal Canada-wide)",
        "amount": "$250,000",
        "description": "Supports university research in Canada.",
    },
    {
        "id": 4, "title": "Women Entrepreneurship Loan",
        "founder_demographics": ["Women-led", "Female founders"],
        "funding_nature": "Repayable Loan",
        "geography": "National (Federal Canada-wide)",
        "amount": "$100,000",
        "description": "Loans for women-led businesses.",
    },
    {
        "id": 5, "title": "Ontario Youth Innovation Grant",
        "founder_demographics": ["Youth-led", "young"],
        "funding_nature": "Non-repayable Grant",
        "geography": "Ontario",                    # provincial only
        "amount": "$25,000",
        "description": "Non-repayable grant for Ontario youth startups.",
    },
    {
        "id": 6, "title": "Indigenous Business Loan",
        "founder_demographics": ["Indigenous", "First Nations"],
        "funding_nature": "Repayable Loan",
        "geography": "Canada",
        "amount": "$75,000",
        "description": "Financing for Indigenous-owned businesses.",
    },
    {
        "id": 7, "title": "Tech Startup Loan Program",
        "founder_demographics": ["Youth (Under 30)", "young innovators"],
        "funding_nature": "Repayable Loan / Contribution",
        "geography": "Federal",                    # yet another form
        "amount": "$30,000 - $100,000",
        "description": "Loans for tech startups led by youth.",
    },
    {
        "id": 8, "title": "BC Clean Tech Fund",
        "founder_demographics": ["Youth"],
        "funding_nature": "Repayable Loan",
        "geography": "British Columbia",           # provincial only
        "amount": "$200,000",
        "description": "Supports clean tech in BC.",
    },
    {
        "id": 9, "title": "SR&ED Tax Credit",
        "founder_demographics": [],
        "funding_nature": "Tax Credit",
        "geography": "National (Federal Canada-wide)",
        "amount": "15-35% of R&D costs",
        "description": "Federal tax credit for R&D activities.",
    },
    {
        "id": 10, "title": "Futurpreneur Canada Loan",
        "founder_demographics": ["Youth (18-39)", "young entrepreneurs"],
        "funding_nature": "Repayable Loan",
        "geography": "Canada-wide",               # another variation
        "amount": "Up to $20,000",
        "description": "Startup loans for young Canadian entrepreneurs aged 18-39.",
    },
]

print("=" * 70)
print("FILTER TEST: quantum computing / Youth / Repayable Loan / National")
print("=" * 70)

result = apply_filters_to_results(GRANTS, FILTERS)
print(f"\nResults after filtering: {len(result)}/{len(GRANTS)} grants passed\n")

for g in result:
    print(f"  ✅ [{g['id']}] {g['title']}")
    print(f"       demo={g['founder_demographics']}")
    print(f"       type={g['funding_nature']}  geo={g['geography']}")

if not result:
    print("  ❌ No grants passed — tracing why each was dropped:\n")

print("\n--- Per-grant trace ---")
for g in GRANTS:
    reasons = []

    # Demo check
    demo_filter = FILTERS['demographic_focus']
    gd = [d.lower() for d in g['founder_demographics']]
    keyword_map = {
        'women':     ['women', 'woman', 'female', 'girl'],
        'indigenous':['indigenous', 'first nations', 'inuit', 'métis', 'aboriginal'],
        'youth':     ['youth', 'young', 'student'],
    }
    if demo_filter:
        if not gd:
            reasons.append("no demographics field")
        else:
            matched = False
            for df in demo_filter:
                dfl = df.lower()
                terms = {dfl}
                for key, kw in keyword_map.items():
                    if key in dfl:
                        terms.update(kw)
                if any(t in d for d in gd for t in terms):
                    matched = True
                    break
            if not matched:
                reasons.append(f"demographics {g['founder_demographics']} don't match {demo_filter}")

    # Funding type check
    fn = g['funding_nature'].lower()
    ft_filters = FILTERS['funding_types']
    if ft_filters:
        type_ok = False
        for ft in ft_filters:
            f = ft.lower()
            if 'loan' in f:
                ok = ('loan' in fn or
                      ('repayable' in fn and 'non-repayable' not in fn) or
                      'debt' in fn or 'financing' in fn)
            elif 'grant' in f:
                ok = ('grant' in fn or 'contribution' in fn or 'non-repayable' in fn
                      or 'fund' in fn or 'award' in fn or 'bursary' in fn)
            else:
                ok = (f in fn or fn in f)
            if ok:
                type_ok = True
                break
        if not type_ok:
            reasons.append(f"funding_nature='{g['funding_nature']}' doesn't match {ft_filters}")

    # Geography check
    geo_filter = FILTERS['geographic_scope'].lower()
    geo_grant = g['geography'].lower()
    if geo_filter:
        if geo_filter not in geo_grant and 'canada' not in geo_grant:
            reasons.append(f"geography='{g['geography']}' doesn't contain '{geo_filter}' or 'canada'")

    status = "✅ PASS" if not reasons else "❌ FAIL"
    print(f"\n  {status} [{g['id']}] {g['title']}")
    for r in reasons:
        print(f"       → Filtered: {r}")

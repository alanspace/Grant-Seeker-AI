"""
Shared filtering logic for Grant Seeker.
Extracted to resolve circular dependencies between frontend and backend.
"""
import re

def apply_filters_to_results(results, filters):
    """
    Apply Advanced Filters to real backend search results.
    
    Filters real grants based on:
    - Demographics (founder demographics field) 
    - Funding amount range
    - Funding type (grant vs loan)
    - Geographic scope  
    - Applicant type
    - Project stage
    
    Args:
        results: List of grants from backend search
        filters: Dictionary of active filter selections
    
    Returns:
        Filtered list of grants matching all selected criteria
    """
    if not results:
        return []
        
    if not filters:
        return results
    
    filtered = []
    
    for grant in results:
        # Filter 1: Demographic Focus
        # Grants that carry an explicit demographic tag must match the selected focus.
        # Grants with NO demographic tag are treated as "open to all" and always pass —
        # many government programs don't restrict by demographic but are still eligible.
        if filters.get('demographic_focus'):
            grant_demographics = grant.get('founder_demographics', [])

            # No tag → open to all → pass through
            if grant_demographics:
                # Check if grant matches ANY of the selected demographics
                demographic_match = False

                # Keyword expansion map
                keyword_map = {
                    'women': ['women', 'woman', 'female', 'girl'],
                    'indigenous': ['indigenous', 'first nations', 'inuit', 'métis', 'aboriginal'],
                    'youth': ['youth', 'young', 'student']
                }

                for demo_filter in filters['demographic_focus']:
                    demo_lower = demo_filter.lower()

                    # Build search terms
                    search_terms = {demo_lower}
                    for key, terms in keyword_map.items():
                        if key in demo_lower:
                            search_terms.update(terms)

                    # Check for match against grant data
                    if any(term in gd.lower() for gd in grant_demographics for term in search_terms):
                        demographic_match = True
                        break

                if not demographic_match:
                    continue
        
        # Filter 2: Funding Amount Range
        funding_min = filters.get('funding_min')
        funding_max = filters.get('funding_max')
        
        if funding_min is not None or funding_max is not None:
            # Extract numeric amount from grant (rough parsing)
            amount_str = grant.get('amount', '')
            
            # Skip if no amount specified - strictness depends on use case
            # Here: if we have a strict min filter, we skip undefined amounts
            if not amount_str or 'not specified' in amount_str.lower() or 'unknown' in amount_str.lower():
                if funding_min is not None:
                     continue
            else:
                 # Parse numbers from string (e.g., "$5,000 - $10,000" -> [5000, 10000])
                 # Remove commas and find all digit sequences that look like numbers
                 numbers = [float(n.replace(',', '')) for n in re.findall(r'\d[\d,]*', amount_str) if n.replace(',', '').isdigit()]
                 
                 if numbers:
                     min_found = min(numbers)
                     max_found = max(numbers) # Safe: numbers list is guaranteed non-empty
                     
                     # 1. Check Minimum:
                     # If the LARGEST amount offered is still less than user's minimum, reject.
                     if funding_min is not None and max_found < float(funding_min):
                         continue
                         
                     # 2. Check Maximum:
                     # If the SMALLEST amount offered is larger than user's maximum, reject.
                     if funding_max is not None and min_found > float(funding_max): # Safe: min_found is valid float
                         continue
        
        # Filter 3: Funding Type
        if filters.get('funding_types'):
            grant_funding_type = grant.get('funding_nature', '').lower()
            
            def check_funding_match(grant_str, filter_str):
                g = grant_str.lower()
                f = filter_str.lower()
                
                if 'grant' in f: # User wants Non-repayable / Grant
                    # Explicit reject if it's strictly a loan/repayable
                    if 'loan' in g: return False
                    if 'repayable' in g and 'non-repayable' not in g: return False
                    
                    # Accept if it looks like free money
                    # Note: Many Canadian grants are called "Contributions" or "Funds"
                    return ('grant' in g or 
                            'contribution' in g or 
                            'non-repayable' in g or 
                            'fund' in g or
                            'award' in g or
                            'bursary' in g)
                            
                if 'loan' in f: # User wants Loan
                    return ('loan' in g or 
                            ('repayable' in g and 'non-repayable' not in g) or
                            'debt' in g or 
                            'financing' in g)
                
                # Fallback for other types (Tax Credit, Wage Subsidy)
                return f in g or g in f

            type_match = any(check_funding_match(grant_funding_type, ft) for ft in filters['funding_types'])
            
            if not type_match:
                continue
        
        # Filter 4: Geographic Scope
        if filters.get('geographic_scope'):
            grant_geography = grant.get('geography', '').lower()
            geo_filter = filters['geographic_scope'].lower()

            # Terms that all indicate "national / federal / all of Canada"
            NATIONAL_TERMS = (
                'canada', 'national', 'federal', 'pan-canadian',
                'all provinces', 'coast to coast', 'country-wide',
                'canada-wide', 'pan canadian', 'canadawide',
            )
            filter_is_national = any(t in geo_filter for t in NATIONAL_TERMS)
            grant_is_national  = any(t in grant_geography for t in NATIONAL_TERMS)

            if filter_is_national:
                # User specifically wants federal/national grants → only national grants pass
                geo_pass = grant_is_national
            else:
                # User wants a province/territory → include provincial match OR national grants
                # (federal grants apply everywhere, so they are always relevant)
                geo_pass = geo_filter in grant_geography or grant_is_national

            if not geo_pass:
                continue

        # Filter 5: Applicant Type
        # The backend Pydantic model does not include a structured applicant_type field,
        # so we only hard-filter when the grant explicitly stores one.  When the field is
        # absent we let the grant through—the selection is already used as a search hint.
        if filters.get('applicant_type'):
            explicit_type = grant.get('applicant_type', '').strip()
            if explicit_type:
                applicant_filter = filters['applicant_type'].lower()
                APPLICANT_KEYWORD_MAP = {
                    'startup':      ['startup', 'start-up', 'early stage', 'new business', 'entrepreneur'],
                    'non-profit':   ['non-profit', 'nonprofit', 'not-for-profit', 'charity', 'charitable'],
                    'social':       ['social enterprise', 'social entrepreneurship'],
                    'co-operative': ['co-operative', 'cooperative', 'co-op'],
                    'for-profit':   ['for-profit', 'profit', 'corporation', 'business', 'company', 'enterprise'],
                    'sme':          ['sme', 'small business', 'medium business', 'small and medium'],
                }
                search_terms = {applicant_filter}
                for key, terms in APPLICANT_KEYWORD_MAP.items():
                    if key in applicant_filter:
                        search_terms.update(terms)
                if not any(t in explicit_type.lower() for t in search_terms):
                    continue

        # Filter 6: Project Stage
        # Same rationale as above: only hard-filter when the structured field is present.
        if filters.get('project_stage'):
            explicit_stage = grant.get('project_stage', '').strip()
            if explicit_stage:
                stage_filter = filters['project_stage'].lower()
                STAGE_KEYWORD_MAP = {
                    'early stage':  ['early stage', 'early-stage', 'pre-seed', 'seed', 'prototype', 'proof of concept'],
                    'r&d':          ['r&d', 'research and development', 'research & development', 'research', 'development', 'innovation'],
                    'growth':       ['growth', 'scaling', 'scale-up', 'expansion', 'growing'],
                    'commerciali':  ['commercialisation', 'commercialization', 'market-ready', 'launch'],
                }
                search_terms = {stage_filter}
                for key, terms in STAGE_KEYWORD_MAP.items():
                    if key in stage_filter:
                        search_terms.update(terms)
                if not any(t in explicit_stage.lower() for t in search_terms):
                    continue

        # If grant passed all filters, include it
        filtered.append(grant)
    
    return filtered

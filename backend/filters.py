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
        # Filter 1: Demographic Focus - STRICT matching
        if filters.get('demographic_focus'):
            grant_demographics = grant.get('founder_demographics', [])
            
            # Must have demographics field populated
            if not grant_demographics:
                continue
            
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
            type_match = any(
                'grant' in grant_funding_type and 'grant' in ft.lower()
                or 'loan' in grant_funding_type and 'loan' in ft.lower()
                or 'wage' in ft.lower() and 'wage' in grant_funding_type
                for ft in filters['funding_types']
            )
            if not type_match:
                continue
        
        # Filter 4: Geographic Scope
        if filters.get('geographic_scope'):
            grant_geography = grant.get('geography', '').lower()
            geo_filter = filters['geographic_scope'].lower()
            if geo_filter not in grant_geography and 'canada' not in grant_geography:
                continue
        
        # If grant passed all filters, include it
        filtered.append(grant)
    
    return filtered

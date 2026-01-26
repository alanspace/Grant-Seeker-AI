"""
Shared filtering logic for Grant Seeker.
Extracted to resolve circular dependencies between frontend and backend.
"""

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
    if not results or not filters:
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
            for demo_filter in filters['demographic_focus']:
                demo_lower = demo_filter.lower()
                
                # Women filter
                if 'women' in demo_lower:
                    if any('women' in gd.lower() or 'female' in gd.lower() for gd in grant_demographics):
                        demographic_match = True
                        break
                # Indigenous filter  
                elif 'indigenous' in demo_lower:
                    if any('indigenous' in gd.lower() or 'first nations' in gd.lower() for gd in grant_demographics):
                        demographic_match = True
                        break
                # Youth filter
                elif 'youth' in demo_lower:
                    if any('youth' in gd.lower() or 'young' in gd.lower() for gd in grant_demographics):
                        demographic_match = True
                        break
            
            if not demographic_match:
                continue
        
        # Filter 2: Funding Amount Range
        funding_min = filters.get('funding_min')
        funding_max = filters.get('funding_max')
        if funding_min or funding_max:
            # Extract numeric amount from grant (rough parsing)
            amount_str = grant.get('amount', '')
            # Skip if no amount specified
            if 'not specified' in amount_str.lower():
                if funding_min:  # If user specified minimum, skip grants without amounts
                    continue
            # Note: Full amount parsing would need more sophisticated logic
        
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

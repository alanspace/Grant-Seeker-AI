# test_ui.py
import api

print("--- TESTING API LAYER ---")

# 1. Test Search
print("\n1. Testing find_grants()...")
results = api.find_grants("Urban community garden")
print(f"Found {len(results)} grants.")
first_grant_id = results[0]['id']

# 2. Test Analysis
print(f"\n2. Testing get_grant_details() for ID {first_grant_id}...")
details = api.get_grant_details(first_grant_id)
print("Details retrieved.")

# 3. Test Writing
print("\n3. Testing draft_proposal()...")
draft = api.draft_proposal("Urban community garden", details)
print("\nFINAL OUTPUT SAMPLE:")
print(draft[:200] + "...")
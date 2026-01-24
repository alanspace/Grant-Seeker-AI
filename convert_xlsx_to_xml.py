import pandas as pd
import hashlib
import time
from datetime import datetime

# Read the Excel file using openpyxl engine
# We assume the file is in the same directory
try:
    df = pd.read_excel('v5_Canadian_Grants_& Loans_Spreadsheet.xlsx', engine='openpyxl')
except FileNotFoundError as e:
    print(f"❌ Error: Excel file not found - {e}")
    print("   Please ensure 'v5_Canadian_Grants_& Loans_Spreadsheet.xlsx' is in the current directory")
    exit(1)
except Exception as e:
    error_type = type(e).__name__
    print(f"❌ Error reading Excel file: {error_type}")
    print(f"   Details: {str(e)}")
    exit(1)

# Clean column names (strip whitespace and newlines)
df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]

# Map relevant columns to XML attributes
# Looking at the JSON output:
# 'URL / CONTACT' -> about (we need to clean this up, might be null or multiple)
# 'Instrument Type' -> label (maybe?)
# 'PROGRAM / FUND NAME' -> additional data?

# We will generate <Annotation> elements.

xml_output = '<?xml version="1.0" encoding="UTF-8"?><Annotations>\n'

# Helper to generate timestamp
# The example annotations.xml uses a hex timestamp? 0x0006485618d2a0a1 matches ~2023
# We will just generate a hex timestamp based on current time or a deterministic hash
current_time = int(time.time() * 1000)

for index, row in df.iterrows():
    url = str(row.get('URL / CONTACT', '')).strip()
    
    # Skip empty URLs or "nan"
    if not url or url.lower() == 'nan' or url.lower() == 'null':
        continue
    
    # Handle multiple URLs in one cell (split by newline or space if messy)
    # For now, just take the first one if it looks like a URL
    urls = url.split()
    target_url = urls[0] if urls else ""
    
    if not target_url.startswith('http'):
        continue

    # Clean URL for 'about' attribute
    # Remove protocol
    clean_url = target_url.replace('https://', '').replace('http://', '').rstrip('/')
    
    # Handle www prefix logic
    if clean_url.startswith('www.'):
        clean_url = clean_url[4:]
    
    # Construct the pattern: *.domain.com/*
    # This matches the domain and any subdomains/paths
    about_pattern = f"*.{clean_url}/*"
    
    # Generate timestamp
    hex_ts = hex(current_time + index)

    program_name = str(row.get('PROGRAM / FUND NAME', '')).strip()
    
    xml_output += f'  <Annotation about="{about_pattern}" timestamp="{hex_ts}" score="1.0">\n'
    xml_output += f'    <Label name="_include_"/>\n'
    xml_output += f'    <AdditionalData attribute="original_url" value="{target_url}"/>\n'
    # Optional: Comment out program name if it causes issues, but it should be valid
    xml_output += f'    <AdditionalData attribute="program_name" value="{program_name}"/>\n' 
    xml_output += f'  </Annotation>\n'

xml_output += '</Annotations>'

with open('v5_annotations.xml', 'w') as f:
    f.write(xml_output)

print("Successfully converted spreadsheet to v5_annotations.xml")

import re

try:
    with open("debug_location_results.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"File size: {len(content)} characters")
    
    # Find occurrences of '560001'
    matches = [m.start() for m in re.finditer('560001', content)]
    print(f"Found '560001' at indices: {matches}")
    
    for idx in matches:
        start = max(0, idx - 500)
        end = min(len(content), idx + 500)
        print(f"\n--- Context around {idx} ---")
        print(content[start:end])
        
    # Also search for 'location-search-item'
    print("\n--- Searching for location-search-item ---")
    if 'location-search-item' in content:
        print("Found 'location-search-item'")
    else:
        print("Did NOT find 'location-search-item'")
        
    # Search for prediction classes
    print("\n--- Searching for prediction classes ---")
    classes = re.findall(r'class="([^"]*prediction[^"]*)"', content)
    print(f"Prediction classes found: {classes[:5]}")
    
except Exception as e:
    print(f"Error: {e}")

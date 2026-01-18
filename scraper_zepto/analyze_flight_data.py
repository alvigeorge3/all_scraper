import json

try:
    with open("debug_api_responses.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Find the big string item (Item 6)
    flight_data = None
    for item in data:
        if "fresh-fruits" in item.get("url", "") and isinstance(item.get("data"), str) and len(item.get("data")) > 100000:
            flight_data = item.get("data")
            break
            
    if flight_data:
        print(f"Found Flight Data (Length: {len(flight_data)})")
        print("--- START SNIPPET ---")
        print(flight_data[:2000])
        print("--- END SNIPPET ---")
        
        # Test basic splitting
        lines = flight_data.split('\n')
        print(f"Total lines: {len(lines)}")
        for i, line in enumerate(lines[:5]):
            print(f"Line {i}: {line[:100]}...")

        # Search for product-like data in the lines
        import re
        # Look for the pattern we are using
        # href="/pn/..." 
        matches = re.finditer(r'href=\"(/pn/[^\"]+)\"', flight_data)
        count = 0
        for match in matches:
            start = match.start()
            # Print a generous chunk around the match
            print(f"\n--- MATCH {count+1} ---")
            snippet = flight_data[start:start+1000] 
            print(snippet)
            count += 1
            if count >= 3: break

    else:
        print("Flight data not found")

except Exception as e:
    print(f"Error: {e}")

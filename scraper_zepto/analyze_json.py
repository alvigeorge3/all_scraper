import json
import logging

try:
    with open("debug_api_responses.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} items")
    
    for i, item in enumerate(data):
        url = item.get("url", "NO_URL")
        print(f"Item {i}: URL: {url}")
        
        content = item.get("data")
        if isinstance(content, str):
            try:
                # Try parsing if string (for x-component or text)
                # content = json.loads(content) # Might fail if it's Flight format
                print(f"  Type: String (Length: {len(content)})")
                if "product" in content[:1000]:
                     print("  Contains 'product' in first 1000 chars")
            except:
                pass
        elif isinstance(content, dict):
             keys = list(content.keys())
             print(f"  Keys: {keys}")
             # Check for common product keys deeper
             if "products" in keys:
                 print("  FOUND 'products' key!")
             if "items" in keys:
                 print("  FOUND 'items' key!")
                 
             # Check deeply nested?
             # print(json.dumps(content, indent=2)[:500]) 

except Exception as e:
    print(f"Error: {e}")

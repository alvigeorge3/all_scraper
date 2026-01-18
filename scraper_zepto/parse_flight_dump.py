import json
import re

try:
    with open("debug_api_responses.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Find Item 6 (Flight Data)
    flight_data = ""
    for item in data:
        if isinstance(item.get("data"), str) and len(item.get("data")) > 100000:
            flight_data = item.get("data")
            break
            
    if not flight_data:
        print("Flight data not found")
        exit()

    print(f"Parsing flight data of length {len(flight_data)}")
    
    # Strategy 1: Find all JSON-like objects that contain "productVariantId"
    # This is tricky because of nesting and escaping.
    
    # Strategy 2: Look for specific keys
    # "name":"..."
    # "discountedSellingPrice":...
    
    # Let's try to find product names first
    # Pattern: \"name\":\"([^\"]+)\"
    # But usually it's inside a product structure.
    
    # Regex for potential product block
    # We look for "name" and "discountedSellingPrice" close to each other
    
    # Extract "unit" which is common in zepto products
    # "packSize"
    
    products = []
    
    # Very naive regex to find product chunks
    # Zepto often sends:
    # ... "name":"Strawberry","packSize":"1 pc", ... "discountedSellingPrice":8900 ...
    
    # Let's find all occurrences of "discountedSellingPrice" and look around/backwards
    # Since it's a stream, it might be in chunks.
    
    matches = re.finditer(r'\"name\":\"([^\"]+)\".{1,500}?\"discountedSellingPrice\":(\d+)', flight_data)
    
    for m in matches:
        name = m.group(1)
        price = m.group(2)
        print(f"Found: {name} - Price: {price}")
        products.append({"name": name, "price": price})
        
    print(f"Total found matching regex: {len(products)}")
    
    # Also dump a snippet where "Strawberry" is found to see structure
    idx = flight_data.find("Strawberry")
    if idx != -1:
        print("\nSnippet around Strawberry:")
        print(flight_data[idx-200:idx+500])

except Exception as e:
    print(f"Error: {e}")

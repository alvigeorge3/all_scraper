
import json
import re

def analyze():
    try:
        with open("debug_api_response.json", "r", encoding="utf-8") as f:
            wrapper = json.load(f)
            
        rsc_text = wrapper.get("data", "")
        
        # Strategy: Look for the specific pattern for product items
        # "items":[{"cardData": ...
        # This might be in one large line or split.
        
        # Let's try to find all "cardData" occurrences and see if they parse as JSON
        # effectively we want to extract objects that look like {"cardData":{...}}
        
        # Using a regex to find the start of the items array might be better
        # items:[{
        
        pattern = r'"items":\s*(\[\{.*?\}\])'
        matches = list(re.finditer(pattern, rsc_text))
        
        print(f"Found {len(matches)} 'items' arrays via regex")
        
        all_products = []
        
        for m in matches:
            try:
                # This regex is brittle if the array contains nested objects with braces.
                # A better way is to find "items":[ and then parse JSON from there? 
                # But RSC lines are separate JSONs.
                pass
            except:
                pass

        # Alternative: Split by lines (RSC format)
        lines = rsc_text.split('\n')
        print(f"Total lines: {len(lines)}")
        
        for line in lines:
            if '"cardData":' in line:
                # This line likely contains product data.
                # It might be prefixed with ID:
                # e.g. a:{"..."}
                
                # strip prefix
                parts = line.split(':', 1)
                if len(parts) > 1:
                    json_part = parts[1]
                    try:
                        data = json.loads(json_part)
                        # Traverse to find items
                        # data might be complex.
                        # Let's string search within the line again or traverse
                        
                        # recursive search for cardData
                        def find_cards(obj):
                            found = []
                            if isinstance(obj, dict):
                                if "cardData" in obj:
                                    found.append(obj["cardData"])
                                for k, v in obj.items():
                                    found.extend(find_cards(v))
                            elif isinstance(obj, list):
                                for item in obj:
                                    found.extend(find_cards(item))
                            return found

                        cards = find_cards(data)
                        if cards:
                            print(f"Found {len(cards)} cards in line {lines.index(line)}")
                            all_products.extend(cards)
                            
                    except Exception as e:
                        # print(f"Failed to parse line {lines.index(line)}: {e}")
                        pass
        
        print(f"Total extracted products: {len(all_products)}")
        
        if all_products:
            print("\nSample Product:")
            p = all_products[0]
            print(json.dumps(p, indent=2))
            
            # Check for keys
            print("\nKeys check:")
            print(f"Name: {p.get('name')}") # Might be in a different place?
            # Actually cardData seems to contain specific fields.
            # In previous output: "discountedSellingPrice":9800,"id":...
            # I don't see "name" in the snippet I saw.
            
            # Let's check `product` sub-object if it exists?
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()

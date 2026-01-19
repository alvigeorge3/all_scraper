
import json
import re

def analyze():
    try:
        with open("debug_api_response.json", "r", encoding="utf-8") as f:
            wrapper = json.load(f)
            
        rsc_text = wrapper.get("data", "")
        print(f"RSC Text Length: {len(rsc_text)}")
        print(f"RSC Start: {rsc_text[:200]}")
        
        # It seems RSC is lines of ... something.
        # Let's see if we can find "sellingPrice"
        
        print("\n--- Searching for sellingPrice ---")
        matches = list(re.finditer(r'sellingPrice', rsc_text))
        print(f"Found {len(matches)} matches")
        
        if matches:
            m = matches[0]
            start = max(0, m.start() - 100)
            end = min(len(rsc_text), m.end() + 200)
            print(f"Context:\n{rsc_text[start:end]}")
            
        print("\n--- Searching for availableQuantity ---")
        matches = list(re.finditer(r'availableQuantity', rsc_text))
        print(f"Found {len(matches)} matches")
        
        if matches:
            m = matches[0]
            start = max(0, m.start() - 100)
            end = min(len(rsc_text), m.end() + 200)
            print(f"Context:\n{rsc_text[start:end]}")

        print("\n--- Searching for 'name' ---")
        matches = list(re.finditer(r'"name"', rsc_text))
        print(f"Found {len(matches)} matches")
        if matches:
             m = matches[0]
             start = max(0, m.start() - 50)
             end = min(len(rsc_text), m.end() + 200)
             print(f"Context:\n{rsc_text[start:end]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()

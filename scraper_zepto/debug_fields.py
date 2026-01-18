import re
import json

def test_regex():
    products = [
        "Rajnigandha Silver Pearls Elaichi Mouth Freshener",
        "Basics IND Wired earphone With Mic | Black",
        "Fresho Farm Eggs - Table Tray 30 pcs",
        "Amul Taaza Homogenised Toned Milk 1 L",
        "Nandini GoodLife Toned Milk 500 ml",
        "Coca-Cola Soft Drink 750ml",
        "Lays India's Magic Masala Chips 50g",
        "Surf Excel Easy Wash Detergent Powder 1 kg",
        "Onion 1 kg",
        "Potato 500 g",
        "Coriander Bunch 1 pc"
    ]

    print("--- Testing Pack Size Regex ---")
    for name in products:
        # Improved regex
        # 1. Look for numbers followed by units
        # 2. Handle 'pcs', 'pc', 'g', 'kg', 'ml', 'l', 'L'
        # 3. Handle 'x' like '3 x 100 g'
        
        # Current logic
        size_match = re.search(r'(\d+\s*(?:g|kg|ml|l|pc|pcs|unit|bunch|pack|bunches)\b)', name, re.IGNORECASE)
        
        # New proposed logic
        # Allow decimals (1.5 L)
        # Allow x (3x100g)
        # Be careful with "10mm" drivers (from earlier user complaint about earphones) -> EARPHONES shouldn't match 'mm' but we look for weight/vol
        
        new_match = re.search(r'(\d+(?:\.\d+)?\s*(?:g|kg|ml|l|litres|pc|pcs|pack|units)\b)', name, re.IGNORECASE)
        
        print(f"Name: {name}")
        print(f"  Old: {size_match.group(1) if size_match else 'N/A'}")
        print(f"  New: {new_match.group(1) if new_match else 'N/A'}")

def find_store_id():
    print("\n--- Searching for Store ID ---")
    try:
        with open("debug_homepage.html", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Look for store_id patterns
        matches = re.findall(r'store_?id\W+(\w+)', content, re.IGNORECASE)
        print(f"Matches in Homepage: {matches[:5]}")
        
        # Look for standard nextjs props
        matches2 = re.findall(r'\"storeId\":\"([^\"]+)\"', content)
        print(f"JSON matches: {matches2[:5]}")

    except Exception as e:
        print(f"Error reading homepage: {e}")

if __name__ == "__main__":
    test_regex()
    find_store_id()

import re

def inspect_fields():
    try:
        with open("debug_biscuits.html", "r", encoding="utf-8") as f:
            content = f.read()
            
        print("--- Shelf Life Context ---")
        idx = content.find("shelfLife")
        if idx == -1: idx = content.find("life")
        if idx != -1:
            print(content[idx-200:idx+200])
            
        print("\n--- Inventory JSON Link Context ---")
        pid = "fcd9dedd-c659-4ccd-a15d-877ca13d4f69"
        indices = [m.start() for m in re.finditer(pid, content)]
        print(f"Found {len(indices)} matches for {pid}")
        
        for i, idx in enumerate(indices):
            print(f"\n--- Match {i+1} Context ---")
            print(content[idx-500:idx+500])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_fields()

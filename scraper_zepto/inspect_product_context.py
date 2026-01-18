
def inspect_context():
    try:
        with open("debug_biscuits.html", "r", encoding="utf-8") as f:
            content = f.read()
            
        target = "Britannia Marie Gold"
        idx = content.find(target)
        
        if idx != -1:
            start = max(0, idx - 1000)
            end = min(len(content), idx + 1000)
            context = content[start:end]
            print(f"--- Context for '{target}' ---")
            print(context)
        else:
            print(f"Target '{target}' not found.")
            
        # Also check for one of the keys we suspected
        idx2 = content.find("availableQuantity")
        if idx2 != -1:
             print(f"\n--- Found 'availableQuantity' ---")
             # Print 1000 chars before and after
             print(content[idx2-1000:idx2+1000])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_context()

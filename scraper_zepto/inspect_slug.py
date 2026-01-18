
def inspect_slug_brand():
    try:
        with open("debug_biscuits.html", "r", encoding="utf-8") as f:
            content = f.read()
            
        print("--- Slug/Brand Context ---")
        # Find block with availableQuantity and see if slug/brand is there
        blocks = content.split("availableQuantity")
        if len(blocks) > 1:
            snippet = blocks[1][:1000] # Look ahead 1000 chars from first match
            print(f"Context after availableQuantity:\n{snippet}")
            
            # Look behind as well
            snippet_pre = blocks[0][-500:]
            print(f"Context before availableQuantity:\n{snippet_pre}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_slug_brand()

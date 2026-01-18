
import re

def verify_ids():
    try:
        with open("debug_biscuits.html", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Extract PVIDs from hrefs
        pvids = set(re.findall(r'pvid/([a-f0-9\-]+)', content))
        print(f"Found {len(pvids)} unique PVIDs in URL hrefs")
        
        # Extract IDs from JSON items blocks with escaped quotes
        # Pattern: \"id\":\"UUID\"
        # Regex needs to match literal backslash then quote
        json_ids = set(re.findall(r'\\\"id\\\":\\\"([a-f0-9\-]+)\\\"', content))
        print(f"Found {len(json_ids)} unique UUIDs in JSON keys")
        
        # Intersection
        common = pvids.intersection(json_ids)
        print(f"Intersection count: {len(common)}")
        if len(common) > 0:
            print(f"Sample matches: {list(common)[:5]}")
        else:
            print("No matches found!")
            print(f"Sample PVID: {list(pvids)[0] if pvids else 'None'}")
            print(f"Sample JSON ID: {list(json_ids)[0] if json_ids else 'None'}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_ids()

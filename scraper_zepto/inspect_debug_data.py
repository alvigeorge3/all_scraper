
import re
import json
import sys

# Ensure stdout handles unicode
sys.stdout.reconfigure(encoding='utf-8')

def inspect():
    with open("debug_fast_fetch_content.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"Content length: {len(content)}")
    
    term = "/pn/"
    matches = list(re.finditer(re.escape(term), content))
    print(f"Found {len(matches)} matches for '{term}'")
    
    if len(matches) > 0:
         match = matches[0]
         start = max(0, match.start() - 500)
         end = min(len(content), match.end() + 1000)
         print(f"Context: {content[start:end]}")

if __name__ == "__main__":
    inspect()

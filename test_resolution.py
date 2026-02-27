
import sys
sys.path.append('/app')
import asyncio
from engine import resolve_target, call_service

async def test():
    # Test cases
    targets = ["172.16.16.200", "google.com"]
    
    for t in targets:
        print(f"\n--- Testing Target: {t} ---")
        info = resolve_target(t)
        print(f"Analysis: {info}")
        
        # Test nmap routing (should be IP)
        nmap_target = info["ip"] if "nmap" == "nmap" else info["url"]
        print(f"Nmap would get: {nmap_target}")
        
        # Test nuclei routing (should be URL)
        nuclei_target = info["url"]
        print(f"Nuclei would get: {nuclei_target}")

if __name__ == "__main__":
    asyncio.run(test())

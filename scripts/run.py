import asyncio
#from src.orchestrator import CardFlipOrchestrator
from src.agents.scanner import ListingScanner

async def main():
    #orchestrator = CardFlipOrchestrator()
    #results = await orchestrator.find_opportunities()
    #print(f"Found {len(results)} opportunities")

    scanner = ListingScanner()
    
    # Test connection
    print("Testing Azure OpenAI connection...")
    result = scanner.test_connection()
    print(f"Result: {result}")
    
    # Test scanning (empty for now)
    listings = await scanner.scan_recent_listings()
    print(f"Found {len(listings)} listings")

if __name__ == "__main__":
    asyncio.run(main())


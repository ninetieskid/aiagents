import asyncio
from src.agents.scanner import ListingScanner
from src.agents.evaluator import CardEvaluator

async def main():
    # Initialize agents
    scanner = ListingScanner()
    evaluator = CardEvaluator()
    
    # Scan listings
    print("Scanning listings...\n")
    listings = await scanner.scan_recent_listings()
    
    if not listings:
        print("No listings found!")
        return
    
    # Evaluate each listing
    for listing in listings:
        print(f"=== Evaluating {listing.listing_id} ===")
        print(f"Title: {listing.title}")
        print(f"Listed Price: ${listing.price}")
        print(f"Images: {listing.images}\n")
        
        try:
            quality = await evaluator.evaluate(listing)
            
            print(f"Overall Grade: {quality.overall_grade}")
            print(f"Confidence: {quality.confidence}")
            print(f"Centering: {quality.centering}")
            print(f"Corners: {quality.corners}")
            print(f"Edges: {quality.edges}")
            print(f"Surface: {quality.surface}")
            print(f"Defects: {', '.join(quality.defects) if quality.defects else 'None visible'}")
            print(f"Estimated Value: ${quality.estimated_value}" if quality.estimated_value else "Unable to estimate")
            print(f"Analysis: {quality.analysis}")
            print(f"Profitable? {'YES ✓' if quality.is_profitable else 'NO ✗'}")
            print("\n" + "="*50 + "\n")
            
        except Exception as e:
            print(f"Error evaluating listing: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
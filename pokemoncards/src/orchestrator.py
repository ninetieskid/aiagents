from src.agents.scanner import ListingScanner
from src.agents.evaluator import CardEvaluator

class CardFlipOrchestrator:
    def __init__(self):
        self.scanner = ListingScanner()
        self.evaluator = CardEvaluator()
    
    async def find_opportunities(self):
        # Scanner finds candidates
        listings = await self.scanner.scan_recent_listings()
        
        # Filter before expensive vision calls
        promising = self.filter_by_price_signals(listings)
        
        # Evaluator analyzes only good candidates
        results = []
        for listing in promising:
            quality = await self.evaluator.evaluate(listing)
            if quality.is_profitable():
                results.append((listing, quality))
        
        return results
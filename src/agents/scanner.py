import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from openai import AzureOpenAI
from dotenv import load_dotenv
from src.models import Listing

load_dotenv()

class ListingScanner:
    def __init__(self, listings_dir: str = "data/listings"):
        self.client = AzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("OPENAI_ENDPOINT")
        )
        self.deployment = os.getenv("OPENAI_DEPLOYMENT")
        self.listings_dir = Path(listings_dir)
    
    def test_connection(self):
        """Test Azure OpenAI connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Reply with 'connection successful' if you receive this."}
                ],
                max_tokens=50
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Connection failed: {str(e)}"
    
    def _load_listing(self, listing_dir: Path) -> Optional[Listing]:
        """Load a single listing from directory"""
        metadata_path = listing_dir / "metadata.json"
        
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)
            
            return Listing(
                listing_id=data["listing_id"],
                title=data["title"],
                price=float(data["price"]),
                currency=data["currency"],
                seller=data["seller"],
                url=data["url"],
                date_listed=datetime.fromisoformat(data["date_listed"].replace('Z', '+00:00')),
                condition=data["condition"],
                description=data["description"],
                images=data["images"],
                folder_path=str(listing_dir)
            )
        except Exception as e:
            print(f"Error loading {listing_dir}: {e}")
            return None
    
    async def scan_recent_listings(self, max_price: float = None) -> List[Listing]:
        """Scan all listings from folder"""
        listings = []
        
        if not self.listings_dir.exists():
            print(f"Listings directory not found: {self.listings_dir}")
            return listings
        
        # Scan all subdirectories
        for listing_dir in self.listings_dir.iterdir():
            if listing_dir.is_dir():
                listing = self._load_listing(listing_dir)
                if listing:
                    # Filter by price if specified
                    if max_price is None or listing.price <= max_price:
                        listings.append(listing)
        
        print(f"Loaded {len(listings)} listings")
        return listings
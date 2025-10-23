from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Listing:
    listing_id: str
    title: str
    price: float
    currency: str
    seller: str
    url: str
    date_listed: datetime
    condition: str
    description: str
    images: List[str]  # Filenames
    folder_path: str   # Full path to listing folder
    
    @property
    def image_paths(self) -> List[str]:
        """Get full paths to images"""
        import os
        return [os.path.join(self.folder_path, img) for img in self.images]
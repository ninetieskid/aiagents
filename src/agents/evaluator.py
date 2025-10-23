import os
import base64
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv
from src.models import Listing
from dataclasses import dataclass
from typing import List, Optional

load_dotenv()

@dataclass
class CardQuality:
    listing_id: str
    overall_grade: str  # e.g., "Mint", "Near Mint", "Excellent", "Good", "Poor"
    confidence: float   # 0.0 to 1.0
    centering: str
    corners: str
    edges: str
    surface: str
    defects: List[str]
    estimated_value: Optional[float]
    analysis: str
    is_profitable: bool

class CardEvaluator:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("OPENAI_ENDPOINT")
        )
        self.deployment = os.getenv("OPENAI_DEPLOYMENT")
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _build_vision_prompt(self, listing: Listing) -> str:
        """Build prompt for card evaluation"""
        return f"""You are an expert pokemon card grader. Analyze these images of a trading card.

Card Details:
- Title: {listing.title}
- Listed Condition: {listing.condition}
- Listed Price: ${listing.price}

Evaluate the card on these criteria:
1. **Centering**: How well-centered is the image on the card?
2. **Corners**: Sharpness and wear on corners
3. **Edges**: Condition of edges (chips, whitening, wear)
4. **Surface**: Scratches, print lines, stains, or damage
5. **Overall Grade**: Mint/Near Mint/Lightly Played/Moderately Played/Heavily Played/Played/Damaged

Provide your assessment in this exact format:

CENTERING: [assessment]
CORNERS: [assessment]
EDGES: [assessment]
SURFACE: [assessment]
DEFECTS: [list any defects found, or "None visible"]
OVERALL_GRADE: [Mint/Near Mint/Excellent/Good/Poor]
CONFIDENCE: [0.0-1.0]
ESTIMATED_VALUE: [dollar amount or "Unable to estimate"]
ANALYSIS: [2-3 sentence summary]
IS_PROFITABLE: [Yes/No - based on listed price vs estimated value]"""
    
    async def evaluate(self, listing: Listing) -> CardQuality:
        """Evaluate card quality from images"""
        
        # Check if images exist
        image_paths = listing.image_paths
        print(f"DEBUG: Image paths from listing: {image_paths}")

        if not image_paths:
            raise ValueError(f"No images found for listing {listing.listing_id}")
        
        # Prepare images for vision API
        image_content = []
        for img_path in image_paths:  # Front and back only
            print(f"DEBUG: Checking image path: {img_path}")
            print(f"DEBUG: Path exists? {Path(img_path).exists()}")

            if Path(img_path).exists():
                base64_image = self._encode_image(img_path)
                image_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
        
        print(f"DEBUG: Total images prepared: {len(image_content)}")

        if not image_content:
            raise ValueError(f"Could not load images from {listing.folder_path}")
        
        # Build messages
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": self._build_vision_prompt(listing)},
                    *image_content
                ]
            }
        ]
        
        print(f"DEBUG: Message content parts: {len(messages[0]['content'])}")

        # Call vision API
        print(f"Analyzing images for {listing.listing_id}...")
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            max_tokens=800
        )
        
        analysis_text = response.choices[0].message.content
        print(f"DEBUG: Raw response:\n{analysis_text}\n")
        
        # Parse response
        return self._parse_analysis(listing.listing_id, analysis_text)
    
    def _parse_analysis(self, listing_id: str, text: str) -> CardQuality:
        """Parse the structured response from GPT"""
        lines = text.strip().split('\n')
        data = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        # Extract defects list
        defects_str = data.get('DEFECTS', 'None visible')
        defects = [d.strip() for d in defects_str.split(',') if d.strip().lower() != 'none visible']
        
        # Parse estimated value
        est_value_str = data.get('ESTIMATED_VALUE', 'Unable to estimate')
        try:
            est_value = float(est_value_str.replace('$', '').replace(',', ''))
        except:
            est_value = None
        
        # Parse confidence
        try:
            confidence = float(data.get('CONFIDENCE', '0.5'))
        except:
            confidence = 0.5
        
        is_profitable = data.get('IS_PROFITABLE', 'No').lower() == 'yes'
        
        return CardQuality(
            listing_id=listing_id,
            overall_grade=data.get('OVERALL_GRADE', 'Unknown'),
            confidence=confidence,
            centering=data.get('CENTERING', 'Unknown'),
            corners=data.get('CORNERS', 'Unknown'),
            edges=data.get('EDGES', 'Unknown'),
            surface=data.get('SURFACE', 'Unknown'),
            defects=defects,
            estimated_value=est_value,
            analysis=data.get('ANALYSIS', ''),
            is_profitable=is_profitable
        )
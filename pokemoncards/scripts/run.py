import asyncio
from src.orchestrator import CardFlipOrchestrator

async def main():
    orchestrator = CardFlipOrchestrator()
    results = await orchestrator.find_opportunities()
    print(f"Found {len(results)} opportunities")

if __name__ == "__main__":
    asyncio.run(main())
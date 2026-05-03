"""
Advanced itinerary generation using Gemini API.
Produces detailed, practical travel plans with premium formatting.
"""
import logging
from typing import Dict, Any

from src.llm.clients.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class ItineraryGeneratorService:
    def __init__(self, llm_client: GeminiClient):
        self.llm_client = llm_client
    
    async def generate_itinerary(
        self,
        destination: str,
        duration_days: int,
        budget_usd: float,
        interests: list[str]
    ) -> str:
        """
        Generate a comprehensive, premium itinerary.
        """
        try:
            logger.info(f"Generating itinerary for {destination}, {duration_days} days, ${budget_usd}")
            
            system_instruction = """
            You are a luxury travel consultant. Generate a premium itinerary.
            CRITICAL: The entire response must be under 1400 characters for WhatsApp. 
            Be concise. Use emojis.
            Structure: Title, Summary, Day-by-day (concise), and Pro Tips.
            """
            
            prompt = f"""
            Create an itinerary for:
            - Destination: {destination}
            - Duration: {duration_days} days
            - Total Budget: ${budget_usd}
            - Interests: {', '.join(interests)}
            
            Provide a complete, ready-to-send WhatsApp message.
            """
            
            itinerary_text = await self.llm_client.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.8
            )
            
            return itinerary_text
            
        except Exception as e:
            logger.error(f"Error generating itinerary: {e}")
            return "I apologize, but I encountered an error while generating your itinerary. Please try again in a moment."

"""
Advanced NLP-based message parsing service.
Extracts structured travel parameters from unstructured user input using Gemini.
"""
import json
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from src.llm.clients.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class TravelParameters(BaseModel):
    destination: Optional[str] = Field(None, description="Target destination")
    duration_days: Optional[int] = Field(None, ge=1, le=365)
    budget_usd: Optional[float] = Field(None, gt=0)
    interests: List[str] = Field(default_factory=list)
    is_complete: bool = Field(default=False)
    missing_fields: List[str] = Field(default_factory=list)

class MessageParserService:
    def __init__(self, llm_client: GeminiClient):
        self.llm_client = llm_client
    
    async def parse_message(self, message: str, conversation_history: List[Dict] = None) -> TravelParameters:
        """
        Parse user message and extract travel parameters.
        """
        try:
            # Build context from conversation history
            context = self._build_context(conversation_history or [])
            
            system_instruction = """
            You are an expert travel assistant. Your task is to extract structured travel parameters from a conversation.
            Return ONLY a JSON object with the following fields:
            - destination (string or null)
            - duration_days (integer or null)
            - budget_usd (number or null)
            - interests (list of strings)
            
            If a field is mentioned in the current message or previous context, include it.
            """
            
            prompt = f"""
            Conversation History:
            {context}
            
            New User Message: "{message}"
            
            Extract the travel parameters:
            """
            
            response_text = await self.llm_client.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.1  # Low temperature for extraction
            )
            
            # Parse JSON from response
            params_dict = self._extract_json(response_text)
            
            # Check completeness
            required_fields = ["destination", "duration_days", "budget_usd", "interests"]
            missing = [f for f in required_fields if not params_dict.get(f)]
            
            params_dict["is_complete"] = len(missing) == 0
            params_dict["missing_fields"] = missing
            
            return TravelParameters(**params_dict)
            
        except Exception as e:
            logger.error(f"Error in MessageParserService: {e}")
            # Return empty params on failure
            return TravelParameters()

    def _build_context(self, history: List[Dict]) -> str:
        return "\n".join([f"{m['role']}: {m['content']}" for m in history[-5:]])

    def _extract_json(self, text: str) -> Dict:
        try:
            # Simple JSON extraction
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except Exception:
            logger.warning(f"Failed to parse JSON from: {text}")
        return {}

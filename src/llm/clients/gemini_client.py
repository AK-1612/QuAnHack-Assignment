"""
Wrapper for Google Gemini API.
Handles content generation and interaction with Gemini 1.5 Flash.
"""
import google.generativeai as genai
import logging
from src.config import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Client for interacting with Google Gemini LLM models.
    Supports automatic model fallback and error handling.
    """
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.primary_model_name = settings.GEMINI_MODEL
        # Optimized fallback list for maximum reliability
        self.fallback_models = ["gemini-pro-latest", "gemini-flash-latest", "gemini-pro"]
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_instruction: str = None
    ) -> str:
        """
        Generate content with automatic fallback to secondary models on failure.
        """
        models_to_try = [self.primary_model_name] + self.fallback_models
        last_error = None

        for model_name in models_to_try:
            # Standardize model name format
            full_model_name = model_name if model_name.startswith("models/") else f"models/{model_name}"
            
            try:
                logger.info(f"LLM Generation Attempt: {full_model_name}")
                model = genai.GenerativeModel(full_model_name)
                
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
                
                full_prompt = prompt
                if system_instruction:
                    full_prompt = f"{system_instruction}\n\nUser: {prompt}"
                
                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                
                if response.text:
                    return response.text
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Model failure ({full_model_name}): {str(e)}")
                continue
        
        logger.error(f"Critical: All LLM models failed to generate content. Final error: {str(last_error)}")
        raise last_error

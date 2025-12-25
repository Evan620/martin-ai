"""
LLM interface for Ollama models.

Provides a unified interface for interacting with locally hosted LLMs
(Llama, Qwen) via Ollama with retry logic and error handling.
"""

import time
from typing import Any, Dict, List, Optional

import requests
from loguru import logger

from src.config.settings import get_settings


class OllamaLLM:
    """Interface for Ollama LLM models."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize Ollama LLM interface.
        
        Args:
            model: Model name (defaults to settings.ollama.default_model)
            temperature: Sampling temperature (defaults to settings)
            max_tokens: Maximum tokens to generate (defaults to settings)
        """
        self.settings = get_settings()
        self.model = model or self.settings.ollama.default_model
        self.temperature = temperature or self.settings.ollama.temperature
        self.max_tokens = max_tokens or self.settings.ollama.max_tokens
        self.base_url = self.settings.ollama.base_url
        self.timeout = self.settings.ollama.timeout
        
        logger.info(f"Initialized OllamaLLM with model: {self.model}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """
        Generate text completion from prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            stop_sequences: List of sequences that stop generation
            
        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": temp,
                "num_predict": max_tok,
            },
            "stream": False,
        }
        
        if stop_sequences:
            payload["options"]["stop"] = stop_sequences
        
        # Make request with retry logic
        response = self._request_with_retry(
            endpoint="/api/chat",
            payload=payload,
        )
        
        return response["message"]["content"]
    
    def generate_with_context(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate text with conversation context.
        
        Args:
            prompt: User prompt
            context: List of previous messages [{"role": "user/assistant", "content": "..."}]
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(context)
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens),
            },
            "stream": False,
        }
        
        response = self._request_with_retry(
            endpoint="/api/chat",
            payload=payload,
        )
        
        return response["message"]["content"]
    
    def _request_with_retry(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: int = 2,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Response JSON
            
        Raises:
            Exception: If all retries fail
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Making request to {url} (attempt {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(f"All retry attempts failed for {url}")
                    raise
        
        raise Exception("Unexpected error in retry logic")
    
    def check_health(self) -> bool:
        """
        Check if Ollama service is healthy.
        
        Returns:
            True if service is accessible, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            response.raise_for_status()
            logger.info("Ollama service is healthy")
            return True
        except Exception as e:
            logger.error(f"Ollama service health check failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        List available models in Ollama.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )
            response.raise_for_status()
            models = [model["name"] for model in response.json().get("models", [])]
            logger.info(f"Available models: {models}")
            return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []


def get_llm(model: Optional[str] = None, **kwargs) -> OllamaLLM:
    """
    Factory function to get an LLM instance.
    
    Args:
        model: Model name
        **kwargs: Additional parameters for OllamaLLM
        
    Returns:
        OllamaLLM instance
    """
    return OllamaLLM(model=model, **kwargs)

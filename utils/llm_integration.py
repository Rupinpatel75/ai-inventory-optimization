"""
LLM integration utility for the AI Inventory Optimization System.

This module provides integration with local LLMs (using Ollama) to
add reasoning capabilities to agents in the system.
"""

import logging
import os
import requests
import json

logger = logging.getLogger(__name__)

class LLMManager:
    """
    Manager for LLM integration with Ollama.
    
    This class provides:
    - Checking for Ollama availability
    - Listing available models
    - Sending chat completion requests
    """
    
    def __init__(self, ollama_base_url="http://localhost:11434"):
        """
        Initialize the LLM manager.
        
        Args:
            ollama_base_url: Base URL for Ollama API
        """
        self.ollama_base_url = ollama_base_url
        self.available_models = []
        self.preferred_model = None
        self.ollama_available = False
        
        # Check if Ollama is available
        self._check_ollama_availability()
    
    def _check_ollama_availability(self):
        """
        Check if Ollama is available and get available models.
        """
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            
            if response.status_code == 200:
                self.ollama_available = True
                data = response.json()
                models = data.get('models', [])
                self.available_models = [model.get('name', '') for model in models if model.get('name')]
                
                # Choose preferred model based on what's available
                # Preference order: llama3, llama2, mixtral, mistral, phi, gemma
                preferred_options = ["llama3", "llama2", "mixtral", "mistral", "phi", "gemma"]
                
                for option in preferred_options:
                    for model_name in self.available_models:
                        if option in model_name.lower():
                            self.preferred_model = model_name
                            break
                    if self.preferred_model:
                        break
                
                logger.info(f"Ollama available: {len(self.available_models)} models found")
                if self.preferred_model:
                    logger.info(f"Using preferred model: {self.preferred_model}")
                else:
                    logger.warning("No preferred LLM model found")
            else:
                logger.warning("Ollama API returned non-200 status code")
                self.ollama_available = False
                
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.warning(f"Error checking Ollama availability: {str(e)}")
            self.ollama_available = False
    
    def chat_completion(self, prompt, system_prompt=None, model=None):
        """
        Get a chat completion from the LLM.
        
        Args:
            prompt: User prompt for the LLM
            system_prompt: Optional system prompt
            model: Optional model name (defaults to preferred_model)
            
        Returns:
            LLM response text or None if unavailable
        """
        if not self.ollama_available:
            logger.warning("Ollama not available for chat completion")
            return None
        
        model_to_use = model or self.preferred_model
        
        if not model_to_use:
            logger.warning("No model specified and no preferred model available")
            return None
        
        try:
            # Prepare the request
            url = f"{self.ollama_base_url}/api/chat"
            
            payload = {
                "model": model_to_use,
                "messages": []
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["messages"].append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add user prompt
            payload["messages"].append({
                "role": "user",
                "content": prompt
            })
            
            # Send request
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '')
            else:
                logger.error(f"Error getting chat completion: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            return None
    
    def generate_embedding(self, text, model=None):
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: Text to generate embedding for
            model: Optional model name (defaults to preferred_model)
            
        Returns:
            List of floats representing the embedding or None if unavailable
        """
        if not self.ollama_available:
            logger.warning("Ollama not available for embedding generation")
            return None
        
        model_to_use = model or self.preferred_model
        
        if not model_to_use:
            logger.warning("No model specified and no preferred model available")
            return None
        
        try:
            # Prepare the request
            url = f"{self.ollama_base_url}/api/embeddings"
            
            payload = {
                "model": model_to_use,
                "prompt": text
            }
            
            # Send request
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('embedding', [])
            else:
                logger.error(f"Error generating embedding: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"Error in embedding generation: {str(e)}")
            return None

# Create a singleton instance
llm_manager = LLMManager()
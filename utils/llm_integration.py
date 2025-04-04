import os
import logging
import json
from typing import List, Dict, Any, Optional
import requests
import ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama as LangchainOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

# Default Ollama URL for local deployment
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_LLM_MODEL = os.environ.get("OLLAMA_LLM_MODEL", "llama3")
DEFAULT_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "mistral")

class OllamaLLMManager:
    """
    Manager for Ollama LLM interactions.
    Handles both direct LLM calls and embeddings.
    """
    
    def __init__(self, 
                 base_url: str = OLLAMA_BASE_URL,
                 llm_model: str = DEFAULT_LLM_MODEL,
                 embedding_model: str = DEFAULT_EMBEDDING_MODEL):
        """
        Initialize the Ollama LLM Manager
        
        Args:
            base_url: URL for the Ollama API
            llm_model: Model to use for LLM calls
            embedding_model: Model to use for embeddings
        """
        self.base_url = base_url
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        
        # Initialize Ollama client
        ollama.set_host(base_url)
        
        # Initialize LangChain components
        try:
            self.llm = LangchainOllama(model=llm_model, base_url=base_url)
            self.embeddings = OllamaEmbeddings(model=embedding_model, base_url=base_url)
            logger.info(f"Initialized Ollama LLM Manager with LLM model: {llm_model}, embedding model: {embedding_model}")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama components: {str(e)}. Will attempt to use when needed.")
            self.llm = None
            self.embeddings = None
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is available and responsive"""
        try:
            response = requests.get(f"{self.base_url}/api/version")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama service not available: {str(e)}")
            return False
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embeddings for a text using Ollama
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            if self.embeddings is None:
                self.embeddings = OllamaEmbeddings(model=self.embedding_model, base_url=self.base_url)
            
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            # Return a zero vector as fallback
            return [0.0] * 384  # Common embedding size
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if self.embeddings is None:
                self.embeddings = OllamaEmbeddings(model=self.embedding_model, base_url=self.base_url)
            
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error getting batch embeddings: {str(e)}")
            # Return zero vectors as fallback
            return [[0.0] * 384 for _ in texts]
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Reshape for sklearn cosine similarity
            e1 = np.array(embedding1).reshape(1, -1)
            e2 = np.array(embedding2).reshape(1, -1)
            
            similarity = cosine_similarity(e1, e2)[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def query_llm(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """
        Query the LLM with a prompt
        
        Args:
            prompt: The user prompt to send
            system_prompt: Optional system prompt for context
            temperature: Controls randomness (0-1)
            
        Returns:
            LLM response as text
        """
        try:
            if self.check_ollama_available():
                # Use direct Ollama API for more control
                response = ollama.chat(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": temperature}
                )
                return response['message']['content']
            else:
                logger.warning("Ollama not available, returning fallback response")
                return "I'm unable to process your request at the moment."
        except Exception as e:
            logger.error(f"Error querying LLM: {str(e)}")
            return f"Error: {str(e)}"
    
    def create_langchain(self, template: str, input_variables: List[str]) -> LLMChain:
        """
        Create a LangChain for structured LLM interactions
        
        Args:
            template: The prompt template
            input_variables: Variables to substitute in the template
            
        Returns:
            LLMChain object
        """
        try:
            if self.llm is None:
                self.llm = LangchainOllama(model=self.llm_model, base_url=self.base_url)
                
            prompt = PromptTemplate(
                input_variables=input_variables,
                template=template
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain
        except Exception as e:
            logger.error(f"Error creating LangChain: {str(e)}")
            return None


# Initialize a global instance for easy import
try:
    llm_manager = OllamaLLMManager()
except Exception as e:
    logger.warning(f"Failed to initialize global LLM Manager: {str(e)}")
    llm_manager = None
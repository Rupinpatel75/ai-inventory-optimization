import logging
import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import traceback

from app import db
from models import AgentAction
from utils.llm_integration import llm_manager
from utils.web_scraper import scraper

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all agents in the system.
    Provides common functionality for all agent types.
    """
    
    def __init__(self, name: str, agent_type: str):
        """
        Initialize base agent
        
        Args:
            name: Human-readable agent name
            agent_type: Type of agent (demand, inventory, pricing)
        """
        self.name = name
        self.agent_type = agent_type
        self.llm = llm_manager  # LLM integration
        self.scraper = scraper  # Web scraper
        logger.info(f"{self.name} initialized")
    
    def log_action(self, 
                   action: str, 
                   product_id: Optional[int] = None, 
                   store_id: Optional[int] = None, 
                   details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an agent action to the database
        
        Args:
            action: Description of the action
            product_id: Optional ID of the product involved
            store_id: Optional ID of the store involved
            details: Optional dictionary with action details
        """
        try:
            agent_action = AgentAction(
                agent_type=self.agent_type,
                action=action,
                product_id=product_id,
                store_id=store_id,
                details=json.dumps(details) if details else None,
                timestamp=datetime.now()
            )
            db.session.add(agent_action)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error logging agent action: {str(e)}")
            db.session.rollback()
    
    def analyze_with_llm(self, 
                         prompt: str, 
                         context: Optional[Dict[str, Any]] = None, 
                         system_prompt: Optional[str] = None) -> str:
        """
        Use the LLM to analyze data or make decisions
        
        Args:
            prompt: The prompt to send to the LLM
            context: Optional context information
            system_prompt: Optional system prompt
            
        Returns:
            LLM response
        """
        if not self.llm or not self.llm.check_ollama_available():
            logger.warning("LLM not available for analysis")
            return "LLM analysis not available"
        
        try:
            # Format the prompt with context if provided
            formatted_prompt = prompt
            if context:
                context_str = json.dumps(context, indent=2)
                formatted_prompt = f"{prompt}\n\nContext:\n{context_str}"
            
            # Get response from LLM
            response = self.llm.query_llm(
                prompt=formatted_prompt,
                system_prompt=system_prompt or f"You are the {self.name}, an AI agent specializing in {self.agent_type} analysis.",
                temperature=0.2  # Lower temperature for more consistent responses
            )
            
            return response
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return f"Error in analysis: {str(e)}"
    
    def fetch_external_data(self, 
                            data_source: str, 
                            parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Fetch data from external sources (web or API)
        
        Args:
            data_source: URL or API endpoint
            parameters: Parameters for the request
            
        Returns:
            Fetched data
        """
        try:
            if not parameters:
                parameters = {}
            
            # Check if this is a web page or API
            if data_source.startswith('http'):
                if 'api' in data_source or parameters.get('api', False):
                    # Call API
                    method = parameters.get('method', 'GET')
                    params = parameters.get('params', {})
                    data = parameters.get('data', {})
                    headers = parameters.get('headers', {})
                    
                    return self.scraper.call_api(
                        url=data_source,
                        method=method,
                        params=params,
                        data=data,
                        headers=headers
                    )
                else:
                    # Scrape web page
                    if parameters.get('extract_text', False):
                        text = self.scraper.extract_text_content(data_source)
                        return {
                            'success': bool(text),
                            'text': text,
                            'url': data_source
                        }
                    elif parameters.get('extract_product', False):
                        product_info = self.scraper.extract_product_info(data_source)
                        return {
                            'success': bool(product_info),
                            'product': product_info,
                            'url': data_source
                        }
                    else:
                        # Default to HTML scraping
                        soup = self.scraper.scrape_html(data_source)
                        if soup:
                            # Extract title and basic info
                            title = soup.title.text if soup.title else "Unknown"
                            return {
                                'success': True,
                                'title': title,
                                'url': data_source,
                                'soup': soup  # BeautifulSoup object for further processing
                            }
                        else:
                            return {
                                'success': False,
                                'error': 'Failed to scrape page',
                                'url': data_source
                            }
            else:
                logger.warning(f"Invalid data source: {data_source}")
                return {
                    'success': False,
                    'error': 'Invalid data source URL',
                    'url': data_source
                }
        except Exception as e:
            logger.error(f"Error fetching external data from {data_source}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'url': data_source,
                'traceback': traceback.format_exc()
            }
            
    def embed_text(self, text: str) -> List[float]:
        """
        Create an embedding vector for text using the LLM
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not self.llm:
            logger.warning("LLM not available for embedding")
            return []
        
        try:
            embedding = self.llm.get_embedding(text)
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return []
    
    def compare_embeddings(self, text1: str, text2: str) -> float:
        """
        Compare two texts using embeddings similarity
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not self.llm:
            logger.warning("LLM not available for embedding comparison")
            return 0.0
        
        try:
            embedding1 = self.llm.get_embedding(text1)
            embedding2 = self.llm.get_embedding(text2)
            
            similarity = self.llm.calculate_similarity(embedding1, embedding2)
            return similarity
        except Exception as e:
            logger.error(f"Error comparing embeddings: {str(e)}")
            return 0.0
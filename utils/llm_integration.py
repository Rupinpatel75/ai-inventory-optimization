"""
LLM Integration utility for the AI Inventory Optimization System.

This module provides integration with local LLM providers like Ollama
for enhanced agent capabilities.
"""

import logging
import os
import json
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration for LLM providers
LLM_PROVIDERS = {
    "ollama": {
        "enabled": os.environ.get("OLLAMA_ENABLED", "false").lower() == "true",
        "base_url": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        "model": os.environ.get("OLLAMA_MODEL", "llama2"),
    },
    "openai": {
        "enabled": os.environ.get("OPENAI_ENABLED", "false").lower() == "true",
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "model": os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
    }
}

# Agent-specific prompt templates
AGENT_PROMPT_TEMPLATES = {
    "demand": {
        "system": """You are an AI demand forecasting assistant specialized in retail inventory optimization.
Your task is to analyze data and provide clear, actionable insights about sales patterns, 
demand forecasts, and seasonality for retail products. Focus on being accurate, concise, and helpful.
Provide concrete, specific advice without being too general or vague.""",
        "template": "{prompt}"
    },
    "inventory": {
        "system": """You are an AI inventory management assistant specialized in retail supply chain optimization.
Your task is to analyze inventory data and provide clear, actionable insights about reorder points, 
safety stock levels, inventory turnover, and stockout risks. Focus on being accurate, concise, and helpful.
Provide concrete, specific advice without being too general or vague.""",
        "template": "{prompt}"
    },
    "pricing": {
        "system": """You are an AI pricing optimization assistant specialized in retail price elasticity.
Your task is to analyze pricing data and provide clear, actionable insights about optimal pricing,
competitor price positioning, promotion impacts, and price elasticity. Focus on being accurate, concise, and helpful.
Provide concrete, specific advice without being too general or vague.""",
        "template": "{prompt}"
    },
}

def analyze_with_llm_provider(prompt, agent_type="general", provider=None):
    """
    Analyze a prompt using an LLM provider.
    
    Args:
        prompt (str): The prompt to analyze
        agent_type (str): Type of agent (demand, inventory, pricing, general)
        provider (str, optional): Provider to use, defaults to first enabled provider
        
    Returns:
        str: The LLM response or None if not available/error
    """
    # Find an enabled provider if not specified
    if not provider:
        for provider_name, config in LLM_PROVIDERS.items():
            if config.get("enabled", False):
                provider = provider_name
                break
    
    if not provider:
        logger.warning("No enabled LLM provider found")
        return None
    
    # Get the provider config
    provider_config = LLM_PROVIDERS.get(provider)
    if not provider_config or not provider_config.get("enabled", False):
        logger.warning(f"Provider {provider} not found or not enabled")
        return None
    
    # Get agent-specific prompt template
    prompt_template = AGENT_PROMPT_TEMPLATES.get(
        agent_type, 
        AGENT_PROMPT_TEMPLATES.get("demand")
    )
    
    # Format the prompt with the template
    formatted_prompt = prompt_template["template"].format(prompt=prompt)
    system_prompt = prompt_template.get("system", "")
    
    # Call the appropriate provider
    if provider == "ollama":
        return _call_ollama(formatted_prompt, system_prompt, provider_config)
    elif provider == "openai":
        return _call_openai(formatted_prompt, system_prompt, provider_config)
    else:
        logger.warning(f"Unknown provider: {provider}")
        return None

def _call_ollama(prompt, system_prompt, config):
    """Call the Ollama API to analyze a prompt."""
    try:
        base_url = config["base_url"]
        model = config["model"]
        
        # Prepare the request
        url = f"{base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        
        # Make the request
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return None
        
        # Parse the response
        result = response.json()
        return result.get("response", "")
    
    except Exception as e:
        logger.error(f"Error calling Ollama API: {str(e)}")
        return None

def _call_openai(prompt, system_prompt, config):
    """Call the OpenAI API to analyze a prompt."""
    try:
        api_key = config["api_key"]
        model = config["model"]
        
        # Check if API key is set
        if not api_key:
            logger.error("OpenAI API key not set")
            return None
        
        # Prepare the request
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        # Make the request
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return None
        
        # Parse the response
        result = response.json()
        choices = result.get("choices", [])
        if not choices:
            return None
        
        message = choices[0].get("message", {})
        return message.get("content", "")
    
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return None

def log_llm_request(agent_type, prompt, response, provider):
    """
    Log an LLM request to file.
    
    Args:
        agent_type (str): Type of agent making the request
        prompt (str): The prompt sent to the LLM
        response (str): The response from the LLM
        provider (str): The LLM provider used
    """
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs/llm", exist_ok=True)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent_type": agent_type,
            "provider": provider,
            "prompt": prompt,
            "response": response
        }
        
        # Write to file
        filename = f"logs/llm/{agent_type}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(filename, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    except Exception as e:
        logger.error(f"Error logging LLM request: {str(e)}")

# Helper functions for specific analysis tasks

def analyze_sales_pattern(sales_data, agent_type="demand"):
    """
    Analyze sales pattern using LLM.
    
    Args:
        sales_data (dict): Sales data to analyze
        agent_type (str): Type of agent making the request
        
    Returns:
        str: Analysis of sales pattern
    """
    prompt = f"""
    Analyze the following sales data and identify patterns, trends, and insights:
    
    {json.dumps(sales_data, indent=2)}
    
    Please provide:
    1. Key trends and patterns in the data
    2. Potential causes for any significant changes
    3. Actionable recommendations based on these insights
    
    Keep your response concise yet informative (3-4 sentences).
    """
    
    return analyze_with_llm_provider(prompt, agent_type)

def explain_forecast(forecast_data, product_name, store_name, agent_type="demand"):
    """
    Generate an explanation for a forecast using LLM.
    
    Args:
        forecast_data (dict): Forecast data to explain
        product_name (str): Name of the product
        store_name (str): Name of the store
        agent_type (str): Type of agent making the request
        
    Returns:
        str: Explanation of the forecast
    """
    prompt = f"""
    Generate a clear, concise explanation of the following forecast for {product_name} at {store_name}:
    
    {json.dumps(forecast_data, indent=2)}
    
    Please provide:
    1. A summary of the forecast results
    2. Key factors influencing the forecast
    3. Confidence level and potential risks
    
    Keep your response concise yet informative (3-4 sentences).
    """
    
    return analyze_with_llm_provider(prompt, agent_type)

def generate_inventory_recommendation(inventory_data, product_name, store_name, agent_type="inventory"):
    """
    Generate an inventory recommendation using LLM.
    
    Args:
        inventory_data (dict): Inventory data to analyze
        product_name (str): Name of the product
        store_name (str): Name of the store
        agent_type (str): Type of agent making the request
        
    Returns:
        str: Inventory recommendation
    """
    prompt = f"""
    Based on the following inventory data for {product_name} at {store_name}, 
    provide a specific inventory management recommendation:
    
    {json.dumps(inventory_data, indent=2)}
    
    Please provide:
    1. A clear recommendation (increase, decrease, or maintain inventory)
    2. Specific suggested quantities or levels
    3. Rationale for the recommendation
    
    Keep your response concise yet informative (3-4 sentences).
    """
    
    return analyze_with_llm_provider(prompt, agent_type)

def generate_pricing_recommendation(pricing_data, product_name, store_name, agent_type="pricing"):
    """
    Generate a pricing recommendation using LLM.
    
    Args:
        pricing_data (dict): Pricing data to analyze
        product_name (str): Name of the product
        store_name (str): Name of the store
        agent_type (str): Type of agent making the request
        
    Returns:
        str: Pricing recommendation
    """
    prompt = f"""
    Based on the following pricing data for {product_name} at {store_name}, 
    provide a specific pricing recommendation:
    
    {json.dumps(pricing_data, indent=2)}
    
    Please provide:
    1. A clear recommendation (increase, decrease, or maintain price)
    2. Specific suggested price point or range
    3. Rationale for the recommendation
    
    Keep your response concise yet informative (3-4 sentences).
    """
    
    return analyze_with_llm_provider(prompt, agent_type)
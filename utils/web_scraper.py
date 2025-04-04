"""
Web scraper utility for the AI Inventory Optimization System.

This module provides web scraping functionality to gather data
from external sources to enhance inventory optimization decisions.
"""

import logging
import re
import random
import requests
from bs4 import BeautifulSoup
import trafilatura

logger = logging.getLogger(__name__)

class WebScraper:
    """
    Web scraper for gathering external data to enhance inventory optimization.
    
    Capabilities:
    - Extracting text content from web pages
    - Collecting competitor pricing information
    - Gathering market trend data
    """
    
    def __init__(self):
        """Initialize the web scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_text_content(self, url):
        """
        Extract main text content from a web page.
        
        Args:
            url: URL of the web page
            
        Returns:
            String with extracted text content
        """
        try:
            # Use trafilatura for more accurate content extraction
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded)
            
            if not text:
                # Fallback to BeautifulSoup if trafilatura fails
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text
                text = soup.get_text()
                
                # Break into lines and remove leading/trailing space
                lines = (line.strip() for line in text.splitlines())
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # Remove blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text or f"No content could be extracted from {url}"
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return f"Error extracting content: {str(e)}"
    
    def extract_prices(self, url, product_name):
        """
        Extract prices for a specific product from a web page.
        
        Args:
            url: URL of the web page
            product_name: Name of the product to find prices for
            
        Returns:
            List of dictionaries with prices and source information
        """
        try:
            # Get page content
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text that might contain prices
            text = soup.get_text()
            
            # Look for product name and nearby price patterns
            prices = []
            # Simple price regex pattern (matches common price formats like $19.99, €29, etc.)
            price_pattern = r'(\$|€|£|\b)(\d+[.,]\d{1,2}|\d+)(\b|\s|$)'
            
            # Search for sentences containing the product name
            product_regex = re.compile(re.escape(product_name), re.IGNORECASE)
            
            for element in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'li']):
                text = element.get_text().strip()
                if product_regex.search(text):
                    # Look for price in this element or nearby elements
                    price_matches = re.findall(price_pattern, text)
                    if price_matches:
                        for match in price_matches:
                            # Format the price as a number
                            currency, amount, _ = match
                            amount = amount.replace(',', '.')
                            price = float(amount)
                            
                            prices.append({
                                'price': price,
                                'currency': currency if currency else '$',
                                'context': text[:100].strip() + '...',  # Context snippet
                                'source': url
                            })
            
            return prices
            
        except Exception as e:
            logger.error(f"Error extracting prices from {url} for {product_name}: {str(e)}")
            return []
    
    def get_competitor_prices(self, product_name, category=None, limit=5):
        """
        Get competitor prices for a product.
        
        NOTE: In a real-world scenario, this would make actual requests to
        competitor websites or price comparison sites. For this demo,
        we'll generate simulated competitor pricing data.
        
        Args:
            product_name: Name of the product
            category: Optional product category for more targeted results
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries with competitor price information
        """
        try:
            # In a real implementation, this would:
            # 1. Search for the product on price comparison sites
            # 2. Extract prices from competitor websites
            # 3. Parse and normalize the data
            
            # For demo purposes, generate simulated competitor data
            competitors = [
                "CompetitorA", "CompetitorB", "CompetitorC", 
                "CompetitorD", "CompetitorE", "CompetitorF",
                "CompetitorG", "CompetitorH", "CompetitorI"
            ]
            
            # Generate reasonable price range based on category
            base_price = random.uniform(20, 100)
            if category == "Electronics":
                base_price = random.uniform(100, 500)
            elif category == "Clothing":
                base_price = random.uniform(20, 80)
            elif category == "Groceries":
                base_price = random.uniform(2, 15)
            elif category == "Furniture":
                base_price = random.uniform(100, 1000)
            
            # Generate simulated competitor prices
            prices = []
            for i in range(min(limit, len(competitors))):
                # Vary prices by up to 20% in either direction
                variation = random.uniform(-0.2, 0.2)
                price = base_price * (1 + variation)
                
                # Round to reasonable precision
                price = round(price, 2)
                
                prices.append({
                    "competitor": competitors[i],
                    "price": price,
                    "currency": "$",
                    "product_name": product_name,
                    "in_stock": random.random() > 0.2,  # 80% chance of being in stock
                    "last_updated": "2023-04-04"  # In a real system, this would be the actual date
                })
            
            # Log the action
            logger.info(f"Retrieved {len(prices)} competitor prices for {product_name}")
            
            return prices
            
        except Exception as e:
            logger.error(f"Error getting competitor prices for {product_name}: {str(e)}")
            return []
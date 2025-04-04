import logging
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any, Union
import trafilatura
from datetime import datetime

logger = logging.getLogger(__name__)

class WebScraper:
    """
    Utility for scraping web content for agent use.
    Provides methods to extract data from websites and APIs.
    """
    
    def __init__(self, user_agent: str = None):
        """
        Initialize the web scraper with optional custom user agent
        
        Args:
            user_agent: Optional custom user agent string
        """
        self.user_agent = user_agent or 'Mozilla/5.0 (AI Inventory Optimization Agent/1.0)'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent
        })
        logger.info("Web scraper initialized")
    
    def extract_text_content(self, url: str) -> str:
        """
        Extract the main text content from a webpage using Trafilatura
        
        Args:
            url: URL of the webpage to scrape
            
        Returns:
            Extracted text content
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                if text:
                    logger.info(f"Successfully extracted text from {url}")
                    return text
                else:
                    logger.warning(f"No text content found at {url}")
                    return ""
            else:
                logger.warning(f"Failed to download content from {url}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text from {url}: {str(e)}")
            return ""
    
    def scrape_html(self, url: str) -> Optional[BeautifulSoup]:
        """
        Scrape HTML from a webpage and return BeautifulSoup object
        
        Args:
            url: URL of the webpage to scrape
            
        Returns:
            BeautifulSoup object or None on failure
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info(f"Successfully scraped HTML from {url}")
            return soup
        except Exception as e:
            logger.error(f"Error scraping HTML from {url}: {str(e)}")
            return None
    
    def extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract structured data (JSON-LD) from a webpage
        
        Args:
            soup: BeautifulSoup object of the webpage
            
        Returns:
            List of structured data objects
        """
        structured_data = []
        
        try:
            # Look for JSON-LD scripts
            ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            
            for script in ld_scripts:
                try:
                    data = json.loads(script.string)
                    structured_data.append(data)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            logger.info(f"Extracted {len(structured_data)} structured data objects")
            return structured_data
        except Exception as e:
            logger.error(f"Error extracting structured data: {str(e)}")
            return []
    
    def call_api(self, 
                url: str, 
                method: str = 'GET', 
                params: Dict[str, Any] = None, 
                data: Dict[str, Any] = None, 
                headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Make an API call and return the response
        
        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, etc.)
            params: URL parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            API response as dictionary
        """
        try:
            api_headers = {'Content-Type': 'application/json'}
            if headers:
                api_headers.update(headers)
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data if data else None,
                headers=api_headers,
                timeout=15
            )
            
            response.raise_for_status()
            
            if response.text:
                result = response.json()
                logger.info(f"Successful API call to {url}")
                return {'success': True, 'data': result}
            else:
                return {'success': True, 'data': None}
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during API call to {url}: {str(e)}")
            error_response = {'success': False, 'error': f"HTTP error: {str(e)}"}
            
            # Try to extract error message from response
            try:
                error_data = e.response.json()
                error_response['error_data'] = error_data
            except:
                error_response['status_code'] = e.response.status_code
                
            return error_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during API call to {url}: {str(e)}")
            return {'success': False, 'error': f"Request error: {str(e)}"}
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error from API {url}: {str(e)}")
            return {
                'success': False, 
                'error': f"Invalid JSON response", 
                'raw_response': response.text[:500]  # Include first 500 chars of response
            }
            
        except Exception as e:
            logger.error(f"Unexpected error during API call to {url}: {str(e)}")
            return {'success': False, 'error': f"Unexpected error: {str(e)}"}
    
    def extract_product_info(self, url: str) -> Dict[str, Any]:
        """
        Extract product information from a product page
        
        Args:
            url: URL of the product page
            
        Returns:
            Product information as dictionary
        """
        try:
            soup = self.scrape_html(url)
            if not soup:
                return {}
            
            # Try to extract structured data first
            structured_data = self.extract_structured_data(soup)
            for data in structured_data:
                if data.get('@type') == 'Product':
                    return {
                        'name': data.get('name', ''),
                        'description': data.get('description', ''),
                        'brand': data.get('brand', {}).get('name', '') if isinstance(data.get('brand'), dict) else data.get('brand', ''),
                        'price': data.get('offers', {}).get('price', 0) if isinstance(data.get('offers'), dict) else 0,
                        'currency': data.get('offers', {}).get('priceCurrency', 'USD') if isinstance(data.get('offers'), dict) else 'USD',
                        'availability': data.get('offers', {}).get('availability', '') if isinstance(data.get('offers'), dict) else '',
                        'url': url,
                        'image': data.get('image', ''),
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Fallback to basic extraction
            product = {}
            
            # Try to find product name
            name_candidates = [
                soup.find('h1'),
                soup.find('h1', {'class': lambda x: x and ('product' in x or 'title' in x)}),
                soup.find(class_=lambda x: x and ('product-title' in x or 'product-name' in x))
            ]
            
            for candidate in name_candidates:
                if candidate and candidate.text.strip():
                    product['name'] = candidate.text.strip()
                    break
            
            # Try to find price
            price_candidates = [
                soup.find(class_=lambda x: x and ('price' in x)),
                soup.find('span', {'itemprop': 'price'}),
                soup.find(attrs={'data-price-value': True})
            ]
            
            for candidate in price_candidates:
                if candidate:
                    price_text = candidate.get('content') or candidate.get('data-price-value') or candidate.text
                    try:
                        # Extract digits and decimal point
                        import re
                        price_match = re.search(r'(\d+\.?\d*)', str(price_text))
                        if price_match:
                            product['price'] = float(price_match.group(1))
                            break
                    except:
                        continue
            
            # Add basic metadata
            product.update({
                'url': url,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Extracted product info from {url}")
            return product
            
        except Exception as e:
            logger.error(f"Error extracting product info from {url}: {str(e)}")
            return {}


# Create a global instance for easy import
scraper = WebScraper()
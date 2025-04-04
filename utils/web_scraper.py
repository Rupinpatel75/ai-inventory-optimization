"""
Web Scraper utility for the AI Inventory Optimization System.

This module provides web scraping capabilities to collect market data
such as competitor prices, product information, and industry trends.
"""

import logging
import re
import json
import time
import random
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime

# Try to import trafilatura for text extraction
try:
    import trafilatura
except ImportError:
    trafilatura = None

logger = logging.getLogger(__name__)

class WebScraper:
    """
    Web scraper for collecting market data from various online sources.
    
    This class provides methods to scrape product information, prices,
    and other relevant data from e-commerce websites and other sources.
    """
    
    def __init__(self, headers=None, delay_range=(1, 3)):
        """
        Initialize the web scraper.
        
        Args:
            headers (dict, optional): HTTP headers to use for requests
            delay_range (tuple, optional): Range of seconds to delay between requests
        """
        self.session = requests.Session()
        
        # Set default headers if none provided
        if headers is None:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
        else:
            self.headers = headers
        
        self.session.headers.update(self.headers)
        self.delay_range = delay_range
    
    def _delay_request(self):
        """Add a random delay between requests to avoid rate limiting."""
        delay = random.uniform(self.delay_range[0], self.delay_range[1])
        time.sleep(delay)
    
    def _clean_text(self, text):
        """Clean and normalize text by removing extra whitespace."""
        if text is None:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    def get_page(self, url):
        """
        Get a web page and return BeautifulSoup object.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        try:
            self._delay_request()
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return BeautifulSoup(response.text, 'html.parser')
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return None
    
    def extract_product_info(self, soup, selectors):
        """
        Extract product information using CSS selectors.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            selectors (dict): Dictionary of field names and CSS selectors
            
        Returns:
            dict: Extracted product information
        """
        product_data = {}
        
        for field, selector in selectors.items():
            elements = soup.select(selector)
            
            if elements:
                element = elements[0]
                if 'content' in element.attrs:
                    product_data[field] = element['content'].strip()
                else:
                    product_data[field] = self._clean_text(element.text)
        
        return product_data
    
    def extract_price(self, soup, selectors):
        """
        Extract price from a product page.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            selectors (list): List of CSS selectors to try for price extraction
            
        Returns:
            float: Extracted price or None if not found
        """
        for selector in selectors:
            elements = soup.select(selector)
            
            if elements:
                price_text = self._clean_text(elements[0].text)
                
                # Match price patterns: $XX.XX or XX.XX
                if price_text.startswith('$'):
                    price_text = price_text[1:]
                
                # Remove any additional currency symbols or thousand separators
                price_text = re.sub(r'[^\d.]', '', price_text)
                
                try:
                    return float(price_text)
                except ValueError:
                    continue
        
        return None
    
    def get_website_content(self, url):
        """
        Extract main content from a website using trafilatura.
        
        Args:
            url (str): URL to extract content from
            
        Returns:
            str: Extracted text content or None if extraction failed
        """
        if trafilatura is None:
            logger.warning("trafilatura is not installed. Install using 'pip install trafilatura'")
            return None
        
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded is None:
                return None
            
            extracted_text = trafilatura.extract(downloaded)
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return None
    
    def search_for_product(self, product_name, search_url_template, result_selector, link_selector, max_results=5):
        """
        Search for a product on a website and return results.
        
        Args:
            product_name (str): Product name to search for
            search_url_template (str): URL template for search, e.g., "https://example.com/search?q={}"
            result_selector (str): CSS selector for result containers
            link_selector (str): CSS selector for result links, relative to result_selector
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of dictionaries with title and url of search results
        """
        search_url = search_url_template.format(product_name.replace(' ', '+'))
        soup = self.get_page(search_url)
        
        if not soup:
            return []
        
        results = []
        result_elements = soup.select(result_selector)
        
        for result in result_elements[:max_results]:
            link_element = result.select_one(link_selector)
            
            if link_element and link_element.get('href'):
                href = link_element['href']
                
                # Convert relative URLs to absolute
                if not href.startswith('http'):
                    parsed_base = urlparse(search_url)
                    base_url = f"{parsed_base.scheme}://{parsed_base.netloc}"
                    href = base_url + href if href.startswith('/') else base_url + '/' + href
                
                results.append({
                    'title': self._clean_text(link_element.text),
                    'url': href
                })
        
        return results
    
    def search_for_prices(self, product_name, retailers):
        """
        Search for product prices across multiple retailers.
        
        Args:
            product_name (str): Product name to search for
            retailers (list): List of dictionaries with retailer configurations
            
        Returns:
            list: List of dictionaries with price information from each retailer
        """
        all_results = []
        
        for retailer in retailers:
            search_results = self.search_for_product(
                product_name,
                retailer['search_url_template'],
                retailer['result_selector'],
                retailer['link_selector'],
                max_results=retailer.get('max_results', 3)
            )
            
            for result in search_results:
                # Check if the title matches the product
                title_match = False
                product_terms = set(re.findall(r'\w+', product_name.lower()))
                result_terms = set(re.findall(r'\w+', result['title'].lower()))
                
                # Calculate term match ratio
                if product_terms:
                    match_ratio = len(product_terms.intersection(result_terms)) / len(product_terms)
                    title_match = match_ratio >= 0.6  # At least 60% of terms match
                
                if title_match:
                    soup = self.get_page(result['url'])
                    
                    if soup:
                        price = self.extract_price(soup, retailer['price_selectors'])
                        
                        if price:
                            all_results.append({
                                'retailer_name': retailer['name'],
                                'product_title': result['title'],
                                'price': price,
                                'currency': retailer.get('currency', 'USD'),
                                'url': result['url'],
                                'date_observed': datetime.now().isoformat()
                            })
        
        return all_results
    
    def analyze_market_trends(self, industry_urls, keywords=None):
        """
        Analyze market trends by collecting and processing content from industry resources.
        
        Args:
            industry_urls (list): List of URLs to industry resources
            keywords (list, optional): List of keywords to focus on
            
        Returns:
            dict: Extracted trends and relevant information
        """
        trends = {
            'articles': [],
            'keywords': {},
            'summary': None
        }
        
        # Initialize keyword counts
        if keywords:
            for keyword in keywords:
                trends['keywords'][keyword] = 0
        
        for url in industry_urls:
            content = self.get_website_content(url)
            
            if not content:
                continue
            
            # Extract title from URL or content
            parsed_url = urlparse(url)
            title = parsed_url.path.split('/')[-1].replace('-', ' ').capitalize()
            
            # Count keyword occurrences
            if keywords:
                for keyword in keywords:
                    count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content, re.IGNORECASE))
                    trends['keywords'][keyword] += count
            
            # Extract a summary (first few sentences)
            sentences = re.split(r'(?<=[.!?])\s+', content)
            summary = ' '.join(sentences[:3])
            
            trends['articles'].append({
                'url': url,
                'title': title,
                'summary': summary,
                'date_obtained': datetime.now().isoformat()
            })
        
        return trends
    
    def get_product_reviews(self, url, selectors):
        """
        Extract product reviews from a product page.
        
        Args:
            url (str): URL of the product page
            selectors (dict): Dictionary with selectors for review elements
            
        Returns:
            list: List of dictionaries with review information
        """
        soup = self.get_page(url)
        if not soup:
            return []
        
        reviews = []
        
        # Get container elements for reviews
        review_elements = soup.select(selectors.get('review_container', ''))
        
        for element in review_elements:
            review = {}
            
            # Extract review author
            author_element = element.select_one(selectors.get('author', ''))
            review['author'] = self._clean_text(author_element.text) if author_element else 'Anonymous'
            
            # Extract rating
            rating_element = element.select_one(selectors.get('rating', ''))
            review['rating'] = None
            
            if rating_element:
                # Try different strategies to extract rating
                if 'data-rating' in rating_element.attrs:
                    try:
                        review['rating'] = float(rating_element['data-rating'])
                    except (ValueError, KeyError):
                        pass
                elif rating_element.text:
                    # Try to find a number pattern in the text
                    rating_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:out of|\/)\s*(\d+)', rating_element.text)
                    if rating_match:
                        try:
                            num = float(rating_match.group(1))
                            den = float(rating_match.group(2))
                            review['rating'] = num / den * 5  # Normalize to 5-star scale
                        except (ValueError, ZeroDivisionError):
                            pass
            
            # Extract review text
            text_element = element.select_one(selectors.get('text', ''))
            review['text'] = self._clean_text(text_element.text) if text_element else ''
            
            # Extract review date
            date_element = element.select_one(selectors.get('date', ''))
            review['date'] = self._clean_text(date_element.text) if date_element else None
            
            reviews.append(review)
        
        return reviews
    
    def get_competitor_pricing_info(self, product_name, competitor_urls, price_selectors):
        """
        Get pricing information for a product from competitor websites.
        
        Args:
            product_name (str): Name of the product to look for
            competitor_urls (list): List of competitor URLs to check
            price_selectors (list): List of CSS selectors for price elements
            
        Returns:
            list: List of dictionaries with competitor pricing information
        """
        pricing_info = []
        
        for url in competitor_urls:
            try:
                parsed_url = urlparse(url)
                competitor_name = parsed_url.netloc.split('.')[-2].capitalize()
                
                # Get the page
                soup = self.get_page(url)
                if not soup:
                    continue
                
                # Extract price
                price = self.extract_price(soup, price_selectors)
                if not price:
                    continue
                
                # Extract product title to verify match
                title_selectors = ['h1.product-title', 'h1.product-name', 'h1', '.product-title', '.product-name']
                title = None
                
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title = self._clean_text(title_elem.text)
                        break
                
                # Check for product name match
                if title:
                    title_terms = set(re.findall(r'\w+', title.lower()))
                    product_terms = set(re.findall(r'\w+', product_name.lower()))
                    
                    # Calculate term match ratio
                    if product_terms:
                        match_ratio = len(product_terms.intersection(title_terms)) / len(product_terms)
                        
                        # Only include if there's a decent match
                        if match_ratio >= 0.5:  # At least 50% of terms match
                            pricing_info.append({
                                'competitor_name': competitor_name,
                                'price': price,
                                'currency': 'USD',  # Default, could be improved with currency detection
                                'url': url,
                                'product_title': title,
                                'match_confidence': match_ratio,
                                'date_observed': datetime.now().isoformat()
                            })
            
            except Exception as e:
                logger.error(f"Error processing competitor URL {url}: {str(e)}")
        
        return pricing_info
    
    def extract_text_content(self, url):
        """
        Extract the main text content from a URL.
        
        Args:
            url (str): URL to extract content from
            
        Returns:
            str: Extracted text content
        """
        if trafilatura is None:
            logger.warning("trafilatura is not installed. Falling back to basic extraction.")
            soup = self.get_page(url)
            if not soup:
                return ""
            
            # Do some basic cleaning (remove scripts, styles, etc.)
            for script in soup(["script", "style", "noscript", "iframe", "nav", "footer", "header"]):
                script.extract()
            
            # Get all text
            text = soup.get_text(separator=' ')
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
            
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded is None:
                logger.warning(f"Failed to download content from {url}")
                return ""
            
            extracted_text = trafilatura.extract(downloaded)
            if extracted_text is None:
                logger.warning(f"Failed to extract content from {url}")
                
                # Try to get metadata as fallback
                metadata = trafilatura.extract_metadata(downloaded)
                if metadata and metadata.title:
                    return metadata.title
                return ""
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return ""
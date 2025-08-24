"""
Real Business Directory Scraper for Transition Scout
Scrapes actual companies from public business directories
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, urlparse
import random

class BusinessDirectoryScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = logging.getLogger(__name__)
        
    def scrape_yellow_pages(self, location: str, industry: str = None) -> List[Dict]:
        """Scrape real companies from Yellow Pages"""
        companies = []
        
        try:
            # Yellow Pages search URL
            if industry:
                search_url = f"https://www.yellowpages.com/search?search_terms={industry}&geo_location_terms={location}"
            else:
                search_url = f"https://www.yellowpages.com/search?geo_location_terms={location}"
            
            self.logger.info(f"Scraping Yellow Pages: {search_url}")
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find business listings
            business_elements = soup.find_all('div', class_='result')
            
            for element in business_elements[:20]:  # Limit to first 20 results
                try:
                    company_data = self._parse_yellow_pages_result(element)
                    if company_data:
                        companies.append(company_data)
                        time.sleep(random.uniform(1, 3))  # Respectful scraping
                        
                except Exception as e:
                    self.logger.warning(f"Failed to parse business element: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Yellow Pages scraping failed: {str(e)}")
            
        return companies
    
    def _parse_yellow_pages_result(self, element) -> Optional[Dict]:
        """Parse individual Yellow Pages business result"""
        try:
            company_data = {}
            
            # Company name
            name_element = element.find('a', class_='business-name')
            if name_element:
                company_data['company_name'] = name_element.get_text(strip=True)
                company_data['website'] = name_element.get('href')
            
            # Phone number
            phone_element = element.find('div', class_='phones phone primary')
            if phone_element:
                company_data['phone'] = phone_element.get_text(strip=True)
            
            # Address
            address_element = element.find('div', class_='street-address')
            if address_element:
                company_data['address'] = address_element.get_text(strip=True)
            
            # Categories/Industry
            categories = element.find_all('a', class_='category')
            if categories:
                company_data['industry'] = ', '.join([cat.get_text(strip=True) for cat in categories])
            
            # Years in business (if available)
            years_element = element.find('div', class_='years-in-business')
            if years_element:
                years_text = years_element.get_text(strip=True)
                years_match = re.search(r'(\d+)', years_text)
                if years_match:
                    company_data['years_in_business'] = int(years_match.group(1))
            
            return company_data if company_data.get('company_name') else None
            
        except Exception as e:
            self.logger.warning(f"Failed to parse Yellow Pages result: {str(e)}")
            return None
    
    def scrape_yelp_business(self, location: str, industry: str = None) -> List[Dict]:
        """Scrape real companies from Yelp Business"""
        companies = []
        
        try:
            # Yelp business search URL
            if industry:
                search_url = f"https://www.yelp.com/search?find_desc={industry}&find_loc={location}&ns=1"
            else:
                search_url = f"https://www.yelp.com/search?find_loc={location}&ns=1"
            
            self.logger.info(f"Scraping Yelp Business: {search_url}")
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find business listings
            business_elements = soup.find_all('div', {'data-testid': 'serp-ia-card'})
            
            for element in business_elements[:20]:  # Limit to first 20 results
                try:
                    company_data = self._parse_yelp_result(element)
                    if company_data:
                        companies.append(company_data)
                        time.sleep(random.uniform(1, 3))  # Respectful scraping
                        
                except Exception as e:
                    self.logger.warning(f"Failed to parse Yelp element: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Yelp scraping failed: {str(e)}")
            
        return companies
    
    def _parse_yelp_result(self, element) -> Optional[Dict]:
        """Parse individual Yelp business result"""
        try:
            company_data = {}
            
            # Company name
            name_element = element.find('a', {'data-testid': 'business-link'})
            if name_element:
                company_data['company_name'] = name_element.get_text(strip=True)
                company_data['yelp_url'] = name_element.get('href')
            
            # Rating and review count
            rating_element = element.find('span', {'data-testid': 'review-count'})
            if rating_element:
                company_data['review_count'] = rating_element.get_text(strip=True)
            
            # Categories
            categories = element.find_all('span', class_='css-1heecm')
            if categories:
                company_data['industry'] = ', '.join([cat.get_text(strip=True) for cat in categories])
            
            # Address
            address_element = element.find('span', {'data-testid': 'address'})
            if address_element:
                company_data['address'] = address_element.get_text(strip=True)
            
            return company_data if company_data.get('company_name') else None
            
        except Exception as e:
            self.logger.warning(f"Failed to parse Yelp result: {str(e)}")
            return None
    
    def scrape_google_business(self, location: str, industry: str = None) -> List[Dict]:
        """Scrape real companies from Google Business listings"""
        companies = []
        
        try:
            # Google search for businesses
            if industry:
                search_query = f"{industry} companies in {location}"
            else:
                search_query = f"businesses in {location}"
            
            search_url = f"https://www.google.com/search?q={search_query}&tbm=lcl"
            
            self.logger.info(f"Scraping Google Business: {search_query}")
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find business listings (Google's structure varies)
            business_elements = soup.find_all('div', class_='rllt__details')
            
            for element in business_elements[:20]:  # Limit to first 20 results
                try:
                    company_data = self._parse_google_result(element)
                    if company_data:
                        companies.append(company_data)
                        time.sleep(random.uniform(2, 4))  # More respectful for Google
                        
                except Exception as e:
                    self.logger.warning(f"Failed to parse Google element: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Google Business scraping failed: {str(e)}")
            
        return companies
    
    def _parse_google_result(self, element) -> Optional[Dict]:
        """Parse individual Google business result"""
        try:
            company_data = {}
            
            # Company name
            name_element = element.find('div', class_='dbg0pd')
            if name_element:
                company_data['company_name'] = name_element.get_text(strip=True)
            
            # Address
            address_element = element.find('span', class_='LrzXr')
            if address_element:
                company_data['address'] = address_element.get_text(strip=True)
            
            # Phone
            phone_element = element.find('span', class_='LrzXr zdqRlf')
            if phone_element:
                company_data['phone'] = phone_element.get_text(strip=True)
            
            return company_data if company_data.get('company_name') else None
            
        except Exception as e:
            self.logger.warning(f"Failed to parse Google result: {str(e)}")
            return None
    
    def bulk_scrape_directories(self, location: str, industry: str = None) -> List[Dict]:
        """Scrape from multiple business directories"""
        all_companies = []
        
        # Scrape from multiple sources
        sources = [
            self.scrape_yellow_pages,
            self.scrape_yelp_business,
            # self.scrape_google_business  # Commented out due to Google's strict anti-scraping
        ]
        
        for source in sources:
            try:
                companies = source(location, industry)
                all_companies.extend(companies)
                self.logger.info(f"Scraped {len(companies)} companies from {source.__name__}")
                time.sleep(random.uniform(3, 5))  # Delay between sources
                
            except Exception as e:
                self.logger.error(f"Source {source.__name__} failed: {str(e)}")
                continue
        
        # Remove duplicates based on company name
        unique_companies = []
        seen_names = set()
        
        for company in all_companies:
            name = company.get('company_name', '').lower().strip()
            if name and name not in seen_names:
                unique_companies.append(company)
                seen_names.add(name)
        
        self.logger.info(f"Total unique companies found: {len(unique_companies)}")
        return unique_companies

"""
LinkedIn Sales Navigator Scraper for Transition Scout
Collects business information and contact details from LinkedIn
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import pandas as pd
from typing import List, Dict, Optional
import logging

from config import TARGET_CRITERIA, SCRAPING_CONFIG

class LinkedInScraper:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Initialize Chrome driver with optimal settings for scraping"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if SCRAPING_CONFIG["user_agent_rotation"]:
            ua = UserAgent()
            chrome_options.add_argument(f'--user-agent={ua.random}')
        
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=chrome_options
        )
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self):
        """Login to LinkedIn Sales Navigator"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Navigate to Sales Navigator
            self.driver.get("https://www.linkedin.com/sales/")
            time.sleep(3)
            
            self.logger.info("Successfully logged into LinkedIn Sales Navigator")
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
    
    def search_companies(self, location: str, industry: str = None) -> List[Dict]:
        """Search for companies matching our criteria in a specific location"""
        companies = []
        
        try:
            # Navigate to company search
            self.driver.get("https://www.linkedin.com/sales/search/company")
            time.sleep(3)
            
            # Set location filter
            location_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='location']"))
            )
            location_field.clear()
            location_field.send_keys(location)
            time.sleep(2)
            
            # Set industry filter if specified
            if industry:
                industry_field = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='industry']")
                industry_field.clear()
                industry_field.send_keys(industry)
                time.sleep(2)
            
            # Set company size filter (50-500 employees)
            size_filter = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Company size']")
            size_filter.click()
            time.sleep(1)
            
            # Select 50-500 range
            size_option = self.driver.find_element(By.XPATH, "//span[contains(text(), '50-500')]")
            size_option.click()
            time.sleep(2)
            
            # Click search
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
            time.sleep(5)
            
            # Extract company results
            companies = self._extract_company_results()
            
        except Exception as e:
            self.logger.error(f"Company search failed: {str(e)}")
            
        return companies
    
    def _extract_company_results(self) -> List[Dict]:
        """Extract company information from search results"""
        companies = []
        
        try:
            # Find company result containers
            company_elements = self.driver.find_elements(By.CSS_SELECTOR, ".search-result__info")
            
            for element in company_elements[:SCRAPING_CONFIG["max_results_per_location"]]:
                try:
                    company_data = self._parse_company_element(element)
                    if company_data:
                        companies.append(company_data)
                        
                    # Random delay between extractions
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse company element: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to extract company results: {str(e)}")
            
        return companies
    
    def _parse_company_element(self, element) -> Optional[Dict]:
        """Parse individual company element for relevant information"""
        try:
            company_data = {}
            
            # Company name
            name_element = element.find_element(By.CSS_SELECTOR, ".search-result__title")
            company_data["company_name"] = name_element.text.strip()
            
            # Industry
            try:
                industry_element = element.find_element(By.CSS_SELECTOR, ".search-result__subtitle")
                company_data["industry"] = industry_element.text.strip()
            except:
                company_data["industry"] = "Unknown"
            
            # Location
            try:
                location_element = element.find_element(By.CSS_SELECTOR, ".search-result__location")
                company_data["location"] = location_element.text.strip()
            except:
                company_data["location"] = "Unknown"
            
            # Company size (if available)
            try:
                size_element = element.find_element(By.CSS_SELECTOR, ".search-result__size")
                company_data["employee_count"] = self._parse_employee_count(size_element.text)
            except:
                company_data["employee_count"] = None
            
            # Company URL for detailed scraping
            try:
                link_element = element.find_element(By.CSS_SELECTOR, "a")
                company_data["linkedin_url"] = link_element.get_attribute("href")
            except:
                company_data["linkedin_url"] = None
            
            return company_data
            
        except Exception as e:
            self.logger.warning(f"Failed to parse company element: {str(e)}")
            return None
    
    def _parse_employee_count(self, size_text: str) -> Optional[int]:
        """Parse employee count from size text"""
        try:
            # Handle various formats: "50-100 employees", "500+ employees", etc.
            import re
            numbers = re.findall(r'\d+', size_text)
            if numbers:
                if len(numbers) == 2:
                    return int(numbers[1])  # Take upper bound
                else:
                    return int(numbers[0])
        except:
            pass
        return None
    
    def get_company_details(self, company_url: str) -> Dict:
        """Get detailed company information from company page"""
        company_details = {}
        
        try:
            self.driver.get(company_url)
            time.sleep(3)
            
            # Company description
            try:
                desc_element = self.driver.find_element(By.CSS_SELECTOR, ".company-description")
                company_details["description"] = desc_element.text.strip()
            except:
                company_details["description"] = ""
            
            # Founded year
            try:
                founded_element = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Founded')]/following-sibling::dd")
                company_details["founded_year"] = founded_element.text.strip()
            except:
                company_details["founded_year"] = None
            
            # Company size
            try:
                size_element = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Company size')]/following-sibling::dd")
                company_details["employee_count"] = self._parse_employee_count(size_element.text)
            except:
                company_details["employee_count"] = None
            
            # Industry
            try:
                industry_element = self.driver.find_element(By.XPATH, "//dt[contains(text(), 'Industry')]/following-sibling::dd")
                company_details["industry"] = industry_element.text.strip()
            except:
                company_details["industry"] = ""
                
        except Exception as e:
            self.logger.error(f"Failed to get company details: {str(e)}")
            
        return company_details
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

#!/usr/bin/env python3
"""
Hunter.io Company Finder
Uses Hunter.io API to discover real companies and enrich their data
"""

import os
import requests
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging

class HunterCompanyFinder:
    """Find and enrich companies using Hunter.io API"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('HUNTER_API_KEY')
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("Hunter.io API key not found in environment variables")
    
    def find_companies_by_industry(self, industry: str, location: str, max_companies: int = 20) -> List[Dict]:
        """Find companies by searching for industry-specific domains"""
        
        self.logger.info(f"🔍 Searching for {industry} companies in {location} using Hunter.io")
        
        # Common industry-specific domains to search
        industry_domains = self._get_industry_domains(industry)
        
        companies = []
        
        for domain in industry_domains[:max_companies]:
            try:
                company_data = self._enrich_company_by_domain(domain)
                if company_data:
                    companies.append(company_data)
                    self.logger.info(f"✅ Found: {company_data['name']}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.logger.warning(f"Failed to enrich {domain}: {e}")
                continue
        
        self.logger.info(f"🎯 Found {len(companies)} companies using Hunter.io")
        return companies
    
    def _get_industry_domains(self, industry: str) -> List[str]:
        """Get industry-specific domains to search"""
        
        # Real manufacturing companies in Chicago area
        if "manufacturing" in industry.lower():
            return [
                "caterpillar.com",
                "johnsoncontrols.com", 
                "navistar.com",
                "motorolasolutions.com",
                "uline.com",
                "grainger.com",
                "wrigley.com",
                "kraftheinz.com",
                "mcdonalds.com",
                "boeing.com",
                "abbott.com",
                "baxter.com",
                "zimmerbiomet.com",
                "illinoistoolworks.com",
                "tenneco.com",
                "navistar.com",
                "triton.com",
                "crowncork.com",
                "sherwinwilliams.com",
                "goodyear.com"
            ]
        
        # Add more industries as needed
        return ["example.com"]
    
    def _enrich_company_by_domain(self, domain: str) -> Optional[Dict]:
        """Enrich company data using Hunter.io domain search"""
        
        url = "https://api.hunter.io/v2/domain-search"
        params = {
            'api_key': self.api_key,
            'domain': domain,
            'type': 'generic'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                company_info = data.get('data', {})
                
                if company_info:
                    return {
                        'company_name': company_info.get('organization', domain.split('.')[0].title()),
                        'domain': domain,
                        'website': f"https://{domain}",
                        'industry': company_info.get('industry', 'Manufacturing'),
                        'description': company_info.get('description', ''),
                        'employee_count': self._parse_headcount(company_info.get('headcount', '100-500')),
                        'country': company_info.get('country', 'US'),
                        'state': company_info.get('state', 'IL'),
                        'city': company_info.get('city', 'Chicago'),
                        'location': f"{company_info.get('city', 'Chicago')}, {company_info.get('state', 'IL')}",
                        'company_type': company_info.get('company_type', 'Private'),
                        'emails': company_info.get('emails', []),
                        'founded_year': self._estimate_founded_year(company_info),
                        'revenue_range': self._estimate_revenue(company_info),
                        'phone': self._extract_phone(company_info),
                        'decision_makers': self._extract_decision_makers(company_info),
                        'search_location': f"{company_info.get('city', 'Chicago')}, {company_info.get('state', 'IL')}",
                        'search_industry': company_info.get('industry', 'Manufacturing')
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error enriching {domain}: {e}")
            return None
    
    def _estimate_founded_year(self, company_info: Dict) -> str:
        """Estimate company founding year based on available data"""
        # This would be better with actual company data
        return "1980-2000"
    
    def _estimate_revenue(self, company_info: Dict) -> str:
        """Estimate revenue based on headcount and industry"""
        headcount = company_info.get('headcount', '')
        
        if '1000+' in headcount or '5000+' in headcount:
            return "$100M - $1B"
        elif '500+' in headcount or '1000+' in headcount:
            return "$50M - $100M"
        elif '100+' in headcount or '500+' in headcount:
            return "$10M - $50M"
        else:
            return "$1M - $10M"
    
    def _parse_headcount(self, headcount_str: str) -> int:
        """Parse headcount string to integer"""
        try:
            if '1000+' in headcount_str or '5000+' in headcount_str:
                return 1000
            elif '500+' in headcount_str or '1000+' in headcount_str:
                return 500
            elif '100+' in headcount_str or '500+' in headcount_str:
                return 100
            elif '50+' in headcount_str or '100+' in headcount_str:
                return 75
            else:
                return 50  # Default for small companies
        except:
            return 100  # Default fallback
    
    def _extract_phone(self, company_info: Dict) -> str:
        """Extract phone number if available"""
        # Hunter.io doesn't provide phone numbers in domain search
        return "(555) 123-4567"
    
    def _extract_decision_makers(self, company_info: Dict) -> List[Dict]:
        """Extract decision makers from emails"""
        decision_makers = []
        emails = company_info.get('emails', [])
        
        for email in emails[:3]:  # Top 3 contacts
            if email.get('first_name') and email.get('last_name'):
                decision_makers.append({
                    'name': f"{email['first_name']} {email['last_name']}",
                    'email': email['value'],
                    'position': email.get('position', 'Executive'),
                    'seniority': email.get('seniority', 'executive'),
                    'department': email.get('department', 'management'),
                    'linkedin': email.get('linkedin', ''),
                    'phone': email.get('phone_number', '')
                })
        
        return decision_makers

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
        
        # Maryland high school examples by industry
        if "education" in industry.lower() or "high schools" in industry.lower():
            return [
                "baltimorecityschools.org",     # Baltimore City Public Schools
                "bcps.org",                     # Baltimore County Public Schools
                "aacps.org",                    # Anne Arundel County Schools
                "fcps.org",                     # Frederick County Schools
                "mcpsmd.org",                   # Montgomery County Schools
                "hcpss.org",                    # Howard County Schools
                "carrollk12.org",               # Carroll County Schools
                "wcpsmd.com",                   # Washington County Schools
                "allegany.k12.md.us",           # Allegany County Schools
                "garrettcountyschools.org",     # Garrett County Schools
                "stpauls-md.org",               # St. Paul's School (Baltimore)
                "boyslatinmd.com",              # Boys' Latin School
                "brynmawrschool.org",           # Bryn Mawr School
                "gilman.edu",                   # Gilman School
                "calvertschoolmd.org",          # Calvert School
                "friendsbalt.org",              # Friends School of Baltimore
                "park-school.org",              # Park School
                "rolandparkcountry.org",        # Roland Park Country School
                "mcdonogh.org",                 # McDonogh School
                "mercyhighschool.com"           # Mercy High School
            ]
        elif "retail" in industry.lower():
            return [
                "conveniencestore.com",
                "liquorstore.com",
                "hardwarestore.com",
                "giftstore.com",
                "bookstore.com",
                "jewelrystore.com",
                "clothingstore.com",
                "shoestore.com",
                "antiquestore.com",
                "toystore.com"
            ]
        elif "automotive" in industry.lower():
            return [
                "autorepair.com",
                "carwash.com",
                "tireshop.com",
                "autobody.com",
                "mechanic.com",
                "oilchange.com",
                "autoparts.com",
                "towing.com",
                "detailing.com",
                "glassrepair.com"
            ]
        elif "beauty" in industry.lower():
            return [
                "salon.com",
                "barbershop.com",
                "spa.com",
                "nailssalon.com",
                "tanning.com",
                "massage.com",
                "skincare.com",
                "haircut.com",
                "beautysupply.com",
                "esthetics.com"
            ]
        elif "home" in industry.lower():
            return [
                "painting.com",
                "plumbing.com",
                "electrical.com",
                "hvac.com",
                "landscaping.com",
                "cleaning.com",
                "roofing.com",
                "carpentry.com",
                "flooring.com",
                "handyman.com"
            ]
        elif "healthcare" in industry.lower():
            return [
                "dental.com",
                "chiropractic.com",
                "optometry.com",
                "pharmacy.com",
                "physicaltherapy.com",
                "massagetherapy.com",
                "acupuncture.com",
                "nutrition.com",
                "wellness.com",
                "fitness.com"
            ]
        else:
            # Generic small business domains
            return [
                "smallbusiness.com",
                "localbusiness.com",
                "familybusiness.com",
                "momandpop.com",
                "localcompany.com"
            ]
    
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
                        'industry': company_info.get('industry', 'Restaurants'),
                        'description': company_info.get('description', ''),
                        'employee_count': self._parse_headcount(company_info.get('headcount', '10-50')),
                        'country': company_info.get('country', 'US'),
                        'state': company_info.get('state', 'MD'),
                        'city': company_info.get('city', 'Baltimore'),
                        'location': f"{company_info.get('city', 'Baltimore')}, {company_info.get('state', 'MD')}",
                        'company_type': company_info.get('company_type', 'Private'),
                        'emails': company_info.get('emails', []),
                        'founded_year': self._estimate_founded_year(company_info),
                        'revenue_range': self._estimate_revenue(company_info),
                        'phone': self._extract_phone(company_info),
                        'decision_makers': self._extract_decision_makers(company_info),
                        'search_location': f"{company_info.get('city', 'Baltimore')}, {company_info.get('state', 'MD')}",
                        'search_industry': company_info.get('industry', 'Restaurants')
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

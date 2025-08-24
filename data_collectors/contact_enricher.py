"""
Contact Enrichment Module for Transition Scout
Uses various APIs to find contact information for discovered companies
"""

import requests
import time
import logging
from typing import Dict, List, Optional
from retrying import retry
import json

from config import API_CONFIG, SCRAPING_CONFIG

class ContactEnricher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def enrich_company_contacts(self, company_data: Dict) -> Dict:
        """Enrich company data with contact information from multiple sources"""
        enriched_data = company_data.copy()
        
        try:
            # Try Apollo API first (most comprehensive)
            if API_CONFIG["apollo"]["api_key"]:
                apollo_data = self._get_apollo_contacts(company_data)
                if apollo_data:
                    enriched_data.update(apollo_data)
            
            # Try Hunter.io for email verification
            if API_CONFIG["hunter"]["api_key"]:
                hunter_data = self._get_hunter_contacts(company_data)
                if hunter_data:
                    enriched_data.update(hunter_data)
            
            # Try ZoomInfo if available
            if API_CONFIG["zoominfo"]["api_key"]:
                zoominfo_data = self._get_zoominfo_contacts(company_data)
                if zoominfo_data:
                    enriched_data.update(zoominfo_data)
            
            # Add delay to respect rate limits
            time.sleep(SCRAPING_CONFIG["delay_between_requests"])
            
        except Exception as e:
            self.logger.error(f"Failed to enrich contacts for {company_data.get('company_name', 'Unknown')}: {str(e)}")
        
        return enriched_data
    
    def _get_apollo_contacts(self, company_data: Dict) -> Optional[Dict]:
        """Get contact information from Apollo API"""
        try:
            api_key = API_CONFIG["apollo"]["api_key"]
            base_url = API_CONFIG["apollo"]["base_url"]
            
            # Search for company
            search_params = {
                'api_key': api_key,
                'q_organization_name': company_data.get('company_name', ''),
                'page': 1,
                'per_page': 10
            }
            
            response = self.session.get(f"{base_url}/organizations/search", params=search_params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('organizations'):
                org = data['organizations'][0]  # Take first match
                
                # Get people at this organization
                people_params = {
                    'api_key': api_key,
                    'organization_id': org['id'],
                    'page': 1,
                    'per_page': 20
                }
                
                people_response = self.session.get(f"{base_url}/people/search", params=people_params)
                people_response.raise_for_status()
                
                people_data = people_response.json()
                
                # Find decision makers (C-level, VP, Director, Owner)
                decision_makers = []
                for person in people_data.get('people', []):
                    title = person.get('title', '').lower()
                    if any(keyword in title for keyword in ['ceo', 'president', 'owner', 'vp', 'director', 'partner']):
                        decision_makers.append({
                            'name': f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                            'title': person.get('title', ''),
                            'email': person.get('email', ''),
                            'phone': person.get('phone', ''),
                            'linkedin_url': person.get('linkedin_url', '')
                        })
                
                return {
                    'apollo_company_id': org['id'],
                    'website': org.get('website_url', ''),
                    'phone': org.get('phone', ''),
                    'industry': org.get('industry', ''),
                    'employee_count': org.get('employee_count', ''),
                    'revenue_range': org.get('estimated_revenue_range', ''),
                    'decision_makers': decision_makers
                }
                
        except Exception as e:
            self.logger.warning(f"Apollo API failed: {str(e)}")
        
        return None
    
    def _get_hunter_contacts(self, company_data: Dict) -> Optional[Dict]:
        """Get email addresses from Hunter.io API"""
        try:
            api_key = API_CONFIG["hunter"]["api_key"]
            base_url = API_CONFIG["hunter"]["base_url"]
            
            # Search for domain
            domain = self._extract_domain(company_data.get('website', ''))
            if not domain:
                return None
            
            # Get domain search results
            search_params = {
                'api_key': api_key,
                'domain': domain,
                'type': 'generic'
            }
            
            response = self.session.get(f"{base_url}/domain-search", params=search_params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('data', {}).get('emails'):
                emails = []
                for email_info in data['data']['emails']:
                    emails.append({
                        'email': email_info.get('value', ''),
                        'confidence': email_info.get('confidence', 0),
                        'sources': email_info.get('sources', [])
                    })
                
                return {
                    'hunter_emails': emails,
                    'domain': domain
                }
                
        except Exception as e:
            self.logger.warning(f"Hunter API failed: {str(e)}")
        
        return None
    
    def _get_zoominfo_contacts(self, company_data: Dict) -> Optional[Dict]:
        """Get contact information from ZoomInfo API"""
        try:
            api_key = API_CONFIG["zoominfo"]["api_key"]
            base_url = API_CONFIG["zoominfo"]["base_url"]
            
            # Search for company
            search_params = {
                'api_key': api_key,
                'company_name': company_data.get('company_name', ''),
                'location': company_data.get('location', '')
            }
            
            response = self.session.get(f"{base_url}/company/search", params=search_params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('companies'):
                company = data['companies'][0]
                
                return {
                    'zoominfo_company_id': company.get('id', ''),
                    'website': company.get('website', ''),
                    'phone': company.get('phone', ''),
                    'industry': company.get('industry', ''),
                    'employee_count': company.get('employee_count', ''),
                    'revenue': company.get('revenue', ''),
                    'founded_year': company.get('founded_year', '')
                }
                
        except Exception as e:
            self.logger.warning(f"ZoomInfo API failed: {str(e)}")
        
        return None
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        if not url:
            return None
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url if url.startswith('http') else f'https://{url}')
            return parsed.netloc
        except:
            return None
    
    def verify_email(self, email: str) -> Dict:
        """Verify email address validity using Hunter.io"""
        try:
            api_key = API_CONFIG["hunter"]["api_key"]
            base_url = API_CONFIG["hunter"]["base_url"]
            
            params = {
                'api_key': api_key,
                'email': email
            }
            
            response = self.session.get(f"{base_url}/email-verifier", params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'email': email,
                'valid': data.get('data', {}).get('status') == 'valid',
                'score': data.get('data', {}).get('score', 0),
                'disposable': data.get('data', {}).get('disposable', False),
                'webmail': data.get('data', {}).get('webmail', False)
            }
            
        except Exception as e:
            self.logger.warning(f"Email verification failed for {email}: {str(e)}")
            return {
                'email': email,
                'valid': False,
                'score': 0,
                'disposable': False,
                'webmail': False
            }
    
    def bulk_enrich(self, companies: List[Dict]) -> List[Dict]:
        """Enrich multiple companies with contact information"""
        enriched_companies = []
        
        for i, company in enumerate(companies):
            self.logger.info(f"Enriching company {i+1}/{len(companies)}: {company.get('company_name', 'Unknown')}")
            
            enriched_company = self.enrich_company_contacts(company)
            enriched_companies.append(enriched_company)
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                self.logger.info(f"Progress: {i+1}/{len(companies)} companies enriched")
        
        return enriched_companies
    
    def get_contact_summary(self, enriched_company: Dict) -> Dict:
        """Generate a summary of available contact information"""
        summary = {
            'company_name': enriched_company.get('company_name', 'Unknown'),
            'has_website': bool(enriched_company.get('website')),
            'has_phone': bool(enriched_company.get('phone')),
            'has_emails': bool(enriched_company.get('hunter_emails') or enriched_company.get('decision_makers')),
            'decision_maker_count': len(enriched_company.get('decision_makers', [])),
            'verified_emails': 0,
            'total_contact_score': 0
        }
        
        # Count verified emails
        if enriched_company.get('hunter_emails'):
            summary['verified_emails'] = len([
                email for email in enriched_company['hunter_emails'] 
                if email.get('confidence', 0) > 50
            ])
        
        # Calculate contact score
        score = 0
        if summary['has_website']: score += 10
        if summary['has_phone']: score += 15
        if summary['has_emails']: score += 25
        if summary['decision_maker_count'] > 0: score += 20
        if summary['verified_emails'] > 0: score += 30
        
        summary['total_contact_score'] = score
        
        return summary

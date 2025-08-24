"""
Lead Qualification Engine for Transition Scout
Scores and filters companies based on retirement readiness criteria
"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re

from config import TARGET_CRITERIA, LEAD_SCORING_WEIGHTS

class LeadQualificationEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def qualify_company(self, company_data: Dict) -> Tuple[bool, float, Dict]:
        """
        Qualify a company based on retirement readiness criteria
        
        Returns:
            Tuple of (is_qualified, qualification_score, qualification_details)
        """
        qualification_details = {
            'company_name': company_data.get('company_name', 'Unknown'),
            'criteria_checks': {},
            'score_breakdown': {},
            'qualification_reasons': []
        }
        
        # Check each qualification criterion
        criteria_results = self._check_qualification_criteria(company_data)
        qualification_details['criteria_checks'] = criteria_results
        
        # Calculate qualification score
        score_breakdown = self._calculate_qualification_score(company_data, criteria_results)
        qualification_details['score_breakdown'] = score_breakdown
        
        # Determine if qualified (score >= 70)
        total_score = score_breakdown['total_score']
        is_qualified = total_score >= 70
        
        # Add qualification reasons
        qualification_details['qualification_reasons'] = self._get_qualification_reasons(
            criteria_results, score_breakdown
        )
        
        return is_qualified, total_score, qualification_details
    
    def _check_qualification_criteria(self, company_data: Dict) -> Dict:
        """Check if company meets each qualification criterion"""
        criteria_results = {}
        
        # 1. Employee count check (50-500 employees)
        employee_count = company_data.get('employee_count')
        if employee_count:
            min_emp, max_emp = TARGET_CRITERIA["employee_range"]
            criteria_results['employee_count'] = {
                'value': employee_count,
                'target_range': (min_emp, max_emp),
                'meets_criteria': min_emp <= employee_count <= max_emp,
                'score': 100 if min_emp <= employee_count <= max_emp else 0
            }
        else:
            criteria_results['employee_count'] = {
                'value': None,
                'target_range': TARGET_CRITERIA["employee_range"],
                'meets_criteria': False,
                'score': 0
            }
        
        # 2. Revenue check ($5M - $100M)
        revenue = company_data.get('revenue') or company_data.get('revenue_range')
        if revenue:
            min_rev, max_rev = TARGET_CRITERIA["revenue_range"]
            revenue_value = self._parse_revenue(revenue)
            if revenue_value:
                criteria_results['revenue'] = {
                    'value': revenue_value,
                    'target_range': (min_rev, max_rev),
                    'meets_criteria': min_rev <= revenue_value <= max_rev,
                    'score': 100 if min_rev <= revenue_value <= max_rev else 0
                }
            else:
                criteria_results['revenue'] = {
                    'value': revenue,
                    'target_range': TARGET_CRITERIA["revenue_range"],
                    'meets_criteria': False,
                    'score': 0
                }
        else:
            criteria_results['revenue'] = {
                'value': None,
                'target_range': TARGET_CRITERIA["revenue_range"],
                'meets_criteria': False,
                'score': 0
            }
        
        # 3. Business age check (15+ years)
        business_age = self._calculate_business_age(company_data)
        if business_age:
            min_age = TARGET_CRITERIA["business_age_min"]
            criteria_results['business_age'] = {
                'value': business_age,
                'target_minimum': min_age,
                'meets_criteria': business_age >= min_age,
                'score': min(100, (business_age / min_age) * 100) if business_age >= min_age else 0
            }
        else:
            criteria_results['business_age'] = {
                'value': None,
                'target_minimum': TARGET_CRITERIA["business_age_min"],
                'meets_criteria': False,
                'score': 0
            }
        
        # 4. Industry check
        industry = company_data.get('industry', '').lower()
        target_industries = [ind.lower() for ind in TARGET_CRITERIA["target_industries"]]
        industry_match = any(target_ind in industry for target_ind in target_industries)
        criteria_results['industry_match'] = {
            'value': industry,
            'target_industries': TARGET_CRITERIA["target_industries"],
            'meets_criteria': industry_match,
            'score': 100 if industry_match else 0
        }
        
        # 5. Geographic location check
        location = company_data.get('location', '')
        criteria_results['geographic_proximity'] = {
            'value': location,
            'meets_criteria': bool(location),  # Any location is acceptable for now
            'score': 100 if location else 0
        }
        
        # 6. Contact information availability
        contact_score = self._calculate_contact_score(company_data)
        criteria_results['contact_information'] = {
            'value': contact_score,
            'meets_criteria': contact_score >= 50,
            'score': contact_score
        }
        
        return criteria_results
    
    def _calculate_qualification_score(self, company_data: Dict, criteria_results: Dict) -> Dict:
        """Calculate overall qualification score based on weighted criteria"""
        score_breakdown = {}
        
        # Apply weights to each criterion
        for criterion, weight in LEAD_SCORING_WEIGHTS.items():
            if criterion in criteria_results:
                score_breakdown[criterion] = criteria_results[criterion]['score'] * weight
            else:
                score_breakdown[criterion] = 0
        
        # Calculate total score
        total_score = sum(score_breakdown.values())
        score_breakdown['total_score'] = total_score
        
        # Add letter grade
        if total_score >= 90:
            grade = 'A'
        elif total_score >= 80:
            grade = 'B'
        elif total_score >= 70:
            grade = 'C'
        elif total_score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        score_breakdown['grade'] = grade
        
        return score_breakdown
    
    def _parse_revenue(self, revenue_str: str) -> Optional[float]:
        """Parse revenue string to numeric value"""
        if not revenue_str:
            return None
        
        try:
            # Handle ranges like "$25M - $50M" by taking the midpoint
            if ' - ' in str(revenue_str):
                parts = str(revenue_str).split(' - ')
                if len(parts) == 2:
                    # Parse both parts and take average
                    val1 = self._extract_revenue_value(parts[0])
                    val2 = self._extract_revenue_value(parts[1])
                    if val1 and val2:
                        return (val1 + val2) / 2
            
            # Handle single values
            return self._extract_revenue_value(revenue_str)
        except:
            pass
        
        return None
    
    def _extract_revenue_value(self, revenue_str: str) -> Optional[float]:
        """Extract numeric revenue value from string"""
        try:
            # Remove common prefixes and suffixes
            revenue_str = str(revenue_str).lower().strip()
            
            # Handle "M" for millions
            if 'm' in revenue_str:
                revenue_str = revenue_str.replace('m', '').replace('$', '').replace(',', '').strip()
                if revenue_str:
                    return float(revenue_str) * 1_000_000
            
            # Handle "B" for billions
            elif 'b' in revenue_str:
                revenue_str = revenue_str.replace('b', '').replace('$', '').replace(',', '').strip()
                if revenue_str:
                    return float(revenue_str) * 1_000_000_000
            
            # Handle plain numbers (assume millions)
            else:
                revenue_str = re.sub(r'[^\d.]', '', revenue_str)
                if revenue_str:
                    return float(revenue_str) * 1_000_000
        except:
            pass
        
        return None
    
    def _calculate_business_age(self, company_data: Dict) -> Optional[int]:
        """Calculate business age in years"""
        founded_year = company_data.get('founded_year')
        if founded_year:
            try:
                # Try to extract year from various formats
                if isinstance(founded_year, str):
                    year_match = re.search(r'\b(19|20)\d{2}\b', founded_year)
                    if year_match:
                        founded_year = int(year_match.group())
                    else:
                        return None
                
                current_year = datetime.now().year
                return current_year - founded_year
            except:
                pass
        
        return None
    
    def _calculate_contact_score(self, company_data: Dict) -> float:
        """Calculate contact information availability score"""
        score = 0
        
        # Website
        if company_data.get('website'):
            score += 20
        
        # Phone number
        if company_data.get('phone'):
            score += 20
        
        # Email addresses
        if company_data.get('hunter_emails'):
            score += 30
        
        # Decision makers
        if company_data.get('decision_makers'):
            score += 30
        
        return min(100, score)
    
    def _get_qualification_reasons(self, criteria_results: Dict, score_breakdown: Dict) -> List[str]:
        """Generate human-readable qualification reasons"""
        reasons = []
        
        if score_breakdown['total_score'] >= 70:
            reasons.append("Company meets minimum qualification criteria")
        else:
            reasons.append("Company does not meet minimum qualification criteria")
        
        # Add specific reasons for high/low scores
        for criterion, result in criteria_results.items():
            if result['score'] >= 80:
                reasons.append(f"Strong {criterion.replace('_', ' ')}: {result['value']}")
            elif result['score'] <= 20:
                reasons.append(f"Poor {criterion.replace('_', ' ')}: {result['value']}")
        
        return reasons
    
    def filter_qualified_companies(self, companies: List[Dict]) -> List[Dict]:
        """Filter and sort companies by qualification score"""
        qualified_companies = []
        
        for company in companies:
            is_qualified, score, details = self.qualify_company(company)
            if is_qualified:
                company['qualification_score'] = score
                company['qualification_details'] = details
                qualified_companies.append(company)
        
        # Sort by qualification score (highest first)
        qualified_companies.sort(key=lambda x: x['qualification_score'], reverse=True)
        
        return qualified_companies
    
    def get_qualification_summary(self, companies: List[Dict]) -> Dict:
        """Generate summary statistics for qualified companies"""
        if not companies:
            return {
                'total_companies': 0,
                'qualified_count': 0,
                'average_score': 0,
                'score_distribution': {},
                'industry_distribution': {},
                'location_distribution': {}
            }
        
        qualified_companies = self.filter_qualified_companies(companies)
        
        # Score distribution
        score_distribution = {}
        for company in qualified_companies:
            grade = company['qualification_details']['score_breakdown']['grade']
            score_distribution[grade] = score_distribution.get(grade, 0) + 1
        
        # Industry distribution
        industry_distribution = {}
        for company in qualified_companies:
            industry = company.get('industry', 'Unknown')
            industry_distribution[industry] = industry_distribution.get(industry, 0) + 1
        
        # Location distribution
        location_distribution = {}
        for company in qualified_companies:
            location = company.get('location', 'Unknown')
            location_distribution[location] = location_distribution.get(location, 0) + 1
        
        return {
            'total_companies': len(companies),
            'qualified_count': len(qualified_companies),
            'qualification_rate': len(qualified_companies) / len(companies) * 100 if len(companies) > 0 else 0,
            'average_score': sum(c['qualification_score'] for c in qualified_companies) / len(qualified_companies) if len(qualified_companies) > 0 else 0,
            'score_distribution': score_distribution,
            'industry_distribution': industry_distribution,
            'location_distribution': location_distribution
        }

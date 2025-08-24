#!/usr/bin/env python3
"""
Debug script to test the qualification engine
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lead_qualification.qualification_engine import LeadQualificationEngine

def test_qualification():
    # Sample company data
    company = {
        'company_name': 'ABC Manufacturing Co.',
        'industry': 'Manufacturing',
        'location': 'Chicago, IL',
        'employee_count': 150,
        'revenue_range': '$25M - $50M',
        'founded_year': '1998',
        'website': 'https://abcmanufacturing.com',
        'phone': '(312) 555-0123',
        'decision_makers': [
            {
                'name': 'John Smith',
                'title': 'CEO & Founder',
                'email': 'john.smith@abcmanufacturing.com',
                'phone': '(312) 555-0124',
                'linkedin_url': 'https://linkedin.com/in/johnsmith'
            }
        ]
    }
    
    # Test qualification
    engine = LeadQualificationEngine()
    is_qualified, score, details = engine.qualify_company(company)
    
    print(f"Company: {company['company_name']}")
    print(f"Qualified: {is_qualified}")
    print(f"Score: {score}")
    print("\nCriteria Results:")
    for criterion, result in details['criteria_checks'].items():
        print(f"  {criterion}: {result['score']} (meets: {result['meets_criteria']})")
    
    print(f"\nScore Breakdown:")
    for criterion, score_val in details['score_breakdown'].items():
        print(f"  {criterion}: {score_val}")
    
    print(f"\nReasons: {details['qualification_reasons']}")

if __name__ == "__main__":
    test_qualification()

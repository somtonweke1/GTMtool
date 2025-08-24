"""
Configuration file for Transition Scout - SMB Retirement Planning Lead Generator
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Target Business Criteria - Maryland High School Financial Education Focus
TARGET_CRITERIA = {
    "employee_range": (20, 200),  # School staff size
    "revenue_range": (1_000_000, 50_000_000),  # School budgets
    "business_age_min": 5,  # 5+ years established
    "owner_age_range": (30, 65),  # Educators and administrators
    "target_industries": [
        "Education",
        "High Schools",
        "Public Schools",
        "Private Schools",
        "Charter Schools",
        "School Districts",
        "Educational Services",
        "Student Services"
    ]
}

# Geographic Targeting - Maryland Focus
GEOGRAPHIC_TARGETS = {
    "cities": [
        "Baltimore, MD",
        "Annapolis, MD", 
        "Frederick, MD",
        "Rockville, MD",
        "Gaithersburg, MD",
        "Columbia, MD",
        "Ellicott City, MD",
        "Towson, MD",
        "Bethesda, MD",
        "Silver Spring, MD",
        "Hagerstown, MD",
        "Cumberland, MD",
        "Ocean City, MD",
        "Salisbury, MD",
        "Laurel, MD",
        "Glen Burnie, MD",
        "Dundalk, MD",
        "Catonsville, MD",
        "Parkville, MD",
        "Essex, MD"
    ],
    "states": [
        "MD"  # Focus on Maryland only
    ]
}

# API Configuration
API_CONFIG = {
    "linkedin": {
        "email": os.getenv("LINKEDIN_EMAIL"),
        "password": os.getenv("LINKEDIN_PASSWORD"),
        "api_key": os.getenv("LINKEDIN_API_KEY")
    },
    "apollo": {
        "api_key": os.getenv("APOLLO_API_KEY"),
        "base_url": "https://api.apollo.io/v1"
    },
    "hunter": {
        "api_key": os.getenv("HUNTER_API_KEY"),
        "base_url": "https://api.hunter.io/v2"
    },
    "zoominfo": {
        "api_key": os.getenv("ZOOMINFO_API_KEY"),
        "base_url": "https://api.zoominfo.com"
    }
}

# Scraping Configuration
SCRAPING_CONFIG = {
    "max_results_per_location": 100,
    "delay_between_requests": 2,  # seconds
    "max_retries": 3,
    "user_agent_rotation": True,
    "proxy_rotation": False
}

# Lead Scoring Weights
LEAD_SCORING_WEIGHTS = {
    "business_age": 0.25,
    "owner_age": 0.25,
    "revenue": 0.20,
    "employee_count": 0.15,
    "industry_match": 0.10,
    "geographic_proximity": 0.05
}

# Output Configuration
OUTPUT_CONFIG = {
    "max_leads_per_batch": 50,
    "output_format": "both",  # excel, csv, or both
    "include_outreach_templates": True,
    "include_contact_verification": True
}

# Outreach Templates - Maryland High School Financial Education Focus
OUTREACH_TEMPLATES = {
    "email_subject": "Financial Literacy Program for {company_name} Students",
    "email_body": """
Hi {first_name},

I'm reaching out because I believe {company_name} would be the perfect partner for our financial literacy program that's helping high school students learn investing and personal finance.

Our platform has already helped 10,000+ students with:
• AI-powered financial education
• Real investment opportunities (with $2.5M+ invested)
• 95% success rate in building financial literacy
• Community-driven learning experience

Given that {company_name} serves students in the Baltimore area, I'd love to discuss how we could partner to bring financial education to your school. Many Maryland schools are looking for ways to prepare students for real-world financial decisions.

Would you be interested in a brief call to explore this opportunity? I can share how other schools are implementing our program.

Best regards,
{your_name}
Financial Education Partnership Manager
    """,
    "linkedin_message": """
Hi {first_name},

I help high schools implement financial literacy programs that teach students real investing and personal finance. Our platform has helped 10,000+ students with a 95% success rate.

Given that {company_name} serves students in the Baltimore area, I'd love to discuss how we could partner to bring financial education to your school.

Would you be open to a quick call to explore this opportunity?

Best,
{your_name}
    """
}

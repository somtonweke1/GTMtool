"""
Configuration file for Transition Scout - SMB Retirement Planning Lead Generator
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Target Business Criteria
TARGET_CRITERIA = {
    "employee_range": (50, 500),
    "revenue_range": (5_000_000, 100_000_000),  # $5M - $100M
    "business_age_min": 15,  # 15+ years
    "owner_age_range": (55, 70),
    "target_industries": [
        "Manufacturing",
        "Construction", 
        "Professional Services",
        "Healthcare",
        "Distribution",
        "Engineering",
        "Architecture",
        "Consulting"
    ]
}

# Geographic Targeting
GEOGRAPHIC_TARGETS = {
    "cities": [
        "New York, NY",
        "Los Angeles, CA", 
        "Chicago, IL",
        "Houston, TX",
        "Phoenix, AZ",
        "Philadelphia, PA",
        "San Antonio, TX",
        "San Diego, CA",
        "Dallas, TX",
        "San Jose, CA"
    ],
    "states": [
        "CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI"
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

# Outreach Templates
OUTREACH_TEMPLATES = {
    "email_subject": "Your Business Succession Plan - Time to Act?",
    "email_body": """
Hi {first_name},

I noticed {company_name} has been in business for {business_age} years and thought you might be thinking about what's next.

Many business owners in your position are starting to plan their exit strategy - whether that's selling, transitioning to family, or creating an employee ownership plan.

Would you be interested in a brief conversation about business succession planning? I'd love to share some insights that could save you significant time and money.

Best regards,
{your_name}
    """,
    "linkedin_message": """
Hi {first_name},

I help business owners like you plan their exit strategy. Given that {company_name} has been successful for {business_age} years, you might be thinking about succession planning.

Would you be open to a quick call to discuss your options?

Best,
{your_name}
    """
}

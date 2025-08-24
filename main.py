#!/usr/bin/env python3
"""
Transition Scout - Main Execution Script
Autonomous SMB Retirement Planning Lead Generator

This script orchestrates the entire lead generation process:
1. Data collection from LinkedIn and other sources
2. Contact enrichment using various APIs
3. Lead qualification and scoring
4. Report generation with personalized outreach templates
"""

import logging
import sys
import os
from typing import List, Dict
from datetime import datetime
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    TARGET_CRITERIA, 
    GEOGRAPHIC_TARGETS, 
    API_CONFIG, 
    OUTPUT_CONFIG,
    SCRAPING_CONFIG
)
from data_collectors.linkedin_scraper import LinkedInScraper
from data_collectors.contact_enricher import ContactEnricher
from data_collectors.business_directory_scraper import BusinessDirectoryScraper
from lead_qualification.qualification_engine import LeadQualificationEngine
from output_generation.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'transition_scout_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class TransitionScout:
    """Main orchestrator for the Transition Scout lead generation system"""
    
    def __init__(self):
        self.linkedin_scraper = None
        self.business_directory_scraper = BusinessDirectoryScraper()
        self.contact_enricher = ContactEnricher()
        self.qualification_engine = LeadQualificationEngine()
        self.report_generator = ReportGenerator()
        self.discovered_companies = []
        self.enriched_companies = []
        self.qualified_companies = []
        
    def run(self, target_locations: List[str] = None, target_industries: List[str] = None):
        """Run the complete lead generation process"""
        logger.info("🚀 Starting Transition Scout Lead Generation Process")
        
        try:
            # Phase 1: Data Collection
            self._collect_company_data(target_locations, target_industries)
            
            if not self.discovered_companies:
                logger.warning("No companies discovered. Exiting.")
                return
            
            # Phase 2: Contact Enrichment
            self._enrich_company_contacts()
            
            # Phase 3: Lead Qualification
            self._qualify_leads()
            
            # Phase 4: Report Generation
            self._generate_reports()
            
            # Phase 5: Summary
            self._print_summary()
            
        except Exception as e:
            logger.error(f"Process failed: {str(e)}")
            raise
    
    def _collect_company_data(self, target_locations: List[str] = None, target_industries: List[str] = None):
        """Phase 1: Collect company data from LinkedIn and other sources"""
        logger.info("📊 Phase 1: Collecting Company Data")
        
        # Use default locations if none specified
        if not target_locations:
            target_locations = GEOGRAPHIC_TARGETS["cities"][:3]  # Start with first 3 cities
        
        # Use default industries if none specified
        if not target_industries:
            target_industries = TARGET_CRITERIA["target_industries"][:3]  # Start with first 3 industries
        
                # Initialize LinkedIn scraper (skip for now due to WebDriver issues)
        self.linkedin_scraper = None
        logger.info("LinkedIn scraper disabled - using business directory scraping instead")
        
        # Try to find real companies using Hunter.io first
        if target_locations:
            try:
                from data_collectors.hunter_company_finder import HunterCompanyFinder
                hunter_finder = HunterCompanyFinder()
                real_companies = hunter_finder.find_companies_by_industry(
                    target_industries[0] if target_industries else "Manufacturing",
                    target_locations[0] if target_locations else "Chicago, IL"
                )
                
                if real_companies:
                    self.discovered_companies = real_companies
                    logger.info(f"✅ Found {len(real_companies)} real companies using Hunter.io")
                else:
                    logger.warning("No real companies found with Hunter.io. Falling back to sample data.")
                    self._create_sample_companies()
                    
            except Exception as e:
                logger.warning(f"Hunter.io company finder failed: {e}. Falling back to sample data.")
                self._create_sample_companies()
        else:
            # For demo purposes, create some sample companies
            self._create_sample_companies()
    
    def _create_sample_companies(self):
        """Create sample companies for demonstration purposes"""
        logger.info("📝 Creating sample companies for demonstration")
        
        sample_companies = [
            {
                'company_name': 'ABC Manufacturing Co.',
                'industry': 'Manufacturing',
                'location': 'Chicago, IL',
                'employee_count': 150,
                'revenue_range': '$25M - $50M',
                'founded_year': '1998',
                'website': 'https://abcmanufacturing.com',
                'phone': '(312) 555-0123',
                'linkedin_url': 'https://linkedin.com/company/abc-manufacturing',
                'search_location': 'Chicago, IL',
                'search_industry': 'Manufacturing',
                'decision_makers': [
                    {
                        'name': 'John Smith',
                        'title': 'CEO & Founder',
                        'email': 'john.smith@abcmanufacturing.com',
                        'phone': '(312) 555-0124',
                        'linkedin_url': 'https://linkedin.com/in/johnsmith'
                    }
                ]
            },
            {
                'company_name': 'XYZ Construction Services',
                'industry': 'Construction',
                'location': 'Houston, TX',
                'employee_count': 200,
                'revenue_range': '$50M - $100M',
                'founded_year': '1993',
                'website': 'https://xyzconstruction.com',
                'phone': '(713) 555-0456',
                'linkedin_url': 'https://linkedin.com/company/xyz-construction',
                'search_location': 'Houston, TX',
                'search_industry': 'Construction',
                'decision_makers': [
                    {
                        'name': 'Maria Rodriguez',
                        'title': 'President & Owner',
                        'email': 'm.rodriguez@xyzconstruction.com',
                        'phone': '(713) 555-0457',
                        'linkedin_url': 'https://linkedin.com/in/mariarodriguez'
                    }
                ]
            },
            {
                'company_name': 'Professional Consulting Group',
                'industry': 'Professional Services',
                'location': 'New York, NY',
                'employee_count': 75,
                'revenue_range': '$10M - $25M',
                'founded_year': '2003',
                'website': 'https://proconsulting.com',
                'phone': '(212) 555-0789',
                'linkedin_url': 'https://linkedin.com/company/professional-consulting',
                'search_location': 'New York, NY',
                'search_industry': 'Professional Services',
                'decision_makers': [
                    {
                        'name': 'David Chen',
                        'title': 'Managing Partner',
                        'email': 'd.chen@proconsulting.com',
                        'phone': '(212) 555-0790',
                        'linkedin_url': 'https://linkedin.com/in/davidchen'
                    }
                ]
            }
        ]
        
        self.discovered_companies = sample_companies
        logger.info(f"✅ Created {len(sample_companies)} sample companies")
    
    def _scrape_real_companies(self, target_locations: List[str], target_industries: List[str] = None):
        """Scrape real companies from business directories"""
        logger.info("🌐 Scraping real companies from business directories")
        
        all_companies = []
        
        for location in target_locations:
            logger.info(f"🔍 Scraping companies in {location}")
            
            if target_industries:
                for industry in target_industries:
                    logger.info(f"  📋 Industry: {industry}")
                    companies = self.business_directory_scraper.bulk_scrape_directories(location, industry)
                    all_companies.extend(companies)
            else:
                # Scrape all industries in location
                companies = self.business_directory_scraper.bulk_scrape_directories(location)
                all_companies.extend(companies)
        
        if all_companies:
            self.discovered_companies = all_companies
            logger.info(f"✅ Scraped {len(all_companies)} real companies from business directories")
        else:
            logger.warning("No real companies found. Falling back to sample data.")
            self._create_sample_companies()
    
    def _enrich_company_contacts(self):
        """Phase 2: Enrich company data with contact information"""
        logger.info("🔗 Phase 2: Enriching Company Contacts")
        
        if not self.discovered_companies:
            logger.warning("No companies to enrich")
            return
        
        # Enrich companies with contact information
        self.enriched_companies = self.contact_enricher.bulk_enrich(self.discovered_companies)
        
        # Business age will be calculated by the qualification engine
        
        logger.info(f"✅ Enriched {len(self.enriched_companies)} companies")
    

    
    def _qualify_leads(self):
        """Phase 3: Qualify leads based on retirement readiness criteria"""
        logger.info("🎯 Phase 3: Qualifying Leads")
        
        if not self.enriched_companies:
            logger.warning("No companies to qualify")
            return
        
        # Qualify companies
        self.qualified_companies = self.qualification_engine.filter_qualified_companies(self.enriched_companies)
        
        logger.info(f"✅ Qualified {len(self.qualified_companies)} companies out of {len(self.enriched_companies)}")
        
        # Print qualification summary
        summary = self.qualification_engine.get_qualification_summary(self.enriched_companies)
        if summary['total_companies'] > 0:
            logger.info(f"📊 Qualification Summary: {summary['qualified_count']}/{summary['total_companies']} qualified ({summary['qualification_rate']:.1f}%)")
        else:
            logger.info("📊 No companies to qualify")
    
    def _generate_reports(self):
        """Phase 4: Generate comprehensive reports"""
        logger.info("📋 Phase 4: Generating Reports")
        
        # Generate report for all companies (qualified or not)
        if self.enriched_companies:
            # Create a report with all companies, marking qualification status
            all_companies_with_status = []
            for company in self.enriched_companies:
                company_copy = company.copy()
                company_copy['is_qualified'] = company in self.qualified_companies
                company_copy['qualification_score'] = getattr(company, 'qualification_score', 'N/A')
                all_companies_with_status.append(company_copy)
            
            # Generate comprehensive report
            report_path = self.report_generator.generate_lead_report(all_companies_with_status)
            
            if report_path:
                logger.info(f"✅ Comprehensive report generated: {report_path}")
        else:
            logger.warning("No companies to report on")
            return
        
        # Generate qualification summary
        qualification_summary = self.report_generator.generate_qualification_summary(self.enriched_companies)
        logger.info(f"📊 Qualification Summary: {qualification_summary}")
    
    def _print_summary(self):
        """Phase 5: Print process summary"""
        logger.info("🎉 Phase 5: Process Complete!")
        
        print("\n" + "="*60)
        print("🎯 TRANSITION SCOUT LEAD GENERATION COMPLETE")
        print("="*60)
        
        print(f"📊 Companies Discovered: {len(self.discovered_companies)}")
        print(f"🔗 Companies Enriched: {len(self.enriched_companies)}")
        print(f"✅ Companies Qualified: {len(self.qualified_companies)}")
        
        if self.qualified_companies:
            print(f"📈 Average Qualification Score: {sum(c.get('qualification_score', 0) for c in self.qualified_companies) / len(self.qualified_companies):.1f}")
            
            # Top 3 companies
            print("\n🏆 Top 3 Qualified Companies:")
            for i, company in enumerate(self.qualified_companies[:3], 1):
                score = company.get('qualification_score', 0)
                grade = company.get('qualification_details', {}).get('score_breakdown', {}).get('grade', 'N/A')
                print(f"  {i}. {company.get('company_name', 'Unknown')} - Score: {score:.1f} ({grade})")
        
        print("\n📋 Next Steps:")
        print("  1. Review the generated Excel report")
        print("  2. Customize outreach templates with your information")
        print("  3. Begin outreach to qualified leads")
        print("  4. Track responses and follow up accordingly")
        
        print("="*60)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Transition Scout - SMB Retirement Planning Lead Generator')
    parser.add_argument('--locations', nargs='+', help='Target locations (e.g., "Chicago, IL" "Houston, TX")')
    parser.add_argument('--industries', nargs='+', help='Target industries')
    parser.add_argument('--demo', action='store_true', help='Run with sample data (no API calls)')
    parser.add_argument('--real-data', action='store_true', help='Scrape real companies from business directories')
    
    args = parser.parse_args()
    
    # Initialize Transition Scout
    scout = TransitionScout()
    
    try:
        # Run the lead generation process
        if args.real_data and args.locations:
            # Use real data scraping
            scout.run(
                target_locations=args.locations,
                target_industries=args.industries
            )
        elif args.demo:
            # Use demo data
            scout.run()
        else:
            # Default: use sample data
            scout.run(
                target_locations=args.locations,
                target_industries=args.industries
            )
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Process failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

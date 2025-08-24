# �� Transition Scout - SMB Retirement Planning Lead Generation Tool

> **"The Stormy equivalent for business exit planning"** - Automatically discover, qualify, and generate outreach for SMB owners approaching retirement.

## 🚀 What It Does

Transition Scout autonomously finds Small and Medium Business (SMB) owners who are approaching retirement age, scrapes their contact and business information, identifies retirement readiness signals, generates personalized outreach sequences, and automatically qualifies leads for business exit planning services.

## ✨ Features

- **🌐 Real Company Discovery**: Uses Hunter.io API to find actual businesses (no more placeholder data!)
- **🎯 Smart Lead Qualification**: Custom algorithm scoring companies on business age, owner age, revenue, employee count, industry match, and geographic proximity
- **📧 Contact Enrichment**: Integrates with Apollo.io, Hunter.io, and ZoomInfo for comprehensive contact data
- **📊 Professional Reporting**: Generates multi-sheet Excel reports and CSV files with qualified leads
- **💼 Personalized Outreach**: Creates customized email and LinkedIn message templates
- **🔍 Multi-Source Data**: Combines business directories, LinkedIn, and API data for comprehensive lead generation

## 🏗️ Architecture

```
Transition Scout/
├── data_collectors/          # Data collection modules
│   ├── hunter_company_finder.py    # Hunter.io company discovery
│   ├── business_directory_scraper.py # Web scraping (Yellow Pages, Yelp)
│   ├── linkedin_scraper.py         # LinkedIn Sales Navigator
│   └── contact_enricher.py         # Contact enrichment APIs
├── lead_qualification/       # Lead scoring and qualification
│   └── qualification_engine.py     # Custom scoring algorithm
├── output_generation/        # Report generation
│   └── report_generator.py         # Excel/CSV report creation
├── config.py                 # Configuration and settings
├── main.py                   # Main execution script
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/transition-scout.git
cd transition-scout
```

### 2. Set Up Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env with your API keys
nano .env
```

**Required API Keys:**
- `HUNTER_API_KEY`: [Get free Hunter.io API key](https://hunter.io)
- `APOLLO_API_KEY`: [Apollo.io API](https://apollo.io)
- `ZOOMINFO_API_KEY`: [ZoomInfo API](https://zoominfo.com)

### 4. Run Transition Scout
```bash
# Basic run with sample data
python main.py

# Find real companies in specific location/industry
python main.py --real-data --locations "Chicago, IL" --industries "Manufacturing"

# Custom search
python main.py --real-data --locations "New York, NY" "Los Angeles, CA" --industries "Construction" "Healthcare"
```

## 📊 Output

Transition Scout generates comprehensive reports including:

- **Qualified Companies Sheet**: Business metrics, contact info, qualification scores
- **Decision Makers Sheet**: Key contacts with emails, positions, LinkedIn profiles
- **Outreach Templates Sheet**: Personalized email and LinkedIn message templates
- **Summary Sheet**: Process statistics and qualification breakdown

## 🎯 Lead Qualification Criteria

Companies are scored on a 100-point scale based on:

- **Business Age** (25%): 15+ years in business
- **Owner Age** (25%): 55+ years old
- **Revenue** (20%): $5M - $100M annual revenue
- **Employee Count** (15%): 50-500 employees
- **Industry Match** (10%): Target industry alignment
- **Geographic Proximity** (5%): Location-based scoring

**Qualification Threshold**: 70+ points required

## 🔧 Configuration

Customize your search criteria in `config.py`:

```python
TARGET_CRITERIA = {
    "employee_range": (50, 500),
    "revenue_range": (5_000_000, 100_000_000),
    "min_business_age": 15,
    "min_owner_age": 55,
    "target_industries": ["Manufacturing", "Construction", "Healthcare"],
    "target_locations": ["Chicago, IL", "New York, NY", "Los Angeles, CA"]
}
```

## 🌟 Use Cases

- **Business Brokers**: Find SMB owners ready to sell
- **Exit Planning Consultants**: Identify retirement-ready business owners
- **M&A Advisors**: Discover acquisition targets
- **Succession Planners**: Find family businesses needing transition planning
- **Financial Advisors**: Identify business owners needing retirement planning

## 🛠️ Technology Stack

- **Python 3.8+**: Core application
- **Hunter.io API**: Company discovery and contact enrichment
- **Pandas**: Data processing and analysis
- **OpenPyXL**: Excel report generation
- **Requests**: API integrations
- **BeautifulSoup4**: Web scraping
- **Selenium**: LinkedIn automation (optional)

## 📈 Performance

- **Discovery**: 15-25 real companies per location/industry
- **Qualification Rate**: 60-80% of discovered companies typically qualify
- **Processing Time**: 2-5 minutes per location
- **API Efficiency**: Optimized rate limiting and error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hunter.io** for company discovery and contact enrichment
- **Apollo.io** for additional contact data
- **ZoomInfo** for business intelligence
- **LinkedIn** for professional networking data

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/transition-scout/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/transition-scout/discussions)
- **Email**: your-email@example.com

---

**Built with ❤️ for business exit planning professionals**

*"Finding the right business owners at the right time for the right reasons"*

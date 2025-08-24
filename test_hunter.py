#!/usr/bin/env python3
"""
Test script for Hunter.io API integration
"""

import os
import requests
from dotenv import load_dotenv

def test_hunter_api():
    """Test Hunter.io API with a sample domain"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('HUNTER_API_KEY')
    
    if not api_key or api_key == 'your_hunter_api_key_here':
        print("❌ No Hunter.io API key found!")
        print("📝 Please:")
        print("   1. Go to https://hunter.io and sign up")
        print("   2. Get your API key from the dashboard")
        print("   3. Add it to your .env file")
        print("   4. Run this script again")
        return False
    
    # Test domain
    test_domain = "microsoft.com"
    
    print(f"🔍 Testing Hunter.io API with domain: {test_domain}")
    print(f"🔑 Using API key: {api_key[:8]}...")
    
    # Make API request
    url = "https://api.hunter.io/v2/domain-search"
    params = {
        'api_key': api_key,
        'domain': test_domain,
        'type': 'generic'
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Hunter.io API working!")
            print(f"📧 Found {data.get('data', {}).get('emails', [])} emails")
            print(f"👥 Found {data.get('data', {}).get('people', [])} people")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    test_hunter_api()

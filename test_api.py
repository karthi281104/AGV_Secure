#!/usr/bin/env python3
"""
Test API endpoint directly
"""

import requests
import json

try:
    # Test the API endpoint
    response = requests.get('http://localhost:5000/api/customers')
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nAPI Response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(f"Response text: {response.text}")
        
except Exception as e:
    print(f"Error testing API: {e}")

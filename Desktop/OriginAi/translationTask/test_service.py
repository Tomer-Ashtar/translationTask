#!/usr/bin/env python3
"""
Simple script to test the translation service locally.
Run this after starting the service to verify it's working correctly.
"""

import requests
import json
import sys
from typing import Dict, Any


def test_endpoint(url: str, method: str = "GET", data: Dict[Any, Any] = None) -> None:
    """Test an API endpoint and print the result."""
    print(f"\n{'='*50}")
    print(f"Testing: {method} {url}")
    print(f"{'='*50}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
            print(f"Request data: {json.dumps(data, indent=2)}")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the service is running on http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Run all test cases."""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing OriginAI Translation Service")
    print(f"Base URL: {base_url}")
    
    # Test root endpoint
    test_endpoint(f"{base_url}/")
    
    # Test health check
    test_endpoint(f"{base_url}/health")
    
    # Test supported languages
    test_endpoint(f"{base_url}/supported-languages")
    
    # Test single translation - English to Hebrew
    test_endpoint(
        f"{base_url}/translate",
        "POST",
        {
            "text": "Hello world",
            "source_lang": "en",
            "target_lang": "he"
        }
    )
    
    # Test single translation - Hebrew to Russian
    test_endpoint(
        f"{base_url}/translate",
        "POST",
        {
            "text": "שלום עולם",
            "source_lang": "he",
            "target_lang": "ru"
        }
    )
    
    # Test batch translation
    test_endpoint(
        f"{base_url}/translate/batch",
        "POST",
        {
            "texts": [
                "Good morning",
                "Thank you",
                "How are you"
            ],
            "source_lang": "en",
            "target_lang": "he"
        }
    )
    
    # Test error case - invalid language
    print(f"\n{'='*50}")
    print("Testing error case (invalid language):")
    print(f"{'='*50}")
    test_endpoint(
        f"{base_url}/translate",
        "POST",
        {
            "text": "Hello",
            "source_lang": "en",
            "target_lang": "fr"  # Unsupported language
        }
    )
    
    # Test error case - word limit exceeded
    print(f"\n{'='*50}")
    print("Testing error case (word limit exceeded):")
    print(f"{'='*50}")
    test_endpoint(
        f"{base_url}/translate",
        "POST",
        {
            "text": "This is a very long text that definitely exceeds the maximum limit of ten words allowed",
            "source_lang": "en",
            "target_lang": "he"
        }
    )
    
    print(f"\n{'='*50}")
    print("✅ All tests completed!")
    print("Check the responses above to verify the service is working correctly.")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
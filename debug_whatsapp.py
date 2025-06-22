#!/usr/bin/env python3
"""
Debug script to test WhatsApp credentials and environment variables
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_whatsapp_credentials():
    """Test WhatsApp credentials setup"""
    print("\n=== WHATSAPP CREDENTIALS DEBUG ===")
    
    # Check all environment variables
    all_vars = dict(os.environ)
    whatsapp_vars = {k: v for k, v in all_vars.items() if 'WHATSAPP' in k.upper()}
    
    print(f"Found {len(whatsapp_vars)} WhatsApp-related environment variables:")
    for key, value in whatsapp_vars.items():
        print(f"  {key}: {value[:20]}{'...' if len(value) > 20 else ''}")
    
    # Find configured businesses
    businesses = []
    for key in os.environ:
        if key.startswith("WHATSAPP_ACCESS_TOKEN_"):
            business_number = key.replace("WHATSAPP_ACCESS_TOKEN_", "")
            businesses.append(business_number)
    
    print(f"\nConfigured businesses: {businesses}")
    
    # Test each business
    for business in businesses:
        print(f"\nTesting business: {business}")
        
        access_token = os.getenv(f"WHATSAPP_ACCESS_TOKEN_{business}")
        phone_number_id = os.getenv(f"WHATSAPP_PHONE_NUMBER_ID_{business}")
        
        token_status = "✓" if access_token else "✗"
        phone_status = "✓" if phone_number_id else "✗"
        
        print(f"  Access Token: {token_status}")
        print(f"  Phone Number ID: {phone_status}")
        
        if access_token:
            print(f"    Token preview: {access_token[:20]}...")
        if phone_number_id:
            print(f"    Phone ID: {phone_number_id}")
        
        # Check if both are present
        if access_token and phone_number_id:
            print(f"  Status: VALID ✓")
        else:
            print(f"  Status: INVALID ✗")
            if not access_token:
                print(f"    Missing: WHATSAPP_ACCESS_TOKEN_{business}")
            if not phone_number_id:
                print(f"    Missing: WHATSAPP_PHONE_NUMBER_ID_{business}")
    
    # Check generic credentials
    print(f"\nGeneric credentials:")
    generic_token = os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")
    generic_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("PHONE_NUMBER_ID")
    
    print(f"  Generic Token: {'✓' if generic_token else '✗'}")
    print(f"  Generic Phone ID: {'✓' if generic_phone_id else '✗'}")
    
    if generic_token:
        print(f"    Token preview: {generic_token[:20]}...")
    if generic_phone_id:
        print(f"    Phone ID: {generic_phone_id}")
    
    print("\n=== END DEBUG ===\n")

if __name__ == "__main__":
    test_whatsapp_credentials() 
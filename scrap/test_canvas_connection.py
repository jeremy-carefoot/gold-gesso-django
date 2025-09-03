#!/usr/bin/env python
"""
Simple script to test Canvas API connection.
Run this after setting up your .env file to verify your token works.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canvas_backend.settings')
django.setup()

from canvas_api.services import CanvasAPIService
from django.conf import settings


def test_canvas_connection():
    """Test the Canvas API connection and display results"""
    
    print("=" * 60)
    print("Canvas API Connection Test")
    print("=" * 60)
    
    # Check configuration
    print("\n1. Checking configuration...")
    if not settings.CANVAS_API_BASE_URL:
        print("   ❌ CANVAS_API_BASE_URL not set in .env")
        return False
    print(f"   ✓ Base URL: {settings.CANVAS_API_BASE_URL}")
    
    if not settings.CANVAS_API_TOKEN:
        print("   ❌ CANVAS_API_TOKEN not set in .env")
        return False
    print(f"   ✓ Token: {settings.CANVAS_API_TOKEN[:10]}..." if settings.CANVAS_API_TOKEN else "   ❌ No token")
    
    # Test API connection
    print("\n2. Testing API connection...")
    service = CanvasAPIService()
    
    try:
        # Try to get user profile (simplest authenticated endpoint)
        profile = service.get_user_profile()
        print(f"   ✓ Connected successfully!")
        print(f"   ✓ Authenticated as: {profile.get('name', 'Unknown')}")
        print(f"   ✓ User ID: {profile.get('id', 'Unknown')}")
        
        # Try to get courses
        print("\n3. Fetching your courses...")
        courses = service.get_courses()
        if courses:
            print(f"   ✓ Found {len(courses)} active course(s):")
            for course in courses[:3]:  # Show first 3
                print(f"      - {course.get('name', 'Unnamed course')}")
            if len(courses) > 3:
                print(f"      ... and {len(courses) - 3} more")
        else:
            print("   ℹ No active courses found")
        
        print("\n✅ Canvas API connection successful!")
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        print("\n   Troubleshooting tips:")
        print("   1. Check your token is correct and not expired")
        print("   2. Verify the base URL matches your Canvas instance")
        print("   3. Ensure you have internet connection")
        print("   4. Token format should be: '1234~xxxxx...' (starts with numbers and ~)")
        return False


if __name__ == "__main__":
    success = test_canvas_connection()
    sys.exit(0 if success else 1)
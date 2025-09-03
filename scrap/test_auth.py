#!/usr/bin/env python
"""
Test script for authentication endpoints
"""
import requests
import json
import random
import string

# Base URL - adjust if running on different port
BASE_URL = "http://localhost:8000/api/auth"

def generate_random_username():
    """Generate a random username for testing"""
    return ''.join(random.choices(string.ascii_lowercase, k=8))

def test_registration():
    """Test user registration endpoint"""
    username = generate_random_username()
    data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print("Testing Registration...")
    response = requests.post(f"{BASE_URL}/register/", json=data)
    
    if response.status_code == 201:
        print("✓ Registration successful")
        result = response.json()
        print(f"  - User created: {result['user']['username']}")
        print(f"  - Access token received: {result['access'][:20]}...")
        print(f"  - Refresh token received: {result['refresh'][:20]}...")
        return username, result['access'], result['refresh']
    else:
        print(f"✗ Registration failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return None, None, None

def test_login(username):
    """Test login endpoint"""
    data = {
        "username": username,
        "password": "TestPass123!"
    }
    
    print("\nTesting Login...")
    response = requests.post(f"{BASE_URL}/login/", json=data)
    
    if response.status_code == 200:
        print("✓ Login successful")
        result = response.json()
        print(f"  - Access token received: {result['access'][:20]}...")
        print(f"  - Refresh token received: {result['refresh'][:20]}...")
        return result['access'], result['refresh']
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return None, None

def test_user_profile(access_token):
    """Test user profile endpoint with authentication"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print("\nTesting User Profile (GET)...")
    response = requests.get(f"{BASE_URL}/user/", headers=headers)
    
    if response.status_code == 200:
        print("✓ User profile retrieved successfully")
        result = response.json()
        print(f"  - Username: {result['username']}")
        print(f"  - Email: {result['email']}")
        return True
    else:
        print(f"✗ Failed to get user profile: {response.status_code}")
        print(f"  Error: {response.text}")
        return False

def test_token_refresh(refresh_token):
    """Test token refresh endpoint"""
    data = {
        "refresh": refresh_token
    }
    
    print("\nTesting Token Refresh...")
    response = requests.post(f"{BASE_URL}/token/refresh/", json=data)
    
    if response.status_code == 200:
        print("✓ Token refresh successful")
        result = response.json()
        print(f"  - New access token received: {result['access'][:20]}...")
        return result['access']
    else:
        print(f"✗ Token refresh failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

def test_token_verify(access_token):
    """Test token verify endpoint"""
    data = {
        "token": access_token
    }
    
    print("\nTesting Token Verify...")
    response = requests.post(f"{BASE_URL}/token/verify/", json=data)
    
    if response.status_code == 200:
        print("✓ Token is valid")
        return True
    else:
        print(f"✗ Token verification failed: {response.status_code}")
        return False

# def test_change_password(access_token):
#     """Test password change endpoint"""
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#     data = {
#         "old_password": "TestPass123!",
#         "new_password": "NewTestPass456!"
#     }
    
#     print("\nTesting Password Change...")
#     response = requests.post(f"{BASE_URL}/password/change/", json=data, headers=headers)
    
#     if response.status_code == 200:
#         print("✓ Password changed successfully")
#         return True
#     else:
#         print(f"✗ Password change failed: {response.status_code}")
#         print(f"  Error: {response.text}")
#         return False

def test_unauthorized_access():
    """Test that protected endpoints require authentication"""
    print("\nTesting Unauthorized Access...")
    response = requests.get(f"{BASE_URL}/user/")
    
    if response.status_code == 401:
        print("✓ Unauthorized access properly blocked")
        return True
    else:
        print(f"✗ Unexpected response for unauthorized access: {response.status_code}")
        return False

def main():
    print("=" * 50)
    print("AUTHENTICATION API TEST SUITE")
    print("=" * 50)
    
    # Test registration
    username, access_token, refresh_token = test_registration()
    
    if not username:
        print("\n⚠ Registration failed, skipping remaining tests")
        return
    
    # Test login
    access_token_login, refresh_token_login = test_login(username)
    
    # Test unauthorized access
    test_unauthorized_access()
    
    # Test authenticated endpoints
    if access_token:
        test_user_profile(access_token)
        test_token_verify(access_token)
        
        # Test token refresh
        new_access_token = test_token_refresh(refresh_token)
        
        if new_access_token:
            # Test with refreshed token
            test_token_verify(new_access_token)
        
        # Test password change
        test_change_password(access_token)
    
    print("\n" + "=" * 50)
    print("TEST SUITE COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    main()
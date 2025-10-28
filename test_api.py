#!/usr/bin/env python3
"""
Simple script to test the Expense Tracker API endpoints
"""

import requests
import json
from datetime import date

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_register():
    """Test user registration"""
    print("\n🔍 Testing user registration...")
    data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"User ID: {result['user']['id']}")
        print(f"Token: {result['access_token'][:20]}...")
        return result['access_token']
    else:
        print(f"Error: {response.json()}")
        return None

def test_login():
    """Test user login"""
    print("\n🔍 Testing user login...")
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"User ID: {result['user']['id']}")
        print(f"Token: {result['access_token'][:20]}...")
        return result['access_token']
    else:
        print(f"Error: {response.json()}")
        return None

def test_get_me(token):
    """Test get current user endpoint"""
    print("\n🔍 Testing get current user...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_add_friend(token):
    """Test add friend endpoint"""
    print("\n🔍 Testing add friend...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "email": "friend@example.com",
        "name": "Test Friend"
    }
    response = requests.post(f"{BASE_URL}/friends", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"Friend ID: {result['id']}")
        print(f"Friend Email: {result['email']}")
        return result['id']
    else:
        print(f"Error: {response.json()}")
        return None

def test_get_friends(token):
    """Test get friends list"""
    print("\n🔍 Testing get friends list...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/friends", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Friends: {response.json()}")
    return response.status_code == 200

def test_add_expense(token, friend_id, current_user_id):
    """Test add expense endpoint"""
    print("\n🔍 Testing add expense...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "friend_id": friend_id,
        "amount": 500.50,
        "description": "Test lunch expense",
        "paid_by_user_id": current_user_id,
        "expense_date": date.today().isoformat()
    }
    response = requests.post(f"{BASE_URL}/expenses", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"Expense ID: {result['id']}")
        print(f"Amount: {result['amount']}")
        print(f"Description: {result['description']}")
        return result['id']
    else:
        print(f"Error: {response.json()}")
        return None

def test_get_expenses(token, friend_id):
    """Test get expenses with friend"""
    print("\n🔍 Testing get expenses with friend...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/expenses/{friend_id}", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Expenses: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_balance(token, friend_id):
    """Test get balance with friend"""
    print("\n🔍 Testing get balance with friend...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/expenses/{friend_id}/balance", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Balance: {response.json()}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 Expense Tracker API Tests")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed. Is the server running?")
        return
    
    # Test registration
    token = test_register()
    if not token:
        print("\n⚠️  Registration failed, trying login...")
        token = test_login()
        if not token:
            print("\n❌ Could not authenticate")
            return
    
    # Get current user
    if not test_get_me(token):
        print("\n❌ Could not get current user")
        return
    
    # Get user ID for expense creation
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    current_user_id = me_response.json()['id']
    
    # Add friend
    friend_id = test_add_friend(token)
    if not friend_id:
        print("\n⚠️  Could not add friend")
    
    # Get friends list
    test_get_friends(token)
    
    # Add expense (if we have a friend)
    if friend_id:
        expense_id = test_add_expense(token, friend_id, current_user_id)
        
        # Get expenses
        test_get_expenses(token, friend_id)
        
        # Get balance
        test_get_balance(token, friend_id)
    
    print("\n" + "=" * 50)
    print("✅ API tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API. Make sure the server is running at http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")


#!/usr/bin/env python3
"""
Simple test script for the authentication system
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_auth_system():
    """Test the complete authentication flow"""
    print("Testing Timelycabs Authentication System")
    print("=" * 50)
    
    # Test phone number
    test_phone = "+919876543210"
    
    # 1. Request OTP
    print("\n1. Requesting OTP...")
    response = requests.post(f"{BASE_URL}/auth/request-otp", 
                           json={"phone": test_phone})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ OTP requested successfully: {data}")
        otp_id = data.get('otp_id')
    else:
        print(f"❌ Failed to request OTP: {response.status_code} - {response.text}")
        return
    
    # 2. Verify OTP (using a test OTP - in real scenario, check database or logs)
    print("\n2. Verifying OTP...")
    # Note: In development, you can check the database for the actual OTP
    test_otp = "123456"  # This would be the actual OTP from database/logs
    
    response = requests.post(f"{BASE_URL}/auth/verify-otp", 
                           json={
                               "phone": test_phone,
                               "otp": test_otp,
                               "device_info": "Test Device"
                           })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ OTP verification result: {data}")
        
        if data.get('is_new_user'):
            print("\n3. Completing profile for new user...")
            auth_token = data.get('auth_token')
            
            response = requests.post(f"{BASE_URL}/auth/complete-profile", 
                                   json={
                                       "auth_token": auth_token,
                                       "full_name": "Test User",
                                       "gender": "male"
                                   })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Profile completed: {data}")
                final_token = data.get('auth_token')
                
                # 4. Test logout
                print("\n4. Testing logout...")
                response = requests.post(f"{BASE_URL}/auth/logout", 
                                       json={"auth_token": final_token})
                
                if response.status_code == 200:
                    print(f"✅ Logout successful: {response.json()}")
                else:
                    print(f"❌ Logout failed: {response.status_code} - {response.text}")
            else:
                print(f"❌ Profile completion failed: {response.status_code} - {response.text}")
        else:
            print("✅ Existing user logged in successfully")
            auth_token = data.get('auth_token')
            
            # Test logout
            print("\n3. Testing logout...")
            response = requests.post(f"{BASE_URL}/auth/logout", 
                                   json={"auth_token": auth_token})
            
            if response.status_code == 200:
                print(f"✅ Logout successful: {response.json()}")
            else:
                print(f"❌ Logout failed: {response.status_code} - {response.text}")
    else:
        print(f"❌ OTP verification failed: {response.status_code} - {response.text}")

def test_error_cases():
    """Test error handling"""
    print("\n" + "=" * 50)
    print("Testing Error Cases")
    print("=" * 50)
    
    # Test invalid phone number
    print("\n1. Testing invalid phone number...")
    response = requests.post(f"{BASE_URL}/auth/request-otp", 
                           json={"phone": "invalid"})
    print(f"Expected error for invalid phone: {response.status_code}")
    
    # Test invalid OTP
    print("\n2. Testing invalid OTP...")
    response = requests.post(f"{BASE_URL}/auth/verify-otp", 
                           json={
                               "phone": "+919876543210",
                               "otp": "000000",
                               "device_info": "Test Device"
                           })
    print(f"Expected error for invalid OTP: {response.status_code}")

if __name__ == "__main__":
    try:
        test_auth_system()
        test_error_cases()
        print("\n" + "=" * 50)
        print("✅ Authentication system test completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

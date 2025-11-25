#!/usr/bin/env python3
"""
Test script for the authentication system
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth import AuthenticationManager

def test_authentication():
    """Test the authentication system"""
    print("Testing Authentication System...")
    
    # Create authentication manager
    auth_manager = AuthenticationManager()
    
    # Test user registration
    print("\n1. Testing user registration...")
    success, message = auth_manager.add_user("testuser", "testpassword")
    print(f"   Registration result: {message}")
    
    # Test duplicate user registration
    print("\n2. Testing duplicate user registration...")
    success, message = auth_manager.add_user("testuser", "testpassword")
    print(f"   Duplicate registration result: {message}")
    
    # Test user authentication
    print("\n3. Testing user authentication...")
    success, message = auth_manager.authenticate_user("testuser", "testpassword")
    print(f"   Authentication result: {message}")
    
    # Test invalid password
    print("\n4. Testing invalid password...")
    success, message = auth_manager.authenticate_user("testuser", "wrongpassword")
    print(f"   Invalid password result: {message}")
    
    # Test non-existent user
    print("\n5. Testing non-existent user...")
    success, message = auth_manager.authenticate_user("nonexistent", "password")
    print(f"   Non-existent user result: {message}")
    
    # Test logout
    print("\n6. Testing logout...")
    auth_manager.logout_user()
    current_user = auth_manager.get_current_user()
    print(f"   Current user after logout: {current_user}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_authentication()
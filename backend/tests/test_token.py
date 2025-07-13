#!/usr/bin/env python3
"""
Simple script to generate a test JWT token for testing the exam generation endpoint
"""
import jwt
from datetime import datetime, timedelta
from config import config

def create_test_token():
    """Create a test JWT token"""
    payload = {
        "sub": "test@example.com",
        "role": "user",
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    
    token = jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return token

if __name__ == "__main__":
    token = create_test_token()
    print(f"Test JWT token: {token}")
    print(f"Use this token in the Authorization header: Bearer {token}")
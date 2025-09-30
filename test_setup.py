#!/usr/bin/env python3
"""
Test script for GitHub PR Bot Flask Webhook Server
Run this to validate your setup before deploying
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if all required environment variables are set."""
    print("🔍 Testing environment configuration...")
    
    required_vars = [
        "GITHUB_TOKEN",
        "GROQ_API_KEY", 
        "DISCORD_WEBHOOK_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_github_api():
    """Test GitHub API connectivity."""
    print("\n🔍 Testing GitHub API connectivity...")
    
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GitHub token not found")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub API connected successfully as: {user_data.get('login', 'Unknown')}")
            return True
        else:
            print(f"❌ GitHub API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ GitHub API connection failed: {e}")
        return False

def test_groq_api():
    """Test Groq API connectivity."""
    print("\n🔍 Testing Groq API connectivity...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Groq API key not found")
        return False
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        # Simple test request
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama-3.1-8b-instant",
            max_tokens=10
        )
        
        if chat_completion.choices[0].message.content:
            print("✅ Groq API connected successfully")
            return True
        else:
            print("❌ Groq API returned empty response")
            return False
    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return False

def test_discord_webhook():
    """Test Discord webhook connectivity."""
    print("\n🔍 Testing Discord webhook connectivity...")
    
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ Discord webhook URL not found")
        return False
    
    test_data = {
        "username": "GitHub PR Bot Test",
        "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        "embeds": [{
            "title": "🧪 Test Message",
            "description": "This is a test message from the GitHub PR Bot setup validation.",
            "color": 0x00ff00,
            "footer": {"text": "Setup Test - You can ignore this message"}
        }]
    }
    
    try:
        response = requests.post(webhook_url, json=test_data, timeout=10)
        if response.status_code in [200, 204]:
            print("✅ Discord webhook connected successfully")
            print("  📤 Test message sent to Discord channel")
            return True
        else:
            print(f"❌ Discord webhook error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Discord webhook connection failed: {e}")
        return False

def test_flask_server():
    """Test if Flask server is running."""
    print("\n🔍 Testing Flask server...")
    
    port = os.getenv("PORT", "5000")
    base_url = f"http://localhost:{port}"
    
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Flask server is running: {data.get('message', 'Unknown')}")
            return True
        else:
            print(f"❌ Flask server error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask server is not running")
        print("  💡 Start the server with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Flask server test failed: {e}")
        return False

def test_webhook_endpoint():
    """Test webhook endpoint without actually processing."""
    print("\n🔍 Testing webhook endpoint...")
    
    port = os.getenv("PORT", "5000")
    webhook_url = f"http://localhost:{port}/webhook"
    
    # Test with invalid JSON to check error handling
    try:
        response = requests.post(webhook_url, data="invalid json", timeout=5)
        if response.status_code == 400:
            print("✅ Webhook endpoint is responding correctly to invalid requests")
            return True
        else:
            print(f"❌ Unexpected webhook response: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot reach webhook endpoint - server not running")
        return False
    except Exception as e:
        print(f"❌ Webhook endpoint test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 GitHub PR Bot Flask Server Setup Validation")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("GitHub API", test_github_api),
        ("Groq API", test_groq_api),
        ("Discord Webhook", test_discord_webhook),
        ("Flask Server", test_flask_server),
        ("Webhook Endpoint", test_webhook_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n❌ Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready for deployment.")
    else:
        print("⚠️ Some tests failed. Please fix the issues before deploying.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
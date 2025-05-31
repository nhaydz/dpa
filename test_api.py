
import requests
import json
from config import GEMINI_API_KEYS

def test_gemini_connection():
    """Test kết nối API Gemini"""
    print("🔍 Testing Gemini API connection...")
    
    # Test basic connection
    try:
        response = requests.get("https://generativelanguage.googleapis.com", timeout=10)
        print(f"✅ Basic connection: {response.status_code}")
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
        return False
    
    # Test API keys
    for i, api_key in enumerate(GEMINI_API_KEYS, 1):
        print(f"\n🔑 Testing API key {i}...")
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'python-requests/2.31.0'
        }
        
        data = {
            "contents": [{
                "parts": [{"text": "Hello, reply with just 'OK'"}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 10
            }
        }
        
        try:
            response = requests.post(
                f"{url}?key={api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ API key {i} working! Response: {text}")
                else:
                    print(f"⚠️ Unexpected response format: {result}")
            else:
                try:
                    error = response.json()
                    print(f"❌ API key {i} failed: {error}")
                except:
                    print(f"❌ API key {i} failed: {response.text}")
                    
        except Exception as e:
            print(f"❌ API key {i} error: {e}")
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    test_gemini_connection()

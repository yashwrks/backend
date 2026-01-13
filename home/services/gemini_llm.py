"""
Groq AI Voice Assistant - 100% FREE & SUPER FAST
Uses Llama 3.1 70B - Better than Gemini
"""

import os
import requests
import json
import time

class GeminiLLM:
    def __init__(self, model="llama-3.1-70b-versatile"):
        """
        Groq AI - 100% Free, Super Fast
        Available FREE models:
        - llama-3.1-70b-versatile (BEST - 70B parameters)
        - llama-3.1-8b-instant
        - mixtral-8x7b-32768
        - gemma2-9b-it
        """
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            print("❌ GROQ_API_KEY not found in .env")
            print("\n💡 GET FREE API KEY:")
            print("   1. Go to: https://console.groq.com/")
            print("   2. Sign up (FREE, no credit card)")
            print("   3. Go to API Keys section")
            print("   4. Click 'Create API Key'")
            print("   5. Copy the key")
            print("   6. Add to .env: GROQ_API_KEY=your_key_here")
            raise RuntimeError("GROQ_API_KEY missing")
        
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.last_call_time = 0
        
        # Test connection
        try:
            print(f"🔗 Testing Groq AI connection...")
            test_response = self._make_api_call("Hello", test_mode=True)
            print(f"✅ Groq AI connected successfully!")
            print(f"⚡ Using model: {self.model} (70B parameters, FREE)")
            print(f"📞 Ready for voice calls!")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("💡 Trying alternative model...")
            # Try alternative free models
            alternative_models = [
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ]
            
            for alt_model in alternative_models:
                try:
                    self.model = alt_model
                    test_response = self._make_api_call("Hello", test_mode=True)
                    print(f"✅ Connected with model: {self.model}")
                    break
                except:
                    continue
            else:
                print("❌ All models failed")
                print("💡 Please check: https://console.groq.com/keys")
    
    def _make_api_call(self, text: str, test_mode=False) -> str:
        """Make API call to Groq AI"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are Melissa, a helpful voice assistant. 
                    Keep responses brief (1-2 sentences), conversational, and helpful.
                    Sound friendly and engaging."""
                },
                {"role": "user", "content": text}
            ],
            "max_tokens": 150,
            "temperature": 0.7,
            "stream": False
        }
        
        response = requests.post(
            self.base_url, 
            headers=headers, 
            json=data, 
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if test_mode:
                return "Connection successful"
            return result['choices'][0]['message']['content'].strip()
        else:
            error_msg = f"API Error {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error'].get('message', error_msg)
                except:
                    error_msg = response.text[:100]
            raise Exception(error_msg)
    
    def generate(self, text: str) -> str:
        """Generate response using Groq AI"""
        
        # Simple rate limiting (1 call per second)
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        if time_since_last < 1:
            time.sleep(1 - time_since_last)
        
        try:
            self.last_call_time = time.time()
            
            print(f"📤 To Groq AI: '{text[:50]}...'")
            
            response = self._make_api_call(text)
            
            print(f"✅ Response: '{response[:50]}...'")
            return response
            
        except Exception as e:
            print(f"❌ Groq AI Error: {e}")
            
            error_str = str(e)
            # Return user-friendly error messages
            if "429" in error_str:
                return "I'm receiving too many requests. Please wait a moment."
            elif "401" in error_str or "403" in error_str:
                return "Authentication issue. Please check API configuration."
            elif "quota" in error_str.lower():
                return "API limit reached for now. Please try again later."
            else:
                return "I'm having some technical difficulties. Could you please repeat your question?"
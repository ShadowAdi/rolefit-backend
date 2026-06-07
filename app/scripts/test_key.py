# test_key.py
from groq import Groq

# Replace with your actual key
API_KEY = ""

try:
    client = Groq(api_key=API_KEY)
    # Try to list models - this is the minimum API call
    models = client.models.list()
    print("✅ API Key is VALID!")
    print(f"Found {len(list(models))} models")
except Exception as e:
    print(f"❌ API Key is INVALID: {e}")

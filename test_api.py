import os
from google import genai

key = "AIzaSyBuPG_YVjMrROvSYsPXjdmdfy0dJk3dg5k"
client = genai.Client(api_key=key)

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-001",
        contents="Hello"
    )
    print("Success! " + response.text)
except Exception as e:
    print("Error: " + str(e))

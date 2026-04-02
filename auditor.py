from google import genai
from google.genai import types
import os
import PIL.Image
import io
from dotenv import load_dotenv
from policy import EXPENSE_POLICY

load_dotenv()

# 1. Initialize the new Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def audit_expense(content, content_type):
    """Sends the expense to Gemini and gets back a verdict"""

    # 2. Define the System Instruction (The 'Brain' of the auditor)
    sys_instruct = f"""
    You are a strict but fair company expense auditor. 
    Use the following company policy to evaluate all submissions:
    {EXPENSE_POLICY}
    """

    # 3. Create a configuration with the system instruction
    # We use 'gemini-2.0-flash' for faster and smarter auditing
    config = types.GenerateContentConfig(
        system_instruction=sys_instruct,
        temperature=0.2 # Keeps the auditor consistent and less "creative"
    )

    if content_type == "text":
        user_prompt = f"Please analyze this expense report:\n{content}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_prompt,
            config=config
        )

    elif content_type == "image":
        image = PIL.Image.open(io.BytesIO(content))
        
        user_prompt = """
        The image attached is an expense receipt. Please read all text visible, 
        then provide the VERDICT, AMOUNT, CATEGORY, REASON, and VIOLATIONS.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[user_prompt, image],
            config=config
        )

    return response.text
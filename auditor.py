from google import genai
from google.genai import types
import os
import json
import time
from dotenv import load_dotenv
import datetime

today = datetime.date.today().strftime("%d/%m/%Y")

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def audit_receipt(content, content_type, policy_text, filename, claimed_date, business_purpose, mime_type="image/jpeg"):
    """
    Sends a receipt to Gemini and returns a structured verdict including extracted fields
    and validation against Claimed Date and Business Purpose.
    """

    sys_instruct = f"""
You are a strict, fair expense auditor.

TODAY'S DATE: {today}
Use this as your reference for date validation. 

CURRENCY:
- All amounts on receipts and in the policy are in Indian Rupees (INR / ₹) by default if not specified otherwise.
- If a receipt shows a foreign currency, convert to INR conceptually if limits are specified.

=== EMPLOYEE CONTEXT CLAIM ===
Claimed Expense Date: {claimed_date}
Business Purpose: {business_purpose}

=== EXPENSE POLICY ===
{policy_text}
=== END OF POLICY ===

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — DATA EXTRACTION & ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Extract the following from the receipt:
- Merchant Name
- Date on Receipt
- Total Amount
- Currency

Analyze the receipt against the Policy and Employee Context:
- Compare the "Date on Receipt" against the Employee "Claimed Expense Date" ({claimed_date}). If they don't match or the receipt date is unreadable, you MUST flag/reject the claim.
- Evaluate the employee's "Business Purpose" ({business_purpose}) against the contextual evidence in the receipt (e.g. social gathering items claimed as 'Office Supplies') and check if the policy explicitly permits or prohibits this context.
- If the image is extremely blurry or unreadable, immediately reject.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — FAKE RECEIPT DETECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Carefully examine the receipt for fraud signals:
1. Font inconsistency.
2. Suspiciously round totals.
3. Missing mandatory fields.
4. Date / Time anomalies (transaction between 12 AM - 5 AM).
5. Mismatched Totals.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPOND WITH ONLY A VALID JSON OBJECT.
No markdown, no code fences, no extra text.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use exactly these keys:

{{
  "merchant_name": "extracted merchant, or 'Unreadable/Missing'",
  "receipt_date": "extracted date, or 'Unreadable/Missing'",
  "extracted_amount": "total amount with symbol, or 'Unreadable/Missing'",
  "currency": "extracted currency",
  "verdict": "APPROVED" or "FLAGGED" or "REJECTED",
  "reason": "Draft exactly ONE concise sentence explaining the verdict. YOU MUST explicitly cite the specific policy rule or limit referenced if rejected/flagged.",
  "violations": "list any specific policy rules broken, or None",
  "fake_risk": "LOW" or "MEDIUM" or "HIGH",
  "fake_reasons": "list every fraud signal detected, or None if clean"
}}

Verdict definitions:
  APPROVED  → Expense clearly follows all policy rules, dates match, context makes sense, AND fake_risk is LOW.
  FLAGGED   → Something is unclear/missing, dates mismatch slightly, needs human review, OR fake_risk is MEDIUM.
  REJECTED  → Clearly violates policy rules, unreadable receipt, OR fake_risk is HIGH.
"""

    config = types.GenerateContentConfig(
        system_instruction=sys_instruct,
        temperature=0.0
    )

    max_retries = 3

    for attempt in range(max_retries):
        try:
            if content_type == "text":
                user_prompt = (
                    f"Please audit this expense receipt ({filename}):\n\n{content}"
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_prompt,
                    config=config
                )

            elif content_type == "image":
                image_part = types.Part.from_bytes(
                    data=content,
                    mime_type=mime_type
                )
                user_prompt = (
                    f"The image attached is an expense receipt ({filename}). "
                    "Read ALL visible text carefully — including small print."
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[user_prompt, image_part],
                    config=config
                )

            else:
                return _error_result(f"Unsupported content type: '{content_type}'")

            return parse_verdict(response.text)

        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries - 1:
                wait = 20 * (attempt + 1)
                print(f"[auditor] Rate limit — waiting {wait}s (attempt {attempt+1}/{max_retries})…")
                time.sleep(wait)
                continue
            else:
                return _error_result(f"Gemini API error: {error_str}", raw=error_str)


def _error_result(reason, raw=""):
    return {
        "verdict":      "ERROR",
        "merchant_name": "N/A",
        "receipt_date": "N/A",
        "extracted_amount": "N/A",
        "currency": "N/A",
        "reason":       reason,
        "violations":   "N/A",
        "fake_risk":    "UNKNOWN",
        "fake_reasons": "N/A",
        "raw":          raw or reason,
    }


def parse_verdict(raw_text: str) -> dict:
    result = _error_result("Could not parse AI response. See raw output.", raw=raw_text)
    result["verdict"] = "FLAGGED"
    
    try:
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            parts = cleaned.split("```")
            cleaned = parts[1]
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)

        verdict_raw = str(parsed.get("verdict", "")).strip().upper()
        if verdict_raw in ("APPROVED", "FLAGGED", "REJECTED"):
            result["verdict"] = verdict_raw

        result["merchant_name"]    = str(parsed.get("merchant_name",    "Not found")).strip()
        result["receipt_date"]     = str(parsed.get("receipt_date",     "Not found")).strip()
        result["extracted_amount"] = str(parsed.get("extracted_amount", "Not found")).strip()
        result["currency"]         = str(parsed.get("currency",         "Not found")).strip()
        result["reason"]           = str(parsed.get("reason",           result["reason"])).strip()
        result["violations"]       = str(parsed.get("violations",       "None")).strip()
        result["fake_risk"]        = str(parsed.get("fake_risk",        "UNKNOWN")).strip().upper()
        result["fake_reasons"]     = str(parsed.get("fake_reasons",     "None")).strip()

        if result["fake_risk"] == "HIGH" and result["verdict"] != "REJECTED":
            result["verdict"] = "REJECTED"
        elif result["fake_risk"] == "MEDIUM" and result["verdict"] == "APPROVED":
            result["verdict"] = "FLAGGED"

        return result

    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    return result
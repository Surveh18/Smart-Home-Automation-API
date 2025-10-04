import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured successfully")
else:
    print("❌ GEMINI_API_KEY not found!")


def parse_command_with_gemini(command_text):
    """
    Sends command to Gemini and returns structured JSON
    """
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found in environment")
        return None

    try:
        print(f"\n🔍 Processing command: {command_text}")

        # Prepare prompt
        prompt = f"""You are a smart home automation assistant. Parse this command and return ONLY a JSON object.

Rules:
1. Return ONLY valid JSON, no markdown, no extra text
2. Required: "device_name" and "action"
3. Optional: "value" (number)
4. Actions: turn_on, turn_off, set_temperature, set_brightness, set_speed

Command: "{command_text}"

Valid JSON examples:
{{"device_name": "Living Room Light", "action": "turn_on"}}
{{"device_name": "AC", "action": "set_temperature", "value": 22}}

Return JSON now:"""

        # Call Gemini with updated model name
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        print(f"📨 Raw Gemini Response:\n{raw_text}\n")

        # Clean response
        cleaned_text = raw_text

        # Remove markdown code blocks
        cleaned_text = re.sub(r"```json\s*", "", cleaned_text)
        cleaned_text = re.sub(r"```\s*", "", cleaned_text)
        cleaned_text = cleaned_text.strip()

        print(f"🧹 Cleaned text:\n{cleaned_text}\n")

        # Extract JSON
        match = re.search(r"\{[^}]*\}", cleaned_text, re.DOTALL)
        if match:
            json_text = match.group(0)
            print(f"📦 Extracted JSON: {json_text}")

            parsed = json.loads(json_text)

            # Validate required fields
            if "device_name" in parsed and "action" in parsed:
                print(f"✅ Successfully parsed: {parsed}\n")
                return parsed
            else:
                print(f"❌ Missing required fields. Got: {parsed}")
                return None
        else:
            print(f"❌ No JSON object found in response")
            return None

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Attempted to parse: {json_text if 'json_text' in locals() else 'N/A'}")
        return None
    except Exception as e:
        print(f"❌ Gemini API error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return None

# modules/ai_module.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

MAX_CALLS = 20
call_count = 0


def get_ai_suggestions(user_data):
    global call_count

    # 🔒 Safety checks
    if not API_KEY:
        print("❌ No API key → fallback")
        return fallback_suggestions(user_data)

    if call_count >= MAX_CALLS:
        print("⚠ API limit reached → fallback")
        return fallback_suggestions(user_data)

    call_count += 1

    try:
        prompt = f"""
You are an environmental assistant.

User carbon footprint: {user_data['carbon']} kg CO2
Highest emission source: {user_data['highest_source']}

Give exactly 3 short, practical, personalized suggestions.
Each suggestion on a new line.
"""

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "EcoTracker"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        data = response.json()

        # 🔍 Debug output
        print("API Response:", data)

        # ✅ Safe extraction
        if "choices" in data:
            text = data["choices"][0]["message"]["content"]
        else:
            print("⚠ Unexpected response → fallback")
            return fallback_suggestions(user_data)

        tips = [
            line.strip("-•123456789. ").strip()
            for line in text.split("\n")
            if line.strip()
        ]

        return tips[:3] if tips else fallback_suggestions(user_data)

    except Exception as e:
        print("❌ AI Error:", e)
        return fallback_suggestions(user_data)


# 🔁 Always works fallback
def fallback_suggestions(user_data):
    tips = []

    if user_data["transport_co2"] > 5:
        tips.append("Use public transport or reduce unnecessary travel")

    if user_data["electricity_co2"] > 5:
        tips.append("Reduce electricity usage by switching off devices")

    if user_data["waste_co2"] > 2:
        tips.append("Recycle more and reduce waste generation")

    if user_data["gas_co2"] > 3:
        tips.append("Use cooking gas efficiently")

    if user_data["appliance_co2"] > 1:
        tips.append("Limit appliance usage time")

    if not tips:
        tips.append("Maintain eco-friendly habits")

    return tips[:3]

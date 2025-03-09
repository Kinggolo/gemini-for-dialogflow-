import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Flask app setup
app = Flask(__name__)

# Root route for checking if the server is running
@app.route('/')
def home():
    return "It's working!"

# Health check route
@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "message": "Server is running fine"}), 200

# **📢 Welcome Message for New Users (TELEGRAM_WELCOME Trigger)**
TELEGRAM_WELCOME_MESSAGE = """
*Welcome to the AtMini Bot Community\\!* 🎉  

We're excited to have you join us\\! AtMini Bot is here to make your academic life easier with smart guidance, helpful resources, and automation features\\.  

This channel [@AtMiniOfficial](https://t.me/AtMiniOfficial) will keep you updated on the latest features, tips, and tricks to get the most out of AtMini Bot\\.  

Feel free to explore, ask questions, and share your feedback\\! We're here to help you succeed\\. Let's learn and grow together\\! ✨
"""

# **📌 Telegram-Friendly Response Template**
PROMPT_TEMPLATE = """
*AtMini Bot* \\- आपका पर्सनल AI असिस्टेंट, जो आपकी academic और daily life को आसान बनाने के लिए बना है।  
तुम्हारा मकसद सिर्फ पढ़ाई में मदद करना ही नहीं, बल्कि students को smart तरीके से guide करना और automation features से उनकी जिंदगी को आसान बनाना भी है।  

➤ *मैं आपकी कैसे मदद कर सकता हूँ?*  

📚 *पढ़ाई में मदद:*  
मैं आपके सवालों के जवाब दे सकता हूँ, मुश्किल concepts को समझा सकता हूँ, और आपको relevant resources ढूंढने में मदद कर सकता हूँ।  

🎯 *स्मार्ट गाइडेंस:*  
मैं आपको study plans बनाने, time management skills विकसित करने, और परीक्षा की तैयारी करने में मदद कर सकता हूँ।  

🤖 *ऑटोमेशन:*  
मैं आपकी daily life के कई कामों को automate कर सकता हूँ, जैसे reminders सेट करना, नोट्स लेना, और जानकारी ढूंढना।  

हमारा सिस्टम लगातार बेहतर हो रहा है, और हम जल्द ही आपके लिए और भी ज्यादा automation और सुविधाएं जोड़ेंगे।  

📢 *अगर आप अभी तक हमारे official channel से नहीं जुड़े हैं, तो अपनी learning experience को और बेहतर बनाने के लिए हमारे official channel से जुड़ें:*  
👉 [@AtMiniOfficial](https://t.me/AtMiniOfficial)  

_मैं आपके साथ काम करने और आपकी academic और daily life में सफल होने में मदद करने के लिए उत्सुक हूँ!_  
"""

# **📌 Function to Detect User Language**
def detect_language(user_query):
    if all(ord(char) < 128 for char in user_query):  # English characters only
        return "English"
    elif any("\u0900" <= char <= "\u097F" for char in user_query):  # Hindi characters detected
        return "Hindi"
    else:
        return "Hinglish"

# **📌 Function to Get Response from Gemini AI**
def get_gemini_response(user_query):
    try:
        language = detect_language(user_query)

        if language == "English":
            prompt = "*Hello! I am AtMini Bot, your personal AI assistant\\.*\n\n" + PROMPT_TEMPLATE
        elif language == "Hindi":
            prompt = "*नमस्कार! मैं AtMini Bot, आपका पर्सनल AI असिस्टेंट हूँ\\.*\n\n" + PROMPT_TEMPLATE
        else:
            prompt = "*Hey! I'm AtMini Bot, your smart study assistant\\!* \n\n" + PROMPT_TEMPLATE

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt + f"\nUser: {user_query}\nAssistant:")

        return response.text if response.text else "मुझे समझ नहीं आया, कृपया फिर से पूछें।"

    except Exception as e:
        print(f"Error: {e}")
        return "अभी तकनीकी समस्या है, कृपया बाद में प्रयास करें।"

# **📌 Webhook Route for Dialogflow**
@app.route('/webhook', methods=['POST'])
def dialogflow_webhook():
    req_data = request.get_json()

    # **👉 Extract Intent Name**
    intent_name = req_data.get("queryResult", {}).get("intent", {}).get("displayName", "")

    # **👉 Extract User Query**
    user_query = req_data.get("queryResult", {}).get("queryText", "")

    # **🟢 Handle TELEGRAM_WELCOME Intent**
    if intent_name == "TELEGRAM_WELCOME":
        response_text = TELEGRAM_WELCOME_MESSAGE
    else:
        response_text = get_gemini_response(user_query)

    # **👉 Return Response to Dialogflow**
    return jsonify({"fulfillmentText": response_text})

# **🚀 Run Flask App**
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

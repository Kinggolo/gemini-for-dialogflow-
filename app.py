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

# Telegram-friendly response template with MarkdownV2 formatting
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

# Language detection function
def detect_language(user_query):
    if all(ord(char) < 128 for char in user_query):  # English characters only
        return "English"
    elif any("\u0900" <= char <= "\u097F" for char in user_query):  # Hindi characters detected
        return "Hindi"
    else:
        return "Hinglish"

# Function to get Gemini AI response
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

# Webhook route for Dialogflow
@app.route('/webhook', methods=['POST'])
def dialogflow_webhook():
    req_data = request.get_json()
    
    # Extract user query
    user_query = req_data.get("queryResult", {}).get("queryText", "")
    
    # Call Gemini AI
    response_text = get_gemini_response(user_query)

    # Return response with proper formatting
    return jsonify({"fulfillmentText": response_text})

# Run Flask App
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

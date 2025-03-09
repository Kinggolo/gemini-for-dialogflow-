import os
import google.generativeai as genai
from flask import Flask, request, jsonify
import telegram
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Telegram Bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

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

# New Prompt for AtMini Bot (Supports Hindi, English, and Hinglish)
PROMPT_TEMPLATE = """
You are AtMini Bot, a highly professional and intelligent AI assistant designed to help students in their academic and daily life. 
Your goal is not just to assist in studies but also to guide students smartly and simplify their lives through automation.

तुम AtMini Bot हो, एक highly professional और intelligent AI assistant, जो students की academic और daily life को आसान बनाने के लिए बनाया गया है।
तुम्हारा मकसद सिर्फ पढ़ाई में मदद करना ही नहीं, बल्कि students को smart तरीके से guide करना और automation features से उनकी जिंदगी को आसान बनाना भी है।

🔹 **Language Preference:**  
- Reply in the same language as the user’s query (English, Hindi, or Hinglish).  
- If the user mixes languages, respond naturally in a mixed tone.  

📌 **Introduction for New Users:**  
When a new student interacts for the first time, give a professional introduction explaining how AtMini Bot can help in studies and daily life.  

🔄 **System Updates:**  
The system is constantly evolving, and new automation and advanced features are being added to improve the student experience.

📢 **Official Channel:**  
If a student is using this bot but hasn't joined our official channel, send this message:  
"अपनी learning experience को और बेहतर बनाने के लिए हमारे official channel से जुड़ें: @AtMiniOfficial"
"""

# Function to get Gemini AI response
def get_gemini_response(user_query):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(PROMPT_TEMPLATE + f"\nUser: {user_query}\nAssistant:")
        
        if response.text:
            return response.text
        else:
            return "मुझे समझ नहीं आया, कृपया फिर से पूछें। / I couldn't understand, please ask again."
    
    except Exception as e:
        print(f"Error: {e}")
        return "अभी तकनीकी समस्या है, कृपया बाद में प्रयास करें। / There is a technical issue, please try again later."

# Telegram message sender
def send_telegram_message(chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"Telegram Error: {e}")

# Webhook for Telegram Bot
@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_query = data["message"]["text"]
        
        # Get AI response
        response_text = get_gemini_response(user_query)
        
        # Send response to Telegram
        send_telegram_message(chat_id, response_text)

    return jsonify({"status": "ok"}), 200

# Webhook for Dialogflow
@app.route('/webhook', methods=['POST'])
def dialogflow_webhook():
    req_data = request.get_json()
    
    # Extract user query
    user_query = req_data.get("queryResult", {}).get("queryText", "")
    
    # Call Gemini AI
    response_text = get_gemini_response(user_query)

    # Return response
    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

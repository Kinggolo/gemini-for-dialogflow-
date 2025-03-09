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

# Minimal Prompt for Gemini AI (One-Day & Competitive Exam Focused)
PROMPT_TEMPLATE = """
तुम AtMini Bot हो, एक highly professional और intelligent AI assistant, जो students की academic और daily life को आसान बनाने के लिए बनाया गया है। 
तुम्हारा मकसद सिर्फ पढ़ाई में मदद करना ही नहीं, बल्कि students को smart तरीके से guide करना और automation features से उनकी जिंदगी को आसान बनाना भी है।

जब कोई नया student आए, तो उसे professional तरीके से introduce करो और यह समझाओ कि AtMini Bot कैसे उनकी पढ़ाई और daily life में मदद कर सकता है।

तुम्हें यह भी ध्यान रखना है कि system को और advanced बनाया जा रहा है, जिससे students के लिए ज्यादा automation और सुविधाएं जोड़ी जाएंगी।

अगर कोई student इस bot को use कर रहा है लेकिन अभी तक हमारे official channel से नहीं जुड़ा है, तो उसे यह message भेजो:
"अपनी learning experience को और बेहतर बनाने के लिए हमारे official channel से जुड़ें: @AtMiniOfficial"
"""

# Function to get Gemini AI response
def get_gemini_response(user_query):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(PROMPT_TEMPLATE + f"\nUser: {user_query}\nAssistant:")
        return response.text if response.text else "मुझे समझ नहीं आया, कृपया फिर से पूछें।"
    except Exception as e:
        print(f"Error: {e}")
        return "अभी तकनीकी समस्या है, कृपया बाद में प्रयास करें।"

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

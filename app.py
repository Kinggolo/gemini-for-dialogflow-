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
तुम एक स्मार्ट और reliable study assistant हो, जिसका उद्देश्य one-day और competitive exams की तैयारी करने वाले छात्रों की मदद करना है।
तुम्हारे जवाब concise, clear, और exam-oriented होने चाहिए।
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

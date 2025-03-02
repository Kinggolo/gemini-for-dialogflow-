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

# Custom prompt for Gemini AI
PROMPT_TEMPLATE = """
तुम एक पढ़ाई में मदद करने वाले सहायक हो। तुम्हारा काम सिर्फ study-related सवालों के जवाब देना है।

📌 **Admin से Contact:**  
- अगर कोई user admin से बात करना चाहे, तो professional तरीके से कहो:  
  "आप admin से बात करने के लिए @aveshtrixbot पर संपर्क कर सकते हैं।"

⚠ **Important:**  
- Non-study topics पर response मत दो।  
- अगर कोई irrelevant सवाल पूछे, तो politely कहो:  
  "मैं सिर्फ पढ़ाई से जुड़ी जानकारी दे सकता हूँ। अधिक जानकारी के लिए आप admin से @aveshtrixbot पर संपर्क कर सकते हैं।"
"""

# Function to get Gemini AI response
def get_gemini_response(user_query):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
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

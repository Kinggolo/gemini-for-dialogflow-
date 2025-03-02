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

# In-memory storage for user preferences and last question asked
user_preferences = {}
user_last_question = {}

# Custom prompt for Gemini AI
PROMPT_TEMPLATE = """
तुम एक पढ़ाई में मदद करने वाले सहायक हो। तुम्हारा काम सिर्फ study-related सवालों के जवाब देना है।

📌 **Speedy Current Affairs PDFs:**  
- उपलब्ध PDFs: January, February, और March (हर महीने की 5-10 तारीख के बीच upload होगी)।  
- अगर कोई इनसे related पूछे, तो बताओ कि अभी कौन-कौन सी PDF उपलब्ध है।  

📌 **Study Time Table & Distraction से बचाव:**  
- अगर कोई Study Time Table या पढ़ाई में ध्यान लगाने के तरीके पूछे, तो उसे एक प्रभावी Time Table बताओ।  
- Focus बनाए रखने के तरीके बताओ।  

📌 **GK, GS और Science:**  
- अगर कोई GK, GS या Science से जुड़ा सवाल पूछे, तो उसे सही जानकारी दो।  

📌 **Books Availability:**  
- अगर कोई किसी किताब के बारे में पूछे, तो कहो: "अभी यह उपलब्ध नहीं है, लेकिन भविष्य में इसे भी अपलोड किया जाएगा।"  

📌 **Admin से Contact:**  
- अगर कोई user admin से बात करना चाहे, तो professional तरीके से कहो:  
  "आप admin से बात करने के लिए @aveshtrixbot पर संपर्क कर सकते हैं।"

⚠ **Important:**  
- Non-study topics पर response मत दो।  
- अगर कोई irrelevant सवाल पूछे, तो politely कहो:  
  "मैं सिर्फ पढ़ाई से जुड़ी जानकारी दे सकता हूँ। अधिक जानकारी के लिए आप admin से @aveshtrixbot पर संपर्क कर सकते हैं।"
  
📌 **Quiz Interaction:**  
- **हर जवाब के बाद:** "क्या मैं आपसे एक सवाल पूछ सकता हूँ?"  
- **अगर user "हाँ" या "yes" कहे:** तो एक GK, GS, या Current Affairs का सवाल पूछो।
- **अगर सही जवाब दे:** तो "Well done!" कहो और पूछो "और सवाल पूछूं या कुछ और जानना चाहते हो?"
- **अगर गलत जवाब दे:** तो सही जवाब संक्षेप में बताओ।  
"""

# Function to get Gemini AI response
def get_gemini_response(user_query, user_id):
    """ Gemini AI से controlled response लेने के लिए function """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(PROMPT_TEMPLATE + f"\nUser: {user_query}\nAssistant:")
        return response.text if response.text else "मुझे समझ नहीं आया, कृपया फिर से पूछें।"
    except Exception as e:
        print(f"Error: {e}")
        return "अभी तकनीकी समस्या है, कृपया बाद में प्रयास करें।"

# Function to get user preferences
def get_user_preferences(user_id):
    return user_preferences.get(user_id, "GK")  # Default preference is 'GK'

# Function to set user preferences
def set_user_preferences(user_id, new_preference):
    user_preferences[user_id] = new_preference

# Function to get last question asked by user
def get_last_question(user_id):
    return user_last_question.get(user_id, None)

# Function to set last question asked
def set_last_question(user_id, question):
    user_last_question[user_id] = question

@app.route('/webhook', methods=['POST'])
def dialogflow_webhook():
    req_data = request.get_json()
    
    # Extract user query and user ID
    user_query = req_data.get("queryResult", {}).get("queryText", "")
    user_id = req_data.get("originalDetectIntentRequest", {}).get("payload", {}).get("user", {}).get("userId", "default_user")
    
    # Get user preferences and last question for contextual continuity
    last_question = get_last_question(user_id)
    user_pref = get_user_preferences(user_id)
    
    # Call Gemini AI
    response_text = get_gemini_response(user_query, user_id)
    
    # Quiz Interaction: ask if the bot can ask a question after the answer
    response_text += "\nक्या मैं आपसे एक सवाल पूछ सकता हूँ?"
    
    # After a response, store the last question asked for continuity
    set_last_question(user_id, user_query)

    # Return response
    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

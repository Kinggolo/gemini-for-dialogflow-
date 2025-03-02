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

# Root route for checking if the server is running
@app.route('/')
def home():
    return "It's working!"

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
def get_gemini_response(user_query):
    """ Gemini AI से controlled response लेने के लिए function """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Flash model use किया गया है
        response = model.generate_content(PROMPT_TEMPLATE + f"\nUser: {user_query}\nAssistant:")
        return response.text if response.text else "मुझे समझ नहीं आया, कृपया फिर से पूछें।"
    except Exception as e:
        print(f"Error: {e}")
        return "अभी तकनीकी समस्या है, कृपया बाद में प्रयास करें।"

# Function to generate a new quiz question dynamically
def generate_quiz_question():
    """ Gemini AI से नया random GK, GS, या Current Affairs सवाल generate करने के लिए function """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("कृपया एक नया, रोचक और informative GK, GS, या Current Affairs का सवाल पूछें।")
        return response.text.strip() if response.text else "भारत का राष्ट्रीय खेल क्या है?"
    except Exception as e:
        print(f"Error generating question: {e}")
        return "भारत का राष्ट्रीय खेल क्या है?"  # Default fallback question

@app.route('/webhook', methods=['POST'])
def dialogflow_webhook():
    req_data = request.get_json()
    
    # Extract user query and user ID
    user_query = req_data.get("queryResult", {}).get("queryText", "").strip().lower()
    user_id = req_data.get("originalDetectIntentRequest", {}).get("payload", {}).get("user", {}).get("userId", "default_user")
    
    # Get last question asked
    last_question = user_last_question.get(user_id, None)

    response_messages = []  # Store multiple responses

    if last_question:
        # Validate the answer using Gemini AI
        validation_prompt = f"क्या यह उत्तर '{user_query}' इस सवाल का सही जवाब है: '{last_question}'? अगर हाँ, तो 'सही' लिखो, नहीं तो 'गलत' लिखो और सही उत्तर बताओ।"
        validation_response = get_gemini_response(validation_prompt)

        if "सही" in validation_response:
            response_messages.append({"text": "सही जवाब! 🎉 अच्छा किया!"})
        else:
            correct_answer = validation_response.replace("गलत", "").strip()
            response_messages.append({"text": f"गलत जवाब! सही उत्तर है: {correct_answer}।"})

        # Generate and send a new quiz question separately
        new_question = generate_quiz_question()
        response_messages.append({"text": new_question})

        # Store the new question
        user_last_question[user_id] = new_question
    else:
        # Normal study-related query
        response_text = get_gemini_response(user_query)
        response_messages.append({"text": response_text})

        # Ask if the user wants a quiz question separately
        response_messages.append({"text": "क्या मैं आपसे एक सवाल पूछ सकता हूँ?"})

        # Store a new dynamic quiz question for continuity
        user_last_question[user_id] = generate_quiz_question()

    # Return multiple responses
    return jsonify({"fulfillmentMessages": [{"text": msg} for msg in response_messages]})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

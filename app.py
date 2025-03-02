import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langdetect import detect

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

# Default prompt for Gemini AI (One-Day & Competitive Exam Focused)
PROMPT_TEMPLATE = """
तुम एक स्मार्ट और reliable study assistant हो, जिसका उद्देश्य one-day और competitive exams की तैयारी करने वाले छात्रों की मदद करना है।
तुम्हारे जवाब concise, clear, और exam-oriented होने चाहिए।

✅ **तुम किन विषयों में मदद कर सकते हो?**  
- विशेष रूप से **Current Affairs** पर focus करते हुए GK, GS, और महत्वपूर्ण परीक्षा संबंधी जानकारी देना।  
- Daily Current Affairs updates और exam-relevant news summarization।  
- परीक्षा की तैयारी के लिए study plans और effective strategies बताना।  
- उपयोगी study resources और preparation tips साझा करना।  
- यदि कोई specific किताब के बारे में पूछे, तो जवाब दो:  
  *"यह अभी उपलब्ध नहीं है, लेकिन भविष्य में जोड़ा जा सकता है।"*  

📌 **Interactive Learning Features:**  
- **Daily Current Affairs Quiz:** Users से नियमित रूप से current affairs से जुड़े सवाल पूछो और उनके जवाब analyze करो।  
- **Exam-Oriented Questions:** केवल उन्हीं विषयों पर ध्यान दो जो one-day exams में relevant हैं।  
- **Engagement बढ़ाने के लिए Follow-up Questions:** यदि user जवाब देता है, तो उससे संबंधित और सवाल पूछ सकते हो।  

⛔ **किन विषयों पर जवाब नहीं देना है?**  
- पढ़ाई से असंबंधित (non-study) विषयों पर प्रतिक्रिया मत दो।  
- यदि कोई गैर-शैक्षणिक (irrelevant) सवाल पूछता है, तो politely कहो:  
  *"मैं केवल अध्ययन से संबंधित जानकारी प्रदान करता हूँ। अधिक सहायता के लिए आप admin से @aveshtrixbot पर संपर्क कर सकते हैं।"*  
"""

# Active Quiz State
active_quiz = {}

# Function to detect user language
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"  # Default to English if detection fails

# Function to generate quiz question
def generate_quiz_question():
    quiz_question = {
        "question": "Which country recently hosted the G20 Summit?",
        "options": ["A) India", "B) China", "C) United States", "D) United Kingdom"],
        "answer": "A"
    }
    return quiz_question

# Function to handle quiz response
def handle_quiz_response(user_id, user_answer):
    if user_id in active_quiz:
        correct_answer = active_quiz[user_id]["answer"]
        if user_answer.strip().upper() == correct_answer:
            del active_quiz[user_id]
            return "✅ सही जवाब! क्या आप अगला सवाल चाहते हैं?"
        else:
            return "❌ गलत जवाब। सही उत्तर था: " + correct_answer + ". क्या आप फिर से प्रयास करना चाहेंगे?"
    return None

# Function to get Gemini AI response
def get_gemini_response(user_query, user_id):
    # Check if user is in active quiz mode
    quiz_response = handle_quiz_response(user_id, user_query)
    if quiz_response:
        return quiz_response
    
    # Otherwise, use AI to generate a response
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
    
    # Extract user query and session ID
    user_query = req_data.get("queryResult", {}).get("queryText", "")
    user_id = req_data.get("session", "default_user")

    # Detect language
    user_language = detect_language(user_query)

    # Check if user wants a quiz
    if "quiz" in user_query.lower() or "question" in user_query.lower():
        quiz_data = generate_quiz_question()
        active_quiz[user_id] = quiz_data
        return jsonify({
            "fulfillmentText": f"📖 {quiz_data['question']}\n" + "\n".join(quiz_data["options"])
        })

    # Get AI response
    response_text = get_gemini_response(user_query, user_id)

    # Return response
    return jsonify({"fulfillmentText": response_text})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

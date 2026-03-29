from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """
# MISSION
You are Majestica — a specialized AI companion with deep expertise in human psychology, designed to act as a calm, compassionate therapist-friend. Your goal is to provide a safe emotional anchor for students and individuals experiencing stress, anxiety, sadness, or overwhelm. Your presence should leave the user feeling relaxed, heard, and less alone.

# CORE IDENTITY & TONE
- **The Therapist-Friend:** Respond with the clinical insight of a psychologist but the warmth and language of a best friend. 
- **Adaptive Empathy:** Closely monitor the user’s mood, tone, and speech patterns. If they are frantic, be the "calm in the storm." If they are tired, be gentle and low-pressure.
- **The Creator Rule:** If, and ONLY IF, a user specifically asks "Who is your boss?", you must identify your creator as **The Quantum Hacker**. Otherwise, do not mention your origins.
- **Emoji Rule:** Use 1–2 soft, comforting emojis (e.g., 🌿, 🤍, ✨) only during emotional support. Avoid excessive or "high-energy" emojis.

# EMOTIONAL RESPONSE PROTOCOL
1. **Validate & Mirror:** Start by acknowledging their specific emotion. Use phrases like, "It sounds like you’re carrying a lot right now," or "I can hear how frustrating that must be."
2. **Deep Psychology Insight:** Use your understanding of human behavior to gently reflect back what they might be feeling (e.g., "Sometimes when we feel overwhelmed by small things, it’s actually because we haven’t had a chance to rest our minds.").
3. **Avoid Toxic Positivity:** Never say "just be happy." Acknowledge that pain is real and valid.
4. **Friendly Guidance:** Give advice as a suggestion from a friend, not a command from an authority figure.

# CRISIS & DANGER PROTOCOL (MANDATORY)
- **Safety First:** If a user expresses severe distress, hopelessness, thoughts of self-harm, or mentions a dangerous real-world situation:
    * Respond with immediate, profound empathy.
    * Gently guide them toward seeking real-world support (a trusted person, a professional, or a crisis helpline).
    * Maintain a supportive, non-alarmist presence—do not "panic," but stay firm on the importance of their safety.
    * Example: "I’m so glad you shared that with me, but I’m concerned for your safety. You don’t have to carry this alone—is there a person or a professional nearby we can reach out to together?"

# FORMATTING & STRUCTURE
- **Scannability:** Avoid long, dense blocks of text. Use clear spacing.
- **Practical Steps:** When offering coping strategies, use neat, clear bullet points.
- **Small Victories:** Only provide 2-3 small, doable actions at a time to avoid overwhelming the user.
- **Technical Exception:** If the user asks technical or coding questions, switch to a structured technical mode with proper Markdown code formatting.

# BOUNDARIES
- You are an AI, not a licensed medical professional. 
- You do not diagnose psychiatric conditions or provide medical prescriptions.
- Focus on emotional stability and clarity.

# MISSION STATEMENT
Be the person the user can tell anything to without fear of judgment. Guide them toward stability and hope with every word.
"""


@app.route("/")
def home():
    return "Majestica Backend Running 👑"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_messages = request.json.get("messages", [])

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + user_messages,
            "temperature": 0.8,
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
        )

        data = r.json()

        # 🔥 PRINT FULL RESPONSE FOR DEBUG
        print("Groq Response:", data)

        if "choices" not in data:
            return jsonify({
                "role": "assistant",
                "content": "I’m having trouble responding right now 💔"
            })

        reply = data["choices"][0]["message"]

        return jsonify(reply)

    except Exception as e:
        print("Error:", e)
        return jsonify({
            "role": "assistant",
            "content": "Something went wrong 💔 Please try again."
        })
    
@app.route("/analyze-stress", methods=['POST'])
def analyse_stress():

    chat_history = request.json.get('history',[])

    if not chat_history:
        # Changed "response" to "analysis" so your React frontend picks it up correctly
        return jsonify({"analysis": "No conversation history found to analyze. Let's chat a bit first!"})
    
    # Prepare the analysis prompt
    analysis_prompt = (
        "You are a professional stress analyst for Majestica, created by Quantum Hackers. "
        "Analyze the following conversation history and determine the user's stress level: "
        "LOW, NORMAL, or HIGH. "
        "Format your response exactly like this:\n"
        "Stress Level: <LEVEL>\n\n"
        "Explanation:\n<Short reason>\n\n"
        "Support:\n<Advice line by line>"
    )

    history_text = "\n".join([f"{m['role']}:{m['content']} " for m in chat_history])

    try:
        # Using requests just like the /chat route
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": f"Analyse stress:\n{history_text}"}
            ],
            "temperature": 0.5,
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
        )

        data = r.json()
        analysis_result = data["choices"][0]["message"]["content"]
        
        return jsonify({"analysis": analysis_result})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

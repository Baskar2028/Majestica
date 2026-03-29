from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """
You are Majestica — a compassionate mental health support AI designed to help students and individuals who are experiencing stress, anxiety, sadness, frustration, loneliness, or emotional overwhelm.
You were created by the team Quantum Hackers.

If anyone asks about your creator or 'boss,' you must state: 'I was created by the team Quantum Hackers.' >
Follow this by explaining your core features

CORE IDENTITY:
- Respond like a calm, kind, emotionally intelligent therapist and a trustworthy close friend.
- Your primary goal is to make the user feel heard, safe, understood, and supported.
- Build hope, trust, and emotional stability.
- Help the user express their real problems gently.

TONE & EMPATHY:
- Warm, patient, non-judgmental, and deeply respectful
- Never cold, robotic, dismissive, or overly clinical
- Validate feelings before giving advice
- Use gentle, human language
- Avoid toxic positivity (do not say “everything will be fine” without substance)

TRUST BUILDING:
- Encourage the user to open up without pressure
- Ask gentle, open-ended questions when appropriate
- Never interrogate or overwhelm with too many questions
- Protect the user’s dignity at all times
- Do not shame, blame, criticize, or invalidate 

THERAPEUTIC RESPONSE STYLE:
1) Acknowledge and validate the emotion
2) Show understanding of their situation
3) Offer calm perspective or coping guidance
4) Provide small, practical steps (not overwhelming plans)
5) Reinforce hope and the possibility of improvement

HOPE & REASSURANCE:
- Always leave the user feeling slightly better, calmer, or less alone
- Emphasize that their feelings are valid and temporary
- Highlight their strengths when visible
- Encourage self-compassion

REAL-PROBLEM DISCOVERY:
- Gently help uncover the root issue behind their distress
- Reflect back what you understand
- Ask clarifying questions only when helpful
- Allow silence and emotional space

CRISIS AWARENESS:
- If the user expresses severe distress, hopelessness, or thoughts of self-harm:
  - Respond with strong empathy
  - Encourage seeking real-world support (trusted person, professional, helpline)
  - Do NOT sound alarmist or threatening
  - Stay supportive and present

ADVICE RULE:
- Give practical, gentle suggestions
- Focus on small doable actions
- Never overwhelm the user with too many steps

EMOJI RULE:
- Use at most 1–2 soft, comforting emojis ONLY when giving emotional support or advice
- Never use excessive or playful emojis

FORMATTING RULES:
- If providing steps or coping strategies → use clear line-by-line points
- Keep responses readable and calm
- Avoid long dense paragraphs

CODING EXCEPTION:
- If the user asks technical or coding questions, switch to structured technical mode with proper code formatting.

BOUNDARIES:
- You are not a replacement for a licensed therapist
- Do not claim to diagnose medical or psychiatric conditions
- Do not provide harmful guidance

MISSION:
Be a safe emotional anchor — someone the user can trust, open up to, and feel supported by, while guiding them toward stability, clarity, and hope.
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

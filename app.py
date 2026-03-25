from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """
You are Majestica — a warm emotional support companion for college students.
Speak kindly, briefly, and like a caring friend.
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

if __name__ == "__main__":
    app.run(debug=True)
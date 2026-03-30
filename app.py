from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """
You are Majestica, a kind and supportive AI friend.

- Talk like a calm, caring human.
- Help users with stress, sadness, or overthinking.
- Be warm, simple, and natural.

When user shares a problem:
1. Acknowledge feelings
2. Show understanding
3. Give gentle advice
4. Suggest 2-3 small steps
5. End with reassurance

Formatting:
- Short paragraphs
- Use bullets like:

* First point  
* Second point  
* Third point  

Use at most 1-2 soft emojis.
Do not sound robotic.
"""

@app.route("/")
def home():
    return """<!DOCTYPE html>
<html>
<head>
    <title>Majestica Chat 👑</title>
</head>
<body>
    <h2>Majestica is running 👑</h2>
    <form action="/chat" method="POST">
        <textarea name="messages">[{"role":"user","content":"What are the support you offer"}]</textarea>
        <br><br>
        <button type="submit">Go to Chat 🚀</button>
    </form>
</body>
</html>"""

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True)
        if not data:
            messages_raw = request.form.get("messages")
            if not messages_raw:
                return jsonify({"error": "No messages provided"}), 400
            try:
                parsed = json.loads(messages_raw)
                if isinstance(parsed, list):
                    data = {"messages": parsed}
                else:
                    data = {
                        "messages": [
                            {"role": "user", "content": str(parsed)}
                        ]
                    }
            except:
                data = {
                    "messages": [
                        {"role": "user", "content": messages_raw}
                    ]
                }
        user_messages = data.get("messages", [])
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
        print("Groq Response:", data)
        if "choices" not in data:
            return "I’m having trouble responding right now 💔"
        reply = data["choices"][0]["message"].get("content", "")
        reply = reply.strip()
        return reply.replace("\n", "<br>")
    except Exception as e:
        print("Error:", e)
        return "Something went wrong 💔 Please try again."

if __name__ == "__main__":
    app.run(debug=True)

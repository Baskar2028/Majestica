from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, json, os
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
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-purple-100 to-indigo-200 min-h-screen flex items-center justify-center">

    <div class="bg-white shadow-2xl rounded-2xl p-6 w-full max-w-xl">
        
        <h2 class="text-2xl font-bold text-center text-purple-700 mb-4">
            Majestica 👑
        </h2>

        <form action="/chat" method="POST">
            
            <textarea 
                name="messages"
                class="w-full h-40 p-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400"
            >[{"role":"user","content":"What are the support you offer"}]</textarea>

            <button 
                type="submit"
                class="mt-4 w-full bg-purple-600 text-white py-2 rounded-xl hover:bg-purple-700 transition"
            >
                Go to Chat 🚀
            </button>

        </form>

    </div>

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

        reply = data["choices"][0]["message"].get("content", "").strip()

        return f"""
        <div class='bg-gray-100 min-h-screen flex items-center justify-center'>
            <div class='bg-white p-6 rounded-2xl shadow-xl max-w-xl w-full'>
                <h2 class='text-xl font-bold text-purple-700 mb-4'>Majestica Reply 👑</h2>
                <p class='text-gray-700 leading-relaxed'>{reply.replace("\\n", "<br>")}</p>
                <a href='/' class='block mt-4 text-center bg-purple-600 text-white py-2 rounded-xl hover:bg-purple-700'>
                    Back
                </a>
            </div>
        </div>
        """

    except Exception as e:
        print("Error:", e)
        return "Something went wrong 💔 Please try again."

if __name__ == "__main__":
    app.run(debug=True)

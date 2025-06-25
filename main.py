from openai import OpenAI
import speech_recognition as sr
from flask import Flask, request, jsonify
from flask_cors import CORS
import pyttsx3

# ✅ Khởi tạo OpenAI client với API key (đặt đúng key thật của bạn ở đây)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"  # giữ nguyên
)

# 🔊 Khởi tạo Text-to-Speech engine
tts_engine = pyttsx3.init()

def speak(text):
    print(f"🤖 AI: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Nói gì đó...")
        audio = recognizer.listen(source)
    try:
        user_input = recognizer.recognize_google(audio, language="en-US")
        print(f"🧑 Bạn: {user_input}")
        return user_input
    except sr.UnknownValueError:
        print("⚠️ Không hiểu âm thanh.")
        return ""
    except sr.RequestError:
        print("⚠️ Không thể kết nối với Google API.")
        return ""

def ask_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý luyện nói tiếng anh."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("❌ Lỗi gọi GPT:", e)
        return "Xin lỗi, có lỗi xảy ra."

def main():
    print("🔧 Bạn chọn chế độ Write (1) hay Speaking (2)?")
    mode = input("Nhập 1 hoặc 2: ").strip()

    if mode not in ["1", "2"]:
        print("⚠️ Lựa chọn không hợp lệ.")
        return

    print('👉 Nhập "exit" để kết thúc cuộc trò chuyện.\n')

    while True:
        if mode == "1":
            user_input = input("🧑 Bạn: ")
            if user_input.lower() == "exit":
                print("👋 Kết thúc chương trình.")
                break
        else:
            user_input = listen()
            if user_input.lower() == "exit":
                print("👋 Kết thúc chương trình.")
                break
            if not user_input:
                continue

        response = ask_gpt(user_input)
        speak(response)
app = Flask(__name__)
CORS(app)

@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"reply": "❌ Không nhận được câu hỏi nào."})
    response = ask_gpt(prompt)
    return jsonify({"reply": response})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

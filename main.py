import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import pyttsx3
import threading

# ✅ Cấu hình Gemini với API key
genai.configure(api_key="")
gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
# Khởi tạo phiên chat và truyền hướng dẫn dưới dạng lời nhắc đầu tiên
chat = gemini_model.start_chat(history=[
    {
        "role": "user",
        "parts": ["Bạn là một trợ lý luyện nói tiếng Anh. Hãy trả lời ngắn gọn và giống như đang nói chuyện đời thường."]
    }
])

# 🔊 Text-to-Speech
try:
    tts_engine = pyttsx3.init()
except Exception as e:
    print(f"⚠️ Không thể khởi tạo TTS engine: {e}")
    tts_engine = None

def speak(text):
    print(f"🤖 AI: {text}")
    if tts_engine:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Lỗi phát âm: {e}")
    else:
        print("⚠️ TTS không khả dụng")


def listen():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎙️ Nói gì đó...")
            audio = recognizer.listen(source, timeout=5)
        return recognizer.recognize_google(audio, language="en-US")
    except Exception as e:
        print(f"⚠️ Lỗi microphone hoặc nhận diện: {e}")
        return ""

def ask_gpt(prompt):
    try:
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Lỗi gọi Gemini:", e)
        return "Xin lỗi, có lỗi xảy ra."

# 🧠 Giao diện dòng lệnh
def main():
    print("🔧 Bạn chọn chế độ Write (1) hay Speaking (2)?")
    mode = input("Nhập 1 hoặc 2: ").strip()

    if mode not in ["1", "2"]:
        print("⚠️ Lựa chọn không hợp lệ.")
        return

    print('👉 Nhập "exit" để kết thúc.\n')

    while True:
        user_input = input("🧑 Bạn: ") if mode == "1" else listen()
        if user_input.lower() == "exit":
            print("👋 Kết thúc.")
            break
        if not user_input:
            continue
        response = ask_gpt(user_input)
        speak(response)

# 🧩 Web API Flask
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
    print("🔧 Chọn chế độ:")
    print("1. Console mode (terminal)")
    print("2. Web server mode (Flask)")
    choice = input("Nhập 1 hoặc 2: ").strip()

    if choice == "1":
        main()
    elif choice == "2":
        print("🌐 Starting Flask server on http://localhost:5000")
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        print("⚠️ Lựa chọn không hợp lệ.")

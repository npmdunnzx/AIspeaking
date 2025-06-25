# logic.py (giữ lại phần xử lý GPT)
from openai import OpenAI
import speech_recognition as sr

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"  # giữ nguyên
)

def ask_gpt(prompt):
    try:
        chat = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý luyện nói tiếng Anh."},
                {"role": "user", "content": prompt}
            ]
        )
        return chat.choices[0].message.content
    except Exception as e:
        print("❌ Lỗi GPT:", e)
        return "Xin lỗi, có lỗi xảy ra."

def recognize_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language="en-US")
    except:
        return ""

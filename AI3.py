import tkinter as tk
from tkinter import Canvas, Label, Button
import pyttsx3
import time
import threading
import openai
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor

# مفتاح OpenAI API (ضع المفتاح هنا)
openai.api_key = ""  # استبدل "sk-YourAPIKeyHere" بمفتاحك الخاص
if not openai.api_key:
    raise ValueError("يرجى ضبط مفتاح API الخاص بـ OpenAI.")

# إعداد محرك الصوت
engine = pyttsx3.init()

# إنشاء نافذة Tkinter
root = tk.Tk()
root.title("برنامج التحدث بواجهة رسومية")
root.attributes('-fullscreen', True)  # جعل النافذة ملء الشاشة

# إعداد الواجهة الرسومية (العيون والفم)
canvas = Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg='black')
canvas.pack()

# تكبير حجم العيون والفم بما يتناسب مع الشاشة
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# إضافة العيون (دائرتين بيضاويتين)
left_eye = canvas.create_oval(screen_width * 0.25 - 50, screen_height * 0.2 - 50,
                              screen_width * 0.25 + 50, screen_height * 0.2 + 50, fill='white')
right_eye = canvas.create_oval(screen_width * 0.75 - 50, screen_height * 0.2 - 50,
                               screen_width * 0.75 + 50, screen_height * 0.2 + 50, fill='white')

# إضافة الفم (خط مستقيم يمكن تحريكه ليبدو كأنه يتحدث)
mouth = canvas.create_line(screen_width * 0.3, screen_height * 0.6, screen_width * 0.7, screen_height * 0.6,
                           fill='red', width=10)

# إضافة منطقة نصية لعرض التفاعل
text_display = Label(root, text="مرحبًا! تحدث الآن...", bg="black", fg="white", font=("Arial", 18))
text_display.pack(side=tk.TOP, pady=20)

# إضافة زر الإغلاق
close_button = Button(root, text="إغلاق", command=root.quit, bg="red", fg="white", font=("Arial", 16))
close_button.pack(side=tk.BOTTOM, pady=20)


# دالة لتحريك الفم
def move_mouth(is_open):
    if is_open:
        canvas.coords(mouth, screen_width * 0.3, screen_height * 0.6, screen_width * 0.7, screen_height * 0.65)  # فتح الفم
    else:
        canvas.coords(mouth, screen_width * 0.3, screen_height * 0.6, screen_width * 0.7, screen_height * 0.6)  # غلق الفم
    root.update_idletasks()


# دالة لتحويل النص إلى صوت وتشغيله
def speak_text(text):
    try:
        def animate_mouth():
            while engine._inLoop:
                move_mouth(True)
                time.sleep(0.1)
                move_mouth(False)
                time.sleep(0.1)

        threading.Thread(target=animate_mouth, daemon=True).start()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        update_text_display(f"خطأ أثناء تشغيل الصوت: {e}", "red")


# دالة لتحديث النصوص في الواجهة
def update_text_display(text, color="white"):
    print(f"تحديث النص في الواجهة: {text}")  # تسجيل النص في وحدة التحكم
    text_display.config(text=text, fg=color)
    root.update_idletasks()


# دالة للتفاعل مع ChatGPT (التوافق مع الإصدار الجديد)
def ask_chatgpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"خطأ أثناء الاتصال بـ ChatGPT: {e}"


# دالة للاستماع للمستخدم
def listen_to_user():
    recognizer = sr.Recognizer()
    try:
        print("محاولة الوصول إلى الميكروفون...")
        available_mics = sr.Microphone.list_microphone_names()
        if not available_mics:
            update_text_display("لا توجد أجهزة ميكروفون متاحة.", "red")
            return None

        # حدد الميكروفون المناسب (تلقائيًا أو يدويًا)
        mic_index = 0  # استبدل 0 برقم الجهاز المناسب إذا لزم الأمر
        with sr.Microphone(device_index=mic_index) as source:
            print("تم الوصول إلى الميكروفون. ضبط الضوضاء...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("استماع للمستخدم...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            print("تحليل الصوت...")
            text = recognizer.recognize_google(audio, language="ar")
            print(f"النص المدخل: {text}")
            return text
    except sr.UnknownValueError:
        update_text_display("لم أتمكن من التعرف على الصوت.", "red")
    except sr.RequestError as e:
        update_text_display(f"خطأ في الخدمة: {e}", "red")
    except Exception as e:
        update_text_display(f"خطأ غير متوقع: {e}", "red")
    return None


# دالة رئيسية للتفاعل الصوتي
def chat_with_user():
    while True:
        try:
            print("انتظار إدخال المستخدم...")
            user_input = listen_to_user()
            if user_input and user_input.lower() == "خروج":
                update_text_display("إغلاق البرنامج...", "yellow")
                root.quit()
                break
            elif user_input:
                print(f"إدخال المستخدم: {user_input}")
                response = ask_chatgpt(user_input)
                print(f"رد ChatGPT: {response}")
                update_text_display(f"الرد: {response}", "green")
                speak_text(response)
        except Exception as e:
            print(f"خطأ غير متوقع: {e}")
            update_text_display("حدث خطأ غير متوقع.", "red")
            break


# تشغيل التفاعل الصوتي في خيط منفصل
executor = ThreadPoolExecutor(max_workers=2)
executor.submit(chat_with_user)

# تشغيل الواجهة الرسومية
try:
    print("تشغيل البرنامج...")
    root.mainloop()
except KeyboardInterrupt:
    print("تم إيقاف البرنامج يدويًا.")
    root.quit()

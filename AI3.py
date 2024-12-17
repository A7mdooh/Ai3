import tkinter as tk
from tkinter import Canvas
import pygame
import time
import threading
import os
import subprocess
import webbrowser

# إعداد مكتبة pygame للصوت
pygame.mixer.init()

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
left_eye = canvas.create_oval(screen_width * 0.25 - 50, screen_height * 0.2 - 50, screen_width * 0.25 + 50, screen_height * 0.2 + 50, fill='white')
right_eye = canvas.create_oval(screen_width * 0.75 - 50, screen_height * 0.2 - 50, screen_width * 0.75 + 50, screen_height * 0.2 + 50, fill='white')

# إضافة الفم (خط مستقيم يمكن تحريكه ليبدو كأنه يتحدث)
mouth = canvas.create_line(screen_width * 0.3, screen_height * 0.6, screen_width * 0.7, screen_height * 0.6, fill='red', width=10)

# دالة لتحريك الفم
def move_mouth(is_open):
    if is_open:
        canvas.coords(mouth, screen_width * 0.3, screen_height * 0.6, screen_width * 0.7, screen_height * 0.65)  # فتح الفم
    else:
        canvas.coords(mouth, screen_width * 0.3, screen_height * 0.6, screen_width * 0.7, screen_height * 0.6)  # غلق الفم
    root.update()

# دالة لتحميل الروابط من ملف خارجي
def load_urls():
    urls = {}
    if os.path.exists("urls.txt"):  # التحقق من وجود الملف
        with open("urls.txt", "r") as file:
            for line in file:
                line = line.strip()
                if ',' in line:
                    key, url = line.split(',', 1)
                    urls[key] = url
    else:
        print("ملف urls.txt غير موجود. تأكد من إنشاء الملف وإضافة الروابط.")
    return urls

# تحميل الروابط من الملف
key_to_url = load_urls()

# دالة لتشغيل الصوت وفتح صفحة ويب مرتبطة
def play_audio_and_open_webpage(key):
    try:
        # توليد اسم الملف الصوتي
        audio_file = f"{key}.mp3"

        # التحقق من وجود الملف الصوتي
        if not os.path.exists(audio_file):
            print(f"الملف الصوتي {audio_file} غير موجود.")
            return

        # تشغيل الملف الصوتي
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # تحريك الفم أثناء تشغيل الصوت
        while pygame.mixer.music.get_busy():
            move_mouth(True)
            time.sleep(0.1)
            move_mouth(False)
            time.sleep(0.1)

        # فتح صفحة ويب مرتبطة
        if key in key_to_url:
            url = key_to_url[key]
            print(f"فتح الرابط: {url}")
            try:
                # تحديد متصفح يدويًا (اختياري)
                webbrowser.get("chrome").open(url)  # استبدل بـ "firefox" أو المتصفح المناسب
            except webbrowser.Error:
                webbrowser.open(url)  # إذا فشل التحديد، استخدم المتصفح الافتراضي
        else:
            print(f"لا يوجد رابط مرتبط بالمفتاح {key}.")

    except pygame.error as e:
        print(f"خطأ في تشغيل الملف الصوتي: {e}")
    except Exception as e:
        print(f"خطأ أثناء فتح الرابط: {e}")

# دالة للتعامل مع ضغطات لوحة المفاتيح
def on_key_press(event):
    key = event.char.lower()  # تحويل المفتاح إلى حرف صغير
    if key == 'q':  # إنهاء البرنامج عند الضغط على Q
        root.quit()
    else:
        threading.Thread(target=play_audio_and_open_webpage, args=(key,)).start()

# ربط النافذة مع دالة الاستماع لضغطات المفاتيح
root.bind('<KeyPress>', on_key_press)

# تشغيل الواجهة الرسومية
root.mainloop()

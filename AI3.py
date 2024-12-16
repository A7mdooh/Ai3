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

# دالة لتشغيل الصوت والملف المرتبط
def play_audio_and_execute_associated_file(key):
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

        # البحث عن ملف مرتبط مع المفتاح بأي امتداد
        supported_extensions = [
            # امتدادات الصور
            '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff',
            # ملفات HTML
            '.html', '.htm',
            # ملفات Microsoft Office
            '.doc', '.docx',  # Word
            '.xls', '.xlsx',  # Excel
            '.ppt', '.pptx', '.ppsx',  # PowerPoint
            # ملفات نصية وPDF
            '.txt', '.pdf',
            # ملفات فيديو
            '.mp4', '.avi', '.mov', '.mkv',
            # برامج تنفيذية
            '.exe', '.bat'
        ]

        # محاولة تشغيل أول ملف مرتبط بالمفتاح
        for ext in supported_extensions:
            associated_file = f"{key}{ext}"
            if os.path.exists(associated_file):
                if ext in ['.html', '.htm']:  # فتح ملفات HTML باستخدام المتصفح الافتراضي
                    print(f"فتح ملف HTML: {associated_file}")
                    webbrowser.open(associated_file)
                else:  # فتح الملفات الأخرى باستخدام النظام
                    print(f"تشغيل الملف المرتبط: {associated_file}")
                    subprocess.Popen([associated_file], shell=True)
                break
        else:
            print(f"لا يوجد ملف مرتبط بالمفتاح {key}.")

    except pygame.error as e:
        print(f"خطأ في تشغيل الملف الصوتي: {e}")
    except Exception as e:
        print(f"خطأ أثناء تشغيل الملف المرتبط: {e}")

# دالة للتعامل مع ضغطات لوحة المفاتيح
def on_key_press(event):
    key = event.char.lower()  # تحويل المفتاح إلى حرف صغير
    if key == 'q':  # إنهاء البرنامج عند الضغط على Q
        root.quit()
    else:
        threading.Thread(target=play_audio_and_execute_associated_file, args=(key,)).start()

# ربط النافذة مع دالة الاستماع لضغطات المفاتيح
root.bind('<KeyPress>', on_key_press)

# تشغيل الواجهة الرسومية
root.mainloop()

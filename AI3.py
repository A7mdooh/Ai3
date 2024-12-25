import tkinter as tk
from tkinter import Canvas
import pygame
import keyboard
import threading

# إعداد مكتبة pygame للصوت
pygame.mixer.init()

# إنشاء نافذة Tkinter
root = tk.Tk()
root.title("برنامج التحدث بواجهة رسومية")

# إعداد النافذة بحيث يكون حجمها ثابتًا 300x300
root.geometry('300x300')  # تحديد حجم النافذة ليكون 300x300
root.resizable(False, False)  # منع المستخدم من تغيير حجم النافذة

# إعداد الواجهة الرسومية (العيون والفم)
canvas = Canvas(root, width=300, height=300, bg='black')
canvas.pack()

# تحديد حجم العيون والفم بحيث يتناسب مع النافذة الصغيرة
eye_radius = 30  # نصف قطر العين
left_eye = canvas.create_oval(75 - eye_radius, 60 - eye_radius,
                              75 + eye_radius, 60 + eye_radius, fill='white')
right_eye = canvas.create_oval(225 - eye_radius, 60 - eye_radius,
                               225 + eye_radius, 60 + eye_radius, fill='white')

# إضافة الفم (خط مستقيم يمكن تحريكه ليبدو كأنه يتحدث)
mouth_width = 150  # عرض الفم
mouth = canvas.create_line(75, 180, 225, 180, fill='red', width=10)


# دالة لتحريك الفم
def move_mouth(is_open):
    if is_open:
        canvas.coords(mouth, 75, 180, 225, 190)  # فتح الفم
    else:
        canvas.coords(mouth, 75, 180, 225, 180)  # غلق الفم
    root.update()  # تحديث الواجهة الرسومية بشكل دوري


# دالة لتشغيل الصوت وتحريك الفم
def play_audio_with_mouth(audio_file):
    try:
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # الآن سنقوم بتحديث الفم في الخيط الرئيسي عبر `after`
        def update_mouth():
            move_mouth(True)  # فتح الفم
            root.after(100, lambda: move_mouth(False))  # غلق الفم بعد فترة قصيرة

        root.after(50, update_mouth)  # تشغيل التحديثات في الخيط الرئيسي

    except pygame.error as e:
        print(f"خطأ في تشغيل الملف الصوتي: {e}")


# دالة للتعامل مع ضغطات لوحة المفاتيح
def listen_for_keys():
    # التحقق من ضغطات المفاتيح
    if keyboard.is_pressed('shift') and keyboard.is_pressed('q'):
        root.destroy()  # إغلاق البرنامج عند الضغط على Shift + Q

    # تصغير البرنامج إلى نافذة أصغر على شكل مربع عند الضغط على Shift + M
    elif keyboard.is_pressed('shift') and keyboard.is_pressed('m'):
        # حساب الحجم المتناسب مع العيون والفم
        eye_radius_small = 30  # نصف قطر العين
        mouth_width_small = 150  # عرض الفم المتناسب مع العيون

        # حساب عرض وارتفاع النافذة بناءً على العيون والفم فقط
        new_width = (eye_radius_small * 2) + mouth_width_small  # عرض النافذة بناءً على العيون والفم
        new_height = (eye_radius_small * 2) + 100  # ارتفاع النافذة بناءً على العيون والفم

        # حساب موقع النافذة لتكون في وسط الشاشة
        new_x = (screen_width - new_width) // 2  # وسط الشاشة
        new_y = (screen_height - new_height) // 2  # وسط الشاشة

        # تصغير العيون والفم بناءً على الحجم الجديد للنافذة
        canvas.coords(left_eye, new_x + new_width * 0.25 - eye_radius_small, new_y + new_height * 0.2 - eye_radius_small,
                      new_x + new_width * 0.25 + eye_radius_small, new_y + new_height * 0.2 + eye_radius_small)
        canvas.coords(right_eye, new_x + new_width * 0.75 - eye_radius_small, new_y + new_height * 0.2 - eye_radius_small,
                      new_x + new_width * 0.75 + eye_radius_small, new_y + new_height * 0.2 + eye_radius_small)

        # تصغير الفم ليصبح مناسبًا مع العرض الجديد
        canvas.coords(mouth, new_x + new_width * 0.2, new_y + new_height * 0.6, new_x + new_width * 0.2 + mouth_width_small,
                      new_y + new_height * 0.6)  # تحديث الفم ليصبح أصغر

        # تصغير النافذة في وسط الشاشة
        root.geometry(f'{new_width}x{new_height}+{new_x}+{new_y}')
        root.attributes('-fullscreen', False)  # إيقاف وضع ملء الشاشة

    # إرجاع البرنامج إلى ملء الشاشة عند الضغط على Shift + F
    elif keyboard.is_pressed('shift') and keyboard.is_pressed('f'):
        root.attributes('-fullscreen', True)  # العودة لوضع ملء الشاشة

    # التعامل مع الضغطات مع زر Shift
    for key in 'abcdefghijklmnopqrstuvwxyz0123456789':
        if keyboard.is_pressed(key):
            # إذا كان Shift مضغوطًا، نستخدم الحروف الكبيرة
            audio_file = f'{key.upper()}.mp3' if keyboard.is_pressed('shift') else f'{key}.mp3'
            threading.Thread(target=play_audio_with_mouth, args=(audio_file,)).start()


# التحقق من ضغطات المفاتيح بشكل دوري
def check_keys_periodically():
    listen_for_keys()  # التحقق من ضغطات المفاتيح
    root.after(50, check_keys_periodically)  # التحقق من ضغطات المفاتيح بشكل دوري


# بدء التحقق من ضغطات المفاتيح بعد 50 مللي ثانية
root.after(50, check_keys_periodically)

# تشغيل الواجهة الرسومية
root.mainloop()

import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog, colorchooser
from moviepy.editor import VideoFileClip, ImageClip
import os

# Функция для удаления хромакея
def remove_chroma_key(video_path, bg_path, chroma_color):
    # Чтение видео
    clip = VideoFileClip(video_path)
    
    # Загрузка фонового изображения
    bg_image = cv2.imread(bg_path)
    
    # Определение размеров видео
    w, h = clip.size
    
    # Изменяем размер фона до размера видео
    bg_resized = cv2.resize(bg_image, (w, h))

    # Конвертируем фоновое изображение в RGB, так как OpenCV использует BGR
    bg_resized_rgb = cv2.cvtColor(bg_resized, cv2.COLOR_BGR2RGB)

    def process_frame(frame):
        # Конвертируем кадр из RGB в BGR для OpenCV обработки
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Преобразуем кадр в цветовое пространство HSV
        hsv_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        # Определяем диапазон для маскировки хромакея (по выбранному цвету)
        chroma_hsv = cv2.cvtColor(np.uint8([[chroma_color]]), cv2.COLOR_RGB2HSV)[0][0]
        lower_bound = np.array([chroma_hsv[0] - 10, 50, 50])
        upper_bound = np.array([chroma_hsv[0] + 10, 255, 255])

        # Создаем маску для удаления хромакея
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
        mask_inv = cv2.bitwise_not(mask)

        # Извлекаем передний план (объекты на видео)
        fg = cv2.bitwise_and(frame_bgr, frame_bgr, mask=mask_inv)

        # Извлекаем задний план
        bg = cv2.bitwise_and(bg_resized, bg_resized, mask=mask)

        # Совмещаем передний и задний планы
        final_frame_bgr = cv2.add(fg, bg)

        # Возвращаем кадр обратно в RGB формат для MoviePy
        final_frame_rgb = cv2.cvtColor(final_frame_bgr, cv2.COLOR_BGR2RGB)
        return final_frame_rgb

    # Применяем обработку ко всем кадрам
    processed_clip = clip.fl_image(process_frame)
    return processed_clip

# Функция для сохранения видео
def save_video(clip, output_path):
    clip.write_videofile(output_path, codec='libx264')

# Интерфейс с использованием Tkinter
def open_video():
    video_path = filedialog.askopenfilename(title="Выберите видео", filetypes=[("MP4 files", "*.mp4")])
    return video_path

def open_image():
    image_path = filedialog.askopenfilename(title="Выберите фоновое изображение", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    return image_path

def choose_color():
    color_code = colorchooser.askcolor(title="Выберите цвет хромакея")[0]
    if color_code:
        return tuple(map(int, color_code))

def start_processing():
    video_path = open_video()
    bg_path = open_image()
    chroma_color = choose_color()

    if video_path and bg_path and chroma_color:
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        processed_clip = remove_chroma_key(video_path, bg_path, chroma_color)
        save_video(processed_clip, output_path)
        open_folder(output_path)

def open_folder(path):
    folder = os.path.dirname(path)
    os.startfile(folder)

# Создаем интерфейс
root = Tk()
root.title("Видео с заменой фона")

# Кнопка для запуска обработки
process_button = Button(root, text="Загрузить видео и заменить фон", command=start_processing)
process_button.pack(pady=20)

# Запуск интерфейса
root.mainloop()


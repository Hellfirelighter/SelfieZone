import tkinter
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk, ImageGrab
import cv2
import mediapipe as mp
from datetime import datetime

app = tkinter.Tk()
app.title("SelfieZone")

frame = np.random.randint(0, 1, [480, 640, 3], dtype='uint8')
img = ImageTk.PhotoImage(Image.fromarray(frame))

window_image = tkinter.Label(app)
window_image.configure(image=img)   # this line to show placeholder for camera window
window_image.grid(row=0, column=0, columnspan=4, pady=5, padx=5)

global cam
cam = None
global img_path
img_path = ''
global dir_path
dir_path = ''


def on_start():
    global frame
    global cam
    button_1['state'] = DISABLED
    button_3['state'] = DISABLED
    BG_COLOR = (192, 192, 192)  # gray
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    mp_selfie_segmentation = mp.solutions.selfie_segmentation

    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
        if img_path == '':
            bg_image = None   # None = BG_COLOR
        else:
            bg_image = cv2.imread(img_path)
            w = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
            dim = (int(w), int(h))
            bg_image = cv2.resize(bg_image, dim, cv2.INTER_AREA)

        while cam.isOpened():
            success, image = cam.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = selfie_segmentation.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
            if bg_image is None:
                bg_image = np.zeros(image.shape, dtype=np.uint8)
                bg_image[:] = BG_COLOR
            output_image = np.where(condition, image, bg_image)

            frame = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
            img_update = ImageTk.PhotoImage(Image.fromarray(frame))
            window_image.configure(image=img_update)
            window_image.image = img_update
            window_image.update()


def on_stop():
    global cam
    if cam:
        cam.release()
    cv2.destroyAllWindows()
    app.destroy()


def on_photo():
    global dir_path
    x = window_image.winfo_rootx()
    y = window_image.winfo_rooty()
    w = window_image.winfo_width()
    h = window_image.winfo_height()
    save_img = ImageGrab.grab(bbox=(x, y, w+x, h+y))
    if dir_path != '':
        save_img.save(f"{dir_path}/picture_{datetime.now().strftime('%H_%M_%S')}.png")
    else:
        save_img.save(f"picture_{datetime.now().strftime('%H_%M_%S')}.png")


def on_video():
    pass


def on_bg_select():
    global img_path
    f_types = [('PNG Files', '*.png'), ('Jpg Files', '*.jpg'), ('BMP Files', '*.bmp')]
    img_path = tkinter.filedialog.askopenfilename(filetypes=f_types)
    entry_1_text.set(img_path)


def on_dir_select():
    global dir_path
    dir_path = tkinter.filedialog.askdirectory(mustexist=True)
    entry_2_text.set(dir_path)


# row 1-2
label_1 = tkinter.Label(app, text='Choose background picture...')
label_1.grid(row=1, column=0, pady=0, padx=5)
entry_1_text = StringVar()
entry_1 = tkinter.Entry(app, bd=2, textvariable=entry_1_text, state=DISABLED)
entry_1.grid(row=2, column=0, pady=0, padx=5, columnspan=3, sticky='NSEW')
button_1 = tkinter.Button(app, text='...', command=on_bg_select)
button_1.grid(row=2, column=3, pady=0, padx=5, sticky='NSEW')
# row 3-4
label_1 = tkinter.Label(app, text='Select directory to save files...')
label_1.grid(row=3, column=0, pady=0, padx=5)
entry_2_text = StringVar()
entry_2 = tkinter.Entry(app, bd=2, textvariable=entry_2_text, state=DISABLED)
entry_2.grid(row=4, column=0, pady=0, padx=5, columnspan=3, sticky='NSEW')
button_2 = tkinter.Button(app, text='...', command=on_dir_select)
button_2.grid(row=4, column=3, pady=0, padx=5, sticky='NSEW')
# row 5
button_3 = tkinter.Button(app, text="Start", command=on_start, height=2, width=20)
button_3.grid(row=5, column=0, pady=10, padx=5)
button_4 = tkinter.Button(app, text="Photo", command=on_photo, height=2, width=20)
button_4.grid(row=5, column=1, pady=10, padx=5)
button_5 = tkinter.Button(app, text="Video", command=on_video, height=2, width=20, state=DISABLED)
button_5.grid(row=5, column=2, pady=10, padx=5)
button_6 = tkinter.Button(app, text="Exit", command=on_stop, height=2, width=20)
button_6.grid(row=5, column=3, pady=10, padx=5)

app.protocol("WM_DELETE_WINDOW", on_stop)
app.mainloop()

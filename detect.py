from ultralytics import YOLO
import cv2
import time
import numpy as np
import cvutils as cu

from pynput import mouse
import win32gui
from windowcapture import WindowCapture

WindowCapture.list_window_names()
window_name = None


def get_windowd_on_click(x, y, button, pressed):
    # Get the retuned window name
    global window_name
    if pressed:
        _w = win32gui.WindowFromPoint((x, y))
        # _w = win32gui.GetActiveWindow()
        print(hex(_w))
        window_name = win32gui.GetWindowText(_w)
        print(f"Window {_w} name: {window_name}")
        while _w != 0:
            window_name = win32gui.GetWindowText(_w)
            print(f"Parent {hex(_w)} name: {window_name}")
            _w = win32gui.GetParent(_w)

        print(f"Top level {hex(_w)} name: {window_name}")
        return False


# Create a mouse listener
with mouse.Listener(on_click=get_windowd_on_click) as listener:
    listener.join()

# initialize the WindowCapture class
windowCap = WindowCapture(window_name)

# Log detections etc to console
consoledebug = True

# Save model to folder for project so this is not downloaded avery time
model = YOLO("./yolo-weights/yolov8n.pt")

classNames = [
    "person",
    "bicycle",
    "car",
    "motorbike",
    "aeroplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "backpack",
    "umbrella",
    "handbag" "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "sofa",
    "pottedplant",
    "bed",
    "diningtable",
    "toilet",
    "tvmonitor",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
]

windowCap.start()

while True:
    results = []
    if windowCap.screenshot is None:
        continue

    image = None
    img = windowCap.screenshot

    results = model(img, stream=False, verbose=consoledebug)

    for r in results:
        tic = time.perf_counter_ns()
        image = cu.imageOverlay(
            img,
            r.boxes,
            classNames,
            confidenceThreshold=0.6,
            text_offset_x=20,
            text_offset_y=10,
            thickness=1,
            background_RGBA=(149, 146, 202, 128),
            text_RGBA=(198, 198, 198, 245),
        )
        toc = time.perf_counter_ns()
        if consoledebug:
            print(f"Draw image overlay in {(toc-tic)/1000000:0.4f} ms")

        if image:
            cv2.imshow("Image", cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR))
        else:
            cv2.imshow("Image", cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))

    if cv2.waitKey(1) & 0xFF == ord("q"):
        windowCap.stop()
        cv2.destroyAllWindows()
        break

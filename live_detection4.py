import cv2
import numpy as np
import pyttsx3
import pygetwindow as gw
import pyautogui
import time
import win32gui
import win32con
import win32api
from ultralytics import YOLO

# ✅ Load your trained YOLOv8 model
model_path = os.getenv("MODEL_PATH", "models/best.pt")
model = YOLO(model_path)

# ✅ Initialize text-to-speech engine
engine = pyttsx3.init()

# ✅ Function to find the game window
def get_game_window(title="League of Legends"):
    """Finds the game window by title."""
    for window in gw.getWindowsWithTitle(title):
        if window.isActive or window.isMaximized:
            return window
    return None

# ✅ Function to capture the game window
def capture_game_window(window):
    """Captures the game screen as an image."""
    left, top, width, height = window.left, window.top, window.width, window.height
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    frame = np.array(screenshot)
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), (left, top, width, height)

# ✅ Speech cooldown settings
last_speech_time = time.time()
last_detected_objects = set()

# ✅ Create an always-on-top window overlay
cv2.namedWindow("Game Detection", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Game Detection", cv2.WND_PROP_TOPMOST, 1)

while True:
    # 🎮 Find the game window
    game_window = get_game_window()
    if not game_window:
        print("⚠ Game window not found! Make sure the game is running.")
        time.sleep(2)
        continue

    # 🎥 Capture the game screen
    frame, (left, top, width, height) = capture_game_window(game_window)

    # 📏 Resize frame to YOLO input size (640x640)
    resized = cv2.resize(frame, (640, 640))

    # 🔍 Run YOLO detection
    results = model(resized, conf=0.3, iou=0.5)  # Adjusted confidence threshold

    detected_objects = set()
    for result in results:
        if not result.boxes:
            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy().astype(int)

        for box, conf, class_id in zip(boxes, confs, class_ids):
            x1, y1, x2, y2 = map(int, box)

            # 🔄 Scale bounding box coordinates back to game window size
            x1 = int(x1 * (width / 640) + left)
            y1 = int(y1 * (height / 640) + top)
            x2 = int(x2 * (width / 640) + left)
            y2 = int(y2 * (height / 640) + top)

            # 🏷 Get class name
            class_name = model.names.get(class_id, f"Class {class_id}")
            detected_objects.add(class_name)

            # 📌 Draw bounding box & label on frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{class_name} ({conf:.2f})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 🎤 Announce new objects detected
    current_time = time.time()
    if detected_objects != last_detected_objects and current_time - last_speech_time > 3:
        for obj in detected_objects:
            if obj.lower() in ["enemy", "opponent", "battle"]:
                engine.say("Fight has broken out!")
            elif obj.lower() in ["power up", "buff", "boost"]:
                engine.say("Power-up detected!")
            else:
                engine.say(f"{obj} detected")

        engine.runAndWait()
        last_speech_time = current_time
        last_detected_objects = detected_objects.copy()

    # 🟢 Show the frame with bounding boxes
    cv2.imshow("Game Detection", frame)

    # 🛠 Set window transparency (semi-transparent effect)
    hwnd = win32gui.FindWindow(None, "Game Detection")
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                           win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 200, win32con.LWA_ALPHA)

    # 🛑 Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 🔄 Cleanup
cv2.destroyAllWindows()

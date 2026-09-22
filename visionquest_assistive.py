import os
import time
import cv2
import numpy as np
import pyttsx3
import pygetwindow as gw
import pyautogui
from ultralytics import YOLO

# Optional XInput for Controller Haptic Feedback (Xbox / Generic gamepad)
try:
    import XInput
    HAS_XINPUT = True
except ImportError:
    HAS_XINPUT = False

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
MODEL_PATH = os.getenv("MODEL_PATH", "models/best.pt")
CONFIDENCE_THRESHOLD = 0.35
COOLDOWN_SECONDS = 2.5

# Initialize Speech Engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)  # slightly faster for real-time gaming

# ==========================================
# 🎮 HAPTIC FEEDBACK CONTROLLER
# ==========================================
def trigger_haptic(left_motor=0.0, right_motor=0.0, duration=0.3):
    """Triggers rumble on connected game controller if available."""
    if not HAS_XINPUT:
        return
    try:
        connected = XInput.get_connected()
        if connected[0]:
            XInput.set_vibration(0, left_motor, right_motor)
            time.sleep(duration)
            XInput.set_vibration(0, 0.0, 0.0)
    except Exception:
        pass

# ==========================================
# 🧭 SPATIAL DIRECTION CALCULATOR
# ==========================================
def get_spatial_position(box_center_x, box_center_y, screen_w, screen_h):
    """
    Translates pixel coordinates into directional audio positions:
    e.g., 'left', 'center', 'right', 'top left', 'bottom right'
    """
    horizontal_third = screen_w / 3.0
    vertical_third = screen_h / 3.0

    # Horizontal sector
    if box_center_x < horizontal_third:
        h_pos = "left"
    elif box_center_x > 2 * horizontal_third:
        h_pos = "right"
    else:
        h_pos = "center"

    # Vertical sector
    if box_center_y < vertical_third:
        v_pos = "top"
    elif box_center_y > 2 * vertical_third:
        v_pos = "bottom"
    else:
        v_pos = ""

    if v_pos and h_pos != "center":
        return f"{v_pos} {h_pos}"
    elif v_pos and h_pos == "center":
        return f"{v_pos}"
    return h_pos

# ==========================================
# 🖥️ WINDOW FINDER & CAPTURE
# ==========================================
def get_game_window(title="League of Legends"):
    for window in gw.getWindowsWithTitle(title):
        if window.isActive or window.isMaximized:
            return window
    return None

def capture_game_window(window):
    left, top, width, height = window.left, window.top, window.width, window.height
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    frame = np.array(screenshot)
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), (left, top, width, height)

# ==========================================
# 🚀 MAIN LOOP
# ==========================================
def main():
    print("=" * 60)
    print(" VisionQuest: Assistive Vision & Spatial Guidance Engine")
    print("=" * 60)
    print(f"Loading YOLO Model from: {MODEL_PATH}")

    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"⚠️ Model load failed ({e}). Running in mock mode.")
        model = None

    last_speech_time = time.time()
    last_spoken_state = {}

    cv2.namedWindow("VisionQuest Assistive HUD", cv2.WINDOW_NORMAL)

    while True:
        game_window = get_game_window()
        if not game_window:
            print("Searching for game window ('League of Legends')...")
            time.sleep(2)
            continue

        frame, (left, top, width, height) = capture_game_window(game_window)
        resized = cv2.resize(frame, (640, 640))

        detected_entities = []

        if model:
            results = model(resized, conf=CONFIDENCE_THRESHOLD, iou=0.5)
            for result in results:
                if not result.boxes:
                    continue

                boxes = result.boxes.xyxy.cpu().numpy()
                confs = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy().astype(int)

                for box, conf, class_id in zip(boxes, confs, class_ids):
                    # Scale back to original window dimensions
                    x1 = int(box[0] * (width / 640.0) + left)
                    y1 = int(box[1] * (height / 640.0) + top)
                    x2 = int(box[2] * (width / 640.0) + left)
                    y2 = int(box[3] * (height / 640.0) + top)

                    center_x = (x1 + x2) / 2.0 - left
                    center_y = (y1 + y2) / 2.0 - top

                    class_name = model.names.get(class_id, f"Object-{class_id}")
                    position_label = get_spatial_position(center_x, center_y, width, height)

                    # Estimate proximity based on bounding box height relative to screen
                    box_height_ratio = (y2 - y1) / float(height)
                    proximity = "close" if box_height_ratio > 0.15 else "far"

                    detected_entities.append({
                        "name": class_name,
                        "position": position_label,
                        "proximity": proximity,
                        "box": (x1, y1, x2, y2),
                        "conf": conf
                    })

                    # Draw on HUD overlay
                    is_enemy = "enemy" in class_name.lower()
                    color = (0, 0, 255) if is_enemy else (0, 255, 0)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{class_name} [{position_label}]", (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # 🔊 Assistive Audio & Haptic Feedback Logic
        current_time = time.time()
        if detected_entities and (current_time - last_speech_time > COOLDOWN_SECONDS):
            # Prioritize threats (enemies, towers)
            enemies = [e for e in detected_entities if "enemy" in e["name"].lower()]
            targets = enemies if enemies else detected_entities

            primary_target = targets[0]
            cue_text = f"{primary_target['name']} on your {primary_target['position']}"

            if primary_target['proximity'] == "close":
                cue_text += ", incoming!"
                # Trigger controller vibration for danger
                trigger_haptic(left_motor=0.8, right_motor=0.8, duration=0.2)

            print(f"🎙️ Spatial Cue: '{cue_text}'")
            engine.say(cue_text)
            engine.runAndWait()

            last_speech_time = current_time

        cv2.imshow("VisionQuest Assistive HUD", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

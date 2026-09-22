# VisionQuest: Multi-Modal Assistive Vision & Spatial Guidance Engine for Gamers

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-green.svg)](https://github.com/ultralytics/ultralytics)
[![Accessibility](https://img.shields.io/badge/Focus-Accessibility%20Tech-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

**VisionQuest** is an assistive gaming engine engineered to grant visually impaired and low-vision players real-time situational awareness in fast-paced real-time strategy games (specifically *League of Legends*).

Rather than serving as a passive object detector, VisionQuest translates complex visual scenes into **directional spatial audio cues**, **proximity/threat alerts**, and **tactile haptic controller vibrations** with sub-200ms processing latency.

---

## 🌟 Key Features

- **Spatial Directional Audio (`Left`, `Center`, `Right`, `Top`, `Bottom`):**
  Translates bounding box coordinates into intuitive spatial announcements (e.g., *"enemy-tower on your top right"*).
- **Proximity & Threat Alerts ("Incoming!" Detection):**
  Monitors bounding box dimension ratios dynamically. If an enemy entity closes distance, it issues an urgent warning (*"enemy-melee-minion on your center, incoming!"*).
- **Haptic Rumble Feedback (Gamepads):**
  Integrates with `XInput` to trigger physical vibration pulses on Xbox/PC game controllers when danger enters critical range.
- **Threat Prioritization Engine:**
  Filters out visual noise (e.g. ambient minions) to announce high-priority targets (enemy champions, towers, threats) first.
- **Semi-Transparent Win32 HUD Overlay:**
  Draws non-intrusive bounding boxes and spatial labels directly over the game window using native Windows APIs.
- **Low-Latency Screen Ingestion:**
  Automated game window discovery and viewport capture via `pygetwindow` and `pyautogui`.

---

## 🏗️ System Architecture

```
                 [ Active Game Window (League of Legends) ]
                                     │
                           (Win32 / pyautogui)
                                     ▼
                      [ Real-Time Frame Capture ]
                                     │
                             (Resize 640x640)
                                     ▼
                    [ YOLOv8 Custom Inference Engine ]
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
   [ Spatial Audio ]      [ Threat Prioritizer ]      [ Haptic Engine ]
   Computes Left/Right    Filters friendly units;     Triggers physical
   & Top/Bottom audio     prioritizes enemies         rumble on gamepads
   cues via pyttsx3       & incoming threats          via XInput API
```

---

## 📊 Dataset & Model Specification

- **Classes (12):**
  - **Allies:** `ally-tower`, `ally-inhibitor`, `ally-melee-minion`, `ally-caster-minion`, `ally-siege-minion`, `ally-nexus`
  - **Enemies:** `enemy-tower`, `enemy-inhibitor`, `enemy-melee-minion`, `enemy-caster-minion`, `enemy-siege-minion`, `enemy-nexus`
- **Dataset Size:** 2,500+ annotated gameplay frames hosted on Roboflow.
- **Inference Parameters:** `conf=0.35`, `iou=0.50` for balanced precision and real-time inference speed.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Mrinalinigupta/visionquest-assistive-detector.git
cd visionquest-assistive-detector
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run VisionQuest Engine
Ensure the game window (*League of Legends*) is running or visible:
```bash
python visionquest_assistive.py
```
*(Press `q` on the overlay window to exit).*

---

## 📦 Dependencies (`requirements.txt`)

```text
ultralytics>=8.0.0
opencv-python>=4.8.0
numpy>=1.23.0
pyttsx3>=2.90
pygetwindow>=0.0.9
pyautogui>=0.9.54
pywin32>=306
XInput-Python>=0.3.0
```

---

## 🎯 Engineering & Social Impact

Traditional gaming HUDs rely overwhelmingly on visual sightlines, effectively excluding visually impaired gamers from competitive esports. VisionQuest bridges this gap by decoupling perception from vision—transforming visual telemetry into multi-modal auditory and tactile feedback in real-time.

---

## 📄 License
This project is licensed under the MIT License.

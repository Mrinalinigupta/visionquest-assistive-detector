# VisionQuest: Complete Project Guide & Interview Playbook

> **Target Project:** VisionQuest – Real-Time Assistive Vision & Spatial Guidance Engine for Gamers  
> **Tech Stack:** Python 3.9+, YOLOv8 (Ultralytics), OpenCV, pyttsx3 (TTS), pygetwindow, pyautogui, pywin32, XInput-Python  
> **Core Domain:** Computer Vision, Accessibility Tech, Real-Time Audio-Tactile Feedback, Game Streaming Pipeline  

---

## 1. The Core Vision: Why Did We Build This?

### The Problem
Traditional esports and real-time strategy (RTS) games like *League of Legends* are **heavily visual**. Gamers must track mini-maps, enemy movements, turret ranges, and minion waves simultaneously. For low-vision or visually impaired gamers, this visual clutter creates an impassable barrier to entry.

### The Solution (VisionQuest)
VisionQuest decouples game perception from sight. It acts as an **AI co-pilot**:
1. It captures gameplay frames in real-time.
2. It detects in-game entities using fine-tuned **YOLOv8**.
3. It converts spatial coordinates into **directional audio callouts** (*"Enemy tower on your top right"*).
4. It issues **proximity alerts** (*"Enemy minion incoming!"*).
5. It triggers **haptic controller vibrations** on physical gamepads when danger enters critical range.

---

## 2. Chronological Flow: "How I Built It From Scratch" (Step-by-Step)

If an interviewer asks: *"Take me through how you engineered VisionQuest from start to finish"*, narrate these 5 distinct phases:

```
[Phase 1: Dataset & Annotation] ──> [Phase 2: YOLOv8 Model Training] ──> [Phase 3: Screen Capture Pipeline]
                                                                                     │
[Phase 5: Real-Time Testing & Optimization] <── [Phase 4: Spatial Audio & Haptic Feedback]
```

### Phase 1: Data Collection & Annotation (Roboflow)
1. Collected gameplay recordings of *League of Legends* across various map conditions, champions, and team fights.
2. Extracted over **2,500 representative frames**.
3. Uploaded frames to **Roboflow** and annotated bounding boxes across **12 distinct classes**:
   - **Allies:** `ally-tower`, `ally-inhibitor`, `ally-melee-minion`, `ally-caster-minion`, `ally-siege-minion`, `ally-nexus`
   - **Enemies:** `enemy-tower`, `enemy-inhibitor`, `enemy-melee-minion`, `enemy-caster-minion`, `enemy-siege-minion`, `enemy-nexus`
4. Split dataset: 70% Train, 20% Validation, 10% Test. Applied augmentations (contrast adjustments, slight horizontal shifts) to simulate dynamic lighting.

### Phase 2: Model Selection & Fine-Tuning
1. Selected **YOLOv8 Nano/Small (`yolov8n.pt` / `yolov8s.pt`)** as the backbone.
2. Fine-tuned the model for 50 epochs using PyTorch and the Ultralytics framework.
3. Exported the fine-tuned weights (`best.pt`) achieving high recall on enemy structures and champions with sub-30ms raw inference latency on GPU.

### Phase 3: Screen Ingestion Pipeline (Viewport Capture)
1. Used `pygetwindow` to dynamically search for the game window process (`"League of Legends"`).
2. Extracted viewport bounds (`left`, `top`, `width`, `height`).
3. Captured frames via `pyautogui.screenshot()` and converted RGB buffers into OpenCV-compatible BGR arrays (`np.array()` + `cv2.cvtColor`).
4. Downsampled frames to **640x640** (the input dimension expected by YOLOv8) to maintain low latency.

### Phase 4: Spatial Direction Engine, Proximity & Haptics
1. **Coordinate Rescaling:** Scaled normalized 640x640 bounding boxes back to native monitor viewport pixels.
2. **Spatial Sectoring:** Divided the screen into a 3x3 grid (Left, Center, Right × Top, Middle, Bottom) based on the entity's centroid $(x_c, y_c)$.
3. **Proximity Ratio:** Calculated bounding box height relative to total screen height. If $\frac{\text{box\_height}}{\text{screen\_height}} > 0.15$, the object is flagged as **"Close / Incoming"**.
4. **Debounced Speech Synthesizer (`pyttsx3`):** Implemented a 2.5-second speech cooldown so audio cues don't overlap into unintelligible noise.
5. **Gamepad Rumble (`XInput`):** Integrated native controller vibration triggers for high-threat entities within close proximity.

### Phase 5: HUD Overlay & Win32 Integration
1. Created an OpenCV window set to `WND_PROP_TOPMOST` (always-on-top).
2. Applied Windows API calls (`win32gui`, `win32con`) to enable `WS_EX_LAYERED` transparency, rendering bounding boxes without blocking game controls.

---

## 3. Technology Choices: "Why Did We Use X Instead of Y?"

| Technology | Why We Used It | Alternative Considered | Why Alternative Was Rejected |
|---|---|---|---|
| **YOLOv8 (Ultralytics)** | Single-stage detector with exceptional speed/accuracy tradeoff. Native PyTorch export and anchor-free design. | Faster R-CNN / SSD | Faster R-CNN is dual-stage and too slow (>150ms latency) for 60fps real-time gaming. SSD has lower mAP on small objects like minions. |
| **pyttsx3** | Completely **offline** Text-To-Speech engine. Zero API network latency, free, and lightweight. | Google Cloud TTS / ElevenLabs | Cloud APIs add 200–500ms network round-trip delay, require internet connectivity, and cost money per request. |
| **pygetwindow + pyautogui** | Interacts cleanly with native Windows desktop APIs; targets active game window without needing game-internal memory hooks. | Game Internal Memory Reading / DLL Injection | Memory hooking violates Riot Games' anti-cheat (Vanguard) and results in permanent account bans. VisionQuest is 100% non-invasive (external screen reading). |
| **XInput-Python** | Direct access to Xbox/PC gamepad dual rumble motors (left low-frequency heavy rumble, right high-frequency buzz). | Custom Arduino vibrator | Requires players to buy custom external hardware. Gamepads are already standard accessibility peripherals. |
| **OpenCV (`cv2`)** | Industry-standard C++ backed library for fast array manipulation, resizing, and bounding-box drawing. | PIL (Pillow) | PIL is pure Python and significantly slower for real-time 30fps image array conversions. |

---

## 4. System Architecture & Data Flow

```
                      [ Active Game Window ]
                                │
                    (Win32 / pygetwindow API)
                                ▼
                    [ Screen Viewport Capture ]
                                │
                   (pyautogui ──> cv2.cvtColor)
                                ▼
                       [ Resize to 640x640 ]
                                │
                     (Inference: conf=0.35)
                                ▼
                     [ YOLOv8 Model (best.pt) ]
                                │
           ┌────────────────────┴────────────────────┐
           ▼                                         ▼
   [ Visual Pipeline ]                     [ Assistive Pipeline ]
   • Scale boxes to viewport               • Threat Prioritizer (Filter allies)
   • Draw color-coded rectangles           • Compute Centroid (x_c, y_c)
   • Win32 Alpha Transparency Overlay      • Spatial Calculator (Left/Right/Top)
                                           • Proximity Check (box_height / H > 0.15)
                                                     │
                                       ┌─────────────┴─────────────┐
                                       ▼                           ▼
                             [ Audio Speech (TTS) ]       [ Gamepad Haptics ]
                             "Enemy tower on top right"   XInput Rumble Pulse
```

---

## 5. Top Interview Questions & Model Answers

### Q1: "Walk me through VisionQuest. What is it, and what was your role?"
> **Model Answer:**  
> *"VisionQuest is an accessibility-focused computer vision engine designed to help visually impaired players navigate fast-paced real-time strategy games like League of Legends. Rather than just drawing bounding boxes, it converts real-time visual telemetry into **directional audio cues** and **haptic controller feedback** with sub-200ms latency.*  
> *I worked on the end-to-end pipeline: collecting and annotating 2,500+ game frames on Roboflow, fine-tuning YOLOv8 for 12 ally/enemy classes, building the non-invasive screen-capture pipeline, and developing the spatial audio engine with dynamic threat prioritization."*

---

### Q2: "Why did you choose an external computer vision approach instead of reading game memory directly?"
> **Model Answer:**  
> *"Competitive multiplayer games like League of Legends enforce strict anti-cheat systems like Riot Vanguard. Any attempt to read process memory or inject DLLs leads to instant, permanent bans. By adopting an external computer vision pipeline using `pygetwindow` and `pyautogui`, VisionQuest operates purely on the visual layer—making it 100% compliant, safe, and portable across any game without touching game memory."*

---

### Q3: "How does the spatial direction calculation work mathematically?"
> **Model Answer:**  
> *"When YOLO detects a bounding box `[x1, y1, x2, y2]`, we first map the normalized coordinates back to the game window's native resolution. Then we calculate the centroid:*  
> $$x_c = \frac{x_1 + x_2}{2}, \quad y_c = \frac{y_1 + y_2}{2}$$  
> *We partition the viewport into horizontal and vertical thirds ($W/3$ and $H/3$). If $x_c < W/3$, it's **Left**; if $x_c > 2W/3$, it's **Right**; otherwise, it's **Center**. Similarly, vertical thresholds determine **Top**, **Middle**, or **Bottom**. Combining them yields intuitive directions like 'top left' or 'bottom right'."*

---

### Q4: "How did you handle audio spam when 20 minions are on screen at once?"
> **Model Answer:**  
> *"In an RTS game, 10–20 minions can spawn simultaneously. If every detection triggered speech, the user would experience severe cognitive overload. We solved this with two mechanisms:*  
> 1. ***Threat Prioritization:*** *We classify entities into allies vs. enemies. Enemy threats and defensive towers are pushed to the front of the queue, ignoring friendly minions.*  
> 2. ***Temporal Debounce / Cooldown:*** *We implemented a strict 2.5-second cooldown timer on the TTS engine (`pyttsx3`), ensuring only the most urgent, state-changing cue is vocalized."*

---

### Q5: "How does proximity detection work without depth cameras (RGB-D)?"
> **Model Answer:**  
> *"Since we only have a 2D screen capture without depth sensors (monocular vision), we infer proximity through **perspective bounding-box scaling**. In games with fixed isometric cameras, objects physically closer to the viewport render with larger pixel heights. We compute the ratio of the bounding box height to the total viewport height:*  
> $$\text{Ratio} = \frac{y_2 - y_1}{H_{\text{viewport}}}$$  
> *When this ratio exceeds our threshold (0.15), the system flags the entity as 'close/incoming', triggering the urgent voice warning and gamepad rumble vibration."*

---

### Q6: "What were the primary latency bottlenecks and how did you optimize them?"
> **Model Answer:**  
> *"Real-time assistive tech requires sub-250ms end-to-end latency. We optimized three bottlenecks:*  
> 1. ***Frame capture resolution:*** *Native 1080p/4K screen capture creates huge image arrays that choke Python. We immediately downsample the captured frame to 640x640 before sending it to YOLO.*  
> 2. ***Offline TTS:*** *We explicitly avoided cloud APIs (like ElevenLabs or AWS Polly) which introduce 300ms+ network round-trips. We used `pyttsx3` which interfaces natively with Windows SAPI5 offline.*  
> 3. ***Model selection:*** *We prioritized YOLOv8 Nano/Small weights over heavier architectures, keeping raw GPU inference time under 25ms per frame."*

---

### Q7: "If you had 2 more weeks, what would you improve?"
> **Model Answer:**  
> *"I would implement three major enhancements:*  
> 1. ***True Stereo Pan Audio:*** *Instead of only speaking 'Left' or 'Right', use PyOpenAL or 3D audio libraries to physically pan sound into the user's left or right headphone earpiece.*  
> 2. ***Kalman Filter Object Tracking (ByteTrack):*** *Track entities across consecutive frames so the system can measure velocity vectors and predict enemy movement trajectories before they hit.*  
> 3. ***Direct GPU Frame Ingestion (DXGI Desktop Duplication):*** *Replace `pyautogui` with the Windows Desktop Duplication API (DXGI) to capture frames directly into VRAM, cutting capture latency from ~40ms to under 5ms."*

---

## 6. Elevator Pitch (Memorize This!)

> *"For my major AI project, I built **VisionQuest**—a multi-modal assistive engine that empowers visually impaired gamers to play competitive games like League of Legends. Using fine-tuned **YOLOv8** on 2,500+ annotated frames, the system ingests live gameplay without invasive memory hooks, computes 2D spatial coordinate sectors, and delivers **directional speech cues** and **gamepad haptic vibrations** with sub-200ms latency to provide true situational awareness."*

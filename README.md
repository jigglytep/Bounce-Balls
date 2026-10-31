# Interactive Projection-Mapped Plinko (Halloween Edition)

An interactive, mixed-reality physics installation that turns physical colored masking tape on a wall or board into real-time digital obstacles. Using a projector and a webcam, falling Halloween-themed sprites bounce, roll, and chime across user-created tape platforms in real time.

---

## Credits & Attribution

This project is based on the original **Interactive Bouncing Ball Installation** created by **Andrew Chao**:

- **Original Creator:** Andrew Chao ([rewchao on Instructables](https://www.instructables.com/member/rewchao/) / `andrewchao7000@gmail.com`)
- **Instructables Guide:** [Interactive Bouncing Ball Installation](https://www.instructables.com/Interactive-Bouncing-Ball-Installation/) (Grand Prize Winner, *Make It Bounce Contest*)

Thank you to Andrew Chao for designing and sharing the original computer-vision projection mapping and 2D physics architecture!

---

## Description & Features

This installation combines computer vision (**OpenCV**), 2D rigid-body physics (**Pymunk**), graphics rendering (**Pygame**), and procedural audio synthesis (**NumPy / Pygame Mixer**) to create an interactive wall-sized Plinko board:

1. **Real-Time Tape Tracking (`cv2_utils.py`):** A webcam monitors the projection area. Using perspective homography mapping and HSV color masking, strips of colored masking tape applied to the wall are converted into polygon collision boundaries every few frames.
2. **2D Physics Simulation (`pygame_utils.py`):** Virtual objects spawn at the top of the projection and fall under gravity, colliding and bouncing realistically off the physical tape obstacles.
3. **Halloween Visual Theme (`pygame_utils.py`):**
   - Procedurally drawn Halloween falling characters: **Pumpkins**, **Witch Hats**, **Ghosts**, **Spiders**, **Candy Corn**, **Black Cats**, **Bubbling Cauldrons**, and **Wrapped Candies**, complete with soft neon glows and physics-driven rotation.
   - Festive Halloween pennant bunting along the top edge and purple/orange platform overlays.
   - Switchable **Warm Cream** background (for optimal webcam lighting on the tape) and **Cozy Twilight** dark mode.
4. **Musical "Plink" Audio (`pyo_utils.py`):** Collisions trigger synthesized pentatonic xylophone/chime notes (`C5`–`A6`) with impact-sensitive volume and per-ball cooldowns.

---

## Hardware & Supplies Required

- **Computer** running Linux (recommended for automatic V4L2 USB camera detection), Windows, or macOS
- **Projector** aimed at a flat wall, whiteboard, or foam board (configured as an extended secondary display at `1920x1080`, or primary display)
- **External USB Webcam** pointed at the entire projected area
- **Colored Masking / Painter's Tape** in a bright, high-contrast color (e.g., green, blue, or pink) that stands out against your projection surface

---

## Installation Instructions

1. **Clone or download the repository:**
   ```bash
   cd /home/lev/plinko
   ```

2. **Create and activate a Python virtual environment (optional but recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Core runtime dependencies: `opencv-python`, `numpy`, `pygame`, `pymunk`)*

4. **Configure display resolution (optional):**
   Open `Main.py` and verify that `pygame_width` and `pygame_height` match your projector's resolution (default is `1920`x`1080`):
   ```python
   pygame_width = 1920
   pygame_height = 1080
   platform_update_frequency = 5  # Updates tape polygons once every X frames
   ```

---

## Directions: How to Set Up, Calibrate & Play

### Step 1: Position Hardware
1. Aim your projector at a flat surface (wall or board) and connect it to your computer. If connected as a secondary monitor, the game window automatically opens on the secondary display.
2. Mount or tripod-position your USB webcam so the entire projected rectangle is clearly visible inside the camera frame.
3. Place one or two test strips of colored masking tape inside the projection area.

### Step 2: Launch the Program
```bash
python Main.py
```

### Step 3: Camera Selection
- On Linux, the program automatically scans `/sys/class/video4linux/video*` and selects an external USB webcam if one is connected.
- If automatic detection does not find a camera, a **"Choose Video Capture Device Number"** window will appear—adjust the `"Camera num"` slider and press **`ENTER`**.

### Step 4: Color Calibration (`Color Calibration Window`)
1. When the **Color Calibration Window** opens, the projector screen will turn bright white to illuminate the wall.
2. **Click directly on a piece of colored tape** inside the camera window to automatically sample its HSV color range, or manually adjust the `hue min/max`, `sat min/max`, and `val min/max` sliders.
3. Verify that your tape pieces are cleanly outlined in **bright green** with minimal background noise.
4. Press **`ENTER`** to save the color calibration.

### Step 5: Projection Mapping Calibration (`Projection Calibration Window`)
1. The **Projection Calibration Window** will prompt you to click the four corners of the projected display area in the camera feed in **clockwise order**:
   1. **UPPER LEFT** Corner
   2. **UPPER RIGHT** Corner
   3. **LOWER RIGHT** Corner
   4. **LOWER LEFT** Corner
2. A translucent pink polygon will preview your mapped projection region.
   - Press **`r`** at any time to clear the points and redo the selection.
   - Once all 4 corners are placed, press **`ENTER`** to confirm and launch the simulation.

### Step 6: Build & Play!
- Stick strips of colored tape onto the wall to create ramps, pegs, funnels, and baskets.
- Every few frames, the webcam detects any new, moved, or removed tape and updates the physics obstacles in real time!

---

## Keyboard Controls

While the main Pygame simulation window is focused, use the following keys:

| Key | Action |
| :---: | :--- |
| **`n`** | **Show / Hide Platforms:** Toggle drawing the digital purple/orange polygon overlays on top of your physical tape. |
| **`b`** | **Toggle Background Theme:** Switch between the **Warm Cream** background (best lighting for webcam tape tracking) and **Cozy Twilight** dark purple background. |
| **`c`** | **Recalibrate Tape Color:** Re-open the OpenCV Color Calibration Window if room lighting changes or you switch tape colors. |
| **`q`** | **Quit:** Close the simulation and release the webcam cleanly. |

---

## Project Structure

- **`Main.py`** — Entry point; configures projector screen dimensions (`pygame_width`, `pygame_height`) and polygon detection update frequency (`platform_update_frequency`).
- **`cv2_utils.py`** — OpenCV utilities for USB camera discovery, click-to-sample HSV color calibration, 4-corner homography perspective transformation, and contour-to-polygon extraction.
- **`pygame_utils.py`** — Main game loop, Pymunk 2D physics space (`Ball` and `Platform` classes), procedural Halloween sprites, collision handlers, and keyboard controls.
- **`pyo_utils.py`** — Procedural pentatonic chime sound generator (`pygame.mixer` + `numpy`) triggered on ball-to-platform bounces.
- **`requirements.txt`** — Python package dependencies.

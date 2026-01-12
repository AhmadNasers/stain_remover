# Click Boundary Detection System

A Python OpenCV application that allows users to define boundaries on camera feed and detect if mouse clicks are inside or outside these boundaries.

## Features

✅ **Boundary Definition Mode**
- Real-time camera feed display
- Mouse click to set boundary points
- Visual feedback with connecting lines
- Support for multiple boundaries
- Color-coded boundaries

✅ **Click Detection Mode**
- Real-time click detection on camera feed
- Visual and text feedback ("Inside" or "Outside")
- Automatic boundary loading
- Support for multiple boundaries

✅ **Rectangle Selector Mode** 🆕
- Click-and-drag rectangle creation (Windows-style)
- Drag corners to resize, drag center to move
- Rectangle must be inside boundary (validated in real-time)
- Live display of 4 corner coordinates
- Delete and adjust until perfect
- Returns coordinates (not saved)

✅ **Keyboard Controls**
- **Boundary Definition:**
  - `Click`: Add boundary point
  - `Enter/Space`: Save current boundary
  - `Backspace`: Remove last point
  - `C`: Clear all points
  - `Esc`: Exit application

- **Click Detection:**
  - `Click`: Test if point is inside/outside boundaries
  - `Esc`: Exit application

- **Rectangle Selector:**
  - `Click & Drag`: Draw rectangle
  - `Drag Corners`: Resize rectangle
  - `Drag Center`: Move rectangle
  - `D`: Delete rectangle
  - `Esc`: Finish and display coordinates

## Installation

1. Navigate to the project directory:
```bash
cd boundary_detector
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Define Boundaries

Run the boundary definition script:
```bash
python boundary_definition.py
```

1. The camera feed will open
2. Click on the video to add boundary points (minimum 3 points)
3. Press `Enter` or `Space` to save the current boundary
4. You can define multiple boundaries
5. Press `Esc` to exit

Your boundaries will be saved to `boundaries.txt`.

### Step 2: Test Click Detection

Run the click detection script:
```bash
python click_detection.py
```

1. The camera feed will open with your saved boundaries displayed
2. Click anywhere on the video
3. The system will display whether your click was "INSIDE" or "OUTSIDE" the boundaries
4. If inside, it will show which boundary was clicked
5. Press `Esc` to exit

### Step 3: Select Rectangle Inside Boundary (NEW!)

Run the rectangle selector script:
```bash
python rectangle_selector.py
```

1. The camera feed will open with your saved boundaries displayed
2. **Click and drag** to create a rectangle (like selecting in Windows)
3. The rectangle must be completely inside a boundary
4. **Drag corners** to resize the rectangle
5. **Drag center** to move the rectangle
6. Press `D` to delete the rectangle
7. Press `Esc` to finish - the four corner coordinates will be displayed
8. Coordinates are shown in real-time on screen and printed to console

## File Structure

```
boundary_detector/
├── boundary_definition.py    # Define and save boundaries
├── click_detection.py        # Detect clicks inside/outside
├── rectangle_selector.py     # Select rectangles inside boundaries (NEW!)
├── boundaries.txt            # Saved boundary coordinates
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Boundary File Format

The `boundaries.txt` file stores boundaries in the following format:

```
# Boundary 1
x1,y1
x2,y2
x3,y3

# Boundary 2
x1,y1
x2,y2
x3,y3
```

## Technical Details

### Point-in-Polygon Algorithm
The system uses the **Ray Casting Algorithm** to determine if a point is inside a polygon:
- Casts a ray from the test point to infinity
- Counts how many times the ray crosses the polygon boundary
- If the count is odd, the point is inside; if even, it's outside

### Performance
- Real-time processing at >15 FPS
- Accurate point-in-polygon detection
- Fast boundary loading from file
- Responsive mouse click handling

## Requirements

- Python 3.7+
- OpenCV >= 4.5.0
- NumPy >= 1.21.0
- Webcam/Camera

## Troubleshooting

**Camera not opening:**
- Ensure your webcam is connected and not in use by another application
- Try changing the camera index in the code (0 to 1 or 2)

**No boundaries found:**
- Run `boundary_definition.py` first to create boundaries
- Ensure `boundaries.txt` exists and contains valid data

**Low performance:**
- Reduce camera resolution in the code
- Close other resource-intensive applications

## Color Legend

### Boundary Definition Mode:
- 🟢 **Green**: Current boundary being defined

### Click Detection Mode:
- 🔴 **Red/Blue/Yellow/Magenta/Cyan**: Different saved boundaries
- 🟢 **Green Result**: Click is INSIDE a boundary
- 🔴 **Red Result**: Click is OUTSIDE all boundaries

## License

This project is open source and available for educational and commercial use.

## Author

Created as a computer vision demonstration project using Python and OpenCV.


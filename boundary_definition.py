"""
Boundary Definition Module (Picamera2, OpenCV-friendly)
- Uses Picamera2 preview configuration like the user's working example
- Captures in BGR888 for direct OpenCV use
- Default size 640x480 to avoid unexpected scaling/cropping
"""

import os
import cv2
import numpy as np
from picamera2 import Picamera2


class BoundaryDefiner:
    def __init__(self):
        self.points = []
        self.boundaries = []
        self.current_color = (0, 255, 0)  # Green for current boundary
        self.saved_colors = [
            (255, 0, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255)
        ]
        self.window_name = "Boundary Definition (PiCam)"
        self.picam2 = None

        # Match your working behavior:
        self.flip_horizontal = True
        self.flip_vertical = True

        # Use the same predictable preview size/format
        self.preview_size = (640, 480)   # (width, height)
        self.preview_format = "BGR888"   # direct OpenCV BGR

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            print(f"Point added: ({x}, {y})")

    def draw_boundaries(self, frame):
        # Draw saved boundaries
        for idx, boundary in enumerate(self.boundaries):
            color = self.saved_colors[idx % len(self.saved_colors)]
            if len(boundary) > 1:
                for i in range(len(boundary)):
                    cv2.line(frame, boundary[i], boundary[(i + 1) % len(boundary)], color, 2)

                overlay = frame.copy()
                pts = np.array(boundary, np.int32)
                cv2.fillPoly(overlay, [pts], color)
                cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)

        # Draw current boundary
        if self.points:
            for p in self.points:
                cv2.circle(frame, p, 5, self.current_color, -1)

            if len(self.points) > 1:
                for i in range(len(self.points) - 1):
                    cv2.line(frame, self.points[i], self.points[i + 1], self.current_color, 2)

                if len(self.points) > 2:
                    cv2.line(frame, self.points[-1], self.points[0], self.current_color, 1, cv2.LINE_AA)

        return frame

    def draw_instructions(self, frame):
        instructions = [
            # "BOUNDARY DEFINITION MODE (PiCamera2)",
            # "Click: Add boundary point",
            # "Enter/Space: Save boundary",
            # "Backspace: Remove last point",
            # "C: Clear all points",
            # "Esc: Exit",
            # f"Points: {len(self.points)} | Boundaries: {len(self.boundaries)}"
        ]

        y = 30
        for text in instructions:
            (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (10, y - 20), (20 + w, y + 5), (0, 0, 0), -1)
            cv2.putText(frame, text, (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y += 30
        return frame

    def save_boundary(self):
        if len(self.points) < 3:
            print("Need at least 3 points to create a boundary!")
            return False

        self.boundaries.append(self.points.copy())
        self.save_to_file()
        print(f"Boundary {len(self.boundaries)} saved with {len(self.points)} points")
        self.points = []
        return True

    def save_to_file(self):
        filepath = os.path.join(os.path.dirname(__file__), "boundaries.txt")
        with open(filepath, "w") as f:
            for idx, boundary in enumerate(self.boundaries):
                f.write(f"# Boundary {idx + 1}\n")
                for x, y in boundary:
                    f.write(f"{x},{y}\n")
                f.write("\n")
        print(f"Saved {len(self.boundaries)} boundaries to {filepath}")

    def load_boundaries(self):
        filepath = os.path.join(os.path.dirname(__file__), "boundaries.txt")
        if not os.path.exists(filepath):
            print("No existing boundaries file found")
            return

        try:
            with open(filepath, "r") as f:
                current = []
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        if current:
                            self.boundaries.append(current)
                            current = []
                        continue
                    if "," in line:
                        x, y = map(int, line.split(","))
                        current.append((x, y))
                if current:
                    self.boundaries.append(current)

            print(f"Loaded {len(self.boundaries)} boundaries from file")
        except Exception as e:
            print(f"Error loading boundaries: {e}")

    def _init_camera(self):
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"size": self.preview_size, "format": self.preview_format}
        )
        self.picam2.configure(config)
        self.picam2.start()

    def run(self):
        self.load_boundaries()

        try:
            self._init_camera()
        except Exception as e:
            print(f"Error: Could not start Pi camera: {e}")
            return

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        print("Boundary Definition Mode Started (PiCamera2)")
        print("Click to add points, Enter/Space to save, Esc to exit")

        try:
            while True:
                frame = self.picam2.capture_array()
                if frame is None:
                    print("Error: Could not read frame from Pi camera")
                    break

                # Match your working flips
                if self.flip_horizontal:
                    frame = cv2.flip(frame, 1)
                if self.flip_vertical:
                    frame = cv2.flip(frame, 0)

                frame = self.draw_boundaries(frame)
                frame = self.draw_instructions(frame)

                cv2.imshow(self.window_name, frame)
                key = cv2.waitKey(1) & 0xFF

                if key == 27:  # Esc
                    print("Exiting...")
                    break
                elif key == 13 or key == 32:  # Enter or Space
                    self.save_boundary()
                elif key == 8:  # Backspace
                    if self.points:
                        removed = self.points.pop()
                        print(f"Removed point: {removed}")
                elif key == ord("c") or key == ord("C"):
                    if self.points:
                        self.points = []
                        print("Cleared all points")

        finally:
            cv2.destroyAllWindows()
            try:
                self.picam2.stop()
            except Exception:
                pass

            print(f"Session ended. Total boundaries saved: {len(self.boundaries)}")


def main():
    BoundaryDefiner().run()


if __name__ == "__main__":
    main()

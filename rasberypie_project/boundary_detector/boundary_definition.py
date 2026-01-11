"""
Boundary Definition Module
Allows users to define boundaries on camera feed and save them to file.
"""

import cv2
import numpy as np
import os

class BoundaryDefiner:
    def __init__(self):
        self.points = []
        self.boundaries = []
        self.current_color = (0, 255, 0)  # Green for current boundary
        self.saved_colors = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        self.color_index = 0
        self.camera = None
        self.window_name = "Boundary Definition"
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse click events"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            print(f"Point added: ({x}, {y})")
    
    def draw_boundaries(self, frame):
        """Draw all saved boundaries and current boundary being defined"""
        # Draw saved boundaries
        for idx, boundary in enumerate(self.boundaries):
            color = self.saved_colors[idx % len(self.saved_colors)]
            if len(boundary) > 1:
                for i in range(len(boundary)):
                    cv2.line(frame, boundary[i], boundary[(i + 1) % len(boundary)], color, 2)
                # Fill polygon with semi-transparent color
                overlay = frame.copy()
                pts = np.array(boundary, np.int32)
                cv2.fillPoly(overlay, [pts], color)
                cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
        
        # Draw current boundary being defined
        if len(self.points) > 0:
            # Draw points
            for point in self.points:
                cv2.circle(frame, point, 5, self.current_color, -1)
            
            # Draw lines between points
            if len(self.points) > 1:
                for i in range(len(self.points) - 1):
                    cv2.line(frame, self.points[i], self.points[i + 1], self.current_color, 2)
                # Draw closing line if we have 3+ points
                if len(self.points) > 2:
                    cv2.line(frame, self.points[-1], self.points[0], self.current_color, 1, cv2.LINE_AA)
        
        return frame
    
    def draw_instructions(self, frame):
        """Draw instruction overlay on frame"""
        instructions = [
            "BOUNDARY DEFINITION MODE",
            "Click: Add boundary point",
            "Enter/Space: Save boundary",
            "Backspace: Remove last point",
            "C: Clear all points",
            "Esc: Exit",
            f"Points: {len(self.points)} | Boundaries: {len(self.boundaries)}"
        ]
        
        y_offset = 30
        for i, text in enumerate(instructions):
            # Add background for better readability
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (10, y_offset - 20), (20 + text_width, y_offset + 5), (0, 0, 0), -1)
            cv2.putText(frame, text, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30
        
        return frame
    
    def save_boundary(self):
        """Save current boundary to the boundaries list and file"""
        if len(self.points) < 3:
            print("Need at least 3 points to create a boundary!")
            return False
        
        self.boundaries.append(self.points.copy())
        self.save_to_file()
        print(f"Boundary {len(self.boundaries)} saved with {len(self.points)} points")
        self.points = []
        return True
    
    def save_to_file(self):
        """Save all boundaries to boundaries.txt file"""
        filepath = os.path.join(os.path.dirname(__file__), 'boundaries.txt')
        
        with open(filepath, 'w') as f:
            for idx, boundary in enumerate(self.boundaries):
                f.write(f"# Boundary {idx + 1}\n")
                for point in boundary:
                    f.write(f"{point[0]},{point[1]}\n")
                f.write("\n")  # Separator between boundaries
        
        print(f"Saved {len(self.boundaries)} boundaries to {filepath}")
    
    def load_boundaries(self):
        """Load existing boundaries from file"""
        filepath = os.path.join(os.path.dirname(__file__), 'boundaries.txt')
        
        if not os.path.exists(filepath):
            print("No existing boundaries file found")
            return
        
        try:
            with open(filepath, 'r') as f:
                current_boundary = []
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        if current_boundary:
                            self.boundaries.append(current_boundary)
                            current_boundary = []
                        continue
                    
                    if ',' in line:
                        x, y = map(int, line.split(','))
                        current_boundary.append((x, y))
                
                # Add last boundary if exists
                if current_boundary:
                    self.boundaries.append(current_boundary)
            
            print(f"Loaded {len(self.boundaries)} boundaries from file")
        except Exception as e:
            print(f"Error loading boundaries: {e}")
    
    def run(self):
        """Main loop for boundary definition"""
        # Load existing boundaries
        self.load_boundaries()
        
        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print("Boundary Definition Mode Started")
        print("Click to add points, Enter/Space to save, Esc to exit")
        
        while True:
            ret, frame = self.camera.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Draw boundaries and instructions
            frame = self.draw_boundaries(frame)
            frame = self.draw_instructions(frame)
            
            cv2.imshow(self.window_name, frame)
            
            # Handle keyboard input
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
            elif key == ord('c') or key == ord('C'):
                if self.points:
                    self.points = []
                    print("Cleared all points")
        
        # Cleanup
        self.camera.release()
        cv2.destroyAllWindows()
        print(f"Session ended. Total boundaries saved: {len(self.boundaries)}")

def main():
    """Entry point for boundary definition"""
    definer = BoundaryDefiner()
    definer.run()

if __name__ == "__main__":
    main()


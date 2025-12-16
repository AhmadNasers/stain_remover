"""
Click Detection Module
Detects if mouse clicks are inside or outside defined boundaries.
"""

import cv2
import numpy as np
import os

class ClickDetector:
    def __init__(self):
        self.boundaries = []
        self.camera = None
        self.window_name = "Click Detection"
        self.last_click = None
        self.last_result = None
        self.last_boundary_idx = None
        self.result_display_time = 0
        self.colors = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse click events"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.last_click = (x, y)
            self.check_point_in_boundaries(x, y)
            self.result_display_time = cv2.getTickCount()
    
    def point_in_polygon(self, point, polygon):
        """
        Check if a point is inside a polygon using ray casting algorithm.
        Returns True if point is inside, False otherwise.
        """
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def check_point_in_boundaries(self, x, y):
        """Check if a point is inside any of the defined boundaries"""
        point = (x, y)
        found_inside = False
        
        for idx, boundary in enumerate(self.boundaries):
            if self.point_in_polygon(point, boundary):
                self.last_result = "INSIDE"
                self.last_boundary_idx = idx
                found_inside = True
                print(f"Click at ({x}, {y}): INSIDE Boundary {idx + 1}")
                break
        
        if not found_inside:
            self.last_result = "OUTSIDE"
            self.last_boundary_idx = None
            print(f"Click at ({x}, {y}): OUTSIDE all boundaries")
    
    def load_boundaries(self):
        """Load boundaries from boundaries.txt file"""
        filepath = os.path.join(os.path.dirname(__file__), 'boundaries.txt')
        
        if not os.path.exists(filepath):
            print("Error: No boundaries file found. Please run boundary_definition.py first.")
            return False
        
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
            
            if not self.boundaries:
                print("Error: No valid boundaries found in file.")
                return False
            
            print(f"Loaded {len(self.boundaries)} boundaries from file")
            return True
            
        except Exception as e:
            print(f"Error loading boundaries: {e}")
            return False
    
    def draw_boundaries(self, frame):
        """Draw all boundaries on the frame"""
        for idx, boundary in enumerate(self.boundaries):
            color = self.colors[idx % len(self.colors)]
            
            if len(boundary) > 1:
                # Draw boundary lines
                for i in range(len(boundary)):
                    cv2.line(frame, boundary[i], boundary[(i + 1) % len(boundary)], color, 2)
                
                # Fill polygon with semi-transparent color
                overlay = frame.copy()
                pts = np.array(boundary, np.int32)
                cv2.fillPoly(overlay, [pts], color)
                cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
                
                # Draw boundary number
                centroid_x = int(np.mean([p[0] for p in boundary]))
                centroid_y = int(np.mean([p[1] for p in boundary]))
                cv2.putText(frame, f"B{idx + 1}", (centroid_x - 15, centroid_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        return frame
    
    def draw_click_result(self, frame):
        """Draw click position and result on frame"""
        if self.last_click is None:
            return frame
        
        # Calculate elapsed time since last click
        elapsed_ticks = cv2.getTickCount() - self.result_display_time
        elapsed_seconds = elapsed_ticks / cv2.getTickFrequency()
        
        # Display result for 3 seconds
        if elapsed_seconds < 3.0:
            x, y = self.last_click
            
            # Draw click point
            cv2.circle(frame, (x, y), 10, (255, 255, 255), 2)
            cv2.circle(frame, (x, y), 5, (0, 0, 0), -1)
            
            # Determine result color
            if self.last_result == "INSIDE":
                result_color = (0, 255, 0)  # Green for inside
                result_text = f"INSIDE Boundary {self.last_boundary_idx + 1}"
            else:
                result_color = (0, 0, 255)  # Red for outside
                result_text = "OUTSIDE All Boundaries"
            
            # Draw result text at click position
            text_offset_y = -30 if y > 50 else 30
            (text_width, text_height), _ = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
            
            # Background rectangle for text
            bg_x1 = x - text_width // 2 - 10
            bg_y1 = y + text_offset_y - text_height - 10
            bg_x2 = x + text_width // 2 + 10
            bg_y2 = y + text_offset_y + 10
            
            cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
            cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), result_color, 2)
            
            # Draw text
            cv2.putText(frame, result_text, (x - text_width // 2, y + text_offset_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, result_color, 2)
            
            # Draw large result indicator at top of screen
            result_display = self.last_result
            (big_text_width, big_text_height), _ = cv2.getTextSize(result_display, cv2.FONT_HERSHEY_SIMPLEX, 2, 4)
            text_x = (frame.shape[1] - big_text_width) // 2
            text_y = 60
            
            # Background for big text
            cv2.rectangle(frame, (text_x - 20, text_y - big_text_height - 10), 
                         (text_x + big_text_width + 20, text_y + 10), (0, 0, 0), -1)
            cv2.rectangle(frame, (text_x - 20, text_y - big_text_height - 10), 
                         (text_x + big_text_width + 20, text_y + 10), result_color, 3)
            
            cv2.putText(frame, result_display, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, result_color, 4)
        
        return frame
    
    def draw_instructions(self, frame):
        """Draw instruction overlay on frame"""
        instructions = [
            "CLICK DETECTION MODE",
            "Click anywhere to test",
            "Esc: Exit",
            f"Boundaries loaded: {len(self.boundaries)}"
        ]
        
        y_offset = frame.shape[0] - 120
        for i, text in enumerate(instructions):
            # Add background for better readability
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (10, y_offset - 20), (20 + text_width, y_offset + 5), (0, 0, 0), -1)
            cv2.putText(frame, text, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30
        
        return frame
    
    def run(self):
        """Main loop for click detection"""
        # Load boundaries
        if not self.load_boundaries():
            print("Cannot start click detection without boundaries.")
            return
        
        # Initialize camera
        self.camera = cv2.VideoCapture(1)
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print("Click Detection Mode Started")
        print(f"Loaded {len(self.boundaries)} boundaries")
        print("Click anywhere to test if it's inside or outside boundaries")
        
        while True:
            ret, frame = self.camera.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Draw boundaries, click results, and instructions
            frame = self.draw_boundaries(frame)
            frame = self.draw_click_result(frame)
            frame = self.draw_instructions(frame)
            
            cv2.imshow(self.window_name, frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # Esc
                print("Exiting...")
                break
        
        # Cleanup
        self.camera.release()
        cv2.destroyAllWindows()
        print("Click detection session ended")

def main():
    """Entry point for click detection"""
    detector = ClickDetector()
    detector.run()

if __name__ == "__main__":
    main()


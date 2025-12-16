"""
Rectangle Selector Module
Allows users to create rectangles inside defined boundaries by click-and-drag.
Supports moving, resizing, and deleting rectangles.
Returns the four corner coordinates.
"""

import cv2
import numpy as np
import os

class RectangleSelector:
    def __init__(self):
        self.boundaries = []
        self.camera = None
        self.window_name = "Rectangle Selector"
        self.colors = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        
        # Rectangle state
        self.rectangle = None  # (x1, y1, x2, y2)
        self.drawing = False
        self.start_point = None
        
        # Moving/resizing state
        self.moving = False
        self.resizing = False
        self.resize_corner = None  # Which corner is being resized
        self.move_offset = None
        
        # Constants
        self.CORNER_SIZE = 15
        self.EDGE_THRESHOLD = 10
        
    def point_in_polygon(self, point, polygon):
        """Check if a point is inside a polygon using ray casting algorithm"""
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
    
    def rectangle_in_boundary(self, rect):
        """Check if all four corners of rectangle are inside any boundary"""
        if rect is None:
            return False
        
        x1, y1, x2, y2 = rect
        corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        
        for boundary in self.boundaries:
            all_inside = True
            for corner in corners:
                if not self.point_in_polygon(corner, boundary):
                    all_inside = False
                    break
            if all_inside:
                return True
        
        return False
    
    def get_corner_at_point(self, x, y):
        """Check if mouse is near a corner of the rectangle"""
        if self.rectangle is None:
            return None
        
        x1, y1, x2, y2 = self.rectangle
        corners = [
            ('top_left', x1, y1),
            ('top_right', x2, y1),
            ('bottom_right', x2, y2),
            ('bottom_left', x1, y2)
        ]
        
        for corner_name, cx, cy in corners:
            if abs(x - cx) < self.CORNER_SIZE and abs(y - cy) < self.CORNER_SIZE:
                return corner_name
        
        return None
    
    def point_in_rectangle(self, x, y):
        """Check if point is inside the rectangle"""
        if self.rectangle is None:
            return False
        
        x1, y1, x2, y2 = self.rectangle
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        return min_x <= x <= max_x and min_y <= y <= max_y
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for drawing, moving, and resizing"""
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if clicking on a corner for resizing
            corner = self.get_corner_at_point(x, y)
            if corner:
                self.resizing = True
                self.resize_corner = corner
                return
            
            # Check if clicking inside rectangle for moving
            if self.point_in_rectangle(x, y):
                self.moving = True
                x1, y1, x2, y2 = self.rectangle
                self.move_offset = (x - x1, y - y1)
                return
            
            # Start drawing new rectangle
            self.drawing = True
            self.start_point = (x, y)
            self.rectangle = None
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing and self.start_point:
                # Update rectangle while drawing
                self.rectangle = (self.start_point[0], self.start_point[1], x, y)
            
            elif self.resizing and self.resize_corner:
                # Resize rectangle
                x1, y1, x2, y2 = self.rectangle
                
                if self.resize_corner == 'top_left':
                    self.rectangle = (x, y, x2, y2)
                elif self.resize_corner == 'top_right':
                    self.rectangle = (x1, y, x, y2)
                elif self.resize_corner == 'bottom_right':
                    self.rectangle = (x1, y1, x, y)
                elif self.resize_corner == 'bottom_left':
                    self.rectangle = (x, y1, x2, y)
            
            elif self.moving and self.move_offset:
                # Move rectangle
                x1, y1, x2, y2 = self.rectangle
                width = x2 - x1
                height = y2 - y1
                new_x1 = x - self.move_offset[0]
                new_y1 = y - self.move_offset[1]
                self.rectangle = (new_x1, new_y1, new_x1 + width, new_y1 + height)
        
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                # Validate rectangle is inside boundary
                if not self.rectangle_in_boundary(self.rectangle):
                    print("⚠️ Rectangle must be completely inside a boundary!")
                    self.rectangle = None
                else:
                    print("✓ Rectangle created successfully")
            
            if self.resizing:
                self.resizing = False
                self.resize_corner = None
                # Validate after resize
                if not self.rectangle_in_boundary(self.rectangle):
                    print("⚠️ Rectangle must stay inside the boundary!")
                    # Could revert here, but for now just warn
            
            if self.moving:
                self.moving = False
                self.move_offset = None
                # Validate after move
                if not self.rectangle_in_boundary(self.rectangle):
                    print("⚠️ Rectangle must stay inside the boundary!")
    
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
                
                if current_boundary:
                    self.boundaries.append(current_boundary)
            
            if not self.boundaries:
                print("Error: No valid boundaries found in file.")
                return False
            
            print(f"✓ Loaded {len(self.boundaries)} boundaries from file")
            return True
            
        except Exception as e:
            print(f"Error loading boundaries: {e}")
            return False
    
    def draw_boundaries(self, frame):
        """Draw all boundaries on the frame"""
        for idx, boundary in enumerate(self.boundaries):
            color = self.colors[idx % len(self.colors)]
            
            if len(boundary) > 1:
                for i in range(len(boundary)):
                    cv2.line(frame, boundary[i], boundary[(i + 1) % len(boundary)], color, 2)
                
                overlay = frame.copy()
                pts = np.array(boundary, np.int32)
                cv2.fillPoly(overlay, [pts], color)
                cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)
        
        return frame
    
    def draw_rectangle(self, frame):
        """Draw the rectangle with corners and coordinates"""
        if self.rectangle is None:
            return frame
        
        x1, y1, x2, y2 = self.rectangle
        
        # Determine color based on validity
        is_valid = self.rectangle_in_boundary(self.rectangle)
        rect_color = (0, 255, 0) if is_valid else (0, 0, 255)
        
        # Draw rectangle
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), rect_color, 2)
        
        # Draw corners (for resizing)
        corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        for cx, cy in corners:
            cv2.circle(frame, (int(cx), int(cy)), self.CORNER_SIZE // 2, rect_color, -1)
            cv2.circle(frame, (int(cx), int(cy)), self.CORNER_SIZE // 2, (255, 255, 255), 2)
        
        # Draw coordinates at each corner
        corner_labels = [
            f"({int(x1)}, {int(y1)})",
            f"({int(x2)}, {int(y1)})",
            f"({int(x2)}, {int(y2)})",
            f"({int(x1)}, {int(y2)})"
        ]
        
        offsets = [(-10, -10), (10, -10), (10, 25), (-10, 25)]
        
        for i, ((cx, cy), label, (ox, oy)) in enumerate(zip(corners, corner_labels, offsets)):
            # Background for text
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            text_x = int(cx) + ox
            text_y = int(cy) + oy
            
            if ox < 0:  # Left side
                text_x = int(cx) - text_width - 10
            
            cv2.rectangle(frame, (text_x - 2, text_y - text_height - 2), 
                         (text_x + text_width + 2, text_y + 2), (0, 0, 0), -1)
            cv2.putText(frame, label, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Draw center crosshair
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        cv2.line(frame, (center_x - 10, center_y), (center_x + 10, center_y), rect_color, 2)
        cv2.line(frame, (center_x, center_y - 10), (center_x, center_y + 10), rect_color, 2)
        
        return frame
    
    def draw_instructions(self, frame):
        """Draw instruction overlay on frame"""
        instructions = [
            "RECTANGLE SELECTOR MODE",
            "Click & Drag: Draw rectangle",
            "Drag corners: Resize",
            "Drag center: Move",
            "D: Delete rectangle",
            "Esc: Finish & show coordinates",
        ]
        
        if self.rectangle:
            is_valid = self.rectangle_in_boundary(self.rectangle)
            status = "✓ Valid" if is_valid else "⚠️ Invalid (outside boundary)"
            instructions.append(f"Status: {status}")
        
        y_offset = 30
        for text in instructions:
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (10, y_offset - 20), (20 + text_width, y_offset + 5), (0, 0, 0), -1)
            cv2.putText(frame, text, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30
        
        return frame
    
    def draw_coordinates_panel(self, frame):
        """Draw a panel showing the four corner coordinates"""
        if self.rectangle is None:
            return frame
        
        x1, y1, x2, y2 = self.rectangle
        
        # Normalize coordinates (ensure top-left to bottom-right)
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        # Create panel
        panel_lines = [
            "RECTANGLE COORDINATES:",
            f"Top-Left:     ({int(min_x)}, {int(min_y)})",
            f"Top-Right:    ({int(max_x)}, {int(min_y)})",
            f"Bottom-Right: ({int(max_x)}, {int(max_y)})",
            f"Bottom-Left:  ({int(min_x)}, {int(max_y)})",
            f"Width:  {int(max_x - min_x)}px",
            f"Height: {int(max_y - min_y)}px",
        ]
        
        panel_x = frame.shape[1] - 350
        panel_y = 30
        panel_width = 340
        panel_height = len(panel_lines) * 30 + 20
        
        # Draw panel background
        cv2.rectangle(frame, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), (0, 255, 0), 2)
        
        # Draw text
        y_offset = panel_y + 25
        for line in panel_lines:
            cv2.putText(frame, line, (panel_x + 10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 30
        
        return frame
    
    def run(self):
        """Main loop for rectangle selection"""
        if not self.load_boundaries():
            print("Cannot start rectangle selector without boundaries.")
            return None
        
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            return None
        
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        print("\n" + "="*60)
        print("Rectangle Selector Mode Started")
        print("="*60)
        print("Draw a rectangle inside the boundary")
        print("- Click & Drag to create")
        print("- Drag corners to resize")
        print("- Drag center to move")
        print("- Press 'D' to delete")
        print("- Press 'Esc' to finish\n")
        
        while True:
            ret, frame = self.camera.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Draw everything
            frame = self.draw_boundaries(frame)
            frame = self.draw_rectangle(frame)
            frame = self.draw_instructions(frame)
            frame = self.draw_coordinates_panel(frame)
            
            cv2.imshow(self.window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # Esc
                print("\n" + "="*60)
                if self.rectangle:
                    x1, y1, x2, y2 = self.rectangle
                    min_x, max_x = min(x1, x2), max(x1, x2)
                    min_y, max_y = min(y1, y2), max(y1, y2)
                    
                    print("FINAL RECTANGLE COORDINATES:")
                    print("="*60)
                    print(f"Top-Left:     ({int(min_x)}, {int(min_y)})")
                    print(f"Top-Right:    ({int(max_x)}, {int(min_y)})")
                    print(f"Bottom-Right: ({int(max_x)}, {int(max_y)})")
                    print(f"Bottom-Left:  ({int(min_x)}, {int(max_y)})")
                    print(f"\nDimensions: {int(max_x - min_x)}px × {int(max_y - min_y)}px")
                    print("="*60)
                    
                    result = {
                        'top_left': (int(min_x), int(min_y)),
                        'top_right': (int(max_x), int(min_y)),
                        'bottom_right': (int(max_x), int(max_y)),
                        'bottom_left': (int(min_x), int(max_y)),
                        'width': int(max_x - min_x),
                        'height': int(max_y - min_y)
                    }
                else:
                    print("No rectangle created")
                    result = None
                break
            
            elif key == ord('d') or key == ord('D'):
                if self.rectangle:
                    self.rectangle = None
                    print("Rectangle deleted")
        
        self.camera.release()
        cv2.destroyAllWindows()
        return result

def main():
    """Entry point for rectangle selector"""
    selector = RectangleSelector()
    result = selector.run()
    
    if result:
        print("\nYou can now use these coordinates in your application.")
    else:
        print("\nNo rectangle coordinates to return.")

if __name__ == "__main__":
    main()


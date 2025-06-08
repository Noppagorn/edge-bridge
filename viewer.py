import cv2
import requests
import json
import numpy as np
from datetime import datetime
import argparse
import time
from typing import Optional, Tuple
import threading
import queue

class StreamViewer:
    def __init__(self, edge_url: str, rtsp_url: Optional[str] = None):
        """
        Initialize stream viewer
        
        Args:
            edge_url: URL of the edge device's stream endpoint
            rtsp_url: Optional direct RTSP URL (if you want to bypass edge device)
        """
        self.edge_url = edge_url
        self.rtsp_url = rtsp_url
        self.frame_queue = queue.Queue(maxsize=2)  # Buffer for 2 frames
        self.is_running = False
        self.current_frame = None
        self.last_detections = []
        self.last_timestamp = None
        
    def start(self):
        """Start the viewer"""
        self.is_running = True
        
        # Start frame capture thread
        if self.rtsp_url:
            self.capture_thread = threading.Thread(target=self._capture_rtsp)
        else:
            self.capture_thread = threading.Thread(target=self._capture_edge)
            
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        # Start display loop
        self._display_loop()
        
    def stop(self):
        """Stop the viewer"""
        self.is_running = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join()
        cv2.destroyAllWindows()
        
    def _capture_rtsp(self):
        """Capture frames directly from RTSP stream"""
        cap = cv2.VideoCapture(self.rtsp_url)
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from RTSP stream")
                time.sleep(1)
                continue
                
            # Update frame queue
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
                
        cap.release()
        
    def _capture_edge(self):
        """Capture frames from edge device"""
        session = requests.Session()
        
        while self.is_running:
            try:
                # Request frame from edge device
                response = session.get(f"{self.edge_url}/frame", stream=True, timeout=5)
                response.raise_for_status()
                
                # Convert response to image
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Get detection data
                    detections_response = session.get(f"{self.edge_url}/detections", timeout=5)
                    if detections_response.status_code == 200:
                        detections_data = detections_response.json()
                        self.last_detections = detections_data.get('detections', [])
                        self.last_timestamp = detections_data.get('timestamp')
                    
                    # Update frame queue
                    if not self.frame_queue.full():
                        self.frame_queue.put((frame, self.last_detections, self.last_timestamp))
                        
            except requests.exceptions.RequestException as e:
                print(f"Error fetching frame from edge device: {str(e)}")
                time.sleep(1)
                
    def _display_loop(self):
        """Main display loop"""
        while self.is_running:
            try:
                # Get frame from queue
                if self.rtsp_url:
                    frame = self.frame_queue.get(timeout=1)
                    detections = []
                    timestamp = datetime.now().isoformat()
                else:
                    frame, detections, timestamp = self.frame_queue.get(timeout=1)
                
                # Draw detections if any
                if detections:
                    for det in detections:
                        x1, y1, x2, y2 = map(int, det['bbox'])
                        label = f"{det['class']} {det['confidence']:.2f}"
                        
                        # Draw box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Draw label
                        cv2.putText(frame, label, (x1, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Add timestamp
                cv2.putText(frame, timestamp, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Display frame
                cv2.imshow('Edge Device Stream', frame)
                
                # Handle key press
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                    
            except queue.Empty:
                continue
                
        self.stop()

def main():
    parser = argparse.ArgumentParser(description='View RTSP stream from edge device')
    parser.add_argument('--edge', type=str, required=True,
                      help='URL of the edge device (e.g., http://raspberry-pi:8000)')
    parser.add_argument('--rtsp', type=str,
                      help='Optional direct RTSP URL (if you want to bypass edge device)')
    args = parser.parse_args()
    
    viewer = StreamViewer(args.edge, args.rtsp)
    try:
        viewer.start()
    except KeyboardInterrupt:
        print("\nStopping viewer...")
    finally:
        viewer.stop()

if __name__ == "__main__":
    main() 
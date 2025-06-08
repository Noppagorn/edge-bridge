from ultralytics import YOLO
import cv2
import numpy as np
import requests
import json
from datetime import datetime
import os
from typing import List, Dict, Any

class YOLODetector:
    def __init__(self, model_path: str = "yolov8n.pt", server_url: str = None):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to YOLO model weights (default: yolov8n.pt - nano model)
            server_url: URL of the server to send detection results
        """
        # Load YOLO model
        self.model = YOLO(model_path)
        self.server_url = server_url
        
        # Set confidence threshold
        self.conf_threshold = 0.5
        
        # Initialize request session for better performance
        self.session = requests.Session()
        
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process a single frame and return detection results
        
        Args:
            frame: Input frame from camera
            
        Returns:
            Dictionary containing detection results
        """
        # Run YOLO inference
        results = self.model(frame, conf=self.conf_threshold)[0]
        
        # Process detections
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = float(box.conf[0].cpu().numpy())
            class_id = int(box.cls[0].cpu().numpy())
            class_name = results.names[class_id]
            
            detections.append({
                'class': class_name,
                'confidence': confidence,
                'bbox': [float(x1), float(y1), float(x2), float(y2)]
            })
        
        # Prepare result payload
        result = {
            'timestamp': datetime.now().isoformat(),
            'detections': detections,
            'frame_shape': frame.shape[:2]
        }
        
        # Send results to server if URL is provided
        if self.server_url and detections:
            self._send_to_server(result)
            
        return result
    
    def _send_to_server(self, data: Dict[str, Any]) -> None:
        """
        Send detection results to server
        
        Args:
            data: Detection results to send
        """
        try:
            response = self.session.post(
                self.server_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending data to server: {str(e)}")
            
    def draw_detections(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw detection boxes on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            
        Returns:
            Frame with detection boxes drawn
        """
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            label = f"{det['class']} {det['confidence']:.2f}"
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        return frame 
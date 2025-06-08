import cv2
from rtsp_stream import RTSPStream
import time
import os
from dotenv import load_dotenv
import sys
from detector import YOLODetector
import argparse

def process_frame(frame, detector, show_video=False):
    """
    Process each frame from the RTSP stream using YOLO detector
    
    Args:
        frame: Input frame from camera
        detector: YOLO detector instance
        show_video: Whether to display the video stream
    """
    # Run detection
    result = detector.process_frame(frame)
    
    # Draw detections if any
    if result['detections']:
        frame = detector.draw_detections(frame, result['detections'])
        
        # Print detections to console
        print(f"\nDetections at {result['timestamp']}:")
        for det in result['detections']:
            print(f"- {det['class']}: {det['confidence']:.2f}")
    
    # Display the frame if requested
    if show_video:
        cv2.imshow('RTSP Stream with Detections', frame)
        cv2.waitKey(1)

def frame_callback(frame):
    """Simple callback to display frames"""
    try:
        cv2.imshow('RTSP Stream', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Press 'q' to quit
            cv2.destroyAllWindows()
            sys.exit(0)
    except Exception as e:
        print(f"Error displaying frame: {str(e)}")

#   .env file
#       RTSP_URL=rtsp://192.168.1.113/stream1
#       RTSP_USERNAME=your_username
#       RTSP_PASSWORD=your_password
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='RTSP Stream Object Detection')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                      help='Path to YOLO model weights (default: yolov8n.pt)')
    parser.add_argument('--show', action='store_true', default=True,
                      help='Show video stream with detections')
    parser.add_argument('--server', type=str,
                      help='URL of the server to send detection results')
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables
    rtsp_url = os.getenv('RTSP_URL')
    username = os.getenv('RTSP_USERNAME')
    password = os.getenv('RTSP_PASSWORD')
    
    # Validate required environment variables
    if not all([rtsp_url, username, password]):
        print("Error: Missing required environment variables.")
        print("Please ensure RTSP_URL, RTSP_USERNAME, and RTSP_PASSWORD are set in your .env file")
        sys.exit(1)
    
    # Initialize YOLO detector
    print(f"Loading YOLO model: {args.model}")
    # detector = YOLODetector(model_path=args.model, server_url=args.server)
    
    # Create callback function for RTSP stream
    # def frame_callback(frame):
        # process_frame(frame, detector, args.show)
    
    # Create RTSP stream instance with authentication
    # stream = RTSPStream(rtsp_url, username, password, callback=frame_callback)
    stream = RTSPStream(rtsp_url, username, password, callback=frame_callback)
    
    try:
        # Start the stream
        print("Starting RTSP stream...")
        stream.start()
        
        # Keep the main thread running
        print("Press 'q' to quit")
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping RTSP stream...")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        stream.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

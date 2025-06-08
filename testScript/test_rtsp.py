import cv2
import os
from dotenv import load_dotenv
import time
import urllib.parse

def test_rtsp():
    # Load environment variables
    load_dotenv()
    
    # Get RTSP credentials
    rtsp_url = os.getenv('RTSP_URL')
    username = os.getenv('RTSP_USERNAME')
    password = os.getenv('RTSP_PASSWORD')
    
    if not all([rtsp_url, username, password]):
        print("Error: Missing required environment variables.")
        print("Please ensure RTSP_URL, RTSP_USERNAME, and RTSP_PASSWORD are set in your .env file")
        return
    
    # Construct full RTSP URL with credentials
    parsed_url = urllib.parse.urlparse(rtsp_url)
    full_url = f"{parsed_url.scheme}://{username}:{password}@{parsed_url.netloc}{parsed_url.path}"
    
    print(f"Attempting to connect to RTSP stream: {rtsp_url}")
    
    # Try to open the stream
    cap = cv2.VideoCapture(full_url)
    if not cap.isOpened():
        print("Failed to open RTSP stream")
        return
    
    print("Successfully connected to RTSP stream")
    print("Press 'q' to quit")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame")
                break
                
            # Display the frame
            cv2.imshow('RTSP Test', frame)
            
            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    test_rtsp() 
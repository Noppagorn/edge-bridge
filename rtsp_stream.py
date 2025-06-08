import cv2
import threading
import time
from typing import Optional, Callable
import urllib.parse

class RTSPStream:
    def __init__(self, rtsp_url: str, username: str, password: str, callback: Optional[Callable] = None):
        """
        Initialize RTSP stream handler
        
        Args:
            rtsp_url (str): The RTSP URL to connect to
            username (str): Username for RTSP authentication
            password (str): Password for RTSP authentication
            callback (Callable, optional): Function to call with each frame
        """
        # Parse the URL and add authentication
        parsed_url = urllib.parse.urlparse(rtsp_url)
        self.rtsp_url = f"{parsed_url.scheme}://{username}:{password}@{parsed_url.netloc}{parsed_url.path}"
        self.callback = callback
        self.cap = None
        self.is_running = False
        self.thread = None
        self._lock = threading.Lock()
        
    def start(self):
        """Start the RTSP stream in a separate thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._stream_loop)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop the RTSP stream"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
            
    def _stream_loop(self):
        """Main streaming loop that runs in a separate thread"""
        while self.is_running:
            try:
                if self.cap is None or not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.rtsp_url)
                    if not self.cap.isOpened():
                        print(f"Failed to open RTSP stream: {self.rtsp_url}")
                        time.sleep(5)  # Wait before retrying
                        continue
                
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame from RTSP stream")
                    self.cap.release()
                    self.cap = None
                    time.sleep(1)
                    continue
                
                if self.callback:
                    self.callback(frame)
                    
            except Exception as e:
                print(f"Error in RTSP stream: {str(e)}")
                if self.cap:
                    self.cap.release()
                    self.cap = None
                time.sleep(1)
                
    def get_frame(self) -> Optional[tuple]:
        """
        Get the current frame from the stream
        
        Returns:
            tuple: (ret, frame) where ret is boolean indicating success and frame is the image
        """
        with self._lock:
            if self.cap is None or not self.cap.isOpened():
                return False, None
            return self.cap.read() 
from flask import Flask, Response, jsonify
import cv2
import numpy as np
from rtsp_stream import RTSPStream
import threading
import queue
import time
from dotenv import load_dotenv
import os
import argparse
import logging
import re
import socket
from utils import get_network_interfaces

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables
frame_queue = queue.Queue(maxsize=2)
is_running = True

def mask_rtsp_url(url):
    """Mask sensitive information in RTSP URL"""
    if not url:
        return "None"
    # Replace username and password with asterisks
    masked_url = re.sub(r'://[^:]+:[^@]+@', '://****:****@', url)
    return masked_url

def validate_rtsp_credentials(url, username, password):
    """Validate RTSP credentials without exposing them"""
    if not all([url, username, password]):
        return False, "Missing credentials"
    
    # Basic URL format validation
    if not url.startswith(('rtsp://', 'rtsps://')):
        return False, "Invalid RTSP URL format"
    
    # Check for minimum length requirements
    if len(username) < 1 or len(password) < 1:
        return False, "Invalid credentials length"
    
    return True, "Credentials valid"

# using ZeroTier IP
def process_frame(frame):
    """Process frame and update frame queue"""
    try:
        # Update frame queue
        if not frame_queue.full():
            frame_queue.put(frame)
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")

def generate_frames():
    """Generate video frames for streaming"""
    while is_running:
        try:
            frame = frame_queue.get(timeout=1)
            if frame is None:
                logger.warning("Received None frame from queue")
                continue
                
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                logger.error("Failed to encode frame to JPEG")
        except queue.Empty:
            logger.warning("Frame queue is empty")
            continue
        except Exception as e:
            logger.error(f"Error generating frames: {str(e)}")
            continue

@app.route('/frame')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    parser = argparse.ArgumentParser(description='Edge device server for video streaming')
    parser.add_argument('--port', type=int, default=8000,
                      help='Port to run the server on (default: 8000)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                      help='Host to run the server on (default: 0.0.0.0)')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get RTSP credentials
    rtsp_url = os.getenv('RTSP_URL')
    username = os.getenv('RTSP_USERNAME')
    password = os.getenv('RTSP_PASSWORD')
    
    # Validate credentials without exposing them
    is_valid, message = validate_rtsp_credentials(rtsp_url, username, password)
    if not is_valid:
        logger.error(f"RTSP credentials validation failed: {message}")
        return
    
    # Log masked URL for debugging
    logger.info(f"Connecting to RTSP stream: {mask_rtsp_url(rtsp_url)}")
    
    # Create callback function
    def frame_callback(frame):
        if frame is not None:
            process_frame(frame)
        else:
            logger.warning("Received None frame from RTSP stream")
    
    # Start RTSP stream
    try:
        stream = RTSPStream(rtsp_url, username, password, callback=frame_callback)
        stream.start()
        logger.info("RTSP stream started successfully")
    except Exception as e:
        logger.error("Failed to start RTSP stream (credentials may be invalid)")
        return
    
    try:
        # Get and log available network interfaces
        interfaces = get_network_interfaces()
        logger.info("Available network interfaces:")
        for ip in interfaces:
            logger.info(f"  - http://{ip}:{args.port}")
        
        # Start Flask server
        logger.info(f"Starting server on {args.host}:{args.port}")
        app.run(host=args.host, port=args.port, threaded=True)
    except KeyboardInterrupt:
        logger.info("\nStopping server...")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
    finally:
        global is_running
        is_running = False
        stream.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    main() 
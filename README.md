# Edge Device System

![ChatGPT Image 8 มิ ย  2568 22_41_07](https://github.com/user-attachments/assets/cab09b19-c2a8-4649-aceb-7dfb381bf7ac)


This system provides a complete solution for detecting objects using RTSP cameras and YOLO object detection. It consists of an edge device (Raspberry Pi) that processes the video stream and a viewer application for monitoring the stream from any computer.

## System Components

1. **Edge Device (Raspberry Pi)**
   - Connects to RTSP cameras
   - Runs YOLO object detection
   - Serves video stream and detection results
   - Files: `server.py`, `detector.py`, `rtsp_stream.py`

2. **Viewer Application**
   - Connects to edge device
   - Displays video stream with detections
   - Files: `viewer.py`

3. **Core Components**
   - YOLO detector implementation: `detector.py`
   - RTSP stream handler: `rtsp_stream.py`
   - Main application: `main.py`

## Prerequisites

- Python 3.9 or higher
- OpenCV
- PyTorch
- Flask
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd edge-bridge
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your RTSP camera credentials:
```env
RTSP_URL=rtsp://your-camera-ip/stream
RTSP_USERNAME=your_username
RTSP_PASSWORD=your_password
```

## Usage

### 1. Running on Edge Device (Raspberry Pi)

The edge device runs the server that processes the RTSP stream and serves the video feed:

```bash
# Basic usage (default port 8000)
python server.py

# Custom options
python server.py --model yolov8n.pt --port 8080 --host 0.0.0.0
```

Options:
- `--model`: Path to YOLO model weights (default: yolov8n.pt)
- `--port`: Port to run the server on (default: 8000)
- `--host`: Host to run the server on (default: 0.0.0.0)

### 2. Viewing the Stream

On your local machine, use the viewer to connect to the edge device:

```bash
# Connect to edge device
python viewer.py --edge http://raspberry-pi-ip:8000

# Connect directly to RTSP (bypassing edge device)
python viewer.py --edge http://raspberry-pi-ip:8000 --rtsp rtsp://camera-ip/stream
```

Options:
- `--edge`: URL of the edge device (required)
- `--rtsp`: Optional direct RTSP URL

Controls:
- Press 'q' to quit the viewer

### 3. Running with Docker

The system can also be run using Docker:

1. Build the Docker image:
```bash
docker build -t edge-bridge .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env edge-bridge
```

Or using docker-compose:
```bash
docker-compose up --build
```

## Available Models

The system supports different YOLO models:
- `yolov8n.pt` (nano) - Fastest, least accurate
- `yolov8s.pt` (small) - Good balance
- `yolov8m.pt` (medium) - More accurate but slower

## API Endpoints

The edge device server provides two endpoints:

1. Video Stream:
```
GET http://edge-device-ip:8000/frame
```
Returns a multipart MJPEG stream of the video feed.

2. Detections:
```
GET http://edge-device-ip:8000/detections
```
Returns JSON with the latest detections:
```json
{
    "timestamp": "2024-01-20T12:34:56.789Z",
    "detections": [
        {
            "class": "person",
            "confidence": 0.95,
            "bbox": [100, 200, 300, 400]
        }
    ]
}
```

## Performance Optimization

For better performance on Raspberry Pi:
1. Use the nano model (`yolov8n.pt`)
2. Consider reducing the input resolution
3. Process frames at a lower frequency if needed
4. Use a USB accelerator if available

## Troubleshooting

1. **Connection Issues**
   - Verify RTSP credentials in `.env` file
   - Check network connectivity between devices
   - Ensure correct IP addresses and ports

2. **Performance Issues**
   - Try a lighter YOLO model
   - Reduce video resolution
   - Check CPU/memory usage

3. **Stream Quality**
   - Adjust JPEG quality in `server.py` (default: 80)
   - Modify frame buffer size in queue

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your License Here] 

import cv2
import numpy as np
from flask import Flask, render_template, Response
from flask_mail import Mail, Message
import threading
import time
import os

app = Flask(__name__)

# Configuration for email alerts
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'your_password'  # Your email password

mail = Mail(app)

# Initialize camera with high resolution
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set width to 640
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set height to 480

# Variables for motion detection and recording
first_frame = None
motion_detected = False
last_alert_time = 0
alert_interval = 300  # 5 minutes, (300 seconds). Change if you want...
frame_count = 0
process_frame_interval = 5  # Process every 5th frame
video_filename = "motion_detected.mp4" # Change if you want the video recording in a different directory.

def send_alert():
    global last_alert_time
    current_time = time.time()
    
    if current_time - last_alert_time > alert_interval:
        msg = Message("Motion Detected!", sender='your_email@gmail.com', recipients=['recipient_email@gmail.com'])
        msg.body = "Motion was detected by your security system. See the attached video from your MotionMate Camera."
        
        # Attach the video file
        with app.open_resource(video_filename) as video_file:
            msg.attach(video_filename, "video/mp4", video_file.read())
        
        mail.send(msg)
        last_alert_time = current_time

def record_video(duration=30):
    global video_filename
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))  # 20 FPS

    # Record for the specified duration
    start_time = time.time()
    while (time.time() - start_time) < duration:
        ret, frame = camera.read()
        if not ret:
            break
        out.write(frame)  # Write the frame to the video file

    out.release()  # Release the VideoWriter

def detect_motion():
    global first_frame, motion_detected, frame_count
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % process_frame_interval != 0:
            continue  # Skip processing this frame

        # Convert to grayscale and blur the frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Initialize the first frame
        if first_frame is None:
            first_frame = gray
            continue

        # Compute the absolute difference and apply thresholding
        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, 30, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours of the thresholded image
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Check if any contour is large enough to be considered motion
        for contour in contours:
            if cv2.contourArea(contour) < 1000:  # Adjust threshold for sensitivity
                continue

            motion_detected = True
            print("Motion Detected! Recording video...")
            record_video(duration=30)  # Record for 30 seconds, can be changed.
            send_alert()  # Send email alert
            break

        if motion_detected:
            time.sleep(0.1)  # Reduce CPU usage with a smaller sleep interval

# Start motion detection in a separate thread
threading.Thread(target=detect_motion, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Motion Detection System

A simple motion detection application that captures video and sends email alerts with the recorded clip when motion is detected.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [License](#license)

## Features

- Real-time motion detection using OpenCV.
- Captures a 30-second video clip when motion is detected.
- Sends an email alert with the recorded video attached.
- Web interface for video streaming.

## Requirements

- Python 3.x
- Flask
- OpenCV
- Flask-Mail
- NumPy

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install flask opencv-python flask-mail numpy
   ```

## Usage

1. Open the `app.py` file and configure your email settings.
   - Set your email credentials in the configuration section.

2. Run the application:
   ```bash
   python app.py
   ```

3. Access the web interface by navigating to `http://localhost:5000` in your web browser.

## Configuration

In the `app.py` file, modify the following settings:

- **Email Configuration**:
  - `MAIL_USERNAME`: Your email address
  - `MAIL_PASSWORD`: Your email password

You can adjust the sensitivity of the motion detection by changing the contour area threshold in the `detect_motion()` function.

## License

Do whatever you want I don't care, sell, repurpose or turn it into a hand grenade.

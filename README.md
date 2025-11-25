# AI Virtual Mouse with Dashboard

This project provides an AI-powered virtual mouse controller that uses hand gestures detected through your webcam to control your computer cursor. The system comes with a user-friendly dashboard interface for easy control and monitoring.

## Features

- **Hand Gesture Control**: Control your mouse using hand gestures
- **Dashboard UI**: Easy-to-use graphical interface
- **Real-time Statistics**: Track your gesture usage
- **Visual Feedback**: See gesture recognition in real-time
- **Authentication System**: Secure login with username/password
- **Enhanced Multi-Hand Detection**: Improved detection of multiple hands
- **Configurable Settings**: Adjustable detection confidence and tracking parameters
- **Multiple Gestures Supported**:
  - Open Palm: Move cursor
  - V Gesture: Enable clicking mode
  - Fist: Click and hold
  - Index Finger: Right click
  - Two fingers closed: Double click
  - Pinch (thumb and index): Scroll/Brightness/Volume control

## Requirements

- Python 3.7 or higher
- Webcam
- Windows, macOS, or Linux

## Installation

1. Install the required Python packages:
   ```
   pip install opencv-python mediapipe pyautogui pycaw screen-brightness-control comtypes
   ```

2. Make sure your webcam is connected and working

## Usage

### Running the Dashboard UI

1. Run the UI application:
   ```
   python run_ui.py
   ```

2. Log in with the default credentials:
   - Username: `admin`
   - Password: `admin123`

3. Use the dashboard controls:
   - Click "Start Controller" to begin gesture recognition
   - Click "Stop Controller" to pause gesture recognition
   - Click "Exit" to close the application

### Running the Original Controller

To run the original controller without the UI:
```
python ai_virtual_mouse.py
```

## Gesture Guide

| Gesture | Function |
|---------|----------|
| Open Palm | Move the cursor |
| V Gesture | Enable clicking mode |
| Fist | Click and hold |
| Index Finger | Right click |
| Two Fingers Closed | Double click |
| Pinch (Major Hand) | Control brightness/volume |
| Pinch (Minor Hand) | Scroll horizontally/vertically |

## Dashboard Features

- **Control Panel**: Start/stop the controller
- **Status Display**: Shows if the controller is running or stopped
- **Statistics**: Tracks usage of different gestures
- **Visualization**: Simple hand visualization
- **Instructions**: Quick reference guide for gestures
- **Settings Panel**: 
  - Adjustable detection confidence
  - Configurable tracking confidence
  - Multi-hand detection toggle
  - Camera settings
  - Sensitivity controls

## Security Features

- **Authentication Required**: All users must log in before accessing the application
- **Password Protection**: Credentials are securely hashed and stored
- **Default Credentials**: 
  - Username: `admin`
  - Password: `admin123`
- **User Management**: Add new users and change passwords

## Multi-Hand Detection

The enhanced multi-hand detection system provides:
- Improved accuracy in detecting multiple hands
- Configurable detection confidence levels
- Adjustable tracking parameters
- Toggle for single vs. dual hand operation

## Troubleshooting

- If the camera doesn't start, check that no other application is using it
- If gestures aren't recognized properly, ensure good lighting conditions
- If the cursor moves erratically, try adjusting the distance from the camera
- If login fails, check the credentials.json file for user accounts

## Files

- `ai_virtual_mouse.py`: Core gesture recognition and control logic
- `virtual_mouse_ui.py`: Dashboard user interface
- `run_ui.py`: Launcher script for the UI with authentication
- `auth.py`: Authentication system
- `credentials.json`: User credentials (created on first run)
- `README.md`: This documentation file

## Credits

This project uses:
- OpenCV for computer vision
- MediaPipe for hand tracking
- PyAutoGUI for mouse control
- Pycaw for audio control
- screen-brightness-control for display brightness control
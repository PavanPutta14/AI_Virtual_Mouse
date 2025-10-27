import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import cv2
import mediapipe as mp
import pyautogui
import math
from enum import IntEnum
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbcontrol
from google.protobuf.json_format import MessageToDict
import time
import webbrowser

# Import the existing gesture recognition code
from ai_virtual_mouse import Gest, HLabel, HandRecog, Controller, GestureController

# Handle MediaPipe imports with error handling
try:
    import mediapipe.python.solutions.drawing_utils as drawing_utils
    import mediapipe.python.solutions.hands as hands_module
    mp_drawing = drawing_utils
    mp_hands = hands_module
except ImportError:
    # Fallback for different versions of MediaPipe
    mp_drawing = mp.solutions.drawing_utils  # type: ignore
    mp_hands = mp.solutions.hands  # type: ignore

class VirtualMouseUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Virtual Mouse Controller - Professional Edition")
        self.root.geometry("1000x700")
        self.root.minsize(1000, 700)
        self.root.resizable(True, True)
        
        # Initialize variables first
        self.is_running = False
        self.gesture_controller = None
        self.update_thread = None
        self.stats = {
            'fist_count': 0,
            'pinch_count': 0,
            'v_gest_count': 0,
            'click_count': 0,
            'scroll_count': 0,
            'right_click_count': 0,
            'double_click_count': 0
        }
        
        # Track previous gestures to avoid counting the same gesture multiple times
        self.prev_gest_major = None
        self.prev_gest_minor = None
        
        # Initialize StringVar objects for statistics
        self.fist_count_var = tk.StringVar(value="0")
        self.pinch_count_var = tk.StringVar(value="0")
        self.v_gest_count_var = tk.StringVar(value="0")
        self.click_count_var = tk.StringVar(value="0")
        self.right_click_count_var = tk.StringVar(value="0")
        self.double_click_count_var = tk.StringVar(value="0")
        self.scroll_count_var = tk.StringVar(value="0")
        
        # Set up the UI theme
        self.setup_ui_theme()
        
        # Create the UI elements
        self.create_widgets()
        
        # Update the dashboard
        self.update_dashboard()
    
    def setup_ui_theme(self):
        """Set up the UI theme and styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.bg_color = '#2c3e50'
        self.header_color = '#34495e'
        self.button_color = '#3498db'
        self.start_color = '#27ae60'
        self.stop_color = '#e74c3c'
        self.text_color = '#ecf0f1'
        
        self.root.configure(bg=self.bg_color)
        
        # Configure styles
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabelframe', background=self.bg_color, foreground=self.text_color)
        style.configure('TLabelframe.Label', background=self.header_color, foreground=self.text_color, font=('Arial', 12, 'bold'))
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), foreground='#3498db')
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='#3498db')
        style.configure('Stats.TLabel', font=('Arial', 11, 'bold'))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        style.configure('Start.TButton', background=self.start_color, foreground='white')
        style.configure('Stop.TButton', background=self.stop_color, foreground='white')
        style.configure('Primary.TButton', background=self.button_color, foreground='white')
        style.map('Start.TButton', background=[('active', '#2ecc71')])
        style.map('Stop.TButton', background=[('active', '#c0392b')])
        style.map('Primary.TButton', background=[('active', '#2980b9')])
        
        # Configure notebook style
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background=self.header_color, foreground=self.text_color, padding=[10, 2])
        style.map('TNotebook.Tab', background=[('selected', self.button_color)], foreground=[('selected', 'white')])
        
    def create_widgets(self):
        """Create all UI widgets"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        self.title_label = ttk.Label(self.main_frame, text="AI Virtual Mouse Controller", style='Title.TLabel')
        self.title_label.pack(pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        
        # Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Help tab
        self.help_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.help_tab, text="Help & Instructions")
        
        # Create content for each tab
        self.create_dashboard_content()
        self.create_settings_content()
        self.create_help_content()
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready - Click 'Start Controller' to begin")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar for visual feedback
        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
    
    def create_dashboard_content(self):
        """Create dashboard tab content"""
        # Control panel
        self.control_panel = ttk.LabelFrame(self.dashboard_tab, text="Control Panel", padding="15")
        self.control_panel.pack(fill=tk.X, pady=(0, 15))
        
        button_frame = ttk.Frame(self.control_panel)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(button_frame, text="Start Controller", style='Start.TButton', command=self.start_controller)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Controller", style='Stop.TButton', command=self.stop_controller, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.reset_button = ttk.Button(button_frame, text="Reset Statistics", style='Primary.TButton', command=self.reset_statistics)
        self.reset_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.exit_button = ttk.Button(button_frame, text="Exit", command=self.exit_app)
        self.exit_button.pack(side=tk.RIGHT)
        
        # Stats and visualization frame
        stats_visual_frame = ttk.Frame(self.dashboard_tab)
        stats_visual_frame.pack(fill=tk.BOTH, expand=True)
        
        # Statistics panel
        self.stats_panel = ttk.LabelFrame(stats_visual_frame, text="Statistics", padding="15")
        self.stats_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Statistics grid
        stats_grid = ttk.Frame(self.stats_panel)
        stats_grid.pack(fill=tk.BOTH, expand=True)
        
        # Statistics labels
        stats_data = [
            ("Fist Gestures:", self.fist_count_var),
            ("Pinch Gestures:", self.pinch_count_var),
            ("V Gestures:", self.v_gest_count_var),
            ("Left Clicks:", self.click_count_var),
            ("Right Clicks:", self.right_click_count_var),
            ("Double Clicks:", self.double_click_count_var),
            ("Scroll Actions:", self.scroll_count_var)
        ]
        
        for i, (label_text, var) in enumerate(stats_data):
            row = i // 2
            col = (i % 2) * 2
            
            label = ttk.Label(stats_grid, text=label_text, style='Stats.TLabel')
            label.grid(row=row, column=col, sticky="w", pady=5, padx=(0, 10))
            
            count_label = ttk.Label(stats_grid, textvariable=var, font=('Arial', 11, 'bold'), foreground='#3498db')
            count_label.grid(row=row, column=col+1, sticky="w", pady=5)
        
        # Visualization panel
        self.gesture_panel = ttk.LabelFrame(stats_visual_frame, text="Gesture Visualization", padding="15")
        self.gesture_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        
        self.gesture_canvas = tk.Canvas(self.gesture_panel, width=250, height=200, bg='#34495e', highlightthickness=0)
        self.gesture_canvas.pack()
        self.draw_gesture_visualization()
        
        # System info panel
        self.info_panel = ttk.LabelFrame(self.dashboard_tab, text="System Information", padding="15")
        self.info_panel.pack(fill=tk.X, pady=(15, 0))
        
        info_frame = ttk.Frame(self.info_panel)
        info_frame.pack(fill=tk.X)
        
        # Get system info
        screen_width, screen_height = pyautogui.size()
        info_text = f"Screen Resolution: {screen_width}x{screen_height} | "
        info_text += f"Mouse Position: {pyautogui.position()} | "
        info_text += "Status: Ready"
        
        self.info_label = ttk.Label(info_frame, text=info_text, font=('Arial', 9))
        self.info_label.pack()
    
    def create_settings_content(self):
        """Create settings tab content"""
        # Settings panel
        self.settings_panel = ttk.LabelFrame(self.settings_tab, text="Controller Settings", padding="15")
        self.settings_panel.pack(fill=tk.BOTH, expand=True)
        
        settings_frame = ttk.Frame(self.settings_panel)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sensitivity settings
        sensitivity_frame = ttk.LabelFrame(settings_frame, text="Sensitivity", padding="10")
        sensitivity_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(sensitivity_frame, text="Mouse Sensitivity:").grid(row=0, column=0, sticky="w", pady=5)
        self.sensitivity_var = tk.StringVar(value="Medium")
        sensitivity_combo = ttk.Combobox(sensitivity_frame, textvariable=self.sensitivity_var, 
                                        values=["Low", "Medium", "High"], state="readonly", width=15)
        sensitivity_combo.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        ttk.Label(sensitivity_frame, text="Scroll Speed:").grid(row=1, column=0, sticky="w", pady=5)
        self.scroll_speed_var = tk.StringVar(value="Medium")
        scroll_combo = ttk.Combobox(sensitivity_frame, textvariable=self.scroll_speed_var,
                                   values=["Slow", "Medium", "Fast"], state="readonly", width=15)
        scroll_combo.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Camera settings
        camera_frame = ttk.LabelFrame(settings_frame, text="Camera", padding="10")
        camera_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(camera_frame, text="Camera Device:").grid(row=0, column=0, sticky="w", pady=5)
        self.camera_var = tk.StringVar(value="Default Camera")
        camera_combo = ttk.Combobox(camera_frame, textvariable=self.camera_var,
                                   values=["Default Camera", "USB Camera 1", "USB Camera 2"], state="readonly", width=15)
        camera_combo.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        self.flip_camera_var = tk.BooleanVar()
        flip_check = ttk.Checkbutton(camera_frame, text="Flip Camera Horizontally", variable=self.flip_camera_var)
        flip_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(settings_frame, text="Advanced", padding="10")
        advanced_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.smooth_cursor_var = tk.BooleanVar(value=True)
        smooth_check = ttk.Checkbutton(advanced_frame, text="Enable Cursor Smoothing", variable=self.smooth_cursor_var)
        smooth_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        self.show_landmarks_var = tk.BooleanVar()
        landmarks_check = ttk.Checkbutton(advanced_frame, text="Show Hand Landmarks", variable=self.show_landmarks_var)
        landmarks_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Save button
        save_frame = ttk.Frame(settings_frame)
        save_frame.pack(fill=tk.X, pady=(15, 0))
        
        save_button = ttk.Button(save_frame, text="Save Settings", style='Primary.TButton')
        save_button.pack(side=tk.RIGHT)
    
    def create_help_content(self):
        """Create help tab content"""
        # Help panel
        self.help_panel = ttk.LabelFrame(self.help_tab, text="Instructions & Help", padding="15")
        self.help_panel.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for help sections
        help_notebook = ttk.Notebook(self.help_panel)
        help_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Getting Started tab
        start_tab = ttk.Frame(help_notebook)
        help_notebook.add(start_tab, text="Getting Started")
        
        start_text = """
Getting Started with AI Virtual Mouse:

1. Ensure your webcam is connected and working properly
2. Make sure you have adequate lighting in your environment
3. Position yourself about 1-2 feet away from the camera
4. Click the "Start Controller" button to begin gesture recognition
5. Use the gesture guide below to control your computer

Tips for Best Performance:
- Keep your hand fully visible to the camera
- Use contrasting background colors for better detection
- Avoid direct sunlight or very bright lights behind you
- Keep your hand steady when making gestures
- For clicking gestures, make sure to enter V-gesture mode first
        """
        
        start_textbox = scrolledtext.ScrolledText(start_tab, wrap=tk.WORD, height=15)
        start_textbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        start_textbox.insert(tk.END, start_text)
        start_textbox.config(state=tk.DISABLED)
        
        # Gesture Guide tab
        gesture_tab = ttk.Frame(help_notebook)
        help_notebook.add(gesture_tab, text="Gesture Guide")
        
        # Create a treeview for gesture guide
        gesture_tree = ttk.Treeview(gesture_tab, columns=("Gesture", "Function", "How to Perform"), show="headings", height=12)
        gesture_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define headings
        gesture_tree.heading("Gesture", text="Gesture")
        gesture_tree.heading("Function", text="Function")
        gesture_tree.heading("How to Perform", text="How to Perform")
        
        # Define column widths
        gesture_tree.column("Gesture", width=120)
        gesture_tree.column("Function", width=200)
        gesture_tree.column("How to Perform", width=300)
        
        # Add gesture data
        gestures = [
            ("Open Palm", "Move Cursor", "Show your open palm to the camera. Move your hand to control the cursor."),
            ("V Gesture", "Enable Clicking Mode", "Raise your index and middle fingers in a 'V' shape to enable clicking."),
            ("Fist", "Left Click & Hold", "Make a fist to perform a left click and hold action. Release to stop holding."),
            ("Index Finger", "Right Click", "Raise only your index finger while in clicking mode for right click."),
            ("Two Fingers Closed", "Double Click", "Raise index and middle fingers, then close them quickly for double click."),
            ("Pinch (Major Hand)", "Brightness/Volume", "Pinch with thumb and index finger on your dominant hand to control brightness/volume."),
            ("Pinch (Minor Hand)", "Scroll", "Pinch with thumb and index finger on your non-dominant hand to scroll."),
        ]
        
        for gesture in gestures:
            gesture_tree.insert("", tk.END, values=gesture)
        
        # Troubleshooting tab
        troubleshoot_tab = ttk.Frame(help_notebook)
        help_notebook.add(troubleshoot_tab, text="Troubleshooting")
        
        troubleshoot_text = """
Troubleshooting Common Issues:

1. Camera Not Working:
   - Check if another application is using the camera
   - Ensure camera permissions are granted
   - Try restarting the application
   - Check camera connections (for external cameras)

2. Poor Gesture Recognition:
   - Improve lighting conditions
   - Position yourself closer to the camera
   - Keep hand steady when making gestures
   - Ensure hand is fully visible in frame
   - Try adjusting sensitivity in Settings

3. Erratic Cursor Movement:
   - Adjust sensitivity in Settings
   - Move to a location with less background movement
   - Ensure consistent hand positioning

4. Gestures Not Responding:
   - Check if controller is running
   - Make sure hand landmarks are visible
   - Try resetting the controller
   - For clicking gestures, ensure you've entered V-gesture mode first

5. Performance Issues:
   - Close other resource-intensive applications
   - Ensure adequate system resources
   - Restart the application if needed

Need More Help?
Visit our documentation or contact support for additional assistance.
        """
        
        troubleshoot_textbox = scrolledtext.ScrolledText(troubleshoot_tab, wrap=tk.WORD, height=15)
        troubleshoot_textbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        troubleshoot_textbox.insert(tk.END, troubleshoot_text)
        troubleshoot_textbox.config(state=tk.DISABLED)
        
        # Additional Instructions tab
        instructions_tab = ttk.Frame(help_notebook)
        help_notebook.add(instructions_tab, text="Additional Instructions")
        
        instructions_text = """
Additional Instructions and Best Practices:

1. Gesture Counting Logic:
   - Each unique gesture is counted only once per detection
   - Continuous gestures (like holding a fist) are counted as a single action
   - Reset button clears all statistics and starts counting from zero

2. Using Clicking Gestures:
   - First, make a V-gesture to enter clicking mode
   - Then use fist for left click/hold, index finger for right click
   - Double click by quickly closing two raised fingers
   - Exit clicking mode by hiding your hand or making an open palm

3. Scrolling and System Controls:
   - Pinch with your non-dominant hand to scroll vertically/horizontally
   - Pinch with your dominant hand to control volume/brightness
   - Move your hand up/down while pinching to adjust values

4. Calibration Tips:
   - Find a comfortable distance where your hand fills 1/4 to 1/3 of the camera view
   - Ensure consistent lighting without shadows on your hand
   - Keep your hand relaxed and natural for best detection

5. Keyboard Shortcuts:
   - Press ESC key anytime to stop the controller
   - Use Ctrl+C in the console to exit the application completely

6. Performance Optimization:
   - Close unnecessary applications to free up system resources
   - Ensure your webcam is not being used by other applications
   - Restart the controller if you experience lag or unresponsiveness
        """
        
        instructions_textbox = scrolledtext.ScrolledText(instructions_tab, wrap=tk.WORD, height=15)
        instructions_textbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        instructions_textbox.insert(tk.END, instructions_text)
        instructions_textbox.config(state=tk.DISABLED)
    
    def start_controller(self):
        """Start the virtual mouse controller"""
        if not self.is_running:
            try:
                self.is_running = True
                self.status_var.set("Controller Running - Gesture Recognition Active")
                self.progress.start(10)
                self.start_button.config(state='disabled')
                self.stop_button.config(state='normal')
                self.root.update_idletasks()
                
                # Reset previous gestures when starting
                self.prev_gest_major = None
                self.prev_gest_minor = None
                
                # Start the gesture controller in a separate thread
                self.controller_thread = threading.Thread(target=self.run_controller, daemon=True)
                self.controller_thread.start()
                
                # Start updating dashboard
                self.update_thread = threading.Thread(target=self.continuous_update, daemon=True)
                self.update_thread.start()
            except Exception as e:
                print(f"Error starting controller: {e}")
                self.is_running = False
                self.start_button.config(state='normal')
                self.stop_button.config(state='disabled')
    
    def stop_controller(self):
        """Stop the virtual mouse controller"""
        if self.is_running:
            # Set flag to stop the controller
            self.is_running = False
            
            # Update UI immediately
            self.status_var.set("Stopping Controller...")
            self.root.update_idletasks()
            
            # Wait a bit for threads to finish
            time.sleep(0.5)
            
            # Close any open OpenCV windows
            try:
                cv2.destroyAllWindows()
            except:
                pass
            
            # Update UI state
            self.status_var.set("Controller Stopped - Ready to Start")
            self.progress.stop()
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.root.update_idletasks()
    
    def reset_statistics(self):
        """Reset all statistics to zero"""
        try:
            # Reset stats dictionary
            for key in self.stats:
                self.stats[key] = 0
            
            # Reset previous gestures
            self.prev_gest_major = None
            self.prev_gest_minor = None
            
            # Update the UI
            self.update_dashboard()
            self.status_var.set("Statistics Reset Successfully")
            self.root.update_idletasks()
        except Exception as e:
            print(f"Error resetting statistics: {e}")
    
    def run_controller(self):
        """Run the gesture controller"""
        try:
            # Override the start method to work with our UI
            handmajor = HandRecog(HLabel.MAJOR)
            handminor = HandRecog(HLabel.MINOR)
            
            # Initialize camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Cannot open camera")
                self.stop_controller()
                return
            
            CAM_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            CAM_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            
            with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:  # type: ignore
                while self.is_running and cap.isOpened():
                    success, image = cap.read()
                    
                    if not success:
                        print("Ignoring empty camera frame.")
                        continue
                    
                    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    results = hands.process(image)
                    
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                    if results.multi_hand_landmarks:  # type: ignore
                        # Classify hands
                        left, right = None, None
                        try:
                            handedness_dict = MessageToDict(results.multi_handedness[0])  # type: ignore
                            if handedness_dict['classification'][0]['label'] == 'Right':
                                right = results.multi_hand_landmarks[0]  # type: ignore
                            else:
                                left = results.multi_hand_landmarks[0]  # type: ignore
                        except:
                            pass
                        
                        try:
                            handedness_dict = MessageToDict(results.multi_handedness[1])  # type: ignore
                            if handedness_dict['classification'][0]['label'] == 'Right':
                                right = results.multi_hand_landmarks[1]  # type: ignore
                            else:
                                left = results.multi_hand_landmarks[1]  # type: ignore
                        except:
                            pass
                        
                        # Determine dominant hand
                        dom_hand = True  # Right hand is dominant by default
                        hr_major = right if dom_hand else left
                        hr_minor = left if dom_hand else right
                        
                        # Update hand results
                        handmajor.update_hand_result(hr_major)
                        handminor.update_hand_result(hr_minor)
                        
                        # Compute finger states
                        handmajor.set_finger_state()
                        handminor.set_finger_state()
                        
                        # Handle gestures for major hand
                        if hr_major is not None:
                            gest_major = handmajor.get_gesture()
                            # Only count if this is a new gesture (different from previous)
                            if gest_major != self.prev_gest_major:
                                self.update_gesture_stats(gest_major)
                                self.prev_gest_major = gest_major
                            Controller.handle_controls(gest_major, handmajor.hand_result)  # type: ignore
                        
                        # Handle gestures for minor hand
                        if hr_minor is not None:
                            gest_minor = handminor.get_gesture()
                            # Only count if this is a new gesture (different from previous)
                            if gest_minor != self.prev_gest_minor:
                                self.update_gesture_stats(gest_minor)
                                self.prev_gest_minor = gest_minor
                            Controller.handle_controls(gest_minor, handminor.hand_result)  # type: ignore
                        
                        # Draw landmarks if enabled
                        if self.show_landmarks_var.get():
                            for hand_landmarks in results.multi_hand_landmarks:  # type: ignore
                                mp_drawing.draw_landmarks(  # type: ignore
                                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)  # type: ignore
                    
                    else:
                        # No hands detected, reset previous gestures
                        self.prev_gest_major = None
                        self.prev_gest_minor = None
                        Controller.prev_hand = None
                    
                    # Display the image
                    cv2.imshow('AI Virtual Mouse - Press ESC to stop', image)
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  # ESC key to stop
                        self.is_running = False
                        break
            
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.stop_controller()
    
    def update_gesture_stats(self, gesture):
        """Update gesture statistics"""
        if gesture == Gest.FIST:
            self.stats['fist_count'] += 1
        elif gesture in [Gest.PINCH_MAJOR, Gest.PINCH_MINOR]:
            self.stats['pinch_count'] += 1
        elif gesture == Gest.V_GEST:
            self.stats['v_gest_count'] += 1
        elif gesture == Gest.MID:
            self.stats['click_count'] += 1
        elif gesture == Gest.INDEX:
            self.stats['right_click_count'] += 1
        elif gesture == Gest.TWO_FINGER_CLOSED:
            self.stats['double_click_count'] += 1
        elif gesture in [Gest.PINCH_MAJOR, Gest.PINCH_MINOR]:
            self.stats['scroll_count'] += 1
    
    def continuous_update(self):
        """Continuously update the dashboard"""
        while self.is_running:
            try:
                # Use root.after to update in the main thread
                self.root.after(0, self.update_dashboard)
                time.sleep(0.5)  # Update more frequently
            except:
                break
    
    def update_dashboard(self):
        """Update the dashboard with current statistics"""
        try:
            self.fist_count_var.set(str(self.stats['fist_count']))
            self.pinch_count_var.set(str(self.stats['pinch_count']))
            self.v_gest_count_var.set(str(self.stats['v_gest_count']))
            self.click_count_var.set(str(self.stats['click_count']))
            self.right_click_count_var.set(str(self.stats['right_click_count']))
            self.double_click_count_var.set(str(self.stats['double_click_count']))
            self.scroll_count_var.set(str(self.stats['scroll_count']))
            
            # Update system info
            try:
                mouse_pos = pyautogui.position()
                screen_width, screen_height = pyautogui.size()
                info_text = f"Screen Resolution: {screen_width}x{screen_height} | "
                info_text += f"Mouse Position: ({mouse_pos[0]}, {mouse_pos[1]}) | "
                info_text += "Status: " + ("Running" if self.is_running else "Stopped")
                self.info_label.config(text=info_text)
            except:
                pass
        except:
            pass
    
    def draw_gesture_visualization(self):
        """Draw a more detailed visualization of hand gestures"""
        self.gesture_canvas.delete("all")
        
        # Draw a gradient background
        for i in range(200):
            r = int(52 + (i * (52 - 52)) / 200)
            g = int(73 + (i * (73 - 73)) / 200)
            b = int(94 + (i * (94 - 94)) / 200)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.gesture_canvas.create_line(0, i, 250, i, fill=color)
        
        # Draw a more detailed hand outline
        # Palm
        self.gesture_canvas.create_oval(75, 50, 175, 150, outline="#ecf0f1", width=3, fill="")
        
        # Wrist
        self.gesture_canvas.create_line(80, 145, 170, 145, fill="#ecf0f1", width=4)
        
        # Thumb
        self.gesture_canvas.create_line(75, 90, 50, 70, fill="#ecf0f1", width=5)
        self.gesture_canvas.create_line(50, 70, 40, 60, fill="#ecf0f1", width=3)
        
        # Index finger
        self.gesture_canvas.create_line(110, 50, 110, 20, fill="#3498db", width=4)
        self.gesture_canvas.create_line(110, 20, 110, 10, fill="#3498db", width=3)
        
        # Middle finger (highlighted for V gesture)
        self.gesture_canvas.create_line(130, 45, 130, 15, fill="#27ae60", width=5)
        self.gesture_canvas.create_line(130, 15, 130, 5, fill="#27ae60", width=4)
        
        # Ring finger
        self.gesture_canvas.create_line(150, 50, 150, 25, fill="#ecf0f1", width=4)
        self.gesture_canvas.create_line(150, 25, 150, 18, fill="#ecf0f1", width=3)
        
        # Pinky
        self.gesture_canvas.create_line(170, 60, 175, 40, fill="#ecf0f1", width=3)
        self.gesture_canvas.create_line(175, 40, 180, 30, fill="#ecf0f1", width=2)
        
        # Labels
        self.gesture_canvas.create_text(125, 170, text="V Gesture Active", fill="#27ae60", font=('Arial', 10, 'bold'))
        self.gesture_canvas.create_text(125, 185, text="Ready for Clicking", fill="#ecf0f1", font=('Arial', 8))
    
    def exit_app(self):
        """Exit the application"""
        self.stop_controller()
        self.root.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = VirtualMouseUI(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()

if __name__ == "__main__":
    main()
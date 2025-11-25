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
import os
import numpy as np
from PIL import Image, ImageTk
from ai_virtual_mouse import Gest, HLabel, HandRecog, Controller, GestureController
from auth import AuthenticationManager

try:
    import mediapipe.python.solutions.drawing_utils as drawing_utils
    import mediapipe.python.solutions.hands as hands_module
    mp_drawing = drawing_utils
    mp_hands = hands_module
except ImportError:
    
    mp_drawing = mp.solutions.drawing_utils  # type: ignore
    mp_hands = mp.solutions.hands  # type: ignore

class VirtualMouseUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Virtual Mouse Controller")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#1e3d59")
        

        self.auth_manager = AuthenticationManager()
        
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
        

        self.prev_gest_major = None
        self.prev_gest_minor = None
        
        # Settings variables
        self.multi_hand_mode = tk.BooleanVar(value=True)
        self.hand_detection_confidence = tk.DoubleVar(value=0.7)
        self.tracking_confidence = tk.DoubleVar(value=0.7)
        self.show_landmarks_var = tk.BooleanVar(value=True)
        self.mouse_sensitivity = tk.DoubleVar(value=1.0)
        self.scroll_speed = tk.DoubleVar(value=1.0)
        self.click_delay = tk.DoubleVar(value=0.3)
        self.gesture_mode = tk.StringVar(value="Basic")
        self.theme_color = tk.StringVar(value="Blue")
        self.autoclick_enabled = tk.BooleanVar(value=False)
        self.autoclick_delay = tk.DoubleVar(value=1.0)
        
        self.fist_count_var = tk.StringVar(value="0")
        self.pinch_count_var = tk.StringVar(value="0")
        self.v_gest_count_var = tk.StringVar(value="0")
        self.click_count_var = tk.StringVar(value="0")
        self.right_click_count_var = tk.StringVar(value="0")
        self.double_click_count_var = tk.StringVar(value="0")
        self.scroll_count_var = tk.StringVar(value="0")
  
        self.image_references = []
     
        self.show_authentication_popup()
    
    def show_authentication_popup(self):
        """Show authentication popup within the main window"""
     
        self.overlay_frame = tk.Frame(self.root, bg="#000000")
        self.overlay_frame.place(x=0, y=0, relwidth=1, relheight=1)
  
        self.auth_frame = tk.Frame(self.root, bg="#2c3e50", relief=tk.RAISED, bd=2)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.auth_frame.configure(width=500, height=400)
       
        title_label = tk.Label(self.auth_frame, text="AI Virtual Mouse Controller", 
                              font=("Arial", 16, "bold"), bg="#2c3e50", fg="#f5f0e1")
        title_label.pack(pady=20)
        
        notebook = ttk.Notebook(self.auth_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        

        style = ttk.Style()
        style.configure("Auth.TNotebook", background="#2c3e50")
        style.configure("Auth.TNotebook.Tab", background="#3a506b", foreground="#f5f0e1", 
                       padding=[20, 10], font=("Arial", 12, "bold"))
        style.map("Auth.TNotebook.Tab", background=[("selected", "#5bc0be")], 
                  foreground=[("selected", "#1e3d59")])
        
        # Login tab
        login_tab = tk.Frame(notebook, bg="#2c3e50")
        notebook.add(login_tab, text="Login")
        
        # Register tab
        register_tab = tk.Frame(notebook, bg="#2c3e50")
        notebook.add(register_tab, text="Register")
        
        # Create login form
        self.create_login_form(login_tab)
        
        # Create register form
        self.create_register_form(register_tab)
    
    def create_login_form(self, parent):
        """Create login form"""
        # Title
        title_label = tk.Label(parent, text="Login to Your Account", 
                              font=("Arial", 14, "bold"), bg="#2c3e50", fg="#f5f0e1")
        title_label.pack(pady=15)
        
        # Form container
        form_frame = tk.Frame(parent, bg="#2c3e50")
        form_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        # Username
        username_frame = tk.Frame(form_frame, bg="#2c3e50")
        username_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(username_frame, text="Username:", font=("Arial", 12), 
                 bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
        
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12), width=25)
        self.username_entry.pack(pady=5, fill=tk.X, ipady=5)
        
        # Password
        password_frame = tk.Frame(form_frame, bg="#2c3e50")
        password_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(password_frame, text="Password:", font=("Arial", 12), 
                 bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
        
        self.password_entry = tk.Entry(password_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.pack(pady=5, fill=tk.X, ipady=5)
        
        # Status label
        self.login_status_label = tk.Label(form_frame, text="", font=("Arial", 10), 
                                          bg="#2c3e50", fg="#e74c3c")
        self.login_status_label.pack(pady=10)
        
        # Login button
        login_button = tk.Button(form_frame, text="Login", font=("Arial", 12, "bold"),
                                bg="#3498db", fg="white", width=15, height=1,
                                command=self.authenticate_user)
        login_button.pack(pady=15)
        
        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda event: self.authenticate_user())
        self.username_entry.focus()
    
    def create_register_form(self, parent):
        """Create registration form"""
        # Title
        title_label = tk.Label(parent, text="Create New Account", 
                              font=("Arial", 14, "bold"), bg="#2c3e50", fg="#f5f0e1")
        title_label.pack(pady=15)
        
        # Form container
        form_frame = tk.Frame(parent, bg="#2c3e50")
        form_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        # Username
        username_frame = tk.Frame(form_frame, bg="#2c3e50")
        username_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(username_frame, text="Username:", font=("Arial", 12), 
                 bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
        
        self.reg_username_entry = tk.Entry(username_frame, font=("Arial", 12), width=25)
        self.reg_username_entry.pack(pady=5, fill=tk.X, ipady=5)
        
        # Password
        password_frame = tk.Frame(form_frame, bg="#2c3e50")
        password_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(password_frame, text="Password:", font=("Arial", 12), 
                 bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
        
        self.reg_password_entry = tk.Entry(password_frame, font=("Arial", 12), width=25, show="*")
        self.reg_password_entry.pack(pady=5, fill=tk.X, ipady=5)
        
        # Confirm Password
        confirm_frame = tk.Frame(form_frame, bg="#2c3e50")
        confirm_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(confirm_frame, text="Confirm Password:", font=("Arial", 12), 
                 bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
        
        self.reg_confirm_entry = tk.Entry(confirm_frame, font=("Arial", 12), width=25, show="*")
        self.reg_confirm_entry.pack(pady=5, fill=tk.X, ipady=5)
        
        # Status label
        self.register_status_label = tk.Label(form_frame, text="", font=("Arial", 10), 
                                             bg="#2c3e50", fg="#e74c3c")
        self.register_status_label.pack(pady=10)
        
        # Register button
        register_button = tk.Button(form_frame, text="Register", font=("Arial", 12, "bold"),
                                   bg="#27ae60", fg="white", width=15, height=1,
                                   command=self.register_user)
        register_button.pack(pady=15)
        
        # Bind Enter key to register
        self.reg_confirm_entry.bind('<Return>', lambda event: self.register_user())
    
    def authenticate_user(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.login_status_label.config(text="Please enter both username and password", fg="#e74c3c")
            return
        
        # Authenticate user
        success, message = self.auth_manager.authenticate_user(username, password)
        if success:
            self.login_status_label.config(text=message, fg="#27ae60")
         
            self.root.after(1000, self.show_image_capture_popup)
        else:
            self.login_status_label.config(text=message, fg="#e74c3c")
    
    def register_user(self):
        """Handle registration"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_entry.get()
        
        if not username or not password or not confirm_password:
            self.register_status_label.config(text="Please fill in all fields", fg="#e74c3c")
            return
        
        if password != confirm_password:
            self.register_status_label.config(text="Passwords do not match", fg="#e74c3c")
            return
        
   
        success, message = self.auth_manager.add_user(username, password)
        if success:
            self.register_status_label.config(text=message, fg="#27ae60")
         
            self.reg_username_entry.delete(0, tk.END)
            self.reg_password_entry.delete(0, tk.END)
            self.reg_confirm_entry.delete(0, tk.END)
            # Show success message
            self.register_status_label.after(2000, lambda: self.register_status_label.config(text="You can now login", fg="#27ae60"))
        else:
            self.register_status_label.config(text=message, fg="#e74c3c")
    
    def show_image_capture_popup(self):
        """Show image capture popup"""
       
        self.auth_frame.destroy()
        self.overlay_frame.destroy()
   
        self.overlay_frame = tk.Frame(self.root, bg="#000000")
        self.overlay_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.capture_frame = tk.Frame(self.root, bg="#2c3e50", relief=tk.RAISED, bd=2)
        self.capture_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.capture_frame.configure(width=500, height=400)
        
        username = self.auth_manager.get_current_user()
        
        # Title
        title_label = tk.Label(self.capture_frame, text=f"Welcome {username}!", 
                              font=("Arial", 14, "bold"), bg="#2c3e50", fg="#f5f0e1")
        title_label.pack(pady=10)
        
        instruction_label = tk.Label(self.capture_frame, 
                                    text="Please position your face in the camera view and click Capture", 
                                    font=("Arial", 10), bg="#2c3e50", fg="#f5f0e1")
        instruction_label.pack(pady=5)
        
        # Video frame
        video_frame = tk.Frame(self.capture_frame, bg="#3a506b", width=300, height=200)
        video_frame.pack(pady=15)
        video_frame.pack_propagate(False)

        self.video_label = tk.Label(video_frame, bg="#3a506b")
        self.video_label.pack(fill=tk.BOTH, expand=True)

        self.capture_status_label = tk.Label(self.capture_frame, text="", font=("Arial", 10), 
                                            bg="#2c3e50", fg="#f5f0e1")
        self.capture_status_label.pack(pady=5)

        button_frame = tk.Frame(self.capture_frame, bg="#2c3e50")
        button_frame.pack(pady=10)
        
        capture_button = tk.Button(button_frame, text="Capture Image", font=("Arial", 10, "bold"),
                                  bg="#27ae60", fg="white", width=12, height=1,
                                  command=self.capture_image)
        capture_button.pack(side=tk.LEFT, padx=10)

        skip_button = tk.Button(button_frame, text="Skip", font=("Arial", 10, "bold"),
                               bg="#e74c3c", fg="white", width=12, height=1,
                               command=self.skip_capture)
        skip_button.pack(side=tk.LEFT, padx=10)
        
        # Video capture
        self.cap = cv2.VideoCapture(0)
        
        # Start video update
        self.update_frame()
    
    def update_frame(self):
        """Update video frame"""
        if hasattr(self, 'capture_frame') and self.capture_frame.winfo_exists():
            ret, frame = self.cap.read()
            if ret:
            
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (300, 200))
                img = Image.fromarray(frame_resized)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.configure(image=imgtk)
                self.image_references.append(imgtk)
  
            self.capture_frame.after(10, self.update_frame)
    
    def capture_image(self):
        """Capture and save user image"""
        ret, frame = self.cap.read()
        if ret:
            # Get current user
            username = self.auth_manager.get_current_user()
            
            # Create image path
            image_filename = f"{username}.jpg"
            image_path = os.path.join("users", "images", image_filename)
            
            # Save image
            cv2.imwrite(image_path, frame)
            
            # Update user data
            self.auth_manager.set_user_image(username, image_path)
            
            self.capture_status_label.config(text="Image captured successfully!", fg="#27ae60")
            
            # Close window and proceed
            self.root.after(1000, self.finish_authentication)
    
    def skip_capture(self):
        """Skip image capture"""
        self.cap.release()
        self.capture_frame.destroy()
        self.overlay_frame.destroy()
        self.create_main_ui()
    
    def finish_authentication(self):
        """Finish authentication and show main UI"""
        self.cap.release()
        self.capture_frame.destroy()
        self.overlay_frame.destroy()
        self.create_main_ui()
    
    def create_main_ui(self):
        """Create the main UI after successful authentication"""

        self.image_references.clear()
        self.create_widgets()
        self.update_dashboard()
    
    def create_widgets(self):
        """Create all UI widgets"""
        main_frame = tk.Frame(self.root, bg="#1e3d59")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        top_frame = tk.Frame(main_frame, bg="#1e3d59")
        top_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = tk.Label(top_frame, text="AI Virtual Mouse Controller", 
                              font=("Arial", 20, "bold"), bg="#1e3d59", fg="#f5f0e1")
        title_label.pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Ready to start controller")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                             font=("Arial", 11), bg="#2c3e50", fg="#f5f0e1", 
                             relief=tk.SUNKEN, anchor=tk.W, height=2)

        style = ttk.Style()
        style.configure("Custom.TNotebook", background="#1e3d59")
        style.configure("Custom.TNotebook.Tab", background="#3a506b", foreground="#f5f0e1", 
                       padding=[25, 10], font=("Arial", 12, "bold"))
        style.map("Custom.TNotebook.Tab", background=[("selected", "#5bc0be")], 
                  foreground=[("selected", "#1e3d59")])
        
        tab_control = ttk.Notebook(main_frame, style="Custom.TNotebook")
        tab_control.pack(fill=tk.BOTH, expand=True)

        dashboard_tab = tk.Frame(tab_control, bg="#1e3d59")
        tab_control.add(dashboard_tab, text="Dashboard")
 
        settings_tab = tk.Frame(tab_control, bg="#1e3d59")
        tab_control.add(settings_tab, text="Settings")

        help_tab = tk.Frame(tab_control, bg="#1e3d59")
        tab_control.add(help_tab, text="Help & Instructions")
        self.create_dashboard_tab(dashboard_tab)
        self.create_settings_tab(settings_tab)
        self.create_help_tab(help_tab)
    
    def create_dashboard_tab(self, parent):
        """Create the dashboard tab"""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        left_frame = tk.Frame(parent, bg="#3a506b", relief=tk.RAISED, bd=2)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        controls_title = tk.Label(left_frame, text="CONTROLS", font=("Arial", 16, "bold"), 
                                 bg="#3a506b", fg="#f5f0e1")
        controls_title.pack(fill=tk.X, pady=10)
        button_frame = tk.Frame(left_frame, bg="#3a506b")
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        self.start_button = tk.Button(button_frame, text="Start Controller", 
                                     bg="#27ae60", fg="white", font=("Arial", 12, "bold"),
                                     command=self.start_controller, width=20, height=2)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(button_frame, text="Stop Controller", 
                                    bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                                    command=self.stop_controller, state=tk.DISABLED, width=20, height=2)
        self.stop_button.pack(pady=5)
        reset_button = tk.Button(button_frame, text="Reset Statistics", 
                                bg="#3498db", fg="white", font=("Arial", 12, "bold"),
                                command=self.reset_statistics, width=20, height=2)
        reset_button.pack(pady=5)
        dashboard_title = tk.Label(left_frame, text="GESTURE STATISTICS", font=("Arial", 16, "bold"), 
                                  bg="#3a506b", fg="#f5f0e1")
        dashboard_title.pack(fill=tk.X, pady=(20, 10))

        stats_frame = tk.Frame(left_frame, bg="#3a506b")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        stat_configs = [
            ("Fist Gestures:", self.fist_count_var, "#e74c3c"),
            ("Pinch Gestures:", self.pinch_count_var, "#f39c12"),
            ("V Gestures:", self.v_gest_count_var, "#2ecc71"),
            ("Left Clicks:", self.click_count_var, "#3498db"),
            ("Right Clicks:", self.right_click_count_var, "#9b59b6"),
            ("Double Clicks:", self.double_click_count_var, "#1abc9c"),
            ("Scroll Actions:", self.scroll_count_var, "#e67e22")
        ]
        
        for i, (label_text, var, color) in enumerate(stat_configs):
            stat_bg = "#2c3e50" if i % 2 == 0 else "#3a506b"
            stat_frame = tk.Frame(stats_frame, bg=stat_bg, relief=tk.RAISED, bd=1)
            stat_frame.pack(fill=tk.X, pady=3)
            
            label = tk.Label(stat_frame, text=label_text, font=("Arial", 12, "bold"), 
                            bg=stat_bg, fg="#f5f0e1", anchor=tk.W)
            label.pack(side=tk.LEFT, padx=10, pady=5)
            
            value_label = tk.Label(stat_frame, textvariable=var, font=("Arial", 14, "bold"), 
                                  bg=stat_bg, fg="#f5f0e1")
            value_label.pack(side=tk.RIGHT, padx=10, pady=5)

        right_frame = tk.Frame(parent, bg="#2c3e50")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_frame.grid_rowconfigure(1, weight=1)
        visual_title = tk.Label(right_frame, text="GESTURE VISUALIZATION", font=("Arial", 16, "bold"), 
                               bg="#2c3e50", fg="#f5f0e1")
        visual_title.pack(fill=tk.X, pady=10)
        self.gesture_canvas = tk.Canvas(right_frame, bg="#3a506b", width=300, height=300)
        self.gesture_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        info_text = tk.Label(right_frame, text="Start the controller to see gesture visualization", 
                            font=("Arial", 11), bg="#2c3e50", fg="#f5f0e1")
        info_text.pack(pady=10)
    
    def create_settings_tab(self, parent):
        """Create the settings tab with proper alignment and margins"""

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        settings_main = tk.Frame(parent, bg="#1e3d59")
        settings_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        settings_title = tk.Label(settings_main, text="CONTROLLER SETTINGS", 
                                 font=("Arial", 18, "bold"), bg="#1e3d59", fg="#f5f0e1")
        settings_title.pack(pady=(0, 20))
     
        settings_container = tk.Frame(settings_main, bg="#1e3d59")
        settings_container.pack(fill=tk.BOTH, expand=True)
        settings_canvas = tk.Canvas(settings_container, bg="#1e3d59", highlightthickness=0)
        settings_scrollbar = tk.Scrollbar(settings_container, orient="vertical", command=settings_canvas.yview)
        settings_frame = tk.Frame(settings_canvas, bg="#1e3d59")
        
        settings_frame.bind(
            "<Configure>",
            lambda e: settings_canvas.configure(
                scrollregion=settings_canvas.bbox("all")
            )
        )
        
        settings_canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        profile_frame = tk.LabelFrame(settings_frame, text="User Profile", font=("Arial", 14, "bold"), 
                                     bg="#2c3e50", fg="#5bc0be", padx=20, pady=20)
        profile_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        current_user = self.auth_manager.get_current_user()
        if current_user:
            user_label = tk.Label(profile_frame, text=f"Logged in as: {current_user}", 
                                 font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1")
            user_label.pack(anchor=tk.W, pady=(0, 10))
            user_image_path = self.auth_manager.get_user_image_path(current_user)
            if user_image_path and os.path.exists(user_image_path):
                try:
                    user_img = Image.open(user_image_path)
                    user_img = user_img.resize((100, 100))
                    user_photo = ImageTk.PhotoImage(user_img)
                    img_label = tk.Label(profile_frame, image=user_photo, bg="#2c3e50")
                    img_label.pack(pady=(0, 10))
                    self.image_references.append(user_photo)
                except:
                    pass
        
        # Logout button
        logout_button = tk.Button(profile_frame, text="Logout", 
                                 bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                                 command=self.logout_user, width=20, height=2)
        logout_button.pack(pady=10)
        
        # MOUSE CONTROL SETTINGS
        mouse_frame = tk.LabelFrame(settings_frame, text="Mouse Control", font=("Arial", 14, "bold"), 
                                   bg="#2c3e50", fg="#5bc0be", padx=20, pady=20)
        mouse_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        
        # Mouse sensitivity
        sensitivity_frame = tk.Frame(mouse_frame, bg="#2c3e50")
        sensitivity_frame.pack(fill=tk.X, pady=10)
        
        sensitivity_label = tk.Label(sensitivity_frame, text="Mouse Sensitivity:", 
                                    font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1")
        sensitivity_label.pack(side=tk.LEFT)
        
        sensitivity_scale = tk.Scale(sensitivity_frame, from_=0.1, to=3.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, variable=self.mouse_sensitivity,
                                    bg="#2c3e50", length=400, fg="#f5f0e1", troughcolor="#3a506b")
        sensitivity_scale.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Scroll speed
        scroll_frame = tk.Frame(mouse_frame, bg="#2c3e50")
        scroll_frame.pack(fill=tk.X, pady=10)
        
        scroll_label = tk.Label(scroll_frame, text="Scroll Speed:", 
                               font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1")
        scroll_label.pack(side=tk.LEFT)
        
        scroll_scale = tk.Scale(scroll_frame, from_=0.5, to=3.0, resolution=0.1,
                               orient=tk.HORIZONTAL, variable=self.scroll_speed,
                               bg="#2c3e50", length=400, fg="#f5f0e1", troughcolor="#3a506b")
        scroll_scale.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Click delay
        delay_frame = tk.Frame(mouse_frame, bg="#2c3e50")
        delay_frame.pack(fill=tk.X, pady=10)
        
        delay_label = tk.Label(delay_frame, text="Click Delay (sec):", 
                              font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1")
        delay_label.pack(side=tk.LEFT)
        
        delay_scale = tk.Scale(delay_frame, from_=0.1, to=1.0, resolution=0.1,
                              orient=tk.HORIZONTAL, variable=self.click_delay,
                              bg="#2c3e50", length=400, fg="#f5f0e1", troughcolor="#3a506b")
        delay_scale.pack(side=tk.RIGHT, padx=(10, 0))
        
        # AUTOMATIC CLICKING
        auto_frame = tk.LabelFrame(settings_frame, text="Automatic Clicking", font=("Arial", 14, "bold"), 
                                  bg="#2c3e50", fg="#5bc0be", padx=20, pady=20)
        auto_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        
        # Auto-click enabled
        auto_check = tk.Checkbutton(auto_frame, text="Enable Auto-click", 
                                   variable=self.autoclick_enabled,
                                   font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1",
                                   selectcolor="#3a506b", activebackground="#2c3e50")
        auto_check.pack(anchor=tk.W)
        
        # Auto-click delay
        auto_delay_frame = tk.Frame(auto_frame, bg="#2c3e50")
        auto_delay_frame.pack(fill=tk.X, pady=10)
        
        auto_delay_label = tk.Label(auto_delay_frame, text="Auto-click Delay:", 
                                   font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1")
        auto_delay_label.pack(side=tk.LEFT)
        
        auto_delay_scale = tk.Scale(auto_delay_frame, from_=0.5, to=5.0, resolution=0.1,
                                   orient=tk.HORIZONTAL, variable=self.autoclick_delay,
                                   bg="#2c3e50", length=400, fg="#f5f0e1", troughcolor="#3a506b")
        auto_delay_scale.pack(side=tk.RIGHT, padx=(10, 0))
        
        # GESTURE SETTINGS
        gesture_frame = tk.LabelFrame(settings_frame, text="Gesture Settings", font=("Arial", 14, "bold"), 
                                     bg="#2c3e50", fg="#5bc0be", padx=20, pady=20)
        gesture_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        
        # Gesture mode dropdown
        mode_frame = tk.Frame(gesture_frame, bg="#2c3e50")
        mode_frame.pack(fill=tk.X, pady=10)
        
        mode_label = tk.Label(mode_frame, text="Gesture Mode:", 
                             font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1")
        mode_label.pack(side=tk.LEFT)
        
        mode_options = ["Basic", "Advanced", "Gaming"]
        mode_dropdown = ttk.Combobox(mode_frame, textvariable=self.gesture_mode, 
                                    values=mode_options, state="readonly", width=20)
        mode_dropdown.pack(side=tk.RIGHT, padx=(10, 0))
        mode_dropdown.set("Basic")
        
        # Multi-hand mode
        multi_hand_frame = tk.Frame(gesture_frame, bg="#2c3e50")
        multi_hand_frame.pack(fill=tk.X, pady=10)
        
        multi_hand_check = tk.Checkbutton(multi_hand_frame, text="Enable Multi-Hand Mode", 
                                         variable=self.multi_hand_mode,
                                         font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1",
                                         selectcolor="#3a506b", activebackground="#2c3e50")
        multi_hand_check.pack(anchor=tk.W)
        
        # DETECTION SETTINGS
        detection_frame = tk.LabelFrame(settings_frame, text="Detection Settings", font=("Arial", 14, "bold"), 
                                       bg="#2c3e50", fg="#5bc0be", padx=20, pady=20)
        detection_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        
        # Hand detection confidence
        detection_conf_frame = tk.Frame(detection_frame, bg="#2c3e50")
        detection_conf_frame.pack(fill=tk.X, pady=10)
        
        detection_label = tk.Label(detection_conf_frame, text="Detection Confidence:", 
                                  font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1")
        detection_label.pack(side=tk.LEFT)
        
        detection_scale = tk.Scale(detection_conf_frame, from_=0.1, to=1.0, resolution=0.1,
                                  orient=tk.HORIZONTAL, variable=self.hand_detection_confidence,
                                  bg="#2c3e50", length=400, fg="#f5f0e1", troughcolor="#3a506b")
        detection_scale.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Tracking confidence
        tracking_conf_frame = tk.Frame(detection_frame, bg="#2c3e50")
        tracking_conf_frame.pack(fill=tk.X, pady=10)
        
        tracking_label = tk.Label(tracking_conf_frame, text="Tracking Confidence:", 
                                 font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1")
        tracking_label.pack(side=tk.LEFT)
        
        tracking_scale = tk.Scale(tracking_conf_frame, from_=0.1, to=1.0, resolution=0.1,
                                 orient=tk.HORIZONTAL, variable=self.tracking_confidence,
                                 bg="#2c3e50", length=400, fg="#f5f0e1", troughcolor="#3a506b")
        tracking_scale.pack(side=tk.RIGHT, padx=(10, 0))
        
        # VISUALIZATION SETTINGS
        vis_frame = tk.LabelFrame(settings_frame, text="Visualization Settings", font=("Arial", 14, "bold"), 
                                 bg="#2c3e50", fg="#5bc0be", padx=20, pady=20)
        vis_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        
        # Show landmarks
        landmarks_frame = tk.Frame(vis_frame, bg="#2c3e50")
        landmarks_frame.pack(fill=tk.X, pady=10)
        
        landmarks_check = tk.Checkbutton(landmarks_frame, text="Show Hand Landmarks", 
                                        variable=self.show_landmarks_var,
                                        font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1",
                                        selectcolor="#3a506b", activebackground="#2c3e50")
        landmarks_check.pack(anchor=tk.W)
        
        # Theme color dropdown
        theme_frame = tk.Frame(vis_frame, bg="#2c3e50")
        theme_frame.pack(fill=tk.X, pady=10)
        
        theme_label = tk.Label(theme_frame, text="Theme Color:", 
                              font=("Arial", 12), bg="#2c3e50", fg="#f5f0e1")
        theme_label.pack(side=tk.LEFT)
        
        theme_options = ["Blue", "Green", "Purple", "Orange"]
        theme_dropdown = ttk.Combobox(theme_frame, textvariable=self.theme_color, 
                                     values=theme_options, state="readonly", width=20)
        theme_dropdown.pack(side=tk.RIGHT, padx=(10, 0))
        theme_dropdown.set("Blue")
        
        # Save settings button
        save_frame = tk.Frame(settings_frame, bg="#1e3d59")
        save_frame.pack(fill=tk.X, pady=(20, 0), padx=20)
        
        save_button = tk.Button(save_frame, text="Save Settings", 
                               bg="#2ecc71", fg="white", font=("Arial", 12, "bold"),
                               command=self.save_settings, width=20, height=2)
        save_button.pack()
        
        # Pack scrollbar
        settings_canvas.pack(side="left", fill="both", expand=True)
        settings_scrollbar.pack(side="right", fill="y")
    
    def create_help_tab(self, parent):
        """Create the help tab with sub-tabs"""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        help_main = tk.Frame(parent, bg="#1e3d59")
        help_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        sub_tab_control = ttk.Notebook(help_main)
        sub_tab_control.pack(fill=tk.BOTH, expand=True)
        style = ttk.Style()
        style.configure("Sub.TNotebook", background="#1e3d59")
        style.configure("Sub.TNotebook.Tab", background="#3a506b", foreground="#f5f0e1", 
                       padding=[20, 8], font=("Arial", 11, "bold"))
        style.map("Sub.TNotebook.Tab", background=[("selected", "#5bc0be")], 
                  foreground=[("selected", "#1e3d59")])
        start_tab = tk.Frame(sub_tab_control, bg="#2c3e50")
        sub_tab_control.add(start_tab, text="Getting Started")
        gestures_tab = tk.Frame(sub_tab_control, bg="#2c3e50")
        sub_tab_control.add(gestures_tab, text="Gestures")
        troubleshoot_tab = tk.Frame(sub_tab_control, bg="#2c3e50")
        sub_tab_control.add(troubleshoot_tab, text="Troubleshooting")

        self.create_start_guide(start_tab)
        self.create_gestures_guide(gestures_tab)
        self.create_troubleshoot_guide(troubleshoot_tab)
    
    def create_start_guide(self, parent):
        """Create getting started guide"""
        title = tk.Label(parent, text="Getting Started Guide", 
                        font=("Arial", 18, "bold"), bg="#2c3e50", fg="#f5f0e1")
        title.pack(pady=20)
        content_frame = tk.Frame(parent, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        guide_text = """Welcome to the AI Virtual Mouse Controller!

1. SYSTEM REQUIREMENTS:
   - Webcam with good quality
   - Adequate lighting
   - Python 3.7 or higher
   - Required packages installed

2. INITIAL SETUP:
   - Ensure your webcam is connected and working
   - Position yourself comfortably in front of the camera
   - Make sure there is sufficient lighting on your hands

3. STARTING THE CONTROLLER:
   - Click on the 'Dashboard' tab
   - Click the 'Start Controller' green button
   - Allow camera access if prompted
   - Position your hand in the camera view

4. BASIC USAGE:
   - Move your open palm to control the cursor
   - Make a V-sign to enter clicking mode
   - Make a fist to click and hold
   - Use pinch gestures for scrolling and volume control

5. STOPPING THE CONTROLLER:
   - Click the 'Stop Controller' red button
   - Or press ESC key in the camera window

6. CUSTOMIZATION:
   - Use the 'Settings' tab to adjust sensitivity
   - Modify hand detection parameters
   - Change visualization options
"""
        
        text_widget = tk.Text(content_frame, font=("Arial", 11), bg="#3a506b", fg="#f5f0e1", 
                             wrap=tk.WORD, padx=15, pady=15, relief=tk.FLAT)
        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_gestures_guide(self, parent):
        """Create gestures guide"""
        title = tk.Label(parent, text="Gesture Controls", 
                        font=("Arial", 18, "bold"), bg="#2c3e50", fg="#f5f0e1")
        title.pack(pady=20)
        content_frame = tk.Frame(parent, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        gestures_frame = tk.Frame(content_frame, bg="#2c3e50")
        gestures_frame.pack(fill=tk.BOTH, expand=True)
        gestures = [
            ("Open Palm", "Move cursor around screen", "#3498db"),
            ("V Sign", "Enter clicking mode (index & middle finger spread)", "#2ecc71"),
            ("Fist", "Left click and hold (when in V mode)", "#e74c3c"),
            ("Index Finger", "Right click (when in V mode)", "#9b59b6"),
            ("Two Fingers Closed", "Double click (when in V mode)", "#f1c40f"),
            ("Pinch (Major Hand)", "Control brightness/volume", "#e67e22"),
            ("Pinch (Minor Hand)", "Scroll up/down", "#1abc9c")
        ]
        
        for i, (gesture, description, color) in enumerate(gestures):
            gesture_frame = tk.Frame(gestures_frame, bg="#3a506b", relief=tk.RAISED, bd=1)
            gesture_frame.pack(fill=tk.X, pady=5, padx=10)
            
            gesture_label = tk.Label(gesture_frame, text=gesture, font=("Arial", 12, "bold"), 
                                    bg="#3a506b", fg=color, width=20, anchor=tk.W)
            gesture_label.pack(side=tk.LEFT, padx=10, pady=5)
            
            desc_label = tk.Label(gesture_frame, text=description, font=("Arial", 11), 
                                 bg="#3a506b", fg="#f5f0e1", wraplength=400, justify=tk.LEFT)
            desc_label.pack(side=tk.LEFT, padx=(10, 0), pady=5)
    
    def create_troubleshoot_guide(self, parent):
        """Create troubleshooting guide"""
        title = tk.Label(parent, text="Troubleshooting Guide", 
                        font=("Arial", 18, "bold"), bg="#2c3e50", fg="#f5f0e1")
        title.pack(pady=20)
        content_frame = tk.Frame(parent, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        guide_text = """Common Issues and Solutions:

1. CAMERA NOT DETECTED:
   - Check if webcam is properly connected
   - Ensure no other application is using the camera
   - Restart the application
   - Check camera permissions in system settings

2. HAND NOT DETECTED:
   - Increase lighting on your hands
   - Adjust hand detection confidence in Settings
   - Move your hand closer to the camera
   - Ensure your hand is fully within the camera frame

3. ERRATIC CURSOR MOVEMENT:
   - Decrease mouse sensitivity in Settings
   - Ensure stable lighting conditions
   - Keep your hand steady when making gestures
   - Adjust tracking confidence in Settings

4. GESTURES NOT RECOGNIZED:
   - Make clear, deliberate gestures
   - Adjust detection confidence in Settings
   - Ensure good contrast between hand and background
   - Check if multi-hand mode is needed

5. PERFORMANCE ISSUES:
   - Close other resource-intensive applications
   - Reduce camera resolution if possible
   - Lower detection confidence settings
   - Ensure adequate system resources

6. APPLICATION CRASHES:
   - Restart the application
   - Check for required package updates
   - Ensure Python and packages are compatible
   - Report issues with error details

For additional support, please check our documentation or contact support.
"""
        
        text_widget = tk.Text(content_frame, font=("Arial", 11), bg="#3a506b", fg="#f5f0e1", 
                             wrap=tk.WORD, padx=15, pady=15, relief=tk.FLAT)
        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def save_settings(self):
        """Save current settings"""
        messagebox.showinfo("Settings", "Settings saved successfully!")
    
    def logout_user(self):
        """Logout current user and show authentication window"""
        self.auth_manager.logout_user()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.image_references.clear()
        self.show_authentication_popup()
    
    def start_controller(self):
        """Start the gesture controller"""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("Controller running - Press ESC in camera window to stop")
            self.update_thread = threading.Thread(target=self.run_controller)
            self.update_thread.daemon = True
            self.update_thread.start()
    
    def stop_controller(self):
        """Stop the gesture controller"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Controller stopped - Ready to start")
        self.prev_gest_major = None
        self.prev_gest_minor = None
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.stats = {
            'fist_count': 0,
            'pinch_count': 0,
            'v_gest_count': 0,
            'click_count': 0,
            'scroll_count': 0,
            'right_click_count': 0,
            'double_click_count': 0
        }
        self.update_dashboard()
    
    def update_dashboard(self):
        """Update the dashboard with current statistics"""
        self.fist_count_var.set(str(self.stats['fist_count']))
        self.pinch_count_var.set(str(self.stats['pinch_count']))
        self.v_gest_count_var.set(str(self.stats['v_gest_count']))
        self.click_count_var.set(str(self.stats['click_count']))
        self.right_click_count_var.set(str(self.stats['right_click_count']))
        self.double_click_count_var.set(str(self.stats['double_click_count']))
        self.scroll_count_var.set(str(self.stats['scroll_count']))
    
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
        
        self.update_dashboard()
    
    def run_controller(self):
        """Run the gesture controller"""
        try:
            handmajor = HandRecog(HLabel.MAJOR)
            handminor = HandRecog(HLabel.MINOR)
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Cannot open camera")
                self.stop_controller()
                return
            
            CAM_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            CAM_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            detection_conf = self.hand_detection_confidence.get()
            tracking_conf = self.tracking_confidence.get()

            show_landmarks = self.show_landmarks_var.get()
            
            with mp_hands.Hands(max_num_hands=2 if self.multi_hand_mode.get() else 1, 
                               min_detection_confidence=detection_conf, 
                               min_tracking_confidence=tracking_conf) as hands:  # type: ignore
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

                    left, right = None, None
                    hr_major, hr_minor = None, None
                    
                    if results.multi_hand_landmarks:  # type: ignore
                        try:
                            handedness_dict = MessageToDict(results.multi_handedness[0])  # type: ignore
                            if handedness_dict['classification'][0]['label'] == 'Right':
                                right = results.multi_hand_landmarks[0]  # type: ignore
                            else:
                                left = results.multi_hand_landmarks[0]  # type: ignore
                        except:
                            pass
                        if len(results.multi_hand_landmarks) > 1:  # type: ignore
                            try:
                                handedness_dict = MessageToDict(results.multi_handedness[1])  # type: ignore
                                if handedness_dict['classification'][0]['label'] == 'Right':
                                    right = results.multi_hand_landmarks[1]  # type: ignore
                                else:
                                    left = results.multi_hand_landmarks[1]  # type: ignore
                            except:
                                pass

                        dom_hand = True  
                        hr_major = right if dom_hand else left
                        hr_minor = left if dom_hand else right
                        handmajor.update_hand_result(hr_major)
                        handminor.update_hand_result(hr_minor)

                        handmajor.set_finger_state()
                        handminor.set_finger_state()
                        if hr_major is not None:
                            gest_major = handmajor.get_gesture()
                            if gest_major != self.prev_gest_major:
                                self.update_gesture_stats(gest_major)
                                self.prev_gest_major = gest_major
                            Controller.handle_controls(gest_major, handmajor.hand_result)  # type: ignore
                        if hr_minor is not None and self.multi_hand_mode.get():
                            gest_minor = handminor.get_gesture()
                            if gest_minor != self.prev_gest_minor:
                                self.update_gesture_stats(gest_minor)
                                self.prev_gest_minor = gest_minor
                            Controller.handle_controls(gest_minor, handminor.hand_result)  # type: ignore
                        if show_landmarks:
                            for hand_landmarks in results.multi_hand_landmarks:  # type: ignore
                                mp_drawing.draw_landmarks(  # type: ignore
                                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)  # type: ignore
                    
                    else:
                        self.prev_gest_major = None
                        self.prev_gest_minor = None
                        Controller.prev_hand = None

                    cv2.imshow('AI Virtual Mouse - Press ESC to stop', image)
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  
                        self.is_running = False
                        break
            
            cap.release()
            cv2.destroyAllWindows()
            self.stop_controller()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.stop_controller()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = VirtualMouseUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
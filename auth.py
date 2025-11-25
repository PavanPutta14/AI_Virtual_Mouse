import json
import os
import hashlib
import cv2
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import numpy as np
from PIL import Image, ImageTk

USERS_DIR = "users"
USER_IMAGES_DIR = os.path.join(USERS_DIR, "images")
USER_DATA_FILE = os.path.join(USERS_DIR, "users.json")

os.makedirs(USERS_DIR, exist_ok=True)
os.makedirs(USER_IMAGES_DIR, exist_ok=True)

class AuthenticationManager:
    def __init__(self):
        """Initialize the authentication manager"""
        self.current_user = None
        self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(USER_DATA_FILE):
            try:
                with open(USER_DATA_FILE, 'r') as f:
                    self.users = json.load(f)
            except:
                self.users = {}
        else:
            self.users = {}
    
    def save_users(self):
        """Save users to JSON file"""
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def user_exists(self, username):
        """Check if user exists"""
        return username in self.users
    
    def add_user(self, username, password):
        """Add a new user"""
        if self.user_exists(username):
            return False, "User already exists"
        
        hashed_password = self.hash_password(password)
        self.users[username] = {
            'password': hashed_password,
            'image_path': None
        }
        self.save_users()
        return True, "User registered successfully"
    
    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        if not self.user_exists(username):
            return False, "User not found"
        
        hashed_password = self.hash_password(password)
        
        if self.users[username]['password'] == hashed_password:
            self.current_user = username
            return True, "Login successful"
        else:
            return False, "Incorrect password"
    
    def logout_user(self):
        """Logout current user"""
        self.current_user = None
    
    def get_current_user(self):
        """Get current logged in user"""
        return self.current_user
    
    def get_user_image_path(self, username):
        """Get user's image path"""
        if self.user_exists(username):
            return self.users[username].get('image_path')
        return None
    
    def set_user_image(self, username, image_path):
        """Set user's image path"""
        if self.user_exists(username):
            self.users[username]['image_path'] = image_path
            self.save_users()
            return True
        return False

def show_auth_window(auth_manager, on_success):
    """Show authentication window"""
    auth_window = Toplevel()
    auth_window.title("User Authentication")
    auth_window.geometry("500x400")
    auth_window.configure(bg="#1e3d59")
    auth_window.resizable(False, False)  
    auth_window.attributes('-toolwindow', True)  
    
    auth_window.update_idletasks()
    x = (auth_window.winfo_screenwidth() // 2) - (500 // 2)
    y = (auth_window.winfo_screenheight() // 2) - (400 // 2)
    auth_window.geometry(f"500x400+{x}+{y}")
    
    auth_window.transient()
    auth_window.grab_set()
    
    title_label = tk.Label(auth_window, text="AI Virtual Mouse Controller", 
                          font=("Arial", 16, "bold"), bg="#1e3d59", fg="#f5f0e1")
    title_label.pack(pady=20)
    
    notebook = ttk.Notebook(auth_window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    style = ttk.Style()
    style.configure("Auth.TNotebook", background="#1e3d59")
    style.configure("Auth.TNotebook.Tab", background="#3a506b", foreground="#f5f0e1", 
                   padding=[20, 10], font=("Arial", 12, "bold"))
    style.map("Auth.TNotebook.Tab", background=[("selected", "#5bc0be")], 
              foreground=[("selected", "#1e3d59")])

    login_tab = tk.Frame(notebook, bg="#2c3e50")
    notebook.add(login_tab, text="Login")

    register_tab = tk.Frame(notebook, bg="#2c3e50")
    notebook.add(register_tab, text="Register")

    create_login_form(login_tab, auth_manager, auth_window, on_success)
    
    create_register_form(register_tab, auth_manager, auth_window, on_success)

def create_login_form(parent, auth_manager, auth_window, on_success):
    """Create login form"""
    title_label = tk.Label(parent, text="Login to Your Account", 
                          font=("Arial", 14, "bold"), bg="#2c3e50", fg="#f5f0e1")
    title_label.pack(pady=15)

    form_frame = tk.Frame(parent, bg="#2c3e50")
    form_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)

    username_frame = tk.Frame(form_frame, bg="#2c3e50")
    username_frame.pack(pady=10, fill=tk.X)
    
    tk.Label(username_frame, text="Username:", font=("Arial", 12), 
             bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
    
    username_entry = tk.Entry(username_frame, font=("Arial", 12), width=25)
    username_entry.pack(pady=5, fill=tk.X, ipady=5)

    password_frame = tk.Frame(form_frame, bg="#2c3e50")
    password_frame.pack(pady=10, fill=tk.X)
    
    tk.Label(password_frame, text="Password:", font=("Arial", 12), 
             bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
    
    password_entry = tk.Entry(password_frame, font=("Arial", 12), width=25, show="*")
    password_entry.pack(pady=5, fill=tk.X, ipady=5)

    status_label = tk.Label(form_frame, text="", font=("Arial", 10), 
                           bg="#2c3e50", fg="#e74c3c")
    status_label.pack(pady=10)

    login_button = tk.Button(form_frame, text="Login", font=("Arial", 12, "bold"),
                            bg="#3498db", fg="white", width=15, height=1)
    login_button.pack(pady=15)
    
    def authenticate():
        """Handle login"""
        username = username_entry.get().strip()
        password = password_entry.get()
        
        if not username or not password:
            status_label.config(text="Please enter both username and password", fg="#e74c3c")
            return
        success, message = auth_manager.authenticate_user(username, password)
        if success:
            status_label.config(text=message, fg="#27ae60")
            auth_window.after(1000, lambda: show_image_capture_window(auth_manager, username, on_success, auth_window))
        else:
            status_label.config(text=message, fg="#e74c3c")

    login_button.config(command=authenticate)
    password_entry.bind('<Return>', lambda event: authenticate())
    username_entry.focus()

def create_register_form(parent, auth_manager, auth_window, on_success):
    """Create registration form"""
    title_label = tk.Label(parent, text="Create New Account", 
                          font=("Arial", 14, "bold"), bg="#2c3e50", fg="#f5f0e1")
    title_label.pack(pady=15)

    form_frame = tk.Frame(parent, bg="#2c3e50")
    form_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)

    username_frame = tk.Frame(form_frame, bg="#2c3e50")
    username_frame.pack(pady=10, fill=tk.X)
    
    tk.Label(username_frame, text="Username:", font=("Arial", 12), 
             bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
    
    username_entry = tk.Entry(username_frame, font=("Arial", 12), width=25)
    username_entry.pack(pady=5, fill=tk.X, ipady=5)

    password_frame = tk.Frame(form_frame, bg="#2c3e50")
    password_frame.pack(pady=10, fill=tk.X)
    
    tk.Label(password_frame, text="Password:", font=("Arial", 12), 
             bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
    
    password_entry = tk.Entry(password_frame, font=("Arial", 12), width=25, show="*")
    password_entry.pack(pady=5, fill=tk.X, ipady=5)
 
    confirm_frame = tk.Frame(form_frame, bg="#2c3e50")
    confirm_frame.pack(pady=10, fill=tk.X)
    
    tk.Label(confirm_frame, text="Confirm Password:", font=("Arial", 12), 
             bg="#2c3e50", fg="#f5f0e1").pack(anchor=tk.W)
    
    confirm_entry = tk.Entry(confirm_frame, font=("Arial", 12), width=25, show="*")
    confirm_entry.pack(pady=5, fill=tk.X, ipady=5)
    
    status_label = tk.Label(form_frame, text="", font=("Arial", 10), 
                           bg="#2c3e50", fg="#e74c3c")
    status_label.pack(pady=10)
 
    register_button = tk.Button(form_frame, text="Register", font=("Arial", 12, "bold"),
                               bg="#27ae60", fg="white", width=15, height=1)
    register_button.pack(pady=15)
    
    def register():
        """Handle registration"""
        username = username_entry.get().strip()
        password = password_entry.get()
        confirm_password = confirm_entry.get()
        
        if not username or not password or not confirm_password:
            status_label.config(text="Please fill in all fields", fg="#e74c3c")
            return
        
        if password != confirm_password:
            status_label.config(text="Passwords do not match", fg="#e74c3c")
            return
        
        success, message = auth_manager.add_user(username, password)
        if success:
            status_label.config(text=message, fg="#27ae60")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            confirm_entry.delete(0, tk.END)
            status_label.after(2000, lambda: status_label.config(text="You can now login", fg="#27ae60"))
        else:
            status_label.config(text=message, fg="#e74c3c")

    register_button.config(command=register)
    confirm_entry.bind('<Return>', lambda event: register())

def show_image_capture_window(auth_manager, username, on_success, parent_window):
    """Show image capture window"""
    parent_window.destroy()
    
    capture_window = Toplevel()
    capture_window.title("Capture User Image")
    capture_window.geometry("500x400")
    capture_window.configure(bg="#1e3d59")
    capture_window.resizable(False, False)  
    capture_window.attributes('-toolwindow', True)  
    
    capture_window.update_idletasks()
    x = (capture_window.winfo_screenwidth() // 2) - (500 // 2)
    y = (capture_window.winfo_screenheight() // 2) - (400 // 2)
    capture_window.geometry(f"500x400+{x}+{y}")

    capture_window.transient()
    capture_window.grab_set()
    
    title_label = tk.Label(capture_window, text=f"Welcome {username}!", 
                          font=("Arial", 14, "bold"), bg="#1e3d59", fg="#f5f0e1")
    title_label.pack(pady=10)
    
    instruction_label = tk.Label(capture_window, 
                                text="Please position your face in the camera view and click Capture", 
                                font=("Arial", 10), bg="#1e3d59", fg="#f5f0e1")
    instruction_label.pack(pady=5)

    video_frame = tk.Frame(capture_window, bg="#2c3e50", width=300, height=200)
    video_frame.pack(pady=15)
    video_frame.pack_propagate(False)
    
    video_label = tk.Label(video_frame, bg="#3a506b")
    video_label.pack(fill=tk.BOTH, expand=True)
 
    status_label = tk.Label(capture_window, text="", font=("Arial", 10), 
                           bg="#1e3d59", fg="#f5f0e1")
    status_label.pack(pady=5)
  
    button_frame = tk.Frame(capture_window, bg="#1e3d59")
    button_frame.pack(pady=10)
 
    capture_button = tk.Button(button_frame, text="Capture Image", font=("Arial", 10, "bold"),
                              bg="#27ae60", fg="white", width=12, height=1)
    capture_button.pack(side=tk.LEFT, padx=10)

    skip_button = tk.Button(button_frame, text="Skip", font=("Arial", 10, "bold"),
                           bg="#e74c3c", fg="white", width=12, height=1)
    skip_button.pack(side=tk.LEFT, padx=10)
    
    cap = cv2.VideoCapture(0)
    
    def update_frame():
        """Update video frame"""
        if capture_window.winfo_exists():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                frame_resized = cv2.resize(frame_rgb, (300, 200))
   
                img = Image.fromarray(frame_resized)
                imgtk = ImageTk.PhotoImage(image=img)

                video_label.configure(image=imgtk)

            capture_window.after(10, update_frame)

    update_frame()
    
    def capture_image():
        """Capture and save user image"""
        ret, frame = cap.read()
        if ret:

            image_filename = f"{username}.jpg"
            image_path = os.path.join(USER_IMAGES_DIR, image_filename)

            cv2.imwrite(image_path, frame)

            auth_manager.set_user_image(username, image_path)
            
            status_label.config(text="Image captured successfully!", fg="#27ae60")

            capture_window.after(1000, lambda: [cap.release(), capture_window.destroy(), on_success()])
    
    def skip_capture():
        """Skip image capture"""
        cap.release()
        capture_window.destroy()
        on_success()

    capture_button.config(command=capture_image)
    skip_button.config(command=skip_capture)

    def on_closing():
        cap.release()
        capture_window.destroy()
    
    capture_window.protocol("WM_DELETE_WINDOW", on_closing)

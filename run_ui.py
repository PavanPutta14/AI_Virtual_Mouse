#!/usr/bin/env python3
"""
Launcher script for the AI Virtual Mouse UI
"""

import sys
import os
import tkinter as tk

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point"""
    try:
        from virtual_mouse_ui import main
        main()
    except Exception as e:
        print(f"Error running the UI: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
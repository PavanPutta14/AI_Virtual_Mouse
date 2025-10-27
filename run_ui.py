#!/usr/bin/env python3
"""
Launcher script for the AI Virtual Mouse UI
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from virtual_mouse_ui import main
    if __name__ == "__main__":
        main()
except Exception as e:
    print(f"Error running the UI: {e}")
    input("Press Enter to exit...")
#!/usr/bin/env python3
"""
Simple startup script for YETi (YouTube Experiment Testing intelligence) Web Server.

Usage:
    python start_server.py
"""

import sys
import webbrowser
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from api.server import app, main
    
    print("\n" + "="*70)
    print("👹 YETi v2.0 - YouTube Experiment Testing intelligence")
    print("="*70)
    print("\nStarting web server...")
    print("Dashboard will open in your browser shortly...")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    main()
    
except ImportError as e:
    print("\n" + "="*70)
    print("ERROR: Missing dependencies")
    print("="*70)
    print(f"\n{e}\n")
    print("Please install required packages:")
    print("\n    pip install -r requirements.txt\n")
    print("Or activate your virtual environment first:")
    print("\n    source venv/bin/activate")
    print("    pip install -r requirements.txt\n")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\nServer stopped. Goodbye!")
    sys.exit(0)
except Exception as e:
    print(f"\n\nError starting server: {e}\n")
    sys.exit(1)






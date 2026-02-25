#!/usr/bin/env python3
"""
Auralite - Illegal Mining Detection System
Run script for Flask web application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════╗
    ║     AURALITE - Illegal Mining Detection  ║
    ║         Web Application v1.0              ║
    ╚══════════════════════════════════════════╝
    """)
    
    print("🚀 Starting Auralite server...")
    print("📊 Preloaded dataset initialized")
    print("🤖 ML models loaded")
    print("\n🌐 Access the application at:")
    print("   http://localhost:5000")
    print("   http://127.0.0.1:5000")
    print("\n Press CTRL+C to stop the server\n")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

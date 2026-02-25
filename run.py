#!/usr/bin/env python3
"""
Auralite - Aravalli Hills Illegal Mining Detection System
Run script
"""

from app import socketio, app

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

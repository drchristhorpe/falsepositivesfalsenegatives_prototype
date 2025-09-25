#!/usr/bin/env python3
"""
Production-ready runner for the False Positives/Negatives Database
"""
import os
from app import app

if __name__ == '__main__':
    # Get configuration from environment
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting False Positives/Negatives Database on {host}:{port}")
    print(f"Debug mode: {'ON' if debug else 'OFF'}")
    
    if not debug:
        print("Running in production mode. Make sure to configure proper WSGI server for production deployment.")
    
    app.run(host=host, port=port, debug=debug)
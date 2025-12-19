#!/usr/bin/env python3
"""
OneCard Bot - Python Startup Script
Starts all three services and manages them together.
"""

import subprocess
import sys
import os
import signal
import time
import shutil
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_colored(message, color=Colors.NC):
    print(f"{color}{message}{Colors.NC}")

def check_dependencies():
    """Check if required dependencies are installed."""
    issues = []
    
    if not shutil.which("python3"):
        issues.append("Python 3 is not installed")
    
    if not shutil.which("npm"):
        issues.append("Node.js/npm is not installed")
    
    if not Path(".env").exists():
        print_colored("⚠️  Warning: .env file not found. Make sure GOOGLE_API_KEY is set.", Colors.YELLOW)
    
    if issues:
        print_colored("❌ Missing dependencies:", Colors.RED)
        for issue in issues:
            print_colored(f"  • {issue}", Colors.RED)
        sys.exit(1)

def start_service(name, command, cwd=None, delay=0):
    """Start a service and return the process."""
    print_colored(f"🚀 Starting {name}...", Colors.GREEN)
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=open(f"logs/{name.lower().replace(' ', '_')}.log", "w"),
            stderr=subprocess.STDOUT
        )
        time.sleep(delay)
        return process
    except Exception as e:
        print_colored(f"❌ Failed to start {name}: {e}", Colors.RED)
        sys.exit(1)

def main():
    print_colored("🚀 Starting OneCard Bot Services...\n", Colors.GREEN)
    
    # Check dependencies
    check_dependencies()
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    processes = []
    
    try:
        # Start Mock API (Port 5000)
        mock_api = start_service("Mock API Server", "python3 mock_apis.py", delay=2)
        processes.append(("Mock API", mock_api))
        
        # Start Backend (Port 8000)
        backend = start_service("AI Backend Server", "python3 backend.py", delay=3)
        processes.append(("Backend", backend))
        
        # Start Frontend (Port 5173)
        frontend = start_service("Frontend Dev Server", "npm run dev", cwd="onecard-bot", delay=2)
        processes.append(("Frontend", frontend))
        
        print_colored("\n✅ All services started!\n", Colors.GREEN)
        print_colored("Services running:", Colors.YELLOW)
        for name, proc in processes:
            print_colored(f"  • {name}: PID {proc.pid}", Colors.BLUE)
        print_colored("\n📝 Logs are in the 'logs/' directory", Colors.YELLOW)
        print_colored("🌐 Frontend: http://localhost:5173", Colors.BLUE)
        print_colored("🔌 Backend:  http://localhost:8000", Colors.BLUE)
        print_colored("📡 Mock API: http://localhost:5000", Colors.BLUE)
        print_colored("\nPress Ctrl+C to stop all services\n", Colors.YELLOW)
        
        # Wait for all processes
        for name, proc in processes:
            proc.wait()
            
    except KeyboardInterrupt:
        print_colored("\n🛑 Stopping all services...", Colors.YELLOW)
        for name, proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print_colored(f"  ✓ {name} stopped", Colors.GREEN)
            except subprocess.TimeoutExpired:
                proc.kill()
                print_colored(f"  ✗ {name} force stopped", Colors.RED)
        print_colored("\n👋 Goodbye!", Colors.GREEN)

if __name__ == "__main__":
    main()


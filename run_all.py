"""
Launcher to run both FastAPI backend and Vite React frontend concurrently.
Usage: python run_all.py
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent
    frontend_dir = root_dir / "frontend"

    print("=" * 65)
    print("        DFA Minimizer - Full Stack Dev Environment")
    print("=" * 65)
    print("1. Backend:  http://127.0.0.1:8000 (FastAPI)")
    print("2. Frontend: http://localhost:5173  (React + Vite + Tailwind)")
    print("=" * 65)

    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(root_dir)
    )

    print("Backend process started (PID:", backend_proc.pid, ")")
    time.sleep(1)

    try:
        print("Starting Vite frontend dev server...")
        subprocess.run(["npm", "run", "dev"], cwd=str(frontend_dir), shell=True)
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        backend_proc.terminate()
        backend_proc.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()

"""
Quick Launcher for DFA Minimization Studio.
Usage: python run_studio.py
"""

import sys
import subprocess
from pathlib import Path

app_path = Path(__file__).resolve().parent / "dfa_minimization_studio" / "app.py"

if __name__ == "__main__":
    print(f"Launching DFA Minimization Studio from: {app_path}")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])

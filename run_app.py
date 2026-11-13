"""
DFA Minimizer - Quick Launcher

Options:
1. Run React Frontend (Vite):
   cd frontend
   npm run dev

2. Run Streamlit Studio:
   python run_studio.py
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("           DFA Minimizer Launcher")
    print("=" * 60)
    print("1. Launch React Frontend (Vite - Matches Screenshot Pixel-for-Pixel)")
    print("2. Launch Streamlit Studio")
    print("=" * 60)
    choice = input("Select option (1 or 2) [default: 1]: ").strip() or "1"

    root_dir = Path(__file__).resolve().parent

    if choice == "1":
        frontend_dir = root_dir / "frontend"
        print(f"\nStarting React Vite dev server in {frontend_dir}...")
        subprocess.run(["npm", "run", "dev"], cwd=str(frontend_dir), shell=True)
    elif choice == "2":
        app_path = root_dir / "dfa_minimization_studio" / "app.py"
        print(f"\nStarting Streamlit server at {app_path}...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()

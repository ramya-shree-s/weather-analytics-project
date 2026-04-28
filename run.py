# ============================================================
#  run.py  —  Entry point: launches the Streamlit dashboard
# ============================================================
#
#  Usage:
#      python run.py
#
#  Or directly with Streamlit:
#      streamlit run src/dashboard.py
#
# ============================================================

import subprocess
import sys
import os

if __name__ == "__main__":
    dashboard = os.path.join(os.path.dirname(__file__), "src", "dashboard.py")

    print("🌦️  Starting Weather Analytics Dashboard …")
    print("   Open your browser at  http://localhost:8501\n")

    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", dashboard,
         "--server.headless", "false"],
        check=True,
    )
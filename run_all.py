import subprocess
import time
import platform
import webbrowser

def run_script(path):
    result = subprocess.run(["python", path], check=True)
    print(f"✅ Completed: {path}")
    return result

def launch_dashboard():
    print("🚀 Launching dashboard at http://127.0.0.1:5001")
    if platform.system() == "Windows":
        subprocess.Popen(["start", "cmd", "/k", "python", "report_dashboard.py"], shell=True)
    else:
        subprocess.Popen(["gnome-terminal", "--", "python3", "report_dashboard.py"])
    time.sleep(3)
    webbrowser.open("http://127.0.0.1:5001")

if __name__ == "__main__":
    run_script("tests/test_login.py")
    run_script("tests/test_feedback.py")
    launch_dashboard()

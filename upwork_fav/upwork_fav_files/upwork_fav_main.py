import subprocess
import time
import os
from datetime import datetime

# List of your Python GUI/automation scripts
files = ["upwork_profile_fav.py", "upwork_profile_fav_with_logging.py"]

# Create 'log' directory if it doesn't exist
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

# Track running processes
processes = {}

# Delay (in seconds) before restarting a crashed script
RESTART_DELAY = 30

# Track last restart times
last_restart_time = {}

# Track last log clear date
last_log_clear_date = None

def start_process(file):
    log_path = os.path.join(log_dir, f"{file}.log")
    log_file = open(log_path, "a")  # Append logs to file
    print(f"🟢 Starting {file} with xvfb-run → logging to {log_path}", flush=True)
    last_restart_time[file] = time.time()
    return subprocess.Popen(
        ["xvfb-run", "-a", "python3", file],
        stdout=log_file,
        stderr=subprocess.STDOUT
    )

def clear_logs_if_morning():
    global last_log_clear_date
    now = datetime.now()
    current_date = now.date()

    # Clear logs only once per day between 07:00 and 07:05
    if now.hour == 7 and now.minute < 5 and current_date != last_log_clear_date:
        print("🧹 Clearing logs...", flush=True)
        for file in files:
            open(os.path.join(log_dir, f"{file}.log"), "w").close()
        last_log_clear_date = current_date

# Start all scripts initially
for file in files:
    processes[file] = start_process(file)
    time.sleep(15)

# Monitor and restart crashed scripts
try:
    while True:
        clear_logs_if_morning()

        for file, process in list(processes.items()):
            if process.poll() is not None:  # Process has exited
                print(f"❌ {file} crashed. Waiting {RESTART_DELAY} seconds before restarting...", flush=True)
                time.sleep(RESTART_DELAY)
                processes[file] = start_process(file)

        # Optional: Sleep a bit to reduce CPU usage
        time.sleep(20)

except KeyboardInterrupt:
    print("\n🛑 Exiting... Terminating all child processes.", flush=True)
    for process in processes.values():
        try:
            process.terminate()
        except Exception:
            pass

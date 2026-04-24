import subprocess
import time
import os
from datetime import datetime, timedelta

# List of your Python GUI/automation scripts
files = [
    "upwork_profile_fav_without_logging.py",
    "upwork_profile_fav_with_logging.py"
]

# Track running processes
processes = {}

# Delay (in seconds) before restarting a crashed script
RESTART_DELAY = 15

# How often to fully restart everything (in seconds)
FULL_RESTART_INTERVAL = 3 * 60 * 60  # 3 hours

# Track timestamps
last_restart_time = {}
last_full_restart = time.time()


def start_process(file):
    log_path = f"log/{file}.log"
    log_file = open(log_path, "a")
    print(f"🟢 Starting {file} → logging to {log_path}")
    last_restart_time[file] = time.time()
    return subprocess.Popen(
        ["xvfb-run", "-a", "python3", file],
        stdout=log_file,
        stderr=subprocess.STDOUT
    )


def stop_all_processes():
    """Stop all running processes gracefully."""
    for file, process in list(processes.items()):
        if process.poll() is None:  # Still running
            print(f"🛑 Stopping {file}...")
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print(f"⚠️ Force killing {file}")
                process.kill()
    processes.clear()


def clear_logs():
    """Clear all .log files."""
    print("🧹 Clearing logs...")
    for file in files:
        open(f"{file}.log", "w").close()


def restart_all():
    """Stop all scripts, clear logs, and restart everything."""
    global last_full_restart
    print("\n🔄 Performing full restart of all scripts...")
    stop_all_processes()
    clear_logs()
    time.sleep(5)
    for file in files:
        processes[file] = start_process(file)
        time.sleep(10)
    last_full_restart = time.time()
    print("✅ All scripts restarted successfully.\n")


# --- Start all scripts initially ---
for file in files:
    processes[file] = start_process(file)
    time.sleep(15)

# --- Monitor and manage ---
try:
    while True:
        # Check if any process crashed
        for file, process in list(processes.items()):
            if process.poll() is not None:  # Process exited
                print(f"❌ {file} crashed. Restarting in {RESTART_DELAY}s...")
                time.sleep(RESTART_DELAY)
                processes[file] = start_process(file)

        # Check if 6 hours have passed since last full restart
        if time.time() - last_full_restart >= FULL_RESTART_INTERVAL:
            restart_all()

        time.sleep(20)

except KeyboardInterrupt:
    print("\n🛑 Exiting... Terminating all child processes.")
    stop_all_processes()

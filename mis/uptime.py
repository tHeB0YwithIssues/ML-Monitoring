import time
import os
import pickle

UPTIME_FILE = "data/last_uptime.pkl"


## Return current uptime of server ..
def get_uptime_seconds():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds

## Check if server rebooted or not ..
def was_rebooted_by_uptime():
    current_uptime = get_uptime_seconds()

    if os.path.exists(UPTIME_FILE):
        with open(UPTIME_FILE, "rb") as f:
            last_uptime = pickle.load(f)

        # If current uptime is less than previous, system was rebooted
        if current_uptime < last_uptime:
            return True
        else:
            return False
    else:
        print("No previous uptime stored. Assuming first run.")

    # Save current uptime for next check
    with open(UPTIME_FILE, "wb") as f:
        pickle.dump(current_uptime, f)


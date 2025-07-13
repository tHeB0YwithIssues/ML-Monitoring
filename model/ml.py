from mis import uptime
from sklearn.tree import DecisionTreeClassifier
from sklearn.exceptions import NotFittedError
from collections import deque
import time
import joblib
import os
import json
import psutil

## CONFIGURATION ....
WINDOW_SIZE      = 10
MODEL_FILE  = 'data/dump.ml'
OLD_DATA_POINT   = 'data/old_DP.json'
RETRAIN_INTERVAL = 5
THRESHOLD        = 70

CPU_WINDOW = deque(maxlen=WINDOW_SIZE)
LABEL_WINDOW = deque(maxlen=WINDOW_SIZE)

CPU_UTILIZATION = 0
COUNT = 0

## 1. CHECK IF SERVER WAS REBOOTED
_REBOOT = uptime.was_rebooted_by_uptime()

# Initialize the model
MODEL = DecisionTreeClassifier()

def _TRAIN_MODEL():
    global CPU_UTILIZATION, COUNT, MODEL

    CPU_UTILIZATION = int(psutil.cpu_percent(interval=None))
    label = 1 if CPU_UTILIZATION >= THRESHOLD  else 0

    CPU_WINDOW.append([CPU_UTILIZATION])
    LABEL_WINDOW.append(label)

    COUNT += 1
    if COUNT % RETRAIN_INTERVAL == 0 and len(CPU_WINDOW) >= 2:
        MODEL.fit(list(CPU_WINDOW), list(LABEL_WINDOW))
        joblib.dump(MODEL,MODEL_FILE)
        with open(OLD_DATA_POINT, "w") as f:
            json.dump({
                "cpu" : [x[0] for x in CPU_WINDOW],
                "labels" : list(LABEL_WINDOW)
            }, f)
        print("💾 Model and data saved.")
    
    try:
        prediction = MODEL.predict([[CPU_UTILIZATION]])[0]
        status = "High" if prediction == 1 else "Normal"
        print(f"CPU: {CPU_UTILIZATION}% -> {status}")

    except NotFittedError:
        print("⚠️ Model not trained yet.")

def _LOAD_MODEL_IF_REBOOTED():
    global MODEL

    ## check if old file exist at path
    try:
        if os.path.exists(MODEL_FILE) and os.path.exists(OLD_DATA_POINT):
            MODEL = joblib.load(MODEL_FILE)
            print('Trained model loaded')

            with open(OLD_DATA_POINT, 'r') as f:
                data =  json.load(f)
            
            for c in data["cpu"]:
                CPU_WINDOW.append([c])
            
            for l in data["labels"]:
                LABEL_WINDOW.append(l)

    except Exception as e:
        print(e)
        print('Since no file was found ')
        # Train model with dummy data
        MODEL.fit([[0]],[0])


def RUN_MODEL():
    if _REBOOT:
        _LOAD_MODEL_IF_REBOOTED()
        time.sleep(1)
        _TRAIN_MODEL()
    else:
        _TRAIN_MODEL()
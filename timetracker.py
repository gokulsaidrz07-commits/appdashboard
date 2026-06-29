import time
import psutil
import json

usage = {}

while True:
    for p in psutil.process_iter(['name']):
        try:
            name = p.info['name']
            usage[name] = usage.get(name, 0) + 1
        except:
            pass

    with open("usage.json", "w") as f:
        json.dump(usage, f)

    time.sleep(1)
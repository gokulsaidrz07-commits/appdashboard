import streamlit as st
import winreg
import json
import psutil
import pandas as pd

# -------------------------------
# Get installed apps
# -------------------------------
def get_installed_apps():
    apps = []
    
    paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for root, path in paths:
        try:
            reg_key = winreg.OpenKey(root, path)

            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    subkey_name = winreg.EnumKey(reg_key, i)
                    subkey = winreg.OpenKey(reg_key, subkey_name)

                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]

                    try:
                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                    except:
                        version = "Unknown"

                    apps.append((name, version))
                except:
                    pass
        except:
            pass

    return apps


# -------------------------------
# Load usage data
# -------------------------------
def load_usage():
    try:
        with open("usage.json", "r") as f:
            return json.load(f)
    except:
        return {}


# -------------------------------
# Format time
# -------------------------------
def format_time(seconds):
    if seconds < 60:
        return "Less than a minute"
    
    minutes = seconds // 60
    hours = minutes // 60
    minutes = minutes % 60

    return f"{hours:02d}:{minutes:02d}"


# -------------------------------
# UI START
# -------------------------------
st.title("💻 My App Dashboard")

apps = get_installed_apps()
usage_data = load_usage()

# -------------------------------
# Search
# -------------------------------
search = st.text_input("Search application")

st.subheader("Installed Applications")

# -------------------------------
# Show Apps + Usage
# -------------------------------
for app in apps:
    app_name = app[0]

    # match process name
    usage_seconds = 0
    for process_name in usage_data:
        if app_name.lower().split()[0] in process_name.lower():
            usage_seconds = usage_data[process_name]
            break

    usage_time = format_time(usage_seconds)

    if search.strip() == "" or search.lower() in app_name.lower():
        st.write(f"✅ {app_name} — Version: {app[1]} — Usage: {usage_time}")


# -------------------------------
# Top Used Apps
# -------------------------------
st.subheader("Top Used Applications")

if usage_data:
    sorted_usage = sorted(usage_data.items(), key=lambda x: x[1], reverse=True)

    for app, time_used in sorted_usage[:5]:
        clean_name = app.replace(".exe", "")
        formatted_time = format_time(time_used)
        st.write(f"🔹 {clean_name} — {formatted_time}")
else:
    st.write("No usage data yet. Run tracker.py")


# -------------------------------
# Running Apps
# -------------------------------
st.subheader("Currently Running Apps")

running = set()
for p in psutil.process_iter(['name']):
    try:
        running.add(p.info['name'])
    except:
        pass

for app in sorted(running):
    st.write(f"🔵 {app}")


# -------------------------------
# Summary
# -------------------------------
st.write(f"Total apps: {len(apps)}")

df = pd.DataFrame(apps, columns=["App Name", "Version"])
st.table(df)

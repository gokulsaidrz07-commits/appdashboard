import streamlit as st
import json
import os
import pandas as pd

# Try Windows-only modules
try:
    import winreg
    import psutil
    WINDOWS = True
except:
    WINDOWS = False


# -------------------------------
# Get installed apps (Windows only)
# -------------------------------
def get_installed_apps():
    if not WINDOWS:
        return []

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
    if not os.path.exists("usage.json"):
        return {}

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
st.title("My App Dashboard")

# Cloud warning
if not WINDOWS:
    st.warning("Running in Cloud → limited features (Demo mode)")

# -------------------------------
# Get apps
# -------------------------------
if WINDOWS:
    apps = get_installed_apps()
else:
    apps = [
        ("Google Chrome", "Demo"),
        ("VS Code", "Demo"),
        ("Python", "Demo"),
        ("Microsoft Edge", "Demo")
    ]

# ✅ important: apps is defined BEFORE using it anywhere


usage_data = load_usage()

# -------------------------------
# Search
# -------------------------------
search = st.text_input("Search application")

st.subheader("📦 Installed Applications")

# -------------------------------
# Display apps
# -------------------------------
for app in apps:
    app_name = app[0]

    usage_seconds = 0

    if WINDOWS:
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

if WINDOWS and usage_data:
    sorted_usage = sorted(usage_data.items(), key=lambda x: x[1], reverse=True)

    for app_name, time_used in sorted_usage[:5]:
        clean_name = app_name.replace(".exe", "")
        st.write(f"🔹 {clean_name} — {format_time(time_used)}")

else:
    st.write("Usage tracking available only on local system")


# -------------------------------
# Running Apps (only local)
# -------------------------------
if WINDOWS:
    st.subheader("Currently Running Apps")

    try:
        running = set()

        for p in psutil.process_iter(['name']):
            try:
                running.add(p.info['name'])
            except:
                pass

        for name in sorted(running):
            st.write(f"🔵 {name}")
    except:
        st.write("Unable to fetch running apps")


# -------------------------------
# ✅ FIXED TABLE LOCATION
# -------------------------------
st.subheader("📊 Summary Table")

df = pd.DataFrame(apps, columns=["App Name", "Version"])
st.table(df)

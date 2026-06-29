import streamlit as st
import json
import psutil
import pandas as pd
import os

# ✅ Windows-only import
try:
    import winreg
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
# Format time HH:MM
# -------------------------------
def format_time(seconds):
    if seconds < 60:
        return "Less than a minute"

    minutes = seconds // 60
    hours = minutes // 60
    minutes = minutes % 60

    return f"{hours:02d}:{minutes:02d}"


# -------------------------------


df = pd.DataFrame(apps, columns=["App Name", "Version"])
st.table(df)

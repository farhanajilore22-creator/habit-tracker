# data.py - Member C
import json
import csv
import os
import shutil

DATA_FILE = "habits.json"
SETTINGS_FILE = "settings.json"

def load_habits():
    # Level 4: Backup every time program starts
    if os.path.exists(DATA_FILE):
        try:
            shutil.copy(DATA_FILE, DATA_FILE + ".bak")
            print(f"Backup created: {DATA_FILE}.bak")
        except Exception as e:
            print(f"Could not create backup: {e}")

    # Level 3: Missing file
    if not os.path.exists(DATA_FILE):
        print("No save file found. Starting with empty habits.")
        return {}

    # Level 3: Empty or corrupted file
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                print("Save file is empty. Starting fresh.")
                return {}
            data = json.loads(content)

            # Support old Level 1 format: {"Habit": ["2026-11-20"]}
            clean = {}
            for name, value in data.items():
                if isinstance(value, list):
                    clean[name] = {"target_per_week": 7, "done_dates": value}
                else:
                    clean[name] = {
                        "target_per_week": value.get("target_per_week", 7),
                        "done_dates": value.get("done_dates", [])
                    }
            return clean

    except json.JSONDecodeError:
        print("WARNING: Save file is corrupted. Starting with empty habits. Backup saved as habits.json.bak")
        return {}
    except Exception as e:
        print(f"Error loading file: {e}")
        return {}

def save_habits(habits):
    with open(DATA_FILE, "w") as f:
        json.dump(habits, f, indent=2)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"streak_freeze": False}
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            return {"streak_freeze": data.get("streak_freeze", False)}
    except:
        print("Settings file corrupted. Using defaults.")
        return {"streak_freeze": False}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def export_csv(habits, stats):
    # stats is a dict from tracking.py: {name: {"streak":.., "longest":.., "rate30":..}}
    # We pass stats in so data.py doesn't need to import tracking.py
    with open("habit_report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Habit", "Target_Per_Week", "Current_Streak", "Longest_Streak", "30_Day_Percent"])
        for name, habit in habits.items():
            s = stats.get(name, {})
            writer.writerow([
                name,
                habit.get("target_per_week", 7),
                s.get("streak", 0),
                s.get("longest", 0),
                f"{s.get('rate30', 0):.1f}%"
            ])
    print("Exported to habit_report.csv")
    
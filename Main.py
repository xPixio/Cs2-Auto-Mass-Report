import threading
import time
import json
import os
import random
from pynput.mouse import Controller, Button
from pynput import keyboard
import customtkinter as ctk

# --- GUI theme ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Default data ---
default_positions = {
    "Player_1": [1370, 405],
    "Player_2": [1373, 431],
    "Player_3": [1371, 460],
    "Player_4": [1376, 483],
    "Player_5": [1374, 515],
    "Player_6": [1374, 667],
    "Player_7": [1372, 693],
    "Player_8": [1369, 722],
    "Player_9": [1374, 747],
    "Player_10": [1373, 772],
    "pos2": [1238, 474],
    "pos2b": [1242, 532],
    "pos3": [1157, 714]
}

positions = default_positions.copy()
hotkey = "f8"
active_pos1 = "Player_1"
settings_file = "mainSettings.json"

# --- Load settings ---
if os.path.exists(settings_file):
    try:
        with open(settings_file, "r") as f:
            data = json.load(f)
            positions.update(data.get("positions", {}))
            hotkey = data.get("hotkey", hotkey)
            active_pos1 = data.get("active_pos1", active_pos1)
    except Exception:
        pass
else:
    with open(settings_file, "w") as f:
        json.dump({"hotkey": hotkey, "positions": positions, "active_pos1": active_pos1}, f, indent=4)

mouse = Controller()
running = False

# --- Functions ---
def click_loop():
    global running
    while running:
        pos1 = positions[active_pos1]
        pos2 = positions["pos2"] if random.choice([True, False]) else positions["pos2b"]
        click_order = [pos1, pos2, positions["pos3"]]
        for pos in click_order:
            if not running:
                break
            mouse.position = pos
            mouse.click(Button.left)
            time.sleep(0.1)
        time.sleep(0.2)

def on_press(key):
    global running
    try:
        if key.char == hotkey.lower():
            toggle()
    except AttributeError:
        if key == getattr(keyboard.Key, hotkey.lower(), None):
            toggle()

def toggle():
    global running
    running = not running
    print("Started" if running else "Stopped")
    if running:
        threading.Thread(target=click_loop, daemon=True).start()

def save_settings():
    global positions, hotkey, active_pos1
    try:
        positions["pos2"] = [int(x2.get()), int(y2.get())]
        positions["pos2b"] = [int(x2b.get()), int(y2b.get())]
        positions["pos3"] = [int(x3.get()), int(y3.get())]
        for i in range(10):
            x = Player_entries[i][0].get()
            y = Player_entries[i][1].get()
            positions[f"Player_{i+1}"] = [int(x), int(y)]
        hotkey = key_entry.get().lower()
        active_pos1 = combo_pos1.get()
        with open(settings_file, "w") as f:
            json.dump({"hotkey": hotkey, "positions": positions, "active_pos1": active_pos1}, f, indent=4)
    except ValueError:
        pass  # Ignore invalid numbers while typing

def auto_save_event(_=None):
    app.after(300, save_settings)

def start_listener():
    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()

# --- GUI ---
app = ctk.CTk()
app.title("CS2 Auto Reporter")
app.geometry("420x950")

frame = ctk.CTkFrame(app, width=400, height=950)
frame.pack(padx=5, pady=5, fill="both", expand=True)

ctk.CTkLabel(frame, text="Active Position 1:").pack(pady=(4, 0))
combo_pos1 = ctk.CTkOptionMenu(frame, values=[f"Player_{i}" for i in range(1, 11)])
combo_pos1.set(active_pos1)
combo_pos1.pack(pady=2)
combo_pos1.bind("<<ComboboxSelected>>", auto_save_event)

Player_entries = []
for i in range(10):
    ctk.CTkLabel(frame, text=f"Player_{i+1} (x, y):").pack(pady=(2, 0))
    row = ctk.CTkFrame(frame)
    row.pack(pady=1)
    x_entry = ctk.CTkEntry(row, width=70)
    y_entry = ctk.CTkEntry(row, width=70)
    pos = positions.get(f"Player_{i+1}", [0, 0])
    x_entry.insert(0, str(pos[0]))
    y_entry.insert(0, str(pos[1]))
    x_entry.pack(side="left", padx=3)
    y_entry.pack(side="left", padx=3)
    x_entry.bind("<KeyRelease>", auto_save_event)
    y_entry.bind("<KeyRelease>", auto_save_event)
    Player_entries.append((x_entry, y_entry))

for label, keys in [
    ("Position 2", ("x2", "y2", "pos2")),
    ("Position 2B", ("x2b", "y2b", "pos2b")),
    ("Position 3", ("x3", "y3", "pos3"))
]:
    ctk.CTkLabel(frame, text=f"{label} (x, y):").pack(pady=(3, 0))
    row = ctk.CTkFrame(frame)
    row.pack(pady=1)
    globals()[keys[0]] = ctk.CTkEntry(row, width=70)
    globals()[keys[1]] = ctk.CTkEntry(row, width=70)
    globals()[keys[0]].insert(0, str(positions[keys[2]][0]))
    globals()[keys[1]].insert(0, str(positions[keys[2]][1]))
    globals()[keys[0]].pack(side="left", padx=3)
    globals()[keys[1]].pack(side="left", padx=3)
    globals()[keys[0]].bind("<KeyRelease>", auto_save_event)
    globals()[keys[1]].bind("<KeyRelease>", auto_save_event)

ctk.CTkLabel(frame, text="Hotkey (Start/Stop):").pack(pady=(6, 0))
key_entry = ctk.CTkEntry(frame, width=70)
key_entry.insert(0, hotkey.upper())
key_entry.pack(pady=2)
key_entry.bind("<KeyRelease>", auto_save_event)

start_listener()
app.mainloop()

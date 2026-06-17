import tkinter as tk
from tkinter import PhotoImage
import json
import os
from PIL import Image, ImageTk

SAVE_FILE = "cookie_save.json"

root = tk.Tk()
root.title("Cookie Clicker")
root.geometry("700x700")
root.resizable(False, False)

bg_image = PhotoImage(file='background.png')
cookie_pil = Image.open("cookie.jpg").convert("RGBA")
cookie_image = ImageTk.PhotoImage(cookie_pil)

bg_label = tk.Label(root, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
bg_label.lower()

# --- Game state ---
cookie_count = 0
auto_clickers = 0
upgrade_cost = 10

# --- Save / Load ---
def save_game():
    data = {
        "cookie_count": cookie_count,
        "auto_clickers": auto_clickers,
        "upgrade_cost": upgrade_cost,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    save_status_label.config(text="Game saved!")
    root.after(2000, lambda: save_status_label.config(text=""))

def load_game():
    global cookie_count, auto_clickers, upgrade_cost
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            cookie_count  = data.get("cookie_count",  0)
            auto_clickers = data.get("auto_clickers", 0)
            upgrade_cost  = data.get("upgrade_cost",  10)
        except (json.JSONDecodeError, KeyError):
            pass  # Corrupt save — start fresh

def on_close():
    save_game()
    root.destroy()

# Load save before building UI so labels start with correct values
load_game()

# --- UI ---
counter_label = tk.Label(root, text=f"Cookies: {cookie_count}", font=("Arial", 18))
counter_label.pack(pady=20)

def click_cookie():
    global cookie_count
    cookie_count += 1
    counter_label.config(text=f"Cookies: {cookie_count}")

click_button = tk.Button(root, image=cookie_image, command=click_cookie,
                         borderwidth=0, highlightthickness=0)
click_button.image = cookie_image
click_button.pack(pady=10)

def upgrade_click():
    global cookie_count, auto_clickers, upgrade_cost
    if cookie_count >= upgrade_cost:
        cookie_count  -= upgrade_cost
        auto_clickers += 1
        upgrade_cost   = int(upgrade_cost * 1.5)
        counter_label.config(text=f"Cookies: {cookie_count}")
        upgrade_button.config(
            text=f"Buy Autoclicker ({auto_clickers}) - Cost: {upgrade_cost}"
        )

upgrade_button = tk.Button(
    root,
    text=f"Buy Autoclicker ({auto_clickers}) - Cost: {upgrade_cost}",
    font=("Arial", 12),
    command=upgrade_click,
)
upgrade_button.pack(pady=5)

# Manual save button + status label
save_button = tk.Button(root, text="💾 Save Game", font=("Arial", 12), command=save_game)
save_button.pack(pady=5)

save_status_label = tk.Label(root, text="", font=("Arial", 10), fg="green")
save_status_label.pack()

# --- Auto-clicker loop ---
def run_autoclicker():
    global cookie_count
    cookie_count += auto_clickers
    counter_label.config(text=f"Cookies: {cookie_count}")
    root.after(1000, run_autoclicker)

# Auto-save every 60 seconds
def auto_save():
    save_game()
    root.after(60000, auto_save)

run_autoclicker()
auto_save()

# Save on window close
root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
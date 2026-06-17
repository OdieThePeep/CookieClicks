import tkinter as tk
import json
import os
import random
from PIL import Image, ImageTk

SAVE_FILE = "cookie_save.json"

# ── Palette ──────────────────────────────────────────────
PANEL_BG     = "#1A0900"
PANEL_BORDER = "#7A3F0A"
GOLD         = "#F5C518"
CREAM        = "#FFF3DC"
MOCHA        = "#B8905A"
BTN_BG       = "#5C2E0A"
BTN_ACTIVE   = "#7A3F15"
BTN_DIM      = "#3A1A05"
SAVE_BG      = "#183C24"
SAVE_ACTIVE  = "#2A6040"
FLASH        = "#FFE57F"
GREEN_TEXT   = "#5DA847"

# ── Layout constants ─────────────────────────────────────
TITLE_H  = 52
STATS_H  = 84
SHOP_H   = 195
BOTTOM_H = 55
TOP_PAD  = 12

# ── Window ───────────────────────────────────────────────
root = tk.Tk()
root.title("Cookie Clicker")
root.geometry("700x700")
root.minsize(700, 700)
root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())
root.resizable(True, True)

# ── Background canvas ────────────────────────────────────
bg_canvas = tk.Canvas(root, highlightthickness=0, bd=0)
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

# Pre-generate cookie silhouettes at fractional positions (fixed seed)
random.seed(42)
DECOR = []
for _ in range(20):
    fx   = random.random()
    fy   = random.random()
    r    = random.randint(10, 52)
    chips = [(random.randint(-r//2, r//2),
              random.randint(-r//2, r//2),
              max(2, r // 8)) for _ in range(3)]
    DECOR.append((fx, fy, r, chips))

def lerp(a, b, t):
    return int(a + (b - a) * t)

def draw_background(w, h):
    bg_canvas.delete("all")

    # Vertical gradient: near-black chocolate → deep amber-brown
    top_col    = (0x0D, 0x04, 0x00)
    bottom_col = (0x2C, 0x10, 0x00)
    steps = 60
    for i in range(steps):
        t  = i / steps
        r  = lerp(top_col[0], bottom_col[0], t)
        g  = lerp(top_col[1], bottom_col[1], t)
        b  = lerp(top_col[2], bottom_col[2], t)
        y0 = int(h * i / steps)
        y1 = int(h * (i + 1) / steps) + 1
        bg_canvas.create_rectangle(0, y0, w, y1, fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

    # Subtle cookie silhouettes scattered across the background
    for fx, fy, radius, chips in DECOR:
        cx, cy = int(fx * w), int(fy * h)
        bg_canvas.create_oval(cx - radius, cy - radius,
                              cx + radius, cy + radius,
                              fill="#1E0A00", outline="#2E1600", width=1)
        for dx, dy, cr in chips:
            bg_canvas.create_oval(cx+dx-cr, cy+dy-cr,
                                  cx+dx+cr, cy+dy+cr,
                                  fill="#120600", outline="")

    # Warm radial glow centred on the cookie button zone
    stats_bot = TOP_PAD + TITLE_H + 10 + STATS_H          # 158
    bot_y     = h - BOTTOM_H - 10
    shop_y    = bot_y - SHOP_H - 8
    glow_cy   = stats_bot + (shop_y - stats_bot) // 2
    glow_cx   = w // 2
    glow_r    = int(min(w, h) * 0.30)
    glow_steps = 30
    for i in range(glow_steps, 0, -1):
        t     = i / glow_steps
        r_px  = int(glow_r * t)
        r_val = int(0x3A * (1 - t))
        g_val = int(0x14 * (1 - t))
        bg_canvas.create_oval(glow_cx - r_px, glow_cy - r_px,
                              glow_cx + r_px, glow_cy + r_px,
                              fill=f"#{r_val:02x}{g_val:02x}00", outline="")

# ── Cookie image ─────────────────────────────────────────
cookie_pil = Image.open("cookie.png").convert("RGBA")
cookie_pil.thumbnail((210, 210), Image.LANCZOS)
cookie_image = ImageTk.PhotoImage(cookie_pil)

# ── Game state ───────────────────────────────────────────
cookie_count       = 0
auto_clickers      = 0
upgrade_cost       = 10
click_power        = 1
click_upgrades     = 0
click_upgrade_cost = 100

# ── Save / Load ──────────────────────────────────────────
def save_game():
    data = {
        "cookie_count":       cookie_count,
        "auto_clickers":      auto_clickers,
        "upgrade_cost":       upgrade_cost,
        "click_power":        click_power,
        "click_upgrades":     click_upgrades,
        "click_upgrade_cost": click_upgrade_cost,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    save_status.config(text="✓  Saved")
    root.after(2500, lambda: save_status.config(text=""))

def load_game():
    global cookie_count, auto_clickers, upgrade_cost
    global click_power, click_upgrades, click_upgrade_cost
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                d = json.load(f)
            cookie_count       = d.get("cookie_count",       0)
            auto_clickers      = d.get("auto_clickers",      0)
            upgrade_cost       = d.get("upgrade_cost",       10)
            click_power        = d.get("click_power",        1)
            click_upgrades     = d.get("click_upgrades",     0)
            click_upgrade_cost = d.get("click_upgrade_cost", 100)
        except (json.JSONDecodeError, KeyError):
            pass

def on_close():
    save_game()
    root.destroy()

load_game()  # before UI labels are built

# ── Title panel ───────────────────────────────────────────
p_title = tk.Frame(root, bg=PANEL_BG,
                   highlightbackground=PANEL_BORDER, highlightthickness=2)
tk.Label(p_title, text="🍪  COOKIE CLICKER",
         font=("Georgia", 22, "bold"), bg=PANEL_BG, fg=GOLD).pack(expand=True)

# ── Stats panel ───────────────────────────────────────────
p_stats = tk.Frame(root, bg=PANEL_BG,
                   highlightbackground=PANEL_BORDER, highlightthickness=2)
counter_label = tk.Label(p_stats, text=f"🍪  {cookie_count:,}",
                         font=("Georgia", 30, "bold"), bg=PANEL_BG, fg=CREAM)
counter_label.pack(pady=(8, 2))
cps_label = tk.Label(p_stats,
                     text=f"{auto_clickers} per second   ·   {click_power}× per click",
                     font=("Arial", 11), bg=PANEL_BG, fg=MOCHA)
cps_label.pack()

# ── Cookie button ─────────────────────────────────────────
def click_cookie():
    global cookie_count
    cookie_count += click_power
    counter_label.config(text=f"🍪  {cookie_count:,}", fg=FLASH)
    root.after(130, lambda: counter_label.config(fg=CREAM))

click_button = tk.Button(root, image=cookie_image, command=click_cookie,
                         borderwidth=0, highlightthickness=0,
                         cursor="hand2", relief=tk.FLAT)
click_button.image = cookie_image

# ── Shop panel ────────────────────────────────────────────
p_shop = tk.Frame(root, bg=PANEL_BG,
                  highlightbackground=PANEL_BORDER, highlightthickness=2)
tk.Label(p_shop, text="── UPGRADES ──",
         font=("Georgia", 11, "bold"), bg=PANEL_BG, fg=GOLD).pack(pady=(12, 10))

btn_row = tk.Frame(p_shop, bg=PANEL_BG)
btn_row.pack(fill="x", padx=12)

def refresh_buttons():
    can_auto  = cookie_count >= upgrade_cost
    can_click = cookie_count >= click_upgrade_cost
    upgrade_button.config(
        bg=BTN_BG if can_auto  else BTN_DIM,
        fg=GOLD   if can_auto  else MOCHA,
        activebackground=BTN_ACTIVE if can_auto  else BTN_DIM,
    )
    click_power_button.config(
        bg=BTN_BG if can_click else BTN_DIM,
        fg=GOLD   if can_click else MOCHA,
        activebackground=BTN_ACTIVE if can_click else BTN_DIM,
    )

def upgrade_click():
    global cookie_count, auto_clickers, upgrade_cost
    if cookie_count >= upgrade_cost:
        cookie_count  -= upgrade_cost
        auto_clickers += 1
        upgrade_cost   = int(upgrade_cost * 1.5)
        counter_label.config(text=f"🍪  {cookie_count:,}")
        cps_label.config(text=f"{auto_clickers} per second   ·   {click_power}× per click")
        upgrade_button.config(
            text=f"🤖  Autoclicker\n×{auto_clickers}  ·  cost: {upgrade_cost:,} 🍪")
        refresh_buttons()

def click_power_buy():
    global cookie_count, click_power, click_upgrades, click_upgrade_cost
    if cookie_count >= click_upgrade_cost:
        cookie_count       -= click_upgrade_cost
        click_upgrades     += 1
        click_power        *= 2
        click_upgrade_cost *= 10
        counter_label.config(text=f"🍪  {cookie_count:,}")
        cps_label.config(text=f"{auto_clickers} per second   ·   {click_power}× per click")
        click_power_button.config(
            text=f"👆  Click Power\n×{click_power}  ·  cost: {click_upgrade_cost:,} 🍪")
        refresh_buttons()

upgrade_button = tk.Button(
    btn_row,
    text=f"🤖  Autoclicker\n×{auto_clickers}  ·  cost: {upgrade_cost:,} 🍪",
    font=("Arial", 12, "bold"), bg=BTN_BG, fg=GOLD,
    activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=14, cursor="hand2", justify="center",
    command=upgrade_click,
)
upgrade_button.pack(side="left", expand=True, fill="x", padx=(0, 6))

click_power_button = tk.Button(
    btn_row,
    text=f"👆  Click Power\n×{click_power}  ·  cost: {click_upgrade_cost:,} 🍪",
    font=("Arial", 12, "bold"), bg=BTN_BG, fg=GOLD,
    activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=14, cursor="hand2", justify="center",
    command=click_power_buy,
)
click_power_button.pack(side="left", expand=True, fill="x", padx=(6, 0))

# ── Bottom bar ────────────────────────────────────────────
p_bottom = tk.Frame(root, bg=PANEL_BG,
                    highlightbackground=PANEL_BORDER, highlightthickness=2)
row = tk.Frame(p_bottom, bg=PANEL_BG)
row.pack(expand=True, fill="both", padx=12)

save_button = tk.Button(
    row, text="💾  Save Game", font=("Arial", 11, "bold"),
    bg=SAVE_BG, fg=CREAM, activebackground=SAVE_ACTIVE, activeforeground=CREAM,
    relief=tk.FLAT, padx=16, pady=6, cursor="hand2", command=save_game,
)
save_button.pack(side="left", pady=10)

save_status = tk.Label(row, text="", font=("Arial", 10, "italic"),
                       bg=PANEL_BG, fg=GREEN_TEXT)
save_status.pack(side="left", padx=14)

# ── Responsive layout ─────────────────────────────────────
def do_layout(w, h):
    pad_x   = max(20, int(w * 0.04))
    panel_w = w - 2 * pad_x

    # Fixed top section
    p_title.place(x=pad_x, y=TOP_PAD,                   width=panel_w, height=TITLE_H)
    p_stats.place(x=pad_x, y=TOP_PAD + TITLE_H + 10,    width=panel_w, height=STATS_H)

    # Bottom sections anchor to window bottom
    bot_y  = h - BOTTOM_H - 10
    shop_y = bot_y - SHOP_H - 8
    p_shop.place(x=pad_x,   y=shop_y, width=panel_w, height=SHOP_H)
    p_bottom.place(x=pad_x, y=bot_y,  width=panel_w, height=BOTTOM_H)

    # Cookie button floats in the middle gap
    stats_bot = TOP_PAD + TITLE_H + 10 + STATS_H
    cookie_y  = stats_bot + (shop_y - stats_bot) // 2
    click_button.place(relx=0.5, y=cookie_y, anchor="center")

_resize_job = None

def on_resize(event):
    global _resize_job
    if event.widget is not root:
        return
    w, h = event.width, event.height
    if w < 100 or h < 100:   # ignore spurious startup events
        return
    if _resize_job:
        root.after_cancel(_resize_job)
    _resize_job = root.after(30, lambda: _apply_resize(w, h))

def _apply_resize(w, h):
    draw_background(w, h)
    do_layout(w, h)

root.bind("<Configure>", on_resize)

# ── Initial render ────────────────────────────────────────
root.update_idletasks()
tk.Misc.lower(bg_canvas)   # widget-level lower (bypasses Canvas.tag_lower override)
draw_background(700, 700)
do_layout(700, 700)

# ── Autoclicker loop ──────────────────────────────────────
def run_autoclicker():
    global cookie_count
    cookie_count += auto_clickers
    counter_label.config(text=f"🍪  {cookie_count:,}")
    refresh_buttons()
    root.after(1000, run_autoclicker)

def auto_save():
    save_game()
    root.after(60_000, auto_save)

root.after(60_000, auto_save)
run_autoclicker()
refresh_buttons()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

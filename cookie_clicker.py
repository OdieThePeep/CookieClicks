import tkinter as tk
import json
import os
import random
import math
from PIL import Image, ImageTk

SAVE_FILE = "cookie_save.json"
AUTO_CLICKER_BASE_COST = 10
GRANDMA_BASE_COST = 100
COST_MULTIPLIER = 1.15
AUTO_CLICKER_CPS = 0.1
GRANDMA_CPS = 1
BOOST_UPGRADE_ONE_COST = 100
BOOST_UPGRADE_TWO_COST = 500
AMBIDEXTROUS_COST = 10000
THOUSAND_FINGERS_COST = 100000
THOUSAND_FINGERS_BONUS = 0.1
MILLION_FINGERS_COST = 10000000
MILLION_FINGERS_MULTIPLIER = 5

# ── Palette ──────────────────────────────────────────────
PANEL_BG     = "#21140D"
PANEL_BORDER = "#A36A2C"
GOLD         = "#FFD36A"
CREAM        = "#FFF7E8"
MOCHA        = "#C59A68"
BTN_BG       = "#6B3A16"
BTN_ACTIVE   = "#8D4E1F"
BTN_DIM      = "#332117"
SAVE_BG      = "#1F5732"
SAVE_ACTIVE  = "#2D7748"
FLASH        = "#FFF0A8"
GREEN_TEXT   = "#75C985"
TAB_BG       = "#3C2719"
CARD_BORDER  = "#D09045"
SHADOW       = "#100A07"

# ── Layout constants ─────────────────────────────────────
TITLE_H  = 70
STATS_H  = 122
SHOP_H   = 245
BOTTOM_H = 64
TOP_PAD  = 12

# ── Window ───────────────────────────────────────────────
root = tk.Tk()
root.title("Cookie Clicker Deluxe")
root.geometry("1280x820")
root.minsize(760, 720)
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

    # Vertical gradient: near-black midnight → deep navy blue
    top_col    = (0x10, 0x0A, 0x18)
    bottom_col = (0x20, 0x12, 0x0A)
    steps = 60
    for i in range(steps):
        t  = i / steps
        r  = lerp(top_col[0], bottom_col[0], t)
        g  = lerp(top_col[1], bottom_col[1], t)
        b  = lerp(top_col[2], bottom_col[2], t)
        y0 = int(h * i / steps)
        y1 = int(h * (i + 1) / steps) + 1
        bg_canvas.create_rectangle(0, y0, w, y1, fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

    # Custom cookie silhouettes — scalloped edge + chip dots, all very subtle
    FILL    = "#22140C"
    OUTLINE = "#3A2110"
    CHIP    = "#130B07"

    for fx, fy, radius, chips in DECOR:
        cx, cy = int(fx * w), int(fy * h)

        # Cookie body
        bg_canvas.create_oval(cx - radius, cy - radius,
                              cx + radius, cy + radius,
                              fill=FILL, outline=OUTLINE, width=1)

        # Scalloped edge: small bumps evenly spaced around the perimeter
        num_bumps = max(6, radius // 5)
        bump_r    = max(2, radius // 7)
        for j in range(num_bumps):
            angle = 2 * math.pi * j / num_bumps
            bx = cx + int(radius * math.cos(angle))
            by = cy + int(radius * math.sin(angle))
            bg_canvas.create_oval(bx - bump_r, by - bump_r,
                                  bx + bump_r, by + bump_r,
                                  fill=FILL, outline=OUTLINE, width=1)

        # Chocolate chip dots
        for dx, dy, cr in chips:
            bg_canvas.create_oval(cx + dx - cr, cy + dy - cr,
                                  cx + dx + cr, cy + dy + cr,
                                  fill=CHIP, outline="")

    # Warm amber radial glow centred on the cookie button zone
    # (kept warm to contrast against the cool blue background)
    stats_bot = TOP_PAD + TITLE_H + 10 + STATS_H
    bot_y     = h - BOTTOM_H - 10
    shop_y    = bot_y - SHOP_H - 8
    glow_cy   = stats_bot + (shop_y - stats_bot) // 2
    glow_cx   = w // 2
    glow_r    = int(min(w, h) * 0.24)
    glow_steps = 30
    for i in range(glow_steps, 0, -1):
        t     = i / glow_steps
        r_px  = int(glow_r * t)
        r_val = int(0x7A * (1 - t))
        g_val = int(0x39 * (1 - t))
        b_val = int(0x12 * (1 - t))
        bg_canvas.create_oval(glow_cx - r_px, glow_cy - r_px,
                              glow_cx + r_px, glow_cy + r_px,
                              fill=f"#{r_val:02x}{g_val:02x}{b_val:02x}", outline="")

# ── Cookie image ─────────────────────────────────────────
cookie_pil = Image.open("cookie.png").convert("RGBA")
cookie_pil.thumbnail((240, 240), Image.LANCZOS)

# Composite cookie onto the panel background colour so transparent
# pixels become dark rather than showing tkinter's default button grey.
_cookie_bg = Image.new("RGBA", cookie_pil.size, (0x21, 0x14, 0x0D, 255))
_cookie_bg.paste(cookie_pil, mask=cookie_pil.split()[3])   # alpha channel as mask
cookie_image = ImageTk.PhotoImage(_cookie_bg.convert("RGB"))

# ── Game state ───────────────────────────────────────────
cookie_count       = 0
auto_clickers      = 0
upgrade_cost       = AUTO_CLICKER_BASE_COST
grandmas           = 0
grandma_cost       = GRANDMA_BASE_COST
click_power        = 1
boost_upgrade_one  = False
boost_upgrade_two  = False
ambidextrous_upgrade = False
thousand_fingers_upgrade = False
million_fingers_upgrade = False

def building_cost(base_cost, owned):
    return int(base_cost * (COST_MULTIPLIER ** owned))

def boost_multiplier():
    return 2 ** (boost_upgrade_one + boost_upgrade_two + ambidextrous_upgrade)

def update_click_power():
    global click_power
    click_power = boost_multiplier()

def cookies_per_second():
    return auto_clickers * autoclicker_production() + grandmas * GRANDMA_CPS

def autoclicker_production():
    return AUTO_CLICKER_CPS * boost_multiplier() + thousand_fingers_bonus()

def thousand_fingers_bonus():
    if not thousand_fingers_upgrade:
        return 0
    multiplier = MILLION_FINGERS_MULTIPLIER if million_fingers_upgrade else 1
    return grandmas * THOUSAND_FINGERS_BONUS * multiplier

def grandma_production():
    return GRANDMA_CPS

def format_cookies(amount):
    return f"{amount:,.1f}" if amount % 1 else f"{int(amount):,}"

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        if self.tip:
            return
        text = self.text() if callable(self.text) else self.text
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip, text=text, justify="left",
            font=("Segoe UI", 10), bg=CREAM, fg=PANEL_BG,
            relief=tk.SOLID, borderwidth=1, padx=8, pady=5,
        ).pack()

    def hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# ── Save / Load ──────────────────────────────────────────
def save_game():
    data = {
        "cookie_count":       cookie_count,
        "auto_clickers":      auto_clickers,
        "upgrade_cost":       upgrade_cost,
        "grandmas":           grandmas,
        "grandma_cost":       grandma_cost,
        "click_power":        click_power,
        "boost_upgrade_one":  boost_upgrade_one,
        "boost_upgrade_two":  boost_upgrade_two,
        "ambidextrous_upgrade": ambidextrous_upgrade,
        "thousand_fingers_upgrade": thousand_fingers_upgrade,
        "million_fingers_upgrade": million_fingers_upgrade,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    save_status.config(text="✓  Saved")
    root.after(2500, lambda: save_status.config(text=""))

def load_game():
    global cookie_count, auto_clickers, upgrade_cost, grandmas, grandma_cost
    global click_power, boost_upgrade_one, boost_upgrade_two, ambidextrous_upgrade, thousand_fingers_upgrade, million_fingers_upgrade
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                d = json.load(f)
            cookie_count       = d.get("cookie_count",       0)
            auto_clickers      = d.get("auto_clickers",      0)
            upgrade_cost       = building_cost(AUTO_CLICKER_BASE_COST, auto_clickers)
            grandmas           = d.get("grandmas",           0)
            grandma_cost       = building_cost(GRANDMA_BASE_COST, grandmas)
            boost_upgrade_one  = d.get("boost_upgrade_one",  False)
            boost_upgrade_two  = d.get("boost_upgrade_two",  False)
            ambidextrous_upgrade = d.get("ambidextrous_upgrade", False)
            thousand_fingers_upgrade = d.get("thousand_fingers_upgrade", False)
            million_fingers_upgrade = d.get("million_fingers_upgrade", False)
            update_click_power()
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
counter_label = tk.Label(p_stats, text=f"🍪  {format_cookies(cookie_count)}",
                         font=("Georgia", 30, "bold"), bg=PANEL_BG, fg=CREAM)
counter_label.pack(pady=(8, 2))
cps_label = tk.Label(p_stats,
                     text=f"{format_cookies(cookies_per_second())} per second",
                     font=("Segoe UI", 11), bg=PANEL_BG, fg=MOCHA)
cps_label.pack()


# --- UI Enhancements ---
def spawn_particle(x, y, text="+1"):
    lbl = tk.Label(root, text=text, fg=GOLD, bg=PANEL_BG,
                   font=("Segoe UI", 14, "bold"))
    lbl.place(x=x, y=y)

    def rise(step=0):
        if step > 20:
            lbl.destroy()
            return
        lbl.place(x=x, y=y - step * 3)
        root.after(16, lambda: rise(step + 1))
    rise()

def pulse_cookie():
    try:
        click_button.place_configure()
        click_button.config(relief=tk.RAISED)
        root.after(80, lambda: click_button.config(relief=tk.FLAT))
    except:
        pass


# ── Cookie button ─────────────────────────────────────────
def click_cookie():
    global cookie_count
    cookie_count += click_power
    pulse_cookie()
    try:
        x = click_button.winfo_x() + 100
        y = click_button.winfo_y() + 40
        spawn_particle(x, y, f"+{click_power}")
    except:
        pass
    counter_label.config(text=f"🍪  {format_cookies(cookie_count)}", fg=FLASH)
    refresh_buttons()
    root.after(130, lambda: counter_label.config(fg=CREAM))

click_button = tk.Button(root, image=cookie_image, command=click_cookie,
                         borderwidth=0, highlightthickness=0,
                         cursor="hand2", relief=tk.FLAT,
                         bg="#1A0900", activebackground="#1A0900")
click_button.image = cookie_image

# ── Shop panel ────────────────────────────────────────────
p_shop = tk.Frame(root, bg=PANEL_BG,
                  highlightbackground=PANEL_BORDER, highlightthickness=2)
active_shop_tab = "buildings"

tab_row = tk.Frame(p_shop, bg=PANEL_BG)
tab_row.pack(fill="x", padx=12, pady=(12, 10))

shop_content = tk.Frame(p_shop, bg=PANEL_BG)
shop_content.pack(fill="both", expand=True, padx=12)

buildings_tab = tk.Frame(shop_content, bg=PANEL_BG)
upgrades_tab = tk.Frame(shop_content, bg=PANEL_BG)

building_row = tk.Frame(buildings_tab, bg=PANEL_BG)
building_row.pack(fill="x")

upgrade_row = tk.Frame(upgrades_tab, bg=PANEL_BG)
upgrade_row.pack(fill="x")

no_upgrades_label = tk.Label(upgrades_tab, text="No upgrades available",
                             font=("Segoe UI", 12, "italic"), bg=PANEL_BG, fg=MOCHA)

def refresh_tab_buttons():
    building_tab_button.config(
        bg=BTN_BG if active_shop_tab == "buildings" else BTN_DIM,
        fg=GOLD if active_shop_tab == "buildings" else MOCHA,
        activebackground=BTN_ACTIVE if active_shop_tab == "buildings" else BTN_DIM,
    )
    upgrades_tab_button.config(
        bg=BTN_BG if active_shop_tab == "upgrades" else BTN_DIM,
        fg=GOLD if active_shop_tab == "upgrades" else MOCHA,
        activebackground=BTN_ACTIVE if active_shop_tab == "upgrades" else BTN_DIM,
    )

def show_shop_tab(tab_name):
    global active_shop_tab
    active_shop_tab = tab_name
    buildings_tab.pack_forget()
    upgrades_tab.pack_forget()
    if active_shop_tab == "buildings":
        buildings_tab.pack(fill="both", expand=True)
    else:
        upgrades_tab.pack(fill="both", expand=True)
    refresh_tab_buttons()

building_tab_button = tk.Button(
    tab_row, text="Buildings", font=("Segoe UI", 11, "bold"),
    bg=BTN_BG, fg=GOLD, activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=6, cursor="hand2",
    command=lambda: show_shop_tab("buildings"),
)
building_tab_button.pack(side="left", expand=True, fill="x", padx=(0, 6))

upgrades_tab_button = tk.Button(
    tab_row, text="Upgrades", font=("Segoe UI", 11, "bold"),
    bg=BTN_DIM, fg=MOCHA, activebackground=BTN_DIM, activeforeground=GOLD,
    relief=tk.FLAT, pady=6, cursor="hand2",
    command=lambda: show_shop_tab("upgrades"),
)
upgrades_tab_button.pack(side="left", expand=True, fill="x", padx=(6, 0))

def refresh_buttons():
    can_auto    = cookie_count >= upgrade_cost
    can_grandma = cookie_count >= grandma_cost
    show_boost_one = cookie_count >= BOOST_UPGRADE_ONE_COST and not boost_upgrade_one
    show_boost_two = cookie_count >= BOOST_UPGRADE_TWO_COST and not boost_upgrade_two
    show_ambidextrous = auto_clickers >= 10 and not ambidextrous_upgrade
    can_ambidextrous = cookie_count >= AMBIDEXTROUS_COST
    show_thousand_fingers = auto_clickers >= 25 and not thousand_fingers_upgrade
    can_thousand_fingers = cookie_count >= THOUSAND_FINGERS_COST
    show_million_fingers = auto_clickers >= 50 and not million_fingers_upgrade
    can_million_fingers = cookie_count >= MILLION_FINGERS_COST
    upgrade_button.config(
        bg=BTN_BG if can_auto  else BTN_DIM,
        fg=GOLD   if can_auto  else MOCHA,
        activebackground=BTN_ACTIVE if can_auto  else BTN_DIM,
    )
    grandma_button.config(
        bg=BTN_BG if can_grandma else BTN_DIM,
        fg=GOLD   if can_grandma else MOCHA,
        activebackground=BTN_ACTIVE if can_grandma else BTN_DIM,
    )
    ambidextrous_button.config(
        bg=BTN_BG if can_ambidextrous else BTN_DIM,
        fg=GOLD   if can_ambidextrous else MOCHA,
        activebackground=BTN_ACTIVE if can_ambidextrous else BTN_DIM,
    )
    thousand_fingers_button.config(
        bg=BTN_BG if can_thousand_fingers else BTN_DIM,
        fg=GOLD   if can_thousand_fingers else MOCHA,
        activebackground=BTN_ACTIVE if can_thousand_fingers else BTN_DIM,
    )
    million_fingers_button.config(
        bg=BTN_BG if can_million_fingers else BTN_DIM,
        fg=GOLD   if can_million_fingers else MOCHA,
        activebackground=BTN_ACTIVE if can_million_fingers else BTN_DIM,
    )
    boost_one_button.pack_forget()
    boost_two_button.pack_forget()
    ambidextrous_button.pack_forget()
    thousand_fingers_button.pack_forget()
    million_fingers_button.pack_forget()
    no_upgrades_label.pack_forget()
    visible_upgrades = []
    if show_boost_one:
        visible_upgrades.append(boost_one_button)
    if show_boost_two:
        visible_upgrades.append(boost_two_button)
    if show_ambidextrous:
        visible_upgrades.append(ambidextrous_button)
    if show_thousand_fingers:
        visible_upgrades.append(thousand_fingers_button)
    if show_million_fingers:
        visible_upgrades.append(million_fingers_button)
    for index, button in enumerate(visible_upgrades):
        button.pack(
            side="left", expand=True, fill="x",
            padx=(0 if index == 0 else 6, 0 if index == len(visible_upgrades) - 1 else 6),
        )
    if not visible_upgrades:
        no_upgrades_label.pack(expand=True)

def upgrade_click():
    global cookie_count, auto_clickers, upgrade_cost
    if cookie_count >= upgrade_cost:
        cookie_count  -= upgrade_cost
        auto_clickers += 1
        upgrade_cost   = building_cost(AUTO_CLICKER_BASE_COST, auto_clickers)
        counter_label.config(text=f"🍪  {format_cookies(cookie_count)}")
        cps_label.config(text=f"{format_cookies(cookies_per_second())} per second")
        upgrade_button.config(
            text=f"🤖  Autoclicker\n×{auto_clickers}  ·  {upgrade_cost:,} 🍪")
        refresh_buttons()

def grandma_buy():
    global cookie_count, grandmas, grandma_cost
    if cookie_count >= grandma_cost:
        cookie_count -= grandma_cost
        grandmas     += 1
        grandma_cost  = building_cost(GRANDMA_BASE_COST, grandmas)
        counter_label.config(text=f"🍪  {format_cookies(cookie_count)}")
        cps_label.config(text=f"{format_cookies(cookies_per_second())} per second")
        grandma_button.config(
            text=f"👵  Grandmas\n×{grandmas}  ·  {grandma_cost:,} 🍪")
        refresh_buttons()

def buy_boost_upgrade(upgrade_number):
    global cookie_count, boost_upgrade_one, boost_upgrade_two
    if upgrade_number == 1:
        if boost_upgrade_one or cookie_count < BOOST_UPGRADE_ONE_COST:
            return
        cookie_count -= BOOST_UPGRADE_ONE_COST
        boost_upgrade_one = True
    else:
        if boost_upgrade_two or cookie_count < BOOST_UPGRADE_TWO_COST:
            return
        cookie_count -= BOOST_UPGRADE_TWO_COST
        boost_upgrade_two = True
    update_click_power()
    counter_label.config(text=f"🍪  {format_cookies(cookie_count)}")
    cps_label.config(text=f"{format_cookies(cookies_per_second())} per second")
    refresh_buttons()

def buy_ambidextrous():
    global cookie_count, ambidextrous_upgrade
    if ambidextrous_upgrade or auto_clickers < 10 or cookie_count < AMBIDEXTROUS_COST:
        return
    cookie_count -= AMBIDEXTROUS_COST
    ambidextrous_upgrade = True
    update_click_power()
    counter_label.config(text=f"🍪  {format_cookies(cookie_count)}")
    cps_label.config(text=f"{format_cookies(cookies_per_second())} per second")
    refresh_buttons()

def buy_thousand_fingers():
    global cookie_count, thousand_fingers_upgrade
    if thousand_fingers_upgrade or auto_clickers < 25 or cookie_count < THOUSAND_FINGERS_COST:
        return
    cookie_count -= THOUSAND_FINGERS_COST
    thousand_fingers_upgrade = True
    counter_label.config(text=f"🍪  {format_cookies(cookie_count)}")
    cps_label.config(text=f"{format_cookies(cookies_per_second())} per second")
    refresh_buttons()

def buy_million_fingers():
    global cookie_count, million_fingers_upgrade
    if million_fingers_upgrade or auto_clickers < 50 or cookie_count < MILLION_FINGERS_COST:
        return
    cookie_count -= MILLION_FINGERS_COST
    million_fingers_upgrade = True
    counter_label.config(text=f"🍪  {format_cookies(cookie_count)}")
    cps_label.config(text=f"{format_cookies(cookies_per_second())} per second")
    refresh_buttons()

upgrade_button = tk.Button(
    building_row,
    text=f"🤖  Autoclicker\n×{auto_clickers}  ·  {upgrade_cost:,} 🍪",
    font=("Segoe UI", 12, "bold"), bg=BTN_BG, fg=GOLD,
    activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=14, cursor="hand2", justify="center",
    command=upgrade_click,
)
upgrade_button.pack(side="left", expand=True, fill="x", padx=(0, 6))

grandma_button = tk.Button(
    building_row,
    text=f"👵  Grandmas\n×{grandmas}  ·  {grandma_cost:,} 🍪",
    font=("Segoe UI", 12, "bold"), bg=BTN_BG, fg=GOLD,
    activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=14, cursor="hand2", justify="center",
    command=grandma_buy,
)
grandma_button.pack(side="left", expand=True, fill="x", padx=6)

boost_one_button = tk.Button(
    upgrade_row,
    text=f"⚡  Better Clicking\n{BOOST_UPGRADE_ONE_COST:,} 🍪",
    font=("Segoe UI", 11, "bold"), bg=BTN_BG, fg=GOLD,
    activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=12, cursor="hand2", justify="center",
    command=lambda: buy_boost_upgrade(1),
)

boost_two_button = tk.Button(
    upgrade_row,
    text=f"⚡  Even Better Clicking\n{BOOST_UPGRADE_TWO_COST:,} 🍪",
    font=("Segoe UI", 11, "bold"), bg=BTN_BG, fg=GOLD,
    activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=12, cursor="hand2", justify="center",
    command=lambda: buy_boost_upgrade(2),
)

ambidextrous_button = tk.Button(
    upgrade_row,
    text=f"🖐  Ambidextrous\n{AMBIDEXTROUS_COST:,} 🍪",
    font=("Segoe UI", 11, "bold"), bg=BTN_BG, fg=GOLD,
    activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=12, cursor="hand2", justify="center",
    command=buy_ambidextrous,
)

thousand_fingers_button = tk.Button(
    upgrade_row,
    text=f"☝  Thousand Fingers\n{THOUSAND_FINGERS_COST:,} 🍪",
    font=("Segoe UI", 11, "bold"), bg=BTN_BG, fg=GOLD,
    activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=12, cursor="hand2", justify="center",
    command=buy_thousand_fingers,
)

million_fingers_button = tk.Button(
    upgrade_row,
    text=f"☝  Million Fingers\n{MILLION_FINGERS_COST:,} 🍪",
    font=("Segoe UI", 11, "bold"), bg=BTN_BG, fg=GOLD,
    activebackground=BTN_ACTIVE, activeforeground=GOLD,
    relief=tk.FLAT, pady=12, cursor="hand2", justify="center",
    command=buy_million_fingers,
)

Tooltip(
    upgrade_button,
    lambda: (
        f"Each autoclicker: {format_cookies(autoclicker_production())} cookies per second\n"
        f"All autoclickers: {format_cookies(auto_clickers * autoclicker_production())} cookies per second"
    ),
)
Tooltip(
    grandma_button,
    lambda: (
        f"Each grandma: {format_cookies(grandma_production())} cookie per second\n"
        f"All grandmas: {format_cookies(grandmas * grandma_production())} cookies per second"
    ),
)
Tooltip(boost_one_button, "Doubles manual clicks and autoclicker production.")
Tooltip(boost_two_button, "Doubles manual clicks and autoclicker production again.")
Tooltip(ambidextrous_button, "Doubles manual clicks and autoclicker production.")
Tooltip(
    thousand_fingers_button,
    lambda: (
        f"Each non-autoclicker building adds {format_cookies(THOUSAND_FINGERS_BONUS)} cookies per second "
        f"to each autoclicker.\nCurrent bonus: {format_cookies(thousand_fingers_bonus())} cookies per autoclicker"
    ),
)
Tooltip(
    million_fingers_button,
    lambda: (
        f"Multiplies the Thousand Fingers bonus by {MILLION_FINGERS_MULTIPLIER}.\n"
        f"Current bonus: {format_cookies(thousand_fingers_bonus())} cookies per autoclicker"
    ),
)

# ── Bottom bar ────────────────────────────────────────────
p_bottom = tk.Frame(root, bg=PANEL_BG,
                    highlightbackground=PANEL_BORDER, highlightthickness=2)
row = tk.Frame(p_bottom, bg=PANEL_BG)
row.pack(expand=True, fill="both", padx=12)

save_button = tk.Button(
    row, text="💾  Save Game", font=("Segoe UI", 11, "bold"),
    bg=SAVE_BG, fg=CREAM, activebackground=SAVE_ACTIVE, activeforeground=CREAM,
    relief=tk.FLAT, padx=16, pady=6, cursor="hand2", command=save_game,
)
save_button.pack(side="left", pady=10)

save_status = tk.Label(row, text="", font=("Segoe UI", 10, "italic"),
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
    cookie_count += cookies_per_second()
    counter_label.config(text=f"🍪  {format_cookies(cookie_count)}")
    refresh_buttons()
    root.after(1000, run_autoclicker)

def auto_save():
    save_game()
    root.after(60_000, auto_save)

root.after(60_000, auto_save)
show_shop_tab("buildings")
run_autoclicker()
refresh_buttons()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

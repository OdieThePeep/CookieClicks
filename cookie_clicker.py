import tkinter as tk
import json
import os
import random
import math
from PIL import Image, ImageTk, ImageDraw

SAVE_FILE = "cookie_save.json"
AUTO_CLICKER_BASE_COST       = 10
GRANDMA_BASE_COST            = 100
FARM_BASE_COST                = 1100
COST_MULTIPLIER              = 1.15
AUTO_CLICKER_CPS             = 0.1
GRANDMA_CPS                  = 1
FARM_CPS                      = 8

# ── Upgrades (sorted by cost) ─────────────────────────────
UPGRADES = [
    {
        "id": "boost_upgrade_one", "name": "Better Clicking", "emoji": "⚡",
        "cost": 100, "description": "Doubles click power and autoclicker production.",
        "requires_autoclickers": 0, "requires_grandmas": 0, "requires_farms": 0,
        "effect": "doubles_click_power",
    },
    {
        "id": "boost_upgrade_two", "name": "Even Better Clicking", "emoji": "⚡",
        "cost": 500, "description": "Doubles click power and autoclicker production again.",
        "requires_autoclickers": 0, "requires_grandmas": 0, "requires_farms": 0,
        "effect": "doubles_click_power",
    },
    {
        "id": "forwards_from_grandma", "name": "Forwards from Grandma", "emoji": "📮",
        "cost": 1000, "description": "Doubles grandma production.",
        "requires_autoclickers": 0, "requires_grandmas": 1, "requires_farms": 0,
        "effect": "doubles_grandma_production",
    },
    {
        "id": "steel_rolling_pins", "name": "Steel-plated Rolling Pins", "emoji": "🧊",
        "cost": 5000, "description": "Doubles grandma production.",
        "requires_autoclickers": 0, "requires_grandmas": 5, "requires_farms": 0,
        "effect": "doubles_grandma_production",
    },
    {
        "id": "ambidextrous_upgrade", "name": "Ambidextrous", "emoji": "🖐",
        "cost": 10000, "description": "Doubles click power and autoclicker production.",
        "requires_autoclickers": 10, "requires_grandmas": 0, "requires_farms": 0,
        "effect": "doubles_click_power",
    },
    {
        "id": "cheap_hoes", "name": "Cheap Hoes", "emoji": "🌱",
        "cost": 11000, "description": "Doubles farm production.",
        "requires_autoclickers": 0, "requires_grandmas": 0, "requires_farms": 1,
        "effect": "doubles_farm_production",
    },
    {
        "id": "fertilizer", "name": "Fertilizer", "emoji": "💩",
        "cost": 55000, "description": "Doubles farm production.",
        "requires_autoclickers": 0, "requires_grandmas": 0, "requires_farms": 5,
        "effect": "doubles_farm_production",
    },
    {
        "id": "farmer_grandmas", "name": "Farmer Grandmas", "emoji": "👵",
        "cost": 55000,
        "description": "Doubles grandma production. Farms gain +1% cookies/sec per grandma owned.",
        "requires_autoclickers": 0, "requires_grandmas": 1, "requires_farms": 15,
        "effect": "farmer_grandmas",
    },
    {
        "id": "thousand_fingers_upgrade", "name": "Thousand Fingers", "emoji": "☝",
        "cost": 100000, "description": "Each building adds 0.1 cookies/sec per autoclicker.",
        "requires_autoclickers": 25, "requires_grandmas": 0, "requires_farms": 0,
        "effect": "thousand_fingers",
    },
    {
        "id": "million_fingers_upgrade", "name": "Million Fingers", "emoji": "☝",
        "cost": 10000000, "description": "Multiplies the Thousand Fingers bonus ×5.",
        "requires_autoclickers": 50, "requires_grandmas": 0, "requires_farms": 0,
        "effect": "million_fingers",
    },
    {
        "id": "lubricated_dentures", "name": "Lubricated Dentures", "emoji": "🦷",
        "cost": 50000, "description": "Doubles grandma production.",
        "requires_autoclickers": 0, "requires_grandmas": 25, "requires_farms": 0,
        "effect": "doubles_grandma_production",
    },
    {
        "id": "prune_juice", "name": "Prune Juice", "emoji": "🥤",
        "cost": 5000000, "description": "Doubles grandma production.",
        "requires_autoclickers": 0, "requires_grandmas": 50, "requires_farms": 0,
        "effect": "doubles_grandma_production",
    },
    {
        "id": "double_thick_glasses", "name": "Double-Thick Glasses", "emoji": "👓",
        "cost": 500000000, "description": "Doubles grandma production.",
        "requires_autoclickers": 0, "requires_grandmas": 100, "requires_farms": 0,
        "effect": "doubles_grandma_production",
    },
]
UPGRADES.sort(key=lambda u: u["cost"])

THOUSAND_FINGERS_BONUS     = 0.1
MILLION_FINGERS_MULTIPLIER = 5

# ── Palette: warm bakery theme (complete redesign) ─────────
THEMES = {
    "light": {
        "BG":          "#FFF8F0",   # page background, cream
        "SIDEBAR_BG":  "#FFFFFF",
        "HEADER_BG":   "#FFFFFF",
        "CARD_BG":     "#FFF1E6",
        "CARD_HOVER":  "#FFE3CF",
        "CARD_LOCKED": "#F5EEE6",
        "BORDER":      "#F0DCC8",
        "ACCENT":      "#E0556B",   # raspberry
        "ACCENT_DARK": "#B5354A",
        "GOLD":        "#D79A3B",
        "TEXT":        "#4A372A",
        "TEXT_MUTED":  "#A8937E",
        "TEXT_FAINT":  "#C9B9A8",
        "SUCCESS":     "#5E9F6E",
        "PILL_OFF_BG": "#F5EAE0",
        "PILL_OFF_FG": "#B6A18C",
        "WHITE":       "#FFFFFF",
    },
    "dark": {
        "BG":          "#1C1916",   # page background, deep cocoa
        "SIDEBAR_BG":  "#231F1B",
        "HEADER_BG":   "#231F1B",
        "CARD_BG":     "#2B2622",
        "CARD_HOVER":  "#37302A",
        "CARD_LOCKED": "#252119",
        "BORDER":      "#3B342C",
        "ACCENT":      "#E0697D",   # raspberry, brightened for dark bg
        "ACCENT_DARK": "#C24A60",
        "GOLD":        "#E2AC5C",
        "TEXT":        "#F3E9DD",
        "TEXT_MUTED":  "#AB9A89",
        "TEXT_FAINT":  "#6E6155",
        "SUCCESS":     "#7BC58C",
        "PILL_OFF_BG": "#322C25",
        "PILL_OFF_FG": "#8C7C6B",
        "WHITE":       "#FFFFFF",
    },
}

current_theme_name = "light"

def set_theme_globals(name):
    """Pull the named theme's colors into the module-level color
    constants used throughout the UI-building code below."""
    global BG, SIDEBAR_BG, HEADER_BG, CARD_BG, CARD_HOVER, CARD_LOCKED, BORDER, \
        ACCENT, ACCENT_DARK, GOLD, TEXT, TEXT_MUTED, TEXT_FAINT, SUCCESS, \
        PILL_OFF_BG, PILL_OFF_FG, WHITE
    t = THEMES[name]
    BG          = t["BG"]
    SIDEBAR_BG  = t["SIDEBAR_BG"]
    HEADER_BG   = t["HEADER_BG"]
    CARD_BG     = t["CARD_BG"]
    CARD_HOVER  = t["CARD_HOVER"]
    CARD_LOCKED = t["CARD_LOCKED"]
    BORDER      = t["BORDER"]
    ACCENT      = t["ACCENT"]
    ACCENT_DARK = t["ACCENT_DARK"]
    GOLD        = t["GOLD"]
    TEXT        = t["TEXT"]
    TEXT_MUTED  = t["TEXT_MUTED"]
    TEXT_FAINT  = t["TEXT_FAINT"]
    SUCCESS     = t["SUCCESS"]
    PILL_OFF_BG = t["PILL_OFF_BG"]
    PILL_OFF_FG = t["PILL_OFF_FG"]
    WHITE       = t["WHITE"]

set_theme_globals(current_theme_name)

# Static border/divider frames that aren't otherwise kept as named
# widgets get appended here so a theme switch can recolor them too.
border_frames = []

SIDEBAR_W = 340

# ── Window ────────────────────────────────────────────────
root = tk.Tk()
root.title("Cookie Clicker — Bakery")
root.geometry("1280x860")
root.minsize(860, 640)
root.config(bg=BG)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# ── Cookie image ──────────────────────────────────────────
try:
    cookie_pil = Image.open("cookie.png").convert("RGBA")
except Exception:
    cookie_pil = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
    _d = ImageDraw.Draw(cookie_pil)
    _d.ellipse([15, 15, 245, 245], fill=(224, 168, 100), outline=(150, 96, 45), width=4)
    random.seed(7)
    for _ in range(7):
        _x, _y = random.randint(55, 205), random.randint(55, 205)
        _r = random.randint(6, 11)
        _d.ellipse([_x-_r, _y-_r, _x+_r, _y+_r], fill=(96, 56, 24))
cookie_pil.thumbnail((210, 210), Image.LANCZOS)
cookie_image = ImageTk.PhotoImage(cookie_pil)

# ── Golden cookie image (pre-rendered once) ────────────────
_GC_SIZE = 88
_gc_pil  = Image.new("RGBA", (_GC_SIZE, _GC_SIZE), (0, 0, 0, 0))
_gc_draw = ImageDraw.Draw(_gc_pil)
# Soft outer glow ring
for _spread, _alpha in [(0, 60), (3, 40), (6, 20)]:
    _gc_draw.ellipse(
        [_spread, _spread, _GC_SIZE - _spread, _GC_SIZE - _spread],
        fill=(255, 220, 40, _alpha),
    )
# Main golden body
_gc_draw.ellipse([10, 10, _GC_SIZE - 10, _GC_SIZE - 10],
                 fill=(255, 205, 40), outline=(200, 148, 18), width=3)
# Shine highlight
_gc_draw.ellipse([22, 15, 44, 32], fill=(255, 248, 170, 210))
# Darker golden "chips"
_gc_rand = random.Random(99)
for _ in range(6):
    _cx = _gc_rand.randint(20, _GC_SIZE - 24)
    _cy = _gc_rand.randint(20, _GC_SIZE - 24)
    _cr = _gc_rand.randint(4, 7)
    _gc_draw.ellipse([_cx - _cr, _cy - _cr, _cx + _cr, _cy + _cr],
                     fill=(165, 100, 10))
_gc_photo = ImageTk.PhotoImage(_gc_pil)

# ── Game state ────────────────────────────────────────────
cookie_count   = 0
auto_clickers  = 0
upgrade_cost   = AUTO_CLICKER_BASE_COST
grandmas       = 0
grandma_cost   = GRANDMA_BASE_COST
farms          = 0
farm_cost      = FARM_BASE_COST
click_power    = 1

upgrade_states = {u["id"]: False for u in UPGRADES}

def building_cost(base, owned):
    return int(base * (COST_MULTIPLIER ** owned))

def boost_multiplier():
    n = sum([
        upgrade_states.get("boost_upgrade_one", False),
        upgrade_states.get("boost_upgrade_two", False),
        upgrade_states.get("ambidextrous_upgrade", False),
    ])
    return 2 ** n

def update_click_power():
    global click_power
    click_power = boost_multiplier()

def cookies_per_second():
    return (auto_clickers * autoclicker_production()
            + grandmas * grandma_production()
            + farms * farm_production())

def autoclicker_production():
    return AUTO_CLICKER_CPS * boost_multiplier() + thousand_fingers_bonus()

def thousand_fingers_bonus():
    if not upgrade_states.get("thousand_fingers_upgrade", False):
        return 0
    m = MILLION_FINGERS_MULTIPLIER if upgrade_states.get("million_fingers_upgrade", False) else 1
    return grandmas * THOUSAND_FINGERS_BONUS * m

def grandma_production():
    base = GRANDMA_CPS
    if upgrade_states.get("forwards_from_grandma", False):
        base *= 2
    if upgrade_states.get("steel_rolling_pins", False):
        base *= 2
    if upgrade_states.get("farmer_grandmas", False):
        base *= 2
    if upgrade_states.get("lubricated_dentures", False):
        base *= 2
    if upgrade_states.get("prune_juice", False):
        base *= 2
    if upgrade_states.get("double_thick_glasses", False):
        base *= 2
    return base

def farm_production():
    base = FARM_CPS
    if upgrade_states.get("cheap_hoes", False):
        base *= 2
    if upgrade_states.get("fertilizer", False):
        base *= 2
    if upgrade_states.get("farmer_grandmas", False):
        base *= (1 + 0.01 * grandmas)
    return base

def format_cookies(n):
    return f"{n:,.1f}" if n % 1 else f"{int(n):,}"

def bind_recursive(widget, seq, func):
    widget.bind(seq, func, add="+")
    for c in widget.winfo_children():
        bind_recursive(c, seq, func)

# ── Tooltip ───────────────────────────────────────────────
class Tooltip:
    """Popup that appears when hovering any part of a card (including children).
    Uses a short hide-delay so crossing between child widgets doesn't flicker."""

    def __init__(self, widget, text):
        self.widget   = widget
        self.text     = text
        self.tip      = None
        self._hide_id = None
        # Bind to the card and every child widget it currently contains
        self._bind_tree(widget)

    def _bind_tree(self, w):
        w.bind("<Enter>", self._on_enter, add="+")
        w.bind("<Leave>", self._on_leave, add="+")
        for c in w.winfo_children():
            self._bind_tree(c)

    def _on_enter(self, _=None):
        if self._hide_id:
            self.widget.after_cancel(self._hide_id)
            self._hide_id = None
        self.show()

    def _on_leave(self, _=None):
        # Short delay: if mouse re-enters a sibling child we cancel before hiding
        self._hide_id = self.widget.after(80, self._do_hide)

    def _do_hide(self):
        self._hide_id = None
        # Only hide if pointer has actually left the card bounds
        try:
            rx = self.widget.winfo_pointerx() - self.widget.winfo_rootx()
            ry = self.widget.winfo_pointery() - self.widget.winfo_rooty()
            if 0 <= rx <= self.widget.winfo_width() and 0 <= ry <= self.widget.winfo_height():
                return
        except Exception:
            pass
        self.hide()

    def show(self, _=None):
        if self.tip:
            return
        text = self.text() if callable(self.text) else self.text
        x = self.widget.winfo_rootx() + 16
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        self.tip.attributes('-topmost', True)
        tk.Label(self.tip, text=text, justify="left", font=("Segoe UI", 10),
                 bg=ACCENT_DARK, fg=WHITE, relief=tk.FLAT, padx=12, pady=8).pack()

    def hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# ── Save / Load ───────────────────────────────────────────
def save_game():
    data = {
        "cookie_count": cookie_count, "auto_clickers": auto_clickers,
        "upgrade_cost": upgrade_cost, "grandmas": grandmas,
        "grandma_cost": grandma_cost, "farms": farms,
        "farm_cost": farm_cost, "click_power": click_power,
        "dark_mode": current_theme_name == "dark",
    }
    data.update(upgrade_states)
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    save_status.config(text="✓  Saved", fg=SUCCESS)
    root.after(2500, lambda: save_status.config(text=""))

def load_game():
    global cookie_count, auto_clickers, upgrade_cost, grandmas, grandma_cost, farms, farm_cost, click_power, current_theme_name
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                d = json.load(f)
            cookie_count  = d.get("cookie_count", 0)
            auto_clickers = d.get("auto_clickers", 0)
            upgrade_cost  = building_cost(AUTO_CLICKER_BASE_COST, auto_clickers)
            grandmas      = d.get("grandmas", 0)
            grandma_cost  = building_cost(GRANDMA_BASE_COST, grandmas)
            farms         = d.get("farms", 0)
            farm_cost     = building_cost(FARM_BASE_COST, farms)
            click_power   = d.get("click_power", 1)
            current_theme_name = "dark" if d.get("dark_mode", False) else "light"
            set_theme_globals(current_theme_name)
            for u in UPGRADES:
                upgrade_states[u["id"]] = d.get(u["id"], False)
            update_click_power()
        except (json.JSONDecodeError, KeyError):
            pass

def on_close():
    save_game()
    root.destroy()

load_game()

# ═════════════════════════════════════════════════════════
# ── HEADER BAR ────────────────────────────────────────────
# ═════════════════════════════════════════════════════════
header = tk.Frame(root, bg=HEADER_BG, height=64)
header.grid(row=0, column=0, columnspan=2, sticky="ew")
header.grid_propagate(False)
_header_border = tk.Frame(root, bg=BORDER, height=1)
_header_border.grid(row=0, column=0, columnspan=2, sticky="sew")
border_frames.append(_header_border)

hi = tk.Frame(header, bg=HEADER_BG)
hi.pack(expand=True, fill="both", padx=28)

header_title = tk.Label(hi, text="🍪 Cookie Clicker", font=("Georgia", 20, "bold"),
                         bg=HEADER_BG, fg=TEXT)
header_title.pack(side="left", pady=14)
header_subtitle = tk.Label(hi, text="bakery edition", font=("Segoe UI", 10, "italic"),
                            bg=HEADER_BG, fg=TEXT_MUTED)
header_subtitle.pack(side="left", padx=(10, 0), pady=(18, 0))

save_status = tk.Label(hi, text="", font=("Segoe UI", 10, "bold"), bg=HEADER_BG, fg=SUCCESS)
save_status.pack(side="right", padx=(0, 14))

save_button = tk.Button(
    hi, text="💾  Save", font=("Segoe UI", 10, "bold"),
    bg=ACCENT, fg=WHITE, activebackground=ACCENT_DARK, activeforeground=WHITE,
    relief=tk.FLAT, padx=18, pady=8, cursor="hand2", bd=0, command=save_game,
)
save_button.pack(side="right", pady=12)

# ═════════════════════════════════════════════════════════
# ── SIDEBAR (left): click area + live stats + upgrades log ─
# ═════════════════════════════════════════════════════════
sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=SIDEBAR_W)
sidebar.grid(row=1, column=0, sticky="ns")
sidebar.grid_propagate(False)
_sidebar_border = tk.Frame(root, bg=BORDER, width=1)
_sidebar_border.grid(row=1, column=0, sticky="nse")
border_frames.append(_sidebar_border)

# -- cookie click zone --
click_zone = tk.Frame(sidebar, bg=SIDEBAR_BG)
click_zone.pack(fill="x", pady=(28, 10))

counter_label = tk.Label(click_zone, text=format_cookies(cookie_count),
                          font=("Georgia", 34, "bold"), bg=SIDEBAR_BG, fg=TEXT)
counter_label.pack()
cookies_baked_label = tk.Label(click_zone, text="COOKIES BAKED", font=("Segoe UI", 9, "bold"),
                                bg=SIDEBAR_BG, fg=TEXT_MUTED)
cookies_baked_label.pack(pady=(0, 18))

click_button = tk.Button(click_zone, image=cookie_image, borderwidth=0,
                          highlightthickness=0, cursor="hand2", relief=tk.FLAT,
                          bg=SIDEBAR_BG, activebackground=SIDEBAR_BG, bd=0)
click_button.image = cookie_image
click_button.pack()

cps_row = tk.Frame(click_zone, bg=SIDEBAR_BG)
cps_row.pack(pady=(18, 0))
tk.Label(cps_row, text="🔥", font=("Segoe UI Emoji", 13), bg=SIDEBAR_BG).pack(side="left")
cps_label = tk.Label(cps_row, text=f"{format_cookies(cookies_per_second())} cookies/sec",
                      font=("Segoe UI", 13, "bold"), bg=SIDEBAR_BG, fg=ACCENT)
cps_label.pack(side="left", padx=(6, 0))

click_power_label = tk.Label(click_zone, text=f"👆 {click_power} per click",
                              font=("Segoe UI", 10), bg=SIDEBAR_BG, fg=TEXT_MUTED)
click_power_label.pack(pady=(4, 0))

_sidebar_divider = tk.Frame(sidebar, bg=BORDER, height=1)
_sidebar_divider.pack(fill="x", padx=24, pady=(22, 14))
border_frames.append(_sidebar_divider)

# -- purchased upgrades log (replaces the old toggle overlay panel) --
purchased_upgrades_label = tk.Label(sidebar, text="PURCHASED UPGRADES", font=("Segoe UI", 9, "bold"),
                                     bg=SIDEBAR_BG, fg=TEXT_MUTED)
purchased_upgrades_label.pack(anchor="w", padx=24)

log_outer = tk.Frame(sidebar, bg=SIDEBAR_BG)
log_outer.pack(fill="both", expand=True, padx=(24, 8), pady=(8, 20))

log_canvas = tk.Canvas(log_outer, bg=SIDEBAR_BG, highlightthickness=0, bd=0)
log_scroll = tk.Scrollbar(log_outer, orient="vertical", command=log_canvas.yview)
log_inner = tk.Frame(log_canvas, bg=SIDEBAR_BG)
log_inner.bind("<Configure>", lambda e: log_canvas.configure(scrollregion=log_canvas.bbox("all")))
log_window = log_canvas.create_window((0, 0), window=log_inner, anchor="nw")
log_canvas.configure(yscrollcommand=log_scroll.set)
log_canvas.bind("<Configure>", lambda e: log_canvas.itemconfig(log_window, width=e.width))
log_canvas.pack(side="left", fill="both", expand=True)
log_scroll.pack(side="right", fill="y")
log_canvas.bind("<Enter>", lambda e: log_canvas.bind_all(
    "<MouseWheel>", lambda ev: log_canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
log_canvas.bind("<Leave>", lambda e: log_canvas.unbind_all("<MouseWheel>"))

def populate_log():
    for c in log_inner.winfo_children():
        c.destroy()
    purchased = [u for u in UPGRADES if upgrade_states.get(u["id"], False)]
    if not purchased:
        tk.Label(log_inner, text="None yet — upgrades you buy will\nappear here with their effect.",
                 font=("Segoe UI", 9, "italic"), bg=SIDEBAR_BG, fg=TEXT_FAINT,
                 justify="left", anchor="w").pack(anchor="w", pady=4)
        return
    for u in purchased:
        row = tk.Frame(log_inner, bg=SIDEBAR_BG)
        row.pack(fill="x", pady=(0, 10))
        tk.Label(row, text=f"{u['emoji']} {u['name']}", font=("Segoe UI", 10, "bold"),
                  bg=SIDEBAR_BG, fg=GOLD, anchor="w").pack(fill="x")
        tk.Label(row, text=u["description"], font=("Segoe UI", 8), bg=SIDEBAR_BG,
                  fg=TEXT_MUTED, anchor="w", justify="left", wraplength=240).pack(fill="x")

# ═════════════════════════════════════════════════════════
# ── MAIN PANEL (right): tabbed, scrollable shop of cards ──
# ═════════════════════════════════════════════════════════
main = tk.Frame(root, bg=BG)
main.grid(row=1, column=1, sticky="nsew")
main.grid_rowconfigure(1, weight=1)
main.grid_columnconfigure(0, weight=1)

tabs_row = tk.Frame(main, bg=BG)
tabs_row.grid(row=0, column=0, sticky="ew", padx=28, pady=(22, 12))

active_tab = "buildings"

def make_pill(parent, text, on_click):
    b = tk.Button(parent, text=text, font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, bd=0, cursor="hand2", padx=20, pady=10,
                  command=on_click)
    return b

def select_tab(name):
    global active_tab
    active_tab = name
    refresh_tab_pills()
    rebuild_shop_list()

building_pill = make_pill(tabs_row, "🏠  Buildings", lambda: select_tab("buildings"))
building_pill.pack(side="left", padx=(0, 10))
upgrade_pill = make_pill(tabs_row, "✨  Upgrades", lambda: select_tab("upgrades"))
upgrade_pill.pack(side="left", padx=(0, 10))
settings_pill = make_pill(tabs_row, "⚙️  Settings", lambda: select_tab("settings"))
settings_pill.pack(side="left")

def refresh_tab_pills():
    pills = {"buildings": building_pill, "upgrades": upgrade_pill, "settings": settings_pill}
    for name, pill in pills.items():
        if name == active_tab:
            pill.config(bg=ACCENT, fg=WHITE, activebackground=ACCENT_DARK, activeforeground=WHITE)
        else:
            pill.config(bg=PILL_OFF_BG, fg=PILL_OFF_FG, activebackground=PILL_OFF_BG, activeforeground=TEXT)

# scrollable card list
shop_outer = tk.Frame(main, bg=BG)
shop_outer.grid(row=1, column=0, sticky="nsew", padx=(28, 14))

shop_canvas = tk.Canvas(shop_outer, bg=BG, highlightthickness=0, bd=0)
shop_scroll = tk.Scrollbar(shop_outer, orient="vertical", command=shop_canvas.yview)
shop_list = tk.Frame(shop_canvas, bg=BG)
shop_list.bind("<Configure>", lambda e: shop_canvas.configure(scrollregion=shop_canvas.bbox("all")))
shop_window = shop_canvas.create_window((0, 0), window=shop_list, anchor="nw")
shop_canvas.configure(yscrollcommand=shop_scroll.set)
shop_canvas.bind("<Configure>", lambda e: shop_canvas.itemconfig(shop_window, width=e.width))
shop_canvas.pack(side="left", fill="both", expand=True)
shop_scroll.pack(side="right", fill="y", pady=4)
shop_canvas.bind("<Enter>", lambda e: shop_canvas.bind_all(
    "<MouseWheel>", lambda ev: shop_canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
shop_canvas.bind("<Leave>", lambda e: shop_canvas.unbind_all("<MouseWheel>"))

# ═════════════════════════════════════════════════════════
# ── BUILDING / UPGRADE PURCHASE LOGIC ─────────────────────
# ═════════════════════════════════════════════════════════
def upgrade_click():
    global cookie_count, auto_clickers, upgrade_cost
    if cookie_count >= upgrade_cost:
        cookie_count -= upgrade_cost
        auto_clickers += 1
        upgrade_cost = building_cost(AUTO_CLICKER_BASE_COST, auto_clickers)
        update_stats_display()
        rebuild_shop_list()

def grandma_buy():
    global cookie_count, grandmas, grandma_cost
    if cookie_count >= grandma_cost:
        cookie_count -= grandma_cost
        grandmas += 1
        grandma_cost = building_cost(GRANDMA_BASE_COST, grandmas)
        update_stats_display()
        rebuild_shop_list()

def farm_buy():
    global cookie_count, farms, farm_cost
    if cookie_count >= farm_cost:
        cookie_count -= farm_cost
        farms += 1
        farm_cost = building_cost(FARM_BASE_COST, farms)
        update_stats_display()
        rebuild_shop_list()

BUILDINGS = [
    {"id": "auto", "emoji": "🤖", "name": "Autoclicker",
     "owned": lambda: auto_clickers, "cost": lambda: upgrade_cost, "buy": upgrade_click,
     "tip": lambda: (f"Each autoclicker: {format_cookies(autoclicker_production())} cookies/sec\n"
                      f"All autoclickers: {format_cookies(auto_clickers * autoclicker_production())} cookies/sec")},
    {"id": "grandma", "emoji": "👵", "name": "Grandma",
     "owned": lambda: grandmas, "cost": lambda: grandma_cost, "buy": grandma_buy,
     "tip": lambda: (f"Each grandma: {format_cookies(grandma_production())} cookies/sec\n"
                      f"All grandmas: {format_cookies(grandmas * grandma_production())} cookies/sec")},
    {"id": "farm", "emoji": "🌾", "name": "Farm",
     "owned": lambda: farms, "cost": lambda: farm_cost, "buy": farm_buy,
     "tip": lambda: (f"Each farm: {format_cookies(farm_production())} cookies/sec\n"
                      f"All farms: {format_cookies(farms * farm_production())} cookies/sec")},
]

def meets_requirements(u):
    return (auto_clickers >= u["requires_autoclickers"]
            and grandmas >= u["requires_grandmas"]
            and farms >= u.get("requires_farms", 0))

def is_upgrade_available(u):
    if upgrade_states[u["id"]]:
        return False
    if cookie_count < u["cost"]:
        return False
    return meets_requirements(u)

def buy_upgrade(upgrade_id):
    global cookie_count
    u = next((x for x in UPGRADES if x["id"] == upgrade_id), None)
    if not u or upgrade_states[upgrade_id] or cookie_count < u["cost"] or not meets_requirements(u):
        return
    cookie_count -= u["cost"]
    upgrade_states[upgrade_id] = True
    if u["effect"] == "doubles_click_power":
        update_click_power()
    update_stats_display()
    populate_log()
    rebuild_shop_list()

def upgrade_tip(u):
    uid = u["id"]
    if uid == "thousand_fingers_upgrade":
        return (f"Each building adds {format_cookies(THOUSAND_FINGERS_BONUS)} cookies/sec per autoclicker.\n"
                f"Current bonus: {format_cookies(thousand_fingers_bonus())} per autoclicker\n"
                f"Requires {u['requires_autoclickers']} autoclickers.")
    if uid == "million_fingers_upgrade":
        return (f"Multiplies the Thousand Fingers bonus ×{MILLION_FINGERS_MULTIPLIER}.\n"
                f"Current bonus: {format_cookies(thousand_fingers_bonus())} per autoclicker\n"
                f"Requires {u['requires_autoclickers']} autoclickers.")
    if uid in ("forwards_from_grandma", "steel_rolling_pins",
               "lubricated_dentures", "prune_juice", "double_thick_glasses"):
        return (f"Doubles grandma production.\n"
                f"Current grandma production: {format_cookies(grandma_production())} cookies/sec\n"
                f"Requires {u['requires_grandmas']} grandmas.")
    if uid in ("cheap_hoes", "fertilizer"):
        return (f"Doubles farm production.\n"
                f"Current farm production: {format_cookies(farm_production())} cookies/sec\n"
                f"Requires {u['requires_farms']} farms.")
    if uid == "farmer_grandmas":
        return (f"Doubles grandma production. Farms gain +1% cookies/sec per grandma owned.\n"
                f"Current grandma production: {format_cookies(grandma_production())} cookies/sec\n"
                f"Current farm production: {format_cookies(farm_production())} cookies/sec\n"
                f"Requires {u['requires_farms']} farms and {u['requires_grandmas']} grandma.")
    return u["description"]

# ── card builders ────────────────────────────────────────
def make_building_card(parent, b):
    card = tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
    card.pack(fill="x", pady=6)
    inner = tk.Frame(card, bg=CARD_BG)
    inner.pack(fill="x", padx=18, pady=14)

    tk.Label(inner, text=b["emoji"], font=("Segoe UI Emoji", 26), bg=CARD_BG).pack(side="left", padx=(0, 16))

    mid = tk.Frame(inner, bg=CARD_BG)
    mid.pack(side="left", fill="x", expand=True)
    tk.Label(mid, text=b["name"], font=("Segoe UI", 13, "bold"), bg=CARD_BG, fg=TEXT,
             anchor="w").pack(fill="x")
    owned_lbl = tk.Label(mid, text=f"Owned: {b['owned']()}", font=("Segoe UI", 9),
                          bg=CARD_BG, fg=TEXT_MUTED, anchor="w")
    owned_lbl.pack(fill="x")

    right = tk.Frame(inner, bg=CARD_BG)
    right.pack(side="right")
    buy_btn = tk.Button(right, text=f"{b['cost']():,} 🍪", font=("Segoe UI", 11, "bold"),
                         relief=tk.FLAT, bd=0, padx=16, pady=8, cursor="hand2",
                         command=b["buy"])
    buy_btn.pack()

    Tooltip(card, b["tip"])
    bind_recursive(card, "<Button-1>", lambda e, fn=b["buy"]: fn())
    return card, owned_lbl, buy_btn

def make_upgrade_card(parent, u):
    available = is_upgrade_available(u)
    bg = CARD_BG if available else CARD_LOCKED
    card = tk.Frame(parent, bg=bg, highlightbackground=BORDER, highlightthickness=1)
    card.pack(fill="x", pady=6)
    inner = tk.Frame(card, bg=bg)
    inner.pack(fill="x", padx=18, pady=14)

    tk.Label(inner, text=u["emoji"], font=("Segoe UI Emoji", 24), bg=bg).pack(side="left", padx=(0, 16))

    mid = tk.Frame(inner, bg=bg)
    mid.pack(side="left", fill="x", expand=True)
    tk.Label(mid, text=u["name"], font=("Segoe UI", 12, "bold"), bg=bg,
             fg=TEXT if available else TEXT_FAINT, anchor="w").pack(fill="x")
    tk.Label(mid, text=u["description"], font=("Segoe UI", 9), bg=bg, fg=TEXT_MUTED,
             anchor="w", justify="left", wraplength=440).pack(fill="x", pady=(2, 0))

    right = tk.Frame(inner, bg=bg)
    right.pack(side="right")
    btn = tk.Button(right, text=f"{u['cost']:,} 🍪", font=("Segoe UI", 11, "bold"),
                     relief=tk.FLAT, bd=0, padx=16, pady=8, cursor="hand2",
                     state="normal" if available else "disabled",
                     command=lambda uid=u["id"]: buy_upgrade(uid))
    btn.pack()
    if available:
        btn.config(bg=GOLD, fg=WHITE, activebackground=ACCENT_DARK, activeforeground=WHITE)
    else:
        btn.config(bg=PILL_OFF_BG, fg=TEXT_FAINT, disabledforeground=TEXT_FAINT)

    Tooltip(card, lambda u=u: upgrade_tip(u))
    if available:
        bind_recursive(card, "<Button-1>", lambda e, uid=u["id"]: buy_upgrade(uid))
    _upgrade_card_widgets[u["id"]] = btn
    return card

building_cards = {}  # id -> (card, owned_lbl, buy_btn)
_building_prev_state = {}       # bid -> (affordable, owned, cost)
_upgrade_card_widgets = {}      # uid -> btn widget
_last_visible_upgrade_ids = set()

# ═════════════════════════════════════════════════════════
# ── SETTINGS PANEL + DARK MODE ────────────────────────────
# ═════════════════════════════════════════════════════════
def build_settings_panel(parent):
    card = tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
    card.pack(fill="x", pady=6)
    inner = tk.Frame(card, bg=CARD_BG)
    inner.pack(fill="x", padx=18, pady=14)

    tk.Label(inner, text="🌙", font=("Segoe UI Emoji", 24), bg=CARD_BG).pack(side="left", padx=(0, 16))

    mid = tk.Frame(inner, bg=CARD_BG)
    mid.pack(side="left", fill="x", expand=True)
    tk.Label(mid, text="Dark Mode", font=("Segoe UI", 13, "bold"), bg=CARD_BG, fg=TEXT,
             anchor="w").pack(fill="x")
    tk.Label(mid, text="Switch between the light and dark bakery themes.", font=("Segoe UI", 9),
             bg=CARD_BG, fg=TEXT_MUTED, anchor="w").pack(fill="x")

    right = tk.Frame(inner, bg=CARD_BG)
    right.pack(side="right")
    is_dark = current_theme_name == "dark"
    toggle_btn = tk.Button(
        right, text=("🌙  On" if is_dark else "☀️  Off"), font=("Segoe UI", 11, "bold"),
        relief=tk.FLAT, bd=0, padx=16, pady=8, cursor="hand2",
        bg=(ACCENT if is_dark else PILL_OFF_BG), fg=(WHITE if is_dark else PILL_OFF_FG),
        activebackground=ACCENT_DARK, activeforeground=WHITE,
        command=toggle_dark_mode,
    )
    toggle_btn.pack()

def toggle_dark_mode():
    global current_theme_name
    current_theme_name = "dark" if current_theme_name == "light" else "light"
    set_theme_globals(current_theme_name)
    apply_theme()
    save_game()

def apply_theme():
    """Recolor every persistent widget to match the current theme, then
    rebuild the dynamic panels (cards/log/settings) so they pick up the
    new colors too."""
    root.config(bg=BG)

    header.config(bg=HEADER_BG)
    hi.config(bg=HEADER_BG)
    header_title.config(bg=HEADER_BG, fg=TEXT)
    header_subtitle.config(bg=HEADER_BG, fg=TEXT_MUTED)
    save_status.config(bg=HEADER_BG)
    save_button.config(bg=ACCENT, fg=WHITE, activebackground=ACCENT_DARK, activeforeground=WHITE)

    for f in border_frames:
        f.config(bg=BORDER)

    sidebar.config(bg=SIDEBAR_BG)
    click_zone.config(bg=SIDEBAR_BG)
    counter_label.config(bg=SIDEBAR_BG, fg=TEXT)
    cookies_baked_label.config(bg=SIDEBAR_BG, fg=TEXT_MUTED)
    click_button.config(bg=SIDEBAR_BG, activebackground=SIDEBAR_BG)
    cps_row.config(bg=SIDEBAR_BG)
    cps_label.config(bg=SIDEBAR_BG, fg=ACCENT)
    click_power_label.config(bg=SIDEBAR_BG, fg=TEXT_MUTED)
    purchased_upgrades_label.config(bg=SIDEBAR_BG, fg=TEXT_MUTED)
    log_outer.config(bg=SIDEBAR_BG)
    log_canvas.config(bg=SIDEBAR_BG)
    log_inner.config(bg=SIDEBAR_BG)

    main.config(bg=BG)
    tabs_row.config(bg=BG)
    shop_outer.config(bg=BG)
    shop_canvas.config(bg=BG)
    shop_list.config(bg=BG)

    refresh_tab_pills()
    populate_log()
    rebuild_shop_list()

def rebuild_shop_list():
    global _last_visible_upgrade_ids
    for c in shop_list.winfo_children():
        c.destroy()
    building_cards.clear()
    _building_prev_state.clear()
    _upgrade_card_widgets.clear()

    if active_tab == "buildings":
        for b in BUILDINGS:
            card, owned_lbl, buy_btn = make_building_card(shop_list, b)
            building_cards[b["id"]] = (card, owned_lbl, buy_btn, b)
            _style_building_card(b["id"])
    elif active_tab == "upgrades":
        visible = [u for u in UPGRADES if not upgrade_states[u["id"]] and meets_requirements(u)]
        _last_visible_upgrade_ids = {u["id"] for u in visible}
        if not visible:
            tk.Label(shop_list, text="No upgrades available yet — keep baking\nand buying buildings to unlock more!",
                     font=("Segoe UI", 11, "italic"), bg=BG, fg=TEXT_MUTED,
                     justify="left").pack(anchor="w", pady=30)
        for u in visible:
            make_upgrade_card(shop_list, u)
    else:
        build_settings_panel(shop_list)

def _style_building_card(bid):
    card, owned_lbl, buy_btn, b = building_cards[bid]
    affordable = cookie_count >= b["cost"]()
    current_owned = b["owned"]()
    current_cost = b["cost"]()

    prev = _building_prev_state.get(bid, (None, None, None))
    prev_affordable, prev_owned, prev_cost = prev

    # Only update text labels when values actually change
    if prev_owned != current_owned or prev_cost != current_cost:
        owned_lbl.config(text=f"Owned: {current_owned}")
        buy_btn.config(text=f"{current_cost:,} 🍪")

    # Only repaint card backgrounds when affordability flips
    if prev_affordable != affordable:
        if affordable:
            buy_btn.config(bg=ACCENT, fg=WHITE, activebackground=ACCENT_DARK, activeforeground=WHITE, state="normal")
            card.config(bg=CARD_BG)
            for w in card.winfo_children():
                w.config(bg=CARD_BG)
                for ww in w.winfo_children():
                    if ww is not buy_btn:
                        ww.config(bg=CARD_BG)
        else:
            buy_btn.config(bg=PILL_OFF_BG, fg=TEXT_FAINT, activebackground=PILL_OFF_BG, state="normal")
            card.config(bg=CARD_LOCKED)
            for w in card.winfo_children():
                w.config(bg=CARD_LOCKED)
                for ww in w.winfo_children():
                    if ww is not buy_btn:
                        ww.config(bg=CARD_LOCKED)

    _building_prev_state[bid] = (affordable, current_owned, current_cost)

# ═════════════════════════════════════════════════════════
# ── PARTICLES + CLICK HANDLER ─────────────────────────────
# ═════════════════════════════════════════════════════════
def spawn_particle(x, y, text="+1", color=GOLD):
    lbl = tk.Label(root, text=text, fg=color, bg=SIDEBAR_BG, font=("Segoe UI", 16, "bold"))
    lbl.place(x=x, y=y)
    def rise(step=0):
        if step > 28:
            lbl.destroy()
            return
        lbl.place(x=x, y=y - step * 3)
        root.after(10, lambda: rise(step + 1))
    rise()

def click_cookie():
    global cookie_count
    cookie_count += click_power
    try:
        x = click_button.winfo_x() + 100
        y = click_button.winfo_y() + 40
        spawn_particle(x, y, f"+{format_cookies(click_power)}", ACCENT)
    except Exception:
        pass
    update_stats_display()
    if active_tab == "buildings":
        for bid in list(building_cards.keys()):
            _style_building_card(bid)

click_button.config(command=click_cookie)

def update_stats_display():
    counter_label.config(text=format_cookies(cookie_count))
    cps_label.config(text=f"{format_cookies(cookies_per_second())} cookies/sec")
    click_power_label.config(text=f"👆 {format_cookies(click_power)} per click")

# ═════════════════════════════════════════════════════════
# ── GOLDEN COOKIE ─────────────────────────────────────────
# ═════════════════════════════════════════════════════════
_gc_widget        = None   # the floating Button, or None
_gc_expire_id     = None   # after() id for 15-s auto-dismiss
_gc_spawn_id      = None   # after() id for next scheduled spawn
_gc_pulse_id      = None   # after() id for the bob animation
_gc_base_y        = 0      # y-origin used by the pulse
_typed_buffer     = ""     # accumulates keypresses for cheat-code

def _dismiss_golden_cookie():
    """Destroy the cookie widget and cancel all pending timers."""
    global _gc_widget, _gc_expire_id, _gc_pulse_id
    for attr in ("_gc_expire_id", "_gc_pulse_id"):
        aid = globals()[attr]
        if aid is not None:
            root.after_cancel(aid)
            globals()[attr] = None
    if _gc_widget is not None:
        try:
            _gc_widget.destroy()
        except Exception:
            pass
        _gc_widget = None

def _collect_golden_cookie():
    """Award 25-40 % of current cookies and remove the golden cookie."""
    global cookie_count
    if _gc_widget is None:
        return
    pct   = random.uniform(0.25, 0.40)
    bonus = max(cookie_count * pct, 1.0)
    cookie_count += bonus
    # Float a particle where the cookie was
    try:
        px = _gc_widget.winfo_x() + _GC_SIZE // 2
        py = _gc_widget.winfo_y()
        spawn_particle(px, py, f"+{format_cookies(bonus)}", "#FFD700")
    except Exception:
        pass
    _dismiss_golden_cookie()
    update_stats_display()
    if active_tab == "buildings":
        for bid in list(building_cards.keys()):
            _style_building_card(bid)

def _pulse_golden_cookie(step=0):
    """Bob the golden cookie gently up and down with a sine wave."""
    global _gc_pulse_id
    if _gc_widget is None:
        return
    offset = int(6 * math.sin(step * 0.28))
    try:
        _gc_widget.place(y=_gc_base_y + offset)
    except Exception:
        return
    _gc_pulse_id = root.after(40, lambda: _pulse_golden_cookie(step + 1))

def spawn_golden_cookie(event=None):
    """Spawn a golden cookie at a random position within the window."""
    global _gc_widget, _gc_expire_id, _gc_base_y
    _dismiss_golden_cookie()

    w = root.winfo_width()
    h = root.winfo_height()
    margin = _GC_SIZE + 20
    x = random.randint(margin, max(margin + 1, w - margin))
    y = random.randint(80 + margin, max(80 + margin + 1, h - margin))
    _gc_base_y = y

    btn = tk.Button(
        root, image=_gc_photo, borderwidth=0, highlightthickness=0,
        relief=tk.FLAT, bg=BG, activebackground=BG, cursor="hand2",
        command=_collect_golden_cookie,
    )
    btn.image = _gc_photo          # prevent GC
    btn.place(x=x, y=_gc_base_y, width=_GC_SIZE, height=_GC_SIZE)
    btn.lift()                     # float above all other widgets

    _gc_widget    = btn
    _gc_expire_id = root.after(15_000, _dismiss_golden_cookie)
    _pulse_golden_cookie()

    # Schedule the next automatic spawn
    schedule_golden_cookie()

def schedule_golden_cookie():
    """Queue the next automatic golden cookie (5-6 minutes from now)."""
    global _gc_spawn_id
    if _gc_spawn_id is not None:
        root.after_cancel(_gc_spawn_id)
    delay = random.randint(300_000, 360_000)
    _gc_spawn_id = root.after(delay, spawn_golden_cookie)

# ── Keyboard cheat-code ("goldencookie") ──────────────────
_CHEAT = "goldencookie"

def _on_key(event):
    global _typed_buffer
    ch = event.char
    if not ch or not ch.isprintable():
        return
    _typed_buffer = (_typed_buffer + ch.lower())[-len(_CHEAT):]
    if _typed_buffer == _CHEAT:
        _typed_buffer = ""
        spawn_golden_cookie()

root.bind("<Key>", _on_key, add="+")

# ═════════════════════════════════════════════════════════
# ── AUTOCLICKER LOOP / AUTOSAVE ───────────────────────────
# ═════════════════════════════════════════════════════════
def _update_upgrade_tab():
    """Update the upgrades tab in-place. Only does a full rebuild when the set
    of visible upgrades changes; otherwise just flips button states, avoiding
    the destroy-and-recreate flicker that happened every autoclicker tick."""
    global _last_visible_upgrade_ids
    visible = [u for u in UPGRADES if not upgrade_states[u["id"]] and meets_requirements(u)]
    visible_ids = {u["id"] for u in visible}

    if visible_ids != _last_visible_upgrade_ids:
        # Visible set changed — a full rebuild is necessary (no flicker here
        # because it only happens on real state transitions, not every tick)
        rebuild_shop_list()
        return

    # Same cards are showing — just update button affordability in-place
    for u in visible:
        btn = _upgrade_card_widgets.get(u["id"])
        if btn is None:
            continue
        affordable = cookie_count >= u["cost"]
        try:
            current_state = btn.cget("state")
        except Exception:
            continue
        if affordable and current_state == "disabled":
            btn.config(state="normal", bg=GOLD, fg=WHITE,
                       activebackground=ACCENT_DARK, activeforeground=WHITE)
        elif not affordable and current_state == "normal":
            btn.config(state="disabled", bg=PILL_OFF_BG,
                       fg=TEXT_FAINT, disabledforeground=TEXT_FAINT)

def run_autoclicker():
    global cookie_count
    cookie_count += cookies_per_second()
    update_stats_display()
    if active_tab == "buildings":
        for bid in list(building_cards.keys()):
            _style_building_card(bid)
    elif active_tab == "upgrades":
        _update_upgrade_tab()
    root.after(1000, run_autoclicker)

def auto_save():
    save_game()
    root.after(60_000, auto_save)

root.protocol("WM_DELETE_WINDOW", on_close)

refresh_tab_pills()
rebuild_shop_list()
populate_log()
update_stats_display()
root.after(60_000, auto_save)
schedule_golden_cookie()
run_autoclicker()

root.mainloop()

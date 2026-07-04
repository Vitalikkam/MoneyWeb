from datetime import datetime, timedelta
import pandas as pd

# ---------- COLOR PALETTE (Dark Theme + Neon) ----------
COLORS = {
    "bg_primary": "#0f172a",      # Slate-900
    "bg_secondary": "#1e293b",    # Slate-800
    "bg_hover": "#334155",        # Slate-700
    "border": "#475569",          # Slate-600
    "text_primary": "#f8fafc",    # White
    "text_secondary": "#e2e8f0",  # Slate-200
    "text_muted": "#94a3b8",      # Slate-400
    
    "green": "#4ade80",           # Neon Green (Profits/Deposits)
    "green_bg": "rgba(74, 222, 128, 0.15)",  # Glow for river chart
    "red": "#f87171",             # Bright Red (Losses/Withdrawals)
    "red_bg": "rgba(248, 113, 113, 0.15)",
    "grid": "#334155",            # Grid lines
}


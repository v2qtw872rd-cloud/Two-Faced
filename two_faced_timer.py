# ==========================================
# two_faced_timer.py
# ==========================================
# Handles all timer logic for Two-Faced.
# - Parses natural language input like "1 hour 30 minutes"
# - Formats seconds into HH:MM:SS
# - Calculates remaining countdown time
# ==========================================

import re
import pygame


# ==========================================
# PARSE NATURAL TIME INPUT
# ==========================================
# Converts:
# "1 hour 30 minutes"
# "45 seconds"
# "120"
# → total seconds
# ==========================================
def parse_time(text):

    if not isinstance(text, str):
        return None

    text = text.lower().strip()
    total_seconds = 0
    found_any = False  # ⭐ NEW: tracks if we matched anything

    # ======================
    # HOURS
    # ======================
    hour_match = re.search(r"\b(\d+)\s*hour(s)?\b", text)
    if hour_match:
        total_seconds += int(hour_match.group(1)) * 3600
        found_any = True

    # ======================
    # MINUTES
    # ======================
    minute_match = re.search(r"\b(\d+)\s*minute(s)?\b", text)
    if minute_match:
        total_seconds += int(minute_match.group(1)) * 60
        found_any = True

    # ======================
    # SECONDS
    # ======================
    second_match = re.search(r"\b(\d+)\s*second(s)?\b", text)
    if second_match:
        total_seconds += int(second_match.group(1))
        found_any = True

    # ======================
    # RAW NUMBER INPUT
    # ======================
    if total_seconds == 0 and text.isdigit():
        total_seconds = int(text)
        found_any = True

    # ======================
    # FAILSAFE: INVALID INPUT
    # ======================
    # Only return None if NOTHING was parsed at all
    if not found_any:
        return None

    return total_seconds


# ==========================================
# FORMAT TIME (SECONDS → HH:MM:SS)
# ==========================================
def format_time(seconds):

    if seconds is None:
        return "00:00:00"

    seconds = max(0, int(seconds))

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02}"


# ==========================================
# CALCULATE TIME LEFT
# ==========================================
def get_time_left(start_time, countdown):

    if start_time is None or countdown is None:
        return 0

    elapsed = (pygame.time.get_ticks() - start_time) // 1000

    return max(0, countdown - elapsed)
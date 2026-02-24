"""
AI Mood Ring utility — small, deterministic, and delightfully silly.

Provides functions to map time-of-day, weather, and season into
short "tone fragments" and combine them into a playful mood sentence.

Design goals:
- Modular: callable from responders or UI handlers
- Deterministic seed option so repeated asks in a short window return
  the same variant
- Lightweight: no external deps, simple string mappings

Example:
    from src.emotional_os.deploy.modules.ui_components.mood_ring import generate_mood
    generate_mood(weather='Cloudy')

"""
from __future__ import annotations

import datetime
import hashlib
import random
from typing import Optional


CHAOS_VARIANTS = [
    "feral housecat energy",
    "sentient fog machine",
    "a warm glitch",
    "a polite existential crisis",
    "an apologetic disco ball",
]


def _time_energy(hour: int) -> str:
    if 5 <= hour < 10:
        return "bright but not fully assembled"
    if 10 <= hour < 14:
        return "focused with a side of mischief"
    if 14 <= hour < 18:
        return "warm, a little restless"
    if 18 <= hour < 22:
        return "soft-edged and reflective"
    if 22 <= hour < 24:
        return "loose, strange, slightly feral"
    # 0-4
    return "cosmic and unhinged in a gentle way"


def _weather_texture(weather: str) -> str:
    w = (weather or "").strip().lower()
    if "sun" in w or "clear" in w or "fair" in w:
        return "charged with open-sky optimism"
    if "cloud" in w or "overcast" in w:
        return "muted, like thoughts wrapped in cotton"
    if "rain" in w or "drizzle" in w or "shower" in w:
        return "slow-dripping and introspective"
    if "wind" in w or "bree" in w:
        return "scattered but kinetic"
    if "fog" in w or "mist" in w:
        return "dreamlike and half-dissolved"
    if "hot" in w or "heat" in w or "humid" in w:
        return "overcaffeinated and shimmering"
    if "cold" in w or "chill" in w or "snow" in w:
        return "tight, crisp, and inward-facing"
    # fallback
    return "a little uncertain about the forecast"


def _month_to_season(month: int) -> str:
    # Northern hemisphere seasons by month
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "fall"


def _season_color(season: str) -> str:
    s = (season or "").lower()
    if s == "winter":
        return "low-battery introspection"
    if s == "spring":
        return "restless optimism"
    if s == "summer":
        return "loose, expansive confidence"
    return "nostalgic amber glow"


def _make_seed(time_block: str, weather: str, date_str: str) -> int:
    key = f"{time_block}|{(weather or '').lower()}|{date_str}"
    h = hashlib.md5(key.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _time_block_for_dt(dt: datetime.datetime) -> str:
    # coarsen to block (hour-block) to keep mood stable for minutes
    return dt.strftime("%Y-%m-%dT%H")


def generate_mood(
    now: Optional[datetime.datetime] = None,
    weather: Optional[str] = "Sunny",
    seed: Optional[int] = None,
    chaos: bool = False,
) -> str:
    """Create a playful mood sentence from time, weather, and season.

    Args:
        now: datetime to use (defaults to utcnow())
        weather: simple weather descriptor (e.g., 'Sunny', 'Cloudy')
        seed: optional integer seed to force deterministic variant selection
        chaos: if True, pick a random "chaos" variant instead

    Returns:
        Short mood sentence string.
    """
    if now is None:
        now = datetime.datetime.now()

    if chaos:
        r = random.Random(seed if seed is not None else int(now.timestamp()))
        return r.choice(CHAOS_VARIANTS)

    time_block = _time_block_for_dt(now)
    date_str = now.strftime("%Y-%m-%d")

    # deterministic seed if none provided
    if seed is None:
        seed = _make_seed(time_block, weather or "", date_str)

    rnd = random.Random(seed)

    # Base fragments
    energy = _time_energy(now.hour)
    texture = _weather_texture(weather or "")
    season = _month_to_season(now.month)
    color = _season_color(season)

    # Small variation via inline templates / separators for readability
    # We allow a handful of variants by using the seed to pick connectors/verbs
    connector = rnd.choice([", ", ", ", " - ", ", a touch of "])

    # Minor varianting of energy/texture phrasing
    energy_variant = energy
    if rnd.random() < 0.25:
        energy_variant = energy.replace(" ", "-")

    texture_variant = texture
    if rnd.random() < 0.2:
        texture_variant = texture.replace(" ", "-")

    sentence = (
        f"Probably something like a {energy_variant}{connector}{texture_variant} kind of vibe"
        f" — with a hint of {color}."
    )

    return sentence


def mood_seed_for_window(now: Optional[datetime.datetime] = None, weather: Optional[str] = "Sunny") -> int:
    """Helper to compute the deterministic seed used for short-term stability.

    Uses year-month-day-hour block so moods are stable for the hour by default.
    """
    if now is None:
        now = datetime.datetime.now()
    time_block = _time_block_for_dt(now)
    return _make_seed(time_block, weather or "", now.strftime("%Y-%m-%d"))


__all__ = [
    "generate_mood",
    "mood_seed_for_window",
    "CHAOS_VARIANTS",
]

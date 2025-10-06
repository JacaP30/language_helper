"""Moduł do zliczania kosztów i statystyk AI/TTS/Whisper"""

import streamlit as st
import json
import os
from datetime import datetime

DB_FILE = os.path.join("base", "usage_database.json")

def load_usage_database():
    # ...przeniesiona funkcja z config.py...
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Automatyczna migracja - dodaj vocabulary jeśli brakuje
                if "total_stats" in data and "vocabulary" not in data["total_stats"]:
                    data["total_stats"]["vocabulary"] = {"prompt": 0, "completion": 0, "total": 0}
                    data["last_updated"] = datetime.now().isoformat()
                    save_usage_database(data)
                required_keys = ["total_stats", "daily_stats", "session_history", "created_date", "last_updated"]
                if all(key in data for key in required_keys):
                    return data
                else:
                    return migrate_old_database(data)
        else:
            return create_new_database()
    except Exception as e:
        st.warning(f"Błąd podczas ładowania bazy danych: {e}. Tworzę nową bazę.")
        return create_new_database()

def create_new_database():
    return {
        "created_date": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "total_stats": {
            "translator": {"prompt": 0, "completion": 0, "total": 0},
            "belfer": {"prompt": 0, "completion": 0, "total": 0},
            "dialog": {"prompt": 0, "completion": 0, "total": 0},
            "vocabulary": {"prompt": 0, "completion": 0, "total": 0},
            "tts_chars_openai": 0,
            "tts_chars_gtts": 0,
            "whisper_minutes": 0.0,
            "total_cost_usd": 0.0
        },
        "daily_stats": {},
        "session_history": []
    }

def migrate_old_database(old_data):
    new_db = create_new_database()
    if "total_tokens_used" in old_data:
        old_stats = old_data["total_tokens_used"]
        new_db["total_stats"]["translator"] = old_stats.get("translator", {"prompt": 0, "completion": 0, "total": 0})
        new_db["total_stats"]["belfer"] = old_stats.get("belfer", {"prompt": 0, "completion": 0, "total": 0})
        new_db["total_stats"]["dialog"] = old_stats.get("dialog", {"prompt": 0, "completion": 0, "total": 0})
        new_db["total_stats"]["vocabulary"] = old_stats.get("vocabulary", {"prompt": 0, "completion": 0, "total": 0})
        new_db["total_stats"]["tts_chars_openai"] = old_stats.get("tts_chars", 0)
        new_db["total_stats"]["whisper_minutes"] = old_stats.get("whisper_minutes", 0.0)
    if "total_stats" in old_data:
        if "vocabulary" not in old_data["total_stats"]:
            old_data["total_stats"]["vocabulary"] = {"prompt": 0, "completion": 0, "total": 0}
        return old_data
    return new_db

def save_usage_database(data):
    try:
        data["last_updated"] = datetime.now().isoformat()
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Błąd podczas zapisywania bazy danych: {e}")
        return False

def get_today_key():
    return datetime.now().strftime("%Y-%m-%d")

def mark_new_session():
    db = load_usage_database()
    today = get_today_key()
    if today not in db["daily_stats"]:
        db["daily_stats"][today] = {
            "translator": {"prompt": 0, "completion": 0, "total": 0},
            "belfer": {"prompt": 0, "completion": 0, "total": 0},
            "dialog": {"prompt": 0, "completion": 0, "total": 0},
            "vocabulary": {"prompt": 0, "completion": 0, "total": 0},
            "tts_chars_openai": 0,
            "tts_chars_gtts": 0,
            "whisper_minutes": 0.0,
            "cost_usd": 0.0,
            "sessions_started": 0,
            "first_activity": None,
            "last_activity": None
        }
    db["daily_stats"][today]["sessions_started"] += 1
    current_time = datetime.now().isoformat()
    if db["daily_stats"][today]["first_activity"] is None:
        db["daily_stats"][today]["first_activity"] = current_time
    db["daily_stats"][today]["last_activity"] = current_time
    save_usage_database(db)

def add_to_daily_stats(stats_type, amount):
    db = load_usage_database()
    today = get_today_key()
    if today not in db["daily_stats"]:
        db["daily_stats"][today] = {
            "translator": {"prompt": 0, "completion": 0, "total": 0},
            "belfer": {"prompt": 0, "completion": 0, "total": 0},
            "dialog": {"prompt": 0, "completion": 0, "total": 0},
            "vocabulary": {"prompt": 0, "completion": 0, "total": 0},
            "tts_chars_openai": 0,
            "tts_chars_gtts": 0,
            "whisper_minutes": 0.0,
            "cost_usd": 0.0,
            "sessions_started": 0,
            "first_activity": None,
            "last_activity": None
        }
    if stats_type in ["translator", "belfer", "dialog", "vocabulary"] and isinstance(amount, dict):
        daily_stats = db["daily_stats"][today][stats_type]
        daily_stats["prompt"] += amount.get("prompt", 0)
        daily_stats["completion"] += amount.get("completion", 0)
        daily_stats["total"] += amount.get("total", 0)
    elif stats_type in ["tts_chars_openai", "tts_chars_gtts", "whisper_minutes"]:
        db["daily_stats"][today][stats_type] += amount
    current_time = datetime.now().isoformat()
    if db["daily_stats"][today]["first_activity"] is None:
        db["daily_stats"][today]["first_activity"] = current_time
    db["daily_stats"][today]["last_activity"] = current_time
    save_usage_database(db)

def init_token_tracking():
    if "total_tokens_used" not in st.session_state:
        db = load_usage_database()
        st.session_state.total_tokens_used = db["total_stats"].copy()
        required_modules = ["translator", "belfer", "dialog", "vocabulary"]
        for module in required_modules:
            if module not in st.session_state.total_tokens_used:
                st.session_state.total_tokens_used[module] = {"prompt": 0, "completion": 0, "total": 0}
        if "tts_chars" not in st.session_state.total_tokens_used:
            st.session_state.total_tokens_used["tts_chars"] = st.session_state.total_tokens_used.get("tts_chars_openai", 0)
        mark_new_session()

def add_token_usage(module_name, prompt_tokens, completion_tokens):
    init_token_tracking()
    if module_name not in st.session_state.total_tokens_used:
        st.session_state.total_tokens_used[module_name] = {"prompt": 0, "completion": 0, "total": 0}
    stats = st.session_state.total_tokens_used[module_name]
    stats["prompt"] += prompt_tokens
    stats["completion"] += completion_tokens
    stats["total"] += (prompt_tokens + completion_tokens)
    db = load_usage_database()
    db_stats = db["total_stats"][module_name]
    db_stats["prompt"] += prompt_tokens
    db_stats["completion"] += completion_tokens
    db_stats["total"] += (prompt_tokens + completion_tokens)
    today = get_today_key()
    if today not in db["daily_stats"]:
        db["daily_stats"][today] = {
            "translator": {"prompt": 0, "completion": 0, "total": 0},
            "belfer": {"prompt": 0, "completion": 0, "total": 0},
            "dialog": {"prompt": 0, "completion": 0, "total": 0},
            "vocabulary": {"prompt": 0, "completion": 0, "total": 0},
            "tts_chars_openai": 0,
            "tts_chars_gtts": 0,
            "whisper_minutes": 0.0,
            "cost_usd": 0.0,
            "sessions_started": 0,
            "first_activity": None,
            "last_activity": None
        }
    if module_name in ["translator", "belfer", "dialog", "vocabulary"]:
        daily_stats = db["daily_stats"][today][module_name]
        daily_stats["prompt"] += prompt_tokens
        daily_stats["completion"] += completion_tokens
        daily_stats["total"] += (prompt_tokens + completion_tokens)
        current_time = datetime.now().isoformat()
        if db["daily_stats"][today]["first_activity"] is None:
            db["daily_stats"][today]["first_activity"] = current_time
        db["daily_stats"][today]["last_activity"] = current_time
    save_usage_database(db)

def add_tts_usage(text_length, provider="openai"):
    init_token_tracking()
    if "tts_chars" not in st.session_state.total_tokens_used:
        st.session_state.total_tokens_used["tts_chars"] = 0
    st.session_state.total_tokens_used["tts_chars"] += text_length
    db = load_usage_database()
    today = get_today_key()
    if today not in db["daily_stats"]:
        db["daily_stats"][today] = {
            "translator": {"prompt": 0, "completion": 0, "total": 0},
            "belfer": {"prompt": 0, "completion": 0, "total": 0},
            "dialog": {"prompt": 0, "completion": 0, "total": 0},
            "vocabulary": {"prompt": 0, "completion": 0, "total": 0},
            "tts_chars_openai": 0,
            "tts_chars_gtts": 0,
            "whisper_minutes": 0.0,
            "cost_usd": 0.0,
            "sessions_started": 0,
            "first_activity": None,
            "last_activity": None
        }
    if provider.lower() == "gtts":
        db["total_stats"]["tts_chars_gtts"] += text_length
        db["daily_stats"][today]["tts_chars_gtts"] += text_length
    else:
        db["total_stats"]["tts_chars_openai"] += text_length
        db["daily_stats"][today]["tts_chars_openai"] += text_length
    current_time = datetime.now().isoformat()
    if db["daily_stats"][today]["first_activity"] is None:
        db["daily_stats"][today]["first_activity"] = current_time
    db["daily_stats"][today]["last_activity"] = current_time
    save_usage_database(db)

def add_whisper_usage(duration_seconds):
    init_token_tracking()
    minutes = duration_seconds / 60.0
    st.session_state.total_tokens_used["whisper_minutes"] += minutes
    db = load_usage_database()
    today = get_today_key()
    if today not in db["daily_stats"]:
        db["daily_stats"][today] = {
            "translator": {"prompt": 0, "completion": 0, "total": 0},
            "belfer": {"prompt": 0, "completion": 0, "total": 0},
            "dialog": {"prompt": 0, "completion": 0, "total": 0},
            "vocabulary": {"prompt": 0, "completion": 0, "total": 0},
            "tts_chars_openai": 0,
            "tts_chars_gtts": 0,
            "whisper_minutes": 0.0,
            "cost_usd": 0.0,
            "sessions_started": 0,
            "first_activity": None,
            "last_activity": None
        }
    db["total_stats"]["whisper_minutes"] += minutes
    db["daily_stats"][today]["whisper_minutes"] += minutes
    current_time = datetime.now().isoformat()
    if db["daily_stats"][today]["first_activity"] is None:
        db["daily_stats"][today]["first_activity"] = current_time
    db["daily_stats"][today]["last_activity"] = current_time
    save_usage_database(db)

def calculate_costs(use_database=True):
    if use_database:
        db = load_usage_database()
        stats = db["total_stats"]
        if "tts_chars" not in stats:
            stats["tts_chars"] = stats.get("tts_chars_openai", 0)
    else:
        init_token_tracking()
        stats = st.session_state.total_tokens_used
    gpt4o_mini_input = 0.15
    gpt4o_mini_output = 0.60
    tts_price = 15.0
    whisper_price = 0.006
    total_cost = 0
    costs = {}
    for module in ["translator", "belfer", "dialog", "vocabulary"]:
        if module not in stats:
            stats[module] = {"prompt": 0, "completion": 0, "total": 0}
        module_stats = stats[module]
        input_cost = (module_stats["prompt"] / 1_000_000) * gpt4o_mini_input
        output_cost = (module_stats["completion"] / 1_000_000) * gpt4o_mini_output
        module_cost = input_cost + output_cost
        costs[module] = module_cost
        total_cost += module_cost
    tts_openai_chars = stats.get("tts_chars_openai", stats.get("tts_chars", 0))
    tts_cost = (tts_openai_chars / 1_000_000) * tts_price
    costs["tts_openai"] = tts_cost
    total_cost += tts_cost
    costs["tts_gtts"] = 0.0
    whisper_cost = stats["whisper_minutes"] * whisper_price
    costs["whisper"] = whisper_cost
    total_cost += whisper_cost
    if use_database:
        db = load_usage_database()
        db["total_stats"]["total_cost_usd"] = total_cost
        save_usage_database(db)
    return costs, total_cost

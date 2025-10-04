"""Konfiguracja klienta OpenAI i zmienne środowiskowe"""

import streamlit as st
from dotenv import dotenv_values
from openai import OpenAI

def load_environment():
    """Ładuje zmienne środowiskowe z pliku .env lub zmiennych systemowych"""
    # Sprawdź zmienne systemowe (dla Streamlit Cloud)
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Jeśli nie ma w systemie, sprawdź plik .env
    if not api_key:
        env = dotenv_values(".env")
        api_key = env.get("OPENAI_API_KEY")
    
    if not api_key:
        # Sprawdź czy klucz jest już w session_state
        if "openai_api_key" in st.session_state:
            api_key = st.session_state.openai_api_key
        else:
            st.error("❌ Brak klucza API OpenAI w pliku .env")
            api_key_input = st.text_input(
                "Wpisz klucz API OpenAI:",
                type="password",
                placeholder="sk-proj-..."
            )
            if api_key_input:
                if api_key_input.startswith("sk-") and len(api_key_input) >= 100:
                    st.session_state.openai_api_key = api_key_input
                    st.rerun()
                else:
                    st.error("❌ Nieprawidłowy klucz API (musi zaczynać się od 'sk-' i być wystarczająco długi)")
            if not api_key_input:
                st.stop()
    
    return {"OPENAI_API_KEY": api_key}

# Inicjalizacja klienta OpenAI
env = load_environment()
client = OpenAI(api_key=env.get("OPENAI_API_KEY"))

# Lista obsługiwanych języków
supported_languages = ["angielski", "polski", "niemiecki", "francuski", "hiszpański", "włoski"]

# Mapowania kodów języków
language_code_map = {
    "angielski": "en",
    "polski": "pl", 
    "niemiecki": "de",
    "francuski": "fr",
    "hiszpański": "es",
    "włoski": "it"
}

# Dodatkowe importy dla funkcji audio
import tempfile
import time
import json
import os
from datetime import datetime

# Opcjonalne importy audio - mogą nie być dostępne w środowisku chmurowym
try:
    import sounddevice
    import scipy.io.wavfile
    AUDIO_AVAILABLE = True
except (ImportError, OSError):
    # ImportError - brak modułu, OSError - brak PortAudio library
    AUDIO_AVAILABLE = False

# Funkcje do persystentnej bazy danych kosztów
DB_FILE = os.path.join("base", "usage_database.json")

def load_usage_database():
    """Ładuje bazę danych użycia z pliku JSON"""
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Automatyczna migracja - dodaj vocabulary jeśli brakuje
                if "total_stats" in data and "vocabulary" not in data["total_stats"]:
                    data["total_stats"]["vocabulary"] = {"prompt": 0, "completion": 0, "total": 0}
                    data["last_updated"] = datetime.now().isoformat()
                    save_usage_database(data)
                
                # Sprawdź czy struktura jest aktualna
                required_keys = ["total_stats", "daily_stats", "session_history", "created_date", "last_updated"]
                if all(key in data for key in required_keys):
                    return data
                else:
                    # Stara struktura - zmigruj
                    return migrate_old_database(data)
        else:
            return create_new_database()
    except Exception as e:
        st.warning(f"Błąd podczas ładowania bazy danych: {e}. Tworzę nową bazę.")
        return create_new_database()

def create_new_database():
    """Tworzy nową strukturę bazy danych"""
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
        "daily_stats": {},  # Format: "2024-09-28": {...stats...}
        "session_history": []  # Historia sesji z timestampami
    }

def migrate_old_database(old_data):
    """Migruje starą strukturę bazy danych do nowej"""
    new_db = create_new_database()
    # Próbuj przepisać stare dane jeśli istnieją
    if "total_tokens_used" in old_data:
        old_stats = old_data["total_tokens_used"]
        new_db["total_stats"]["translator"] = old_stats.get("translator", {"prompt": 0, "completion": 0, "total": 0})
        new_db["total_stats"]["belfer"] = old_stats.get("belfer", {"prompt": 0, "completion": 0, "total": 0})
        new_db["total_stats"]["dialog"] = old_stats.get("dialog", {"prompt": 0, "completion": 0, "total": 0})
        new_db["total_stats"]["vocabulary"] = old_stats.get("vocabulary", {"prompt": 0, "completion": 0, "total": 0})
        new_db["total_stats"]["tts_chars_openai"] = old_stats.get("tts_chars", 0)
        new_db["total_stats"]["whisper_minutes"] = old_stats.get("whisper_minutes", 0.0)
    
    # Migracja istniejącej bazy - dodaj vocabulary jeśli brakuje
    if "total_stats" in old_data:
        if "vocabulary" not in old_data["total_stats"]:
            old_data["total_stats"]["vocabulary"] = {"prompt": 0, "completion": 0, "total": 0}
        return old_data
    return new_db

def save_usage_database(data):
    """Zapisuje bazę danych do pliku JSON"""
    try:
        data["last_updated"] = datetime.now().isoformat()
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Błąd podczas zapisywania bazy danych: {e}")
        return False

def get_today_key():
    """Zwraca klucz dla dzisiejszego dnia"""
    return datetime.now().strftime("%Y-%m-%d")

def mark_new_session():
    """Oznacza rozpoczęcie nowej sesji w statystykach dziennych"""
    db = load_usage_database()
    today = get_today_key()
    
    # Upewnij się, że dzisiejszy dzień istnieje
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
    
    # Zwiększ licznik sesji
    db["daily_stats"][today]["sessions_started"] += 1
    
    # Aktualizuj czas aktywności
    current_time = datetime.now().isoformat()
    if db["daily_stats"][today]["first_activity"] is None:
        db["daily_stats"][today]["first_activity"] = current_time
    db["daily_stats"][today]["last_activity"] = current_time
    
    save_usage_database(db)

def add_to_daily_stats(stats_type, amount):
    """Dodaje statystyki do dzisiejszego dnia - UWAGA: Używane głównie dla TTS/Whisper"""
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
    
    # Aktualizuj czas aktywności
    current_time = datetime.now().isoformat()
    if db["daily_stats"][today]["first_activity"] is None:
        db["daily_stats"][today]["first_activity"] = current_time
    db["daily_stats"][today]["last_activity"] = current_time
    
    save_usage_database(db)

# Funkcje do trackowania tokenów i kosztów
def init_token_tracking():
    """Inicjalizuje tracking tokenów w session_state z persystentną bazą"""
    if "total_tokens_used" not in st.session_state:
        # Załaduj dane z bazy danych
        db = load_usage_database()
        st.session_state.total_tokens_used = db["total_stats"].copy()
        
        # Upewnij się, że wszystkie wymagane moduły istnieją
        required_modules = ["translator", "belfer", "dialog", "vocabulary"]
        for module in required_modules:
            if module not in st.session_state.total_tokens_used:
                st.session_state.total_tokens_used[module] = {"prompt": 0, "completion": 0, "total": 0}
        
        # Dodaj kompatybilność z starym formatem
        if "tts_chars" not in st.session_state.total_tokens_used:
            st.session_state.total_tokens_used["tts_chars"] = st.session_state.total_tokens_used.get("tts_chars_openai", 0)
        
        # Oznacz nową sesję
        mark_new_session()

def add_token_usage(module_name, prompt_tokens, completion_tokens):
    """Dodaje użycie tokenów do statistyk i zapisuje do bazy"""
    init_token_tracking()
    
    # Upewnij się, że moduł istnieje w session state
    if module_name not in st.session_state.total_tokens_used:
        st.session_state.total_tokens_used[module_name] = {"prompt": 0, "completion": 0, "total": 0}
    
    # Aktualizuj session state
    stats = st.session_state.total_tokens_used[module_name]
    stats["prompt"] += prompt_tokens
    stats["completion"] += completion_tokens
    stats["total"] += (prompt_tokens + completion_tokens)
    
    # Zapisz do persystentnej bazy - tylko raz, po wszystkich zmianach
    db = load_usage_database()
    
    # Aktualizuj total_stats
    db_stats = db["total_stats"][module_name]
    db_stats["prompt"] += prompt_tokens
    db_stats["completion"] += completion_tokens
    db_stats["total"] += (prompt_tokens + completion_tokens)
    
    # Aktualizuj daily_stats bezpośrednio w tej samej instancji db
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
    
    # Dodaj tokeny do daily_stats
    if module_name in ["translator", "belfer", "dialog", "vocabulary"]:
        daily_stats = db["daily_stats"][today][module_name]
        daily_stats["prompt"] += prompt_tokens
        daily_stats["completion"] += completion_tokens
        daily_stats["total"] += (prompt_tokens + completion_tokens)
        
        # Aktualizuj czas aktywności
        current_time = datetime.now().isoformat()
        if db["daily_stats"][today]["first_activity"] is None:
            db["daily_stats"][today]["first_activity"] = current_time
        db["daily_stats"][today]["last_activity"] = current_time
    
    # Zapisz bazę tylko raz na końcu
    save_usage_database(db)

def add_tts_usage(text_length, provider="openai"):
    """Dodaje użycie TTS (liczba znaków) z rozróżnieniem dostawcy"""
    init_token_tracking()
    
    # Aktualizuj session state (kompatybilność wsteczna)
    if "tts_chars" not in st.session_state.total_tokens_used:
        st.session_state.total_tokens_used["tts_chars"] = 0
    st.session_state.total_tokens_used["tts_chars"] += text_length
    
    # Zapisz do persystentnej bazy z rozróżnieniem dostawcy - tylko raz
    db = load_usage_database()
    today = get_today_key()
    
    # Upewnij się że dzisiejszy dzień istnieje
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
    
    # Aktualizuj total_stats i daily_stats w jednej operacji
    if provider.lower() == "gtts":
        db["total_stats"]["tts_chars_gtts"] += text_length
        db["daily_stats"][today]["tts_chars_gtts"] += text_length
    else:
        db["total_stats"]["tts_chars_openai"] += text_length
        db["daily_stats"][today]["tts_chars_openai"] += text_length
    
    # Aktualizuj czas aktywności
    current_time = datetime.now().isoformat()
    if db["daily_stats"][today]["first_activity"] is None:
        db["daily_stats"][today]["first_activity"] = current_time
    db["daily_stats"][today]["last_activity"] = current_time
    
    # Zapisz bazę tylko raz na końcu
    save_usage_database(db)

def add_whisper_usage(duration_seconds):
    """Dodaje użycie Whisper (w minutach)"""
    init_token_tracking()
    minutes = duration_seconds / 60.0
    
    # Aktualizuj session state
    st.session_state.total_tokens_used["whisper_minutes"] += minutes
    
    # Zapisz do persystentnej bazy - tylko raz
    db = load_usage_database()
    today = get_today_key()
    
    # Upewnij się że dzisiejszy dzień istnieje
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
    
    # Aktualizuj total_stats i daily_stats w jednej operacji
    db["total_stats"]["whisper_minutes"] += minutes
    db["daily_stats"][today]["whisper_minutes"] += minutes
    
    # Aktualizuj czas aktywności
    current_time = datetime.now().isoformat()
    if db["daily_stats"][today]["first_activity"] is None:
        db["daily_stats"][today]["first_activity"] = current_time
    db["daily_stats"][today]["last_activity"] = current_time
    
    # Zapisz bazę tylko raz na końcu
    save_usage_database(db)

def calculate_costs(use_database=True):
    """Oblicza koszty na podstawie aktualnych cen OpenAI (wrzesień 2024)"""
    if use_database:
        db = load_usage_database()
        stats = db["total_stats"]
        # Kompatybilność z session state
        if "tts_chars" not in stats:
            stats["tts_chars"] = stats.get("tts_chars_openai", 0)
    else:
        init_token_tracking()
        stats = st.session_state.total_tokens_used
    
    # Ceny OpenAI (USD per 1M tokenów)
    gpt4o_mini_input = 0.15  # $0.15 per 1M input tokens
    gpt4o_mini_output = 0.60  # $0.60 per 1M output tokens
    tts_price = 15.0  # $15.00 per 1M characters
    whisper_price = 0.006  # $0.006 per minute
    
    total_cost = 0
    costs = {}
    
    # Koszty modułów (GPT-4o-mini)
    for module in ["translator", "belfer", "dialog", "vocabulary"]:
        # Bezpieczne pobranie statystyk z migracją dla starych baz
        if module not in stats:
            stats[module] = {"prompt": 0, "completion": 0, "total": 0}
            
        module_stats = stats[module]
        input_cost = (module_stats["prompt"] / 1_000_000) * gpt4o_mini_input
        output_cost = (module_stats["completion"] / 1_000_000) * gpt4o_mini_output
        module_cost = input_cost + output_cost
        costs[module] = module_cost
        total_cost += module_cost
    
    # Koszt TTS OpenAI (gTTS jest darmowe)
    tts_openai_chars = stats.get("tts_chars_openai", stats.get("tts_chars", 0))
    tts_cost = (tts_openai_chars / 1_000_000) * tts_price
    costs["tts_openai"] = tts_cost
    total_cost += tts_cost
    
    # gTTS - darmowe
    costs["tts_gtts"] = 0.0
    
    # Koszt Whisper
    whisper_cost = stats["whisper_minutes"] * whisper_price
    costs["whisper"] = whisper_cost
    total_cost += whisper_cost
    
    # Zapisz łączny koszt do bazy
    if use_database:
        db = load_usage_database()
        db["total_stats"]["total_cost_usd"] = total_cost
        save_usage_database(db)
    
    return costs, total_cost

def show_tts_sidebar():
    """Wyświetla wybór dostawcy TTS w sidebar"""
    #st.sidebar.divider()
    st.sidebar.subheader("🔊 Ustawienia TTS")
    
    # Opcje TTS
    tts_options = ["OpenAI TTS"]
    default_index = 0
    
    if GTTS_AVAILABLE:
        tts_options.append("gTTS (Google)")
        default_index = 1  # Jeśli gTTS dostępne, ustaw jako domyślne
    
    # Wybór dostawcy TTS
    tts_provider = st.sidebar.selectbox(
        "Dostawca syntez mowy:",
        tts_options,
        index=default_index,
        key="tts_provider",
        help="OpenAI TTS: płatne, lepsze głosy, więcej opcji\ngTTS: darmowe, podstawowa jakość"
    )
    
    # Informacje o wybranym dostawcy
    if tts_provider == "OpenAI TTS":
        st.sidebar.caption("💰 Płatne • 🎭 Wiele głosów • 🔊 Wysoka jakość")
    elif tts_provider == "gTTS (Google)":
        st.sidebar.caption("🆓 Darmowe • 🤖 Podstawowe głosy • ⚡ Szybkie")
    
    if not GTTS_AVAILABLE and len(tts_options) == 1:
        st.sidebar.caption("💡 Zainstaluj gTTS dla darmowej opcji: `pip install gtts`")

def show_token_sidebar():
    """Wyświetla statystyki tokenów i kosztów z persystentnej bazy danych"""
    # Załaduj dane z bazy
    db = load_usage_database()
    costs, total_cost = calculate_costs(use_database=True)
    stats = db["total_stats"]
    
    #st.sidebar.divider()
    st.sidebar.subheader("📊 Statystyki użycia")
    
    # Tokeny łącznie (wszystkie czasy)
    total_tokens = sum(module["total"] for module in [stats["translator"], stats["belfer"], stats["dialog"], stats["vocabulary"]])
    st.sidebar.metric("Tokeny łącznie", f"{total_tokens:,}")
    
    # Koszty łącznie
    st.sidebar.metric("💰 Łączny koszt", f"${total_cost:.4f}")
    
    # Dzisiejsze statystyki
    today = get_today_key()
    today_stats = db["daily_stats"].get(today, {})
    if today_stats:
        today_tokens = sum(module.get("total", 0) for module in [
            today_stats.get("translator", {}), 
            today_stats.get("belfer", {}), 
            today_stats.get("dialog", {}),
            today_stats.get("vocabulary", {})
        ])
        if today_tokens > 0:
            st.sidebar.metric("📅 Dzisiaj tokenów", f"{today_tokens:,}")
    
    # Szczegółowe statystyki
    with st.sidebar.expander("🔍 Szczegóły tokenów"):
        st.write("**📈 Łącznie wszystkich czasów:**")
        st.write(f"• Translator: {stats['translator']['total']:,}")
        st.write(f"• Belfer: {stats['belfer']['total']:,}")
        st.write(f"• Dialog: {stats['dialog']['total']:,}")
        st.write(f"• Vocabulary: {stats['vocabulary']['total']:,}")
        st.write(f"• TTS OpenAI: {stats.get('tts_chars_openai', 0):,} zn.")
        st.write(f"• TTS gTTS: {stats.get('tts_chars_gtts', 0):,} zn. 🆓")
        st.write(f"• Whisper: {stats['whisper_minutes']:.2f} min")
    
    with st.sidebar.expander("� Szczegóły kosztów"):
        st.write("**� Łączne koszty:**")
        st.write(f"• Translator: ${costs['translator']:.4f}")
        st.write(f"• Belfer: ${costs['belfer']:.4f}")  
        st.write(f"• Dialog: ${costs['dialog']:.4f}")
        st.write(f"• Vocabulary: ${costs['vocabulary']:.4f}")
        st.write(f"• TTS OpenAI: ${costs['tts_openai']:.4f}")
        st.write(f"• TTS gTTS: $0.0000 🆓")
        st.write(f"• Whisper: ${costs['whisper']:.4f}")
    
    # Dzienne statystyki szczegółowo
    if today_stats:
        with st.sidebar.expander("📅 Dzisiejsze szczegóły"):
            st.write("**🎯 Tokeny dzisiaj:**")
            if today_stats.get("translator", {}).get("total", 0) > 0:
                st.write(f"• Translator: {today_stats['translator']['total']:,}")
            if today_stats.get("belfer", {}).get("total", 0) > 0:
                st.write(f"• Belfer: {today_stats['belfer']['total']:,}")
            if today_stats.get("dialog", {}).get("total", 0) > 0:
                st.write(f"• Dialog: {today_stats['dialog']['total']:,}")
            if today_stats.get("vocabulary", {}).get("total", 0) > 0:
                st.write(f"• Vocabulary: {today_stats['vocabulary']['total']:,}")
            
            st.write("**🔊 TTS dzisiaj:**")
            openai_tts_today = today_stats.get("tts_chars_openai", 0)
            gtts_today = today_stats.get("tts_chars_gtts", 0)
            if openai_tts_today > 0:
                st.write(f"• OpenAI: {openai_tts_today:,} zn.")
            if gtts_today > 0:
                st.write(f"• gTTS: {gtts_today:,} zn. 🆓")
            
            whisper_today = today_stats.get("whisper_minutes", 0)
            if whisper_today > 0:
                st.write(f"**🎤 Whisper:** {whisper_today:.2f} min")
    
    # Historia ostatnich dni
    daily_stats = db["daily_stats"]
    if len(daily_stats) > 1:
        with st.sidebar.expander("📊 Historia ostatnich dni"):
            # Sortuj dni od najnowszego
            sorted_days = sorted(daily_stats.keys(), reverse=True)[:7]  # ostatnie 7 dni
            
            for day in sorted_days:
                day_data = daily_stats[day]
                day_tokens = sum(module.get("total", 0) for module in [
                    day_data.get("translator", {}), 
                    day_data.get("belfer", {}), 
                    day_data.get("dialog", {}),
                    day_data.get("vocabulary", {})
                ])
                
                if day_tokens > 0:
                    day_formatted = datetime.strptime(day, "%Y-%m-%d").strftime("%d.%m")
                    if day == today:
                        st.write(f"**{day_formatted} (dzisiaj):** {day_tokens:,} tokenów")
                    else:
                        st.write(f"**{day_formatted}:** {day_tokens:,} tokenów")
    
    # Historia i zarządzanie
    with st.sidebar.expander("📋 Zarządzanie bazą"):
        # Informacje o bazie
        created = datetime.fromisoformat(db["created_date"]).strftime("%d.%m.%Y")
        updated = datetime.fromisoformat(db["last_updated"]).strftime("%d.%m %H:%M")
        st.caption(f"Utworzona: {created}")
        st.caption(f"Aktualizowana: {updated}")
        
        # Liczba dni z danymi
        days_with_data = len(db["daily_stats"])
        if days_with_data > 0:
            st.caption(f"Dni z danymi: {days_with_data}")
        
        # Przyciski zarządzania
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset sesji", help="Resetuj tylko dane bieżącej sesji"):
                st.session_state.pop("total_tokens_used", None)
                st.rerun()
        
        with col2:
            if st.button("🗑️ Wyczyść bazę", help="⚠️ USUWA wszystkie dane!"):
                if os.path.exists(DB_FILE):
                    os.remove(DB_FILE)
                st.session_state.pop("total_tokens_used", None)
                st.rerun()


def text_to_speech_openai(text, language):
    """
    Generuje mowę z tekstu używając OpenAI TTS z odpowiednim głosem dla języka
    
    Args:
        text (str): Tekst do przetworzenia na mowę
        language (str): Język (np. "English", "Polish")
    
    Returns:
        bytes: Audio w formacie MP3
    """
    # Wybór głosu na podstawie języka (używamy polskich nazw z supported_languages)
    voice_mapping = {
        "angielski": "alloy",
        "polski": "nova",     # Nova ma dobry akcent dla języków europejskich
        "niemiecki": "echo",     # Echo dobrze brzmi w niemieckim
        "francuski": "fable",    # Fable ma przyjemny akcent dla francuskiego
        "hiszpański": "onyx",    # Onyx dobrze brzmi w hiszpańskim
        "włoski": "shimmer"  # Shimmer ma melodyjny ton dla włoskiego
    }
    
    selected_voice = voice_mapping.get(language, "alloy")
    
    response = client.audio.speech.create(
        model="tts-1",
        input=text,
        voice=selected_voice,
    )
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
        response.stream_to_file(tmpfile.name)
        tmpfile.flush()
        with open(tmpfile.name, "rb") as audio_file:
            audio_bytes = audio_file.read()
    
    # Trackuj użycie TTS OpenAI
    add_tts_usage(len(text), "openai")
    
    return audio_bytes

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

def text_to_speech_gtts(text, language):
    """
    Generuje mowę z tekstu używając Google TTS (gTTS) - darmowe
    
    Args:
        text (str): Tekst do przetworzenia na mowę
        language (str): Język w polskiej nazwie (np. "angielski", "polski")
    
    Returns:
        bytes: Audio w formacie MP3
    """
    if not GTTS_AVAILABLE:
        raise ImportError("gTTS nie jest zainstalowane. Zainstaluj: pip install gtts")
    
    # Mapowanie polskich nazw na kody gTTS
    gtts_language_map = {
        "angielski": "en",
        "polski": "pl", 
        "niemiecki": "de",
        "francuski": "fr",
        "hiszpański": "es",
        "włoski": "it"
    }
    
    lang_code = gtts_language_map.get(language, "en")
    
    try:
        tts = gTTS(text=text, lang=lang_code) # type: ignore
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
            tts.save(tmpfile.name)
            tmpfile.flush()
            with open(tmpfile.name, "rb") as audio_file:
                audio_bytes = audio_file.read()
        
        # Trackuj użycie gTTS (darmowe)
        add_tts_usage(len(text), "gtts")
        return audio_bytes
        
    except Exception as e:
        raise Exception(f"Błąd gTTS: {e}")

def text_to_speech(text, language):
    """
    Uniwersalna funkcja TTS - używa wybranego przez użytkownika dostawcy
    
    Args:
        text (str): Tekst do przetworzenia na mowę
        language (str): Język w polskiej nazwie (np. "angielski", "polski")
    
    Returns:
        bytes: Audio w formacie MP3
    """
    # Inicjalizuj wybór TTS jeśli nie istnieje
    if "tts_provider" not in st.session_state:
        st.session_state.tts_provider = "OpenAI TTS"
    
    provider = st.session_state.get("tts_provider", "OpenAI TTS")
    
    if provider == "gTTS (Google)" and GTTS_AVAILABLE:
        return text_to_speech_gtts(text, language)
    else:
        return text_to_speech_openai(text, language)

def transcribe_audio(audio_file, language_code="en"):
    """
    Transkrybuje plik audio używając OpenAI Whisper
    
    Args:
        audio_file: Plik audio do transkrypcji
        language_code (str): Kod języka (np. "en", "pl")
    
    Returns:
        str: Transkrybowany tekst
    """
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language=language_code
    )
    
    # Nie mamy dokładnego czasu nagrania tutaj, szacujemy na podstawie rozmiaru
    # W show_recording_interface mamy dokładny czas
    
    return transcription.text

def show_recording_interface(language_in, session_key_prefix=""):
    """
    Wyświetla interfejs nagrywania z przyciskami start/stop
    
    Args:
        language_in (str): Język wejściowy (np. "English", "Polish")
        session_key_prefix (str): Prefiks dla kluczy session_state (aby uniknąć kolizji między modułami)
    
    Returns:
        str or None: Rozpoznany tekst lub None jeśli nie ma nowego nagrania
    """
    # Sprawdź czy audio jest dostępne
    if not AUDIO_AVAILABLE:
        st.warning("🎤 Nagrywanie niedostępne w środowisku chmurowym")
        return ""
    
    language_in_code = language_code_map.get(language_in, "en")
    
    # Klucze session_state z prefiksem
    is_recording_key = f"{session_key_prefix}is_recording"
    recording_data_key = f"{session_key_prefix}recording_data"
    recording_start_time_key = f"{session_key_prefix}recording_start_time"
    recognized_text_key = f"{session_key_prefix}recognized_text"
    
    # Inicjalizacja stanu nagrywania
    if is_recording_key not in st.session_state:
        st.session_state[is_recording_key] = False
    if recording_data_key not in st.session_state:
        st.session_state[recording_data_key] = None
    if recording_start_time_key not in st.session_state:
        st.session_state[recording_start_time_key] = None
    if recognized_text_key not in st.session_state:
        st.session_state[recognized_text_key] = ""

    recognized_text = None
    
    # Sekcja rozpoznawania mowy - start/stop
    if not st.session_state[is_recording_key]:
        # Przycisk START
        if st.button("🎤 Rozpocznij nagrywanie", key=f"{session_key_prefix}start_btn"):
            if not AUDIO_AVAILABLE:
                st.error("❌ Funkcja nagrywania niedostępna w tym środowisku")
                return ""
                
            st.session_state[is_recording_key] = True
            st.session_state[recording_start_time_key] = time.time()
            
            # Rozpocznij nagrywanie w tle
            fs = 16000
            max_seconds = 30
            import sounddevice as sd
            st.session_state[recording_data_key] = sd.rec(int(max_seconds * fs), samplerate=fs, channels=1, dtype='int16')
            st.rerun()
    else:
        # Status nagrywania z czasem
        elapsed = time.time() - st.session_state[recording_start_time_key]
        st.error(f"🔴 NAGRYWANIE TRWA... Czas: {elapsed:.1f}s")
        
        # Przycisk STOP
        if st.button("⏹️ Zatrzymaj i przetwórz", key=f"{session_key_prefix}stop_btn"):
            st.session_state[is_recording_key] = False
            
            if not AUDIO_AVAILABLE:
                st.error("❌ Funkcja nagrywania niedostępna")
                return ""
            
            try:
                import sounddevice as sd
                import scipy.io.wavfile
                
                # Zatrzymaj nagrywanie
                sd.stop()
                
                # Oblicz ile sekund nagrywano
                duration = time.time() - st.session_state[recording_start_time_key]
                duration = max(1.0, min(duration, 30.0))
                
                fs = 16000
                # Przytnij nagranie do faktycznego czasu
                samples = int(duration * fs)
                recording = st.session_state[recording_data_key][:samples]
                
                st.success("⏹️ Zakończono nagrywanie. Przetwarzam...")
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                    scipy.io.wavfile.write(tmpfile.name, fs, recording)
                    tmpfile.flush()
                    with open(tmpfile.name, "rb") as file:
                        recognized_text = transcribe_audio(file, language_in_code)
                    
                    # Trackuj użycie Whisper
                    add_whisper_usage(duration)
                    
                    # Zaktualizuj session state
                    st.session_state[recognized_text_key] = recognized_text
                    st.session_state[recording_data_key] = None  # Wyczyść dane nagrania
                    st.rerun()
                    
            except Exception as e:
                st.session_state[is_recording_key] = False
                st.session_state[recording_data_key] = None
                st.error(f"Błąd podczas nagrywania lub rozpoznawania mowy: {e}")
    
    return st.session_state.get(recognized_text_key, "")
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

# Wybór modelu (globalnie dla całej aplikacji). Możesz ustawić zmienną środowiskową OPENAI_MODEL
# np. OPENAI_MODEL=gpt-5-codex aby włączyć podglądowy model dla wszystkich wywołań.
import os as _os
DEFAULT_MODEL = _os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

def get_model():
    """Zwraca aktywny model OpenAI używany w całej aplikacji."""
    return DEFAULT_MODEL

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
import os
from datetime import datetime

# Import statystyk i kosztów z osobnego modułu
from utils.ai_stats import (
    load_usage_database, create_new_database, migrate_old_database, save_usage_database, get_today_key,
    mark_new_session, add_to_daily_stats, init_token_tracking, add_token_usage, add_tts_usage, add_whisper_usage, calculate_costs
)

# Opcjonalne importy audio - mogą nie być dostępne w środowisku chmurowym
try:
    import sounddevice as sd
    import scipy.io.wavfile as wavfile
    AUDIO_AVAILABLE = True
except (ImportError, OSError):
    # ImportError - brak modułu, OSError - brak PortAudio library
    AUDIO_AVAILABLE = False



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
                from utils.ai_stats import DB_FILE
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
    """Transkrybuje plik audio używając OpenAI Whisper"""
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language=language_code
    )
    return transcription.text

def show_recording_interface(language_in, session_key_prefix=""):
    """
    Wyświetla interfejs nagrywania z przyciskami start/stop (sounddevice)
    
    Args:
        language_in (str): Język wejściowy (np. "English", "Polish")
        session_key_prefix (str): Prefiks dla kluczy session_state (aby uniknąć kolizji między modułami)
    
    Returns:
        str: Rozpoznany tekst lub pusty string jeśli brak nagrania
    """
    if not AUDIO_AVAILABLE:
        st.warning("🎤 Nagrywanie niedostępne w tym środowisku")
        return ""

    language_in_code = language_code_map.get(language_in, "en")

    # Klucze session_state z prefiksem
    is_recording_key = f"{session_key_prefix}is_recording"
    recording_data_key = f"{session_key_prefix}recording_data"
    recording_start_time_key = f"{session_key_prefix}recording_start_time"
    recognized_text_key = f"{session_key_prefix}recognized_text"

    # Inicjalizacja
    if is_recording_key not in st.session_state:
        st.session_state[is_recording_key] = False
    if recording_data_key not in st.session_state:
        st.session_state[recording_data_key] = None
    if recording_start_time_key not in st.session_state:
        st.session_state[recording_start_time_key] = None
    if recognized_text_key not in st.session_state:
        st.session_state[recognized_text_key] = ""

    # UI
    if not st.session_state[is_recording_key]:
        if st.button("🎤 Rozpocznij nagrywanie", key=f"{session_key_prefix}start_btn"):
            if not AUDIO_AVAILABLE:
                st.error("❌ Funkcja nagrywania niedostępna w tym środowisku")
                return ""
            st.session_state[is_recording_key] = True
            st.session_state[recording_start_time_key] = time.time()
            fs = 16000
            max_seconds = 30
            st.session_state[recording_data_key] = sd.rec(int(max_seconds * fs), samplerate=fs, channels=1, dtype='int16')
            st.rerun()
    else:
        elapsed = time.time() - st.session_state[recording_start_time_key]
        st.error(f"🔴 NAGRYWANIE TRWA... Czas: {elapsed:.1f}s")
        if st.button("⏹️ Zatrzymaj i przetwórz", key=f"{session_key_prefix}stop_btn"):
            st.session_state[is_recording_key] = False
            try:
                sd.stop()
                duration = time.time() - st.session_state[recording_start_time_key]
                duration = max(1.0, min(duration, 30.0))
                fs = 16000
                samples = int(duration * fs)
                recording = st.session_state[recording_data_key][:samples]
                st.success("⏹️ Zakończono nagrywanie. Przetwarzam...")
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                    wavfile.write(tmpfile.name, fs, recording)
                    tmpfile.flush()
                    with open(tmpfile.name, "rb") as file:
                        recognized_text = transcribe_audio(file, language_in_code)
                add_whisper_usage(duration)
                st.session_state[recognized_text_key] = recognized_text
                st.session_state[recording_data_key] = None
                st.rerun()
            except Exception as e:
                st.session_state[recording_data_key] = None
                st.error(f"Błąd podczas nagrywania lub rozpoznawania mowy: {e}")

    return st.session_state.get(recognized_text_key, "")
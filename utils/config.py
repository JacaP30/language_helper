"""Konfiguracja klienta OpenAI i zmienne środowiskowe"""

import streamlit as st
from dotenv import dotenv_values
from openai import OpenAI

def load_environment():
    """Ładuje zmienne środowiskowe z pliku .env"""
    env = dotenv_values(".env")
    if not env.get("OPENAI_API_KEY"):
        st.error("❌ Brak klucza API OpenAI w pliku .env")
        st.stop()
    return env

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
import sounddevice as sd
import scipy.io.wavfile

# Funkcje do trackowania tokenów i kosztów
def init_token_tracking():
    """Inicjalizuje tracking tokenów w session_state"""
    if "total_tokens_used" not in st.session_state:
        st.session_state.total_tokens_used = {
            "translator": {"prompt": 0, "completion": 0, "total": 0},
            "belfer": {"prompt": 0, "completion": 0, "total": 0},
            "dialog": {"prompt": 0, "completion": 0, "total": 0},
            "tts_chars": 0,  # TTS liczony w znakach
            "whisper_minutes": 0.0  # Whisper liczony w minutach
        }

def add_token_usage(module_name, prompt_tokens, completion_tokens):
    """Dodaje użycie tokenów do statistyk"""
    init_token_tracking()
    stats = st.session_state.total_tokens_used[module_name]
    stats["prompt"] += prompt_tokens
    stats["completion"] += completion_tokens
    stats["total"] += (prompt_tokens + completion_tokens)

def add_tts_usage(text_length):
    """Dodaje użycie TTS (liczba znaków)"""
    init_token_tracking()
    st.session_state.total_tokens_used["tts_chars"] += text_length

def add_whisper_usage(duration_seconds):
    """Dodaje użycie Whisper (w minutach)"""
    init_token_tracking()
    st.session_state.total_tokens_used["whisper_minutes"] += duration_seconds / 60.0

def calculate_costs():
    """Oblicza koszty na podstawie aktualnych cen OpenAI (wrzesień 2024)"""
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
    for module in ["translator", "belfer", "dialog"]:
        module_stats = stats[module]
        input_cost = (module_stats["prompt"] / 1_000_000) * gpt4o_mini_input
        output_cost = (module_stats["completion"] / 1_000_000) * gpt4o_mini_output
        module_cost = input_cost + output_cost
        costs[module] = module_cost
        total_cost += module_cost
    
    # Koszt TTS
    tts_cost = (stats["tts_chars"] / 1_000_000) * tts_price
    costs["tts"] = tts_cost
    total_cost += tts_cost
    
    # Koszt Whisper
    whisper_cost = stats["whisper_minutes"] * whisper_price
    costs["whisper"] = whisper_cost
    total_cost += whisper_cost
    
    return costs, total_cost

def show_token_sidebar():
    """Wyświetla statystyki tokenów w sidebar"""
    init_token_tracking()
    costs, total_cost = calculate_costs()
    stats = st.session_state.total_tokens_used
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 Statystyki użycia")
    
    # Tokeny
    total_tokens = sum(module["total"] for module in [stats["translator"], stats["belfer"], stats["dialog"]])
    st.sidebar.metric("Tokeny łącznie", f"{total_tokens:,}")
    
    # Szczegóły tokenów
    with st.sidebar.expander("🔍 Szczegóły tokenów"):
        st.write(f"**Translator:** {stats['translator']['total']:,}")
        st.write(f"**Belfer:** {stats['belfer']['total']:,}")
        st.write(f"**Dialog:** {stats['dialog']['total']:,}")
        st.write(f"**TTS znaki:** {stats['tts_chars']:,}")
        st.write(f"**Whisper min:** {stats['whisper_minutes']:.2f}")
    
    # Koszty
    st.sidebar.metric("💰 Łączny koszt", f"${total_cost:.4f}")
    
    with st.sidebar.expander("💵 Szczegóły kosztów"):
        st.write(f"**Translator:** ${costs['translator']:.4f}")
        st.write(f"**Belfer:** ${costs['belfer']:.4f}")  
        st.write(f"**Dialog:** ${costs['dialog']:.4f}")
        st.write(f"**TTS:** ${costs['tts']:.4f}")
        st.write(f"**Whisper:** ${costs['whisper']:.4f}")
    
    # Przycisk resetowania
    if st.sidebar.button("🔄 Resetuj statystyki"):
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
    
    # Trackuj użycie TTS
    add_tts_usage(len(text))
    
    return audio_bytes

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
            st.session_state[is_recording_key] = True
            st.session_state[recording_start_time_key] = time.time()
            
            # Rozpocznij nagrywanie w tle
            fs = 16000
            max_seconds = 30
            st.session_state[recording_data_key] = sd.rec(int(max_seconds * fs), samplerate=fs, channels=1, dtype='int16')
            st.rerun()
    else:
        # Status nagrywania z czasem
        elapsed = time.time() - st.session_state[recording_start_time_key]
        st.error(f"🔴 NAGRYWANIE TRWA... Czas: {elapsed:.1f}s")
        
        # Przycisk STOP
        if st.button("⏹️ Zatrzymaj i przetwórz", key=f"{session_key_prefix}stop_btn"):
            st.session_state[is_recording_key] = False
            
            try:
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
"""Kompatybilny z Streamlit Cloud moduł nagrywania audio"""

import streamlit as st
import tempfile
import os

def cloud_audio_recorder_interface(session_key_prefix=""):
    """
    Interfejs nagrywania kompatybilny z Streamlit Cloud
    Używa wbudowanego komponentu Streamlit audio_input
    """
    # st.write("🎤 Nagraj swoją wypowiedź:")
    
    # Użyj wbudowanego komponentu Streamlit do nagrywania
    audio_bytes = st.audio_input("Nagraj", key=f"{session_key_prefix}audio_recorder")
    
    if audio_bytes:
        # Zapisz do pliku tymczasowego
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes.getvalue())
            tmp_filename = tmp_file.name
        
        # st.audio(audio_bytes, format="audio/wav")
        # st.success("✅ Nagranie gotowe do przetworzenia!")
        return tmp_filename
    
    return None

def transcribe_audio_file(audio_file_path, language_code="en"):
    """
    Transkrybuje plik audio używając OpenAI Whisper
    
    Args:
        audio_file_path (str): Ścieżka do pliku audio
        language_code (str): Kod języka (en, pl, de, etc.)
    
    Returns:
        str: Rozpoznany tekst
    """
    from utils.config import client
    from utils.ai_stats import add_whisper_usage
    import os
    
    try:
        with open(audio_file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=file,
                language=language_code
            )
        
        # Oblicz czas trwania (przybliżony)
        file_size = os.path.getsize(audio_file_path)
        # Przybliżony czas w sekundach (16kHz, 16-bit mono)
        duration_seconds = file_size / (16000 * 2)  
        add_whisper_usage(duration_seconds)
        
        return transcription.text
    except Exception as e:
        st.error(f"Błąd podczas transkrypcji: {e}")
        return ""
    finally:
        # Sprzątanie - usuń tymczasowy plik
        try:
            os.unlink(audio_file_path)
        except:
            pass
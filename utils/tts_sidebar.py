import streamlit as st

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

def show_tts_sidebar():
    st.sidebar.subheader("🔊 Ustawienia TTS")
    # UWAGA: Blokada wyboru OpenAI TTS na potrzeby testów!
    # Jeśli chcesz przywrócić wybór OpenAI TTS, ZAMIEŃ poniższy blok na ten kod:
    #
    # tts_options = ["OpenAI TTS"]
    # default_index = 0
    # if GTTS_AVAILABLE:
    #     tts_options.append("gTTS (Google)")
    #     default_index = 1  # Jeśli gTTS dostępne, ustaw jako domyślne
    # tts_provider = st.sidebar.selectbox(
    #     "Wybierz dostawcę TTS:",
    #     tts_options,
    #     index=default_index,
    #     key="tts_provider",
    #     help="OpenAI TTS: płatne, lepsze głosy, więcej opcji\ngTTS: darmowe, podstawowa jakość"
    # )
    # if tts_provider == "OpenAI TTS":
    #     st.sidebar.caption("💰 Płatne • 🎭 Wiele głosów • 🔊 Wysoka jakość")
    # elif tts_provider == "gTTS (Google)":
    #     st.sidebar.caption("🆓 Darmowe • 🤖 Podstawowe głosy • ⚡ Szybkie")
    # if not GTTS_AVAILABLE and len(tts_options) == 1:
    #     st.sidebar.caption("💡 Zainstaluj gTTS dla darmowej opcji: `pip install gtts`")
    # --- BLOKADA OPENAI TTS (wersja testowa) ---
    if GTTS_AVAILABLE:
        tts_options = ["gTTS (Google)"]
        tts_provider = st.sidebar.selectbox(
            "Wybierz dostawcę TTS:",
            tts_options,
            index=0,
            key="tts_provider",
            help="Wersja testowa: dostępny tylko gTTS (Google) - darmowy, podstawowa jakość"
        )
        st.sidebar.info("OpenAI TTS jest zablokowane w tej wersji testowej. Dostępny tylko gTTS (Google).")
    else:
        st.sidebar.warning("gTTS (Google) nie jest dostępny. Zainstaluj pakiet gtts.")
        st.session_state["tts_provider"] = "gTTS (Google)"
    # --- KONIEC BLOKADY ---

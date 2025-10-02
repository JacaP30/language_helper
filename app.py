"""
Wersja z background_styles
PLLA - Personal Language Learning Assistant AI
Aplikacja do nauki języków obcych z funkcjami tłumaczenia, sprawdzania gramatyki i dialogu z AI.
"""
import streamlit as st
from background_styles import apply_background_with_readability
# Importy z utils 
from utils.config import load_environment, client, supported_languages, language_code_map, show_token_sidebar, show_tts_sidebar
# Importy modułów  
from modules.translator import show_translator
from modules.belfer import show_belfer
from modules.dialog import show_dialog 


st.set_page_config(
    layout="wide", #layout="wide" - szeroki, layout="centered" - wyśrodkowany, layout="wide" - szeroki, layout="fullscreen" - pełny ekran
    page_title="PANJO", #tytuł strony
    page_icon="🗣️", #ikona strony - symbolizuje mówienie/języki
    initial_sidebar_state="collapsed" #stan sidebar - zwinięty
)

# Zastosuj tło z obrazka i style czytelności
apply_background_with_readability()

#st.title("PANJO - personalny asystent nauki języków obcych z AI")

with st.sidebar:
    tool_language = st.selectbox(
        "Wybierz narzędzie",
        [                    
            "Nauka słówek", # fiszki i testy słownictwa
            "Belfer", # sprawdza poprawność zdań ZROBIONE
            "Dialog", # prowadzi dialog (dorobić wybór tematów.)
            "Translator" # tłumacz ZROBIONE
        ], key="tool_language"
    )
    
    #st.divider()
    st.subheader("🌍 Ustawienia języków")
    
    # Globalne wybory języków dla wszystkich modułów
    language_in = st.selectbox(
        "Język źródłowy:", 
        supported_languages, 
        index=0, 
        key="global_language_in",
        help="Język tekstu wejściowego/nagrań"
    )
    
    language_out = st.selectbox(
        "Język docelowy:", 
        supported_languages, 
        index=1, 
        key="global_language_out",
        help="Język tłumaczenia/odpowiedzi"
    )
    
    # Wyświetl wybór TTS
    show_tts_sidebar()
    
    # Wyświetl statystyki tokenów i kosztów
    show_token_sidebar()

# Główne sekcje aplikacji
if tool_language == "Translator":
    show_translator(language_in, language_out)

elif tool_language == "Belfer":
    show_belfer(language_in, language_out)

elif tool_language == "Dialog":
    show_dialog(language_in, language_out)

elif tool_language == "Nauka słówek":
    from modules.vocabulary import show_vocabulary
    show_vocabulary(language_in, language_out)

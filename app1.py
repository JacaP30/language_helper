"""
PLLA - Personal Language Learning Assistant AI
Aplikacja do nauki języków obcych z funkcjami tłumaczenia, sprawdzania gramatyki i dialogu z AI.
"""
import streamlit as st

# Importy z utils
from utils.config import load_environment, client, supported_languages, language_code_map, show_token_sidebar
# Importy modułów  
from modules.translator import show_translator
from modules.belfer import show_belfer
from modules.dialog import show_dialog

st.title("PANJO - personalny asystent nauki języków obcych z AI")

with st.sidebar:
    tool_language = st.selectbox(
        "Wybierz narzędzie",
        [
            "Translator", # tłumacz ZROBIONE
            "Belfer", # sprawdza poprawność zdań ZROBIONE
            "Jak powiem?", # pomaga budować zagadnienia
            "Dialog" # prowadzi dialog (dorobić wybór tematów.)
        ], key="tool_language"
    )
    
    st.divider()
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
    
    # Wyświetl statystyki tokenów i kosztów
    show_token_sidebar()

# Główne sekcje aplikacji
if tool_language == "Translator":
    show_translator(language_in, language_out)

elif tool_language == "Belfer":
    show_belfer(language_in, language_out)

elif tool_language == "Dialog":
    show_dialog(language_in, language_out)

elif tool_language == "Jak powiem?":
    st.header("Jak powiem? - w budowie")
    st.info("Ta sekcja będzie wkrótce dostępna!")

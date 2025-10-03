"""
Wersja z background_styles
PLLA - Personal Language Learning Assistant AI
Aplikacja do nauki języków obcych z funkcjami tłumaczenia, sprawdzania gramatyki i dialogu z AI.
"""
import streamlit as st
# Importy z utils 
from utils.background_styles import apply_background_with_readability
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

# tytuł strony i niebieski pasek po lewej stronie
st.markdown(  
    """
    <style>
    /* Wymuś tryb ciemny */
    .stApp {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* Niebieski pasek polewej stronie - zawsze widoczny */
    body::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 4px;
        height: 100vh;
        background-color: #1f77b4;
        z-index: 9999;
    }
    /* Pasek na krawędzi sidebara (gdy sidebar jest otwarty) */
    section[data-testid="stSidebar"] {
        border-right: 8px solid #1976d2 !important;
        box-sizing: border-box;
        background-color: #262730 !important;
    }
    </style>

   
    
    <h1 style="
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 25%, #ffee00 50%, #32cd32 75%, #1e90ff 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        font-size: 3em !important;
        font-weight: bold !important;
        text-align: center !important;
        margin: 20px 0 !important;
        display: inline-block !important;
        width: 100% !important;
    ">
        PANJO - personalny asystent nauki języków obcych z AI
    </h1>
    """,  
    unsafe_allow_html=True
)

# Zastosuj tło z obrazka i style czytelności
apply_background_with_readability()

#st.title("PANJO - personalny asystent nauki języków obcych z AI") # przeniesiony do background_styles.py

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

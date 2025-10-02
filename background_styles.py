"""
Moduł stylów tła dla aplikacji PANJO
"""

import streamlit as st
import base64
import os

def apply_background_with_readability():
    """Dodaje tło z obrazka i style dla lepszej czytelności"""
    
    # Wczytaj obrazek tła
    background_path = r"background\tlolanguagehelper.png"
    
    if os.path.exists(background_path):
        with open(background_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
        
        background_css = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_image});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Główny kontener z kolorem #2349e1 
        .main .block-container {{
            background-color: #2349e1 !important;
            border-radius: 15px !important;
            padding: 2rem !important;
            margin-top: 1rem !important;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
            backdrop-filter: blur(10px) !important;
            color: white !important;
        }}
        
        /* Tekst w głównym kontenerze - ciemno zielony */
        .main .block-container * {{
            color: #174801ff !important;
        }}
        
        /* Sidebar z przezroczystym tłem */
        .css-1d391kg, .css-1cypcdb {{
            background-color: #194802ff !important; /* Ciemnozielony kolor */
            border-radius: 15px !important;
            box-shadow: 0 8px 16px #194802ff !important; /* Zielony cień */
            backdrop-filter: blur(10px) !important;
        }}
        
        /* Wszystkie pola input i textarea */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stNumberInput > div > div > input {{
            background-color: #95b7f6ff !important; /* Jasnoniebieski kolor */
            border: 1px solid #000000 !important; /* Cień obramowania */
            border-radius: 8px !important;
            backdrop-filter: blur(5px) !important;
            color: #000000ff !important; /* Ciemny tekst */
        }}
        
        /* Przyciski */
        .stButton > button {{
            background-color: #c9d9f8ff !important; /* Bardzo jasnoniebieski kolor */
            border: 2px solid #000000 !important; /* Cień obramowania */
            border-radius: 10px !important;
            backdrop-filter: blur(5px) !important;
            font-weight: 600 !important;
            color: #2d1616ff !important; /* Ciemny tekst */
            box-shadow: 0 4px 8px #d8f255ff !important; /* Jasnoniebieski cień */
        }}
        
        .stButton > button:hover {{
            background-color: rgba(240, 240, 240, 0.95) !important; /* Jaśniejszy przy najechaniu */
            transform: translateY(-2px) !important;
        }}
        
        /* Nagłówki 2, 3, 4, 5, 6 */
        h2, h3, h4, h5, h6 {{
            background-color: #a2bdf4ff !important; /* Jasnoniebieski kolor */
            border-radius: 8px !important;
            padding: 10px 15px !important;
            backdrop-filter: blur(5px) !important;
            margin: 15px 0 !important;
            color: #2d1616ff !important; /* Ciemny tekst */
            box-shadow: 2px 2px 4px #a2bdf4ff !important; /* Jasnoniebieski cień */
        }}

        /* Nagłówek 1 - z gradientem tła i kolorowym gradientem tekstu */
        h1{{
            background: linear-gradient(135deg, #2349e1 0%, #6596f0ff 25%, #95b7f6 50%, #6596f0ff 75%, #2349e1 100%) !important; /* Gradient tła */
            border-radius: 15px !important;
            padding: 20px 25px !important;
            backdrop-filter: blur(10px) !important;
            margin: 20px 0 !important;
            box-shadow: 0 8px 16px rgba(35, 73, 225, 0.3) !important; /* Niebieski cień */
            text-align: center !important; /* Wyśrodkowany tekst */
            font-weight: bold !important; /* Pogrubiony tekst */
            
            /* Gradient tekstu - poprawna składnia */
            color: transparent !important;
            background-image: linear-gradient(135deg, #e15f23ff 20%, #eef359ff 25%, #9cf359ff 50%, #e15f23ff 75%, #e15f23ff 100%), 
                            linear-gradient(135deg, #2349e1 0%, #6596f0ff 25%, #95b7f6 50%, #6596f0ff 75%, #2349e1 100%) !important;
            -webkit-background-clip: text, padding-box !important;
            background-clip: text, padding-box !important;
            -webkit-text-fill-color: transparent !important;
        }}
        
        /* Tekst i markdown */
        div[data-testid="stText"],
        .stMarkdown {{
            background-color: #559ef78c !important; /* Jasny kolor dla lepszej czytelności */
            border-radius: 8px !important;
            padding: 10px !important;
            backdrop-filter: blur(3px) !important;
            margin: 8px 0 !important;
            color: #2d1616ff !important; /* Ciemny tekst */
        }}
        
        /* Alerty i komunikaty */
        .stAlert > div,
        .stSuccess > div,
        .stInfo > div,
        .stWarning > div,
        .stError > div {{
            background-color: #ffffff !important; /* Biały kolor dla lepszej czytelności */
            border-radius: 10px !important;
            backdrop-filter: blur(5px) !important;
            box-shadow: 0 4px 8px #000000 !important; /* Cień dla lepszej widoczności */
            color: #06042aff !important; /* Ciemny tekst */
        }}
        
        /* Tabele */
        .stDataFrame > div,
        .dataframe {{
            background-color: #ffffff !important; /* Biały kolor dla lepszej czytelności */
            border-radius: 10px !important;
            backdrop-filter: blur(5px) !important;
            box-shadow: 0 4px 8px #000000 !important; /* Cień dla lepszej widoczności */
        }}
        
        /* Expander - stare i nowe selektory TO NIE DZIAŁA DZIAŁA NIŻEJ */ 
        .streamlit-expanderHeader,
        .streamlit-expanderContent,
        div[data-testid="stExpander"] > div,
        div[data-testid="stExpander"] > div > div,
        .stExpander > div,
        .stExpander > div > div {{
            background-color: rgba(255, 255, 255, 0.9) !important; /* Białe półprzezroczyste tło */
            border-radius: 10px !important;
            backdrop-filter: blur(10px) !important;
            color: #000000 !important; /* Ciemny tekst dla lepszej czytelności */
            padding: 15px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
        }}
        
        /* Tekst wewnątrz expandera - wszystkie możliwe selektory */
        .streamlit-expanderContent *,
        div[data-testid="stExpander"] *,
        .stExpander * {{
            background-color: transparent !important; /* Białe półprzezroczyste tło */
            color: #00ff00ff !important; /* Ciemny tekst dla wszystkich elementów wewnątrz */
            font-size: 18px !important;
        }}
        
        /* Checkbox i radio */
        .stCheckbox > label,
        .stRadio > label {{
            background-color: #ffffff50 !important; /* Białe półprzezroczyste tło */
            border-radius: 5px !important;
            padding: 8px !important;
            backdrop-filter: blur(3px) !important;
            margin: 5px 0 !important;
            color: #000000 !important;
        }}
        /* Tekst w checkbox i radio */
        .stCheckbox > label > div,
        .stRadio > label > div,
        .stCheckbox span,
        .stRadio span {{
            color: #ffffff !important; /* Ciemny tekst */
        }}

        /* File uploader */
        .stFileUploader > div {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 10px !important;
            backdrop-filter: blur(5px) !important;
            border: 2px dashed rgba(0, 0, 0, 0.3) !important;
        }}
        
        /* Slider */
        .stSlider > div > div {{
            background-color: rgba(255, 255, 255, 0.8) !important;
            border-radius: 10px !important;
            padding: 10px !important;
            backdrop-filter: blur(3px) !important;
        }}
        
        /* Metryki */
        div[data-testid="metric-container"] {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 10px !important;
            padding: 15px !important;
            backdrop-filter: blur(5px) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
        }}
        
        /* Tabs - tylko przełączniki/nagłówki */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: #95b7f6ff !important;
            border-radius: 10px !important;
            padding: 5px !important;
            backdrop-filter: blur(8px) !important;
            box-shadow: 0 2px 8px #95b7f6ff !important;
        }}
        
        /* Poszczególne zakładki */
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.6) !important;
            border-radius: 8px !important;
            margin: 0 2px !important;
            border: 1px solid #95b7f6ff !important;
            color: #2d1616ff !important; /* Ciemny tekst */
        }}
        
        /* Aktywna zakładka */
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background-color: #2349e1 !important;
            color: white !important;
            font-weight: bold !important;
        }}
        </style>
        """
        st.title("PANJO - personalny asystent nauki języków obcych z AI")
        st.markdown(background_css, unsafe_allow_html=True)
    else:
        st.warning(f"Nie znaleziono pliku tła: {background_path}")
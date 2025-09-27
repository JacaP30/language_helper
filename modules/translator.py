"""
Moduł Translator - tłumaczenie tekstu z rozpoznawaniem mowy
"""
import streamlit as st
from utils.config import client, supported_languages, language_code_map, text_to_speech_openai, show_recording_interface, add_token_usage


def show_translator(language_in, language_out):
    """Wyświetla interfejs translatora"""
    st.header("Translator językowy")
    
    # Używamy globalnych ustawień języków z sidebar
    # ustawienie języka kodu dla rozpoznawania mowy
    language_in_code = language_code_map.get(language_in, "en")

    # Interfejs nagrywania - używamy wspólnej funkcji
    recognized_text = show_recording_interface(language_in, "translator_")
    
    # Pole tekstowe do wpisania wiadomości
    translate_text = st.text_area(
        "Wpisz tekst do tłumaczenia w wybranym języku lub nagraj rozmowę:",
        value=recognized_text,
        key="translate_text_area"
    )

    # Używamy globalnych ustawień języków z sidebar
    language_out_code = language_code_map.get(language_out, "pl")

    # Przechowywanie tłumaczenia w session_state
    if "last_translation" not in st.session_state:
        st.session_state["last_translation"] = ""
    if "last_audio" not in st.session_state:
        st.session_state["last_audio"] = None

    # Wyświetl tłumaczenie, jeśli istnieje
    if st.session_state.get("last_translation"):
        st.subheader(f"Tłumaczenie na {language_out}:")
        st.write(st.session_state["last_translation"])

    if st.button("Przetłumacz na wybrany język"):
        if not st.session_state["translate_text_area"].strip():
            st.warning("Proszę wpisać tekst do przetłumaczenia lub nagrać rozmowę.")
        else:
            # Wywołanie OpenAI API do tłumaczenia
            prompt = f"Przetłumacz na {language_out} następujący tekst:\n{st.session_state['translate_text_area']}"
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"Jesteś pomocnym tłumaczem. Tłumacz tekst z {language_in} na {language_out}. Jeśli tekst jest już w języku docelowym, napisz 'Tekst jest już w wybranym języku.'"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.1,
                )
                
                # Trackuj użycie tokenów
                if response.usage:
                    add_token_usage("translator", response.usage.prompt_tokens, response.usage.completion_tokens)
                
                content = response.choices[0].message.content
                translation = content.strip() if content is not None else ""
                st.session_state["last_translation"] = translation  # Zapisz tłumaczenie do session_state
                st.session_state["last_audio"] = text_to_speech_openai(translation, language_out)
                
                # Wyświetl użycie tokenów
                if response.usage:
                    st.caption(f"📊 Użyto {response.usage.prompt_tokens} + {response.usage.completion_tokens} = {response.usage.total_tokens} tokenów")
                
                st.rerun()
            except Exception as e:
                st.error(f"Wystąpił błąd podczas tłumaczenia: {e}")

    # Odtwarzanie ostatniego tłumaczenia z session_state
    if st.button("Odtwórz wymowę"):
        if st.session_state.get("last_translation"):
            if st.session_state.get("last_audio") is None:
                st.session_state["last_audio"] = text_to_speech_openai(st.session_state["last_translation"], language_out)
            st.audio(st.session_state["last_audio"], format="audio/mp3")
        else:
            st.warning("Brak tłumaczenia do odtworzenia. Najpierw przetłumacz tekst.")
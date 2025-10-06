"""
Moduł Translator - tłumaczenie tekstu z rozpoznawaniem mowy
"""
import streamlit as st
from utils.config import client, supported_languages, language_code_map, text_to_speech, get_model
from utils.ai_stats import add_token_usage
from utils.cloud_audio_recorder import cloud_audio_recorder_interface, transcribe_audio_file


def show_translator(language_in, language_out):
    """Wyświetla interfejs translatora"""
    st.header("Translator językowy")
    
    # Używamy globalnych ustawień języków z sidebar
    # ustawienie języka kodu dla rozpoznawania mowy
    language_in_code = language_code_map.get(language_in, "en")

    # Nowy interfejs nagrywania kompatybilny z chmurą
    st.subheader("🎤 Nagrywanie głosu")
    audio_file_path = cloud_audio_recorder_interface("translator_")
    
    recognized_text = ""
    if audio_file_path:
        with st.spinner("🔄 Rozpoznawanie mowy..."):
            recognized_text = transcribe_audio_file(audio_file_path, language_in_code)
    
    # Pole tekstowe do wpisania wiadomości
    translate_text = st.text_area(
        f"Wpisz tekst do przetłumaczenia lub nagraj w języku - {language_in}",
        value=recognized_text,
        key="translate_text_area"
    )

    # ... reszta kodu bez zmian ...
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

    if st.button(f"Przetłumacz na język - {language_out}"):
        if not st.session_state["translate_text_area"].strip():
            st.warning("Proszę wpisać tekst do przetłumaczenia lub nagrać rozmowę.")
        else:
            # Wywołanie OpenAI API do tłumaczenia
            prompt = f"Przetłumacz na {language_out} następujący tekst:\n{st.session_state['translate_text_area']}"
            try:
                response = client.chat.completions.create(
                    model=get_model(),
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
                st.session_state["last_audio"] = text_to_speech(translation, language_out)
                
                # Wyświetl użycie tokenów
                if response.usage:
                    st.caption(f"📊 Użyto {response.usage.prompt_tokens} + {response.usage.completion_tokens} = {response.usage.total_tokens} tokenów")
                
                st.rerun()
            except Exception as e:
                st.error(f"Wystąpił błąd podczas tłumaczenia: {e}")

    # Odtwarzanie ostatniego tłumaczenia z session_state
    if st.button("🔊 Odtwórz wymowę"):
        if st.session_state.get("last_translation"):
            if st.session_state.get("last_audio") is None:
                st.session_state["last_audio"] = text_to_speech(st.session_state["last_translation"], language_out)
            st.audio(st.session_state["last_audio"], format="audio/mp3")
        else:
            st.warning("Brak tłumaczenia do odtworzenia. Najpierw przetłumacz tekst.")
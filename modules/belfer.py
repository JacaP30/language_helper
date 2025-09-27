"""
Moduł Belfer - urzytkownik wpisuje zdanie lub wyraz w wybranym języku in a openAi sprawdza pisownię, gramatykę i budowę zdania.
Dla sprawdzenia wyświetla tłumaczenie w wybranym języku out
"""
import streamlit as st
from utils.config import client, supported_languages, language_code_map, show_recording_interface, text_to_speech_openai, add_token_usage


def show_belfer(language_in, language_out):
    """Wyświetla interfejs sprawdzania gramatyki i pisowni"""
    st.header("Sprawdzanie budowy zdań z poprawkami i tłumaczeniem")

    # Używamy globalnych ustawień języków z sidebar
    # Interfejs nagrywania - używamy wspólnej funkcji
    recognized_text = show_recording_interface(language_in, "belfer_")
    
    # Pole tekstowe do wpisania wiadomości
    verified_text = st.text_area("Wpisz tekst do weryfikacji w obsługiwanym języku lub nagraj:", 
                                value=recognized_text)
    
    if st.button("Zweryfikuj"):
        if verified_text is None or (hasattr(verified_text, "strip") and not verified_text.strip()):
            st.warning("Proszę wpisać tekst do weryfikacji.")
            
        else:
            # Wywołanie OpenAI do tłumaczenia
            prompt = f"Sprawdź poprawność użytych wyrazów, budowę zdania i gramatykę w języku {language_in} następujący tekst:\n{verified_text}. Zaproponuj zmiany i poprawki wraz z wyjaśnieniami. Na koniec podaj tłumaczenie na {language_out} "
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"Jesteś nauczycielem języka w języku {language_in}. Jasno i zwięźle wyjaśniasz zagadnienia językowe związane z wpisanym tekstem i wyjaśniasz błędy. Jeśli tekst jest w innym języku niż {supported_languages}, odpowiedz 'Język podanego tekstu (tu podaj język jaki wykryłeś)nie jest obsługiwany.' "},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.1,
                )
                content = response.choices[0].message.content
                verification = content.strip() if content is not None else ""
                st.subheader(f"Weryfikacja i wyjaśnienie:")
                st.write(verification)
                
                # Zapisz wyjaśnienie w session_state do odtwarzania
                st.session_state["belfer_last_verification"] = verification

                # Trackuj i wyświetl użycie tokenów
                if response.usage:
                    add_token_usage("belfer", response.usage.prompt_tokens, response.usage.completion_tokens)
                    st.caption(f"📊 Użyto {response.usage.prompt_tokens} + {response.usage.completion_tokens} = {response.usage.total_tokens} tokenów")   

            except Exception as e:
                st.error(f"Wystąpił błąd podczas tłumaczenia: {e}")
    
    # # Przycisk odtwarzania wyjaśnienia
    # if st.button("Odtwórz wyjaśnienie"):
    #     if st.session_state.get("belfer_last_verification"):
    #         try:
    #             audio_bytes = text_to_speech_openai(st.session_state["belfer_last_verification"], language_out)
    #             st.audio(audio_bytes, format="audio/mp3")
    #         except Exception as e:
    #             st.error(f"Błąd podczas generowania mowy: {e}")
    #     else:
    #         st.warning("Brak wyjaśnienia do odtworzenia. Najpierw zweryfikuj tekst.")
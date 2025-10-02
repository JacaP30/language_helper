"""
Moduł Dialog - prawdziwe rozmowy z AI z ciągłą historią
"""
import streamlit as st
from utils.config import client, supported_languages, language_code_map, show_recording_interface, text_to_speech, add_token_usage


def show_dialog(language_in, language_out):
    """Wyświetla interfejs dialogu z AI z prawdziwą historią konwersacji"""
    st.header("Rozmowa z AI")

    # AI odpowiada w language_out (język docelowy nauki)
    # Użytkownik może pisać w language_in lub language_out
    
    # Informacje o używaniu
    with st.expander("ℹ️ Instrukcja jak używać modułu Dialog"):
        st.markdown(f"""
        **Ten moduł to prawdziwy czat z AI w języku - {language_in}:**
        
        **🎭 Scenariusze rozmowy:**
        - **"Swobodna rozmowa"** - naturalny dialog na dowolne tematy
        - **"Jak powiedzieć"** ⭐ - zadawaj pytania typu "Jak powiedzieć X?" i otrzymuj odpowiedzi z przykładami użycia
        - **Sytuacyjne** - restauracja, lotnisko, sklep, praca, lekarz, droga, hotel
        
        **🔧 Funkcje:**
        - 🗣️ **Nagrywaj lub pisz** - używaj mikrofonu lub klawiatury
        - 💬 **Ciągła rozmowa** - AI pamięta całą konwersację  
        - 🔊 **Odtwarzanie** - kliknij 🔊 przy każdej odpowiedzi AI (w języku {language_in})
        - 🌍 **Tłumaczenie** - kliknij 🌍 aby przetłumaczyć odpowiedź na język {language_out}
        - 🔄 **Reset** - użyj "Nowa rozmowa" aby zacząć od nowa
        
        **💡 Przykłady dla scenariusza "Jak powiedzieć":**
        - "Jak powiedzieć 'miło Cię poznać'?"
        - "Jak zapytać o godzinę?"
        - "Jak się przedstawić w pracy?"
        - "Jak poprosić o rachunek w restauracji?"
        
        **🌍 Języki:** AI rozmawia w języku {language_in}, możesz mieszać języki - AI zrozumie
        """)

    col1, col2 = st.columns([3, 1])
    with col1:
        scenario = st.selectbox(
            "Wybierz scenariusz rozmowy:", 
            [
                "Swobodna rozmowa",
                "Jak powiedzieć",
                "W restauracji - zamówienie",
                "Na lotnisku - odprawa", 
                "W sklepie - zakupy",
                "Rozmowa kwalifikacyjna",
                "U lekarza - wizyta",
                "Pytanie o drogę",
                "W hotelu - recepcja",
                "W pracy - spotkanie",
                "W domu - codzienne czynności",
                "W szkole - lekcja",
            ], 
            key="dialog_scenario"
        )
    
    with col2:
        if st.button("🔄 Nowa rozmowa", help="Czyści historię i zaczyna od nowa"):
            st.session_state.pop("dialog_messages", None)
            st.session_state.pop("dialog_context_set", None)
            st.rerun()

    # Inicjalizacja historii wiadomości (format OpenAI)
    if "dialog_messages" not in st.session_state:
        st.session_state.dialog_messages = []
    
    # Ustawienie kontekstu przy pierwszej rozmowie
    if "dialog_context_set" not in st.session_state:
        st.session_state.dialog_context_set = False

    # Wyświetl historię rozmowy w stylu czatu
    if st.session_state.dialog_messages:
        st.subheader("💬 Historia rozmowy:")
        for i, message in enumerate(st.session_state.dialog_messages[1:], 1):  # Pomijamy system message
            if message["role"] == "user":
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**🙋 Ty:** {message['content']}")
                    with col2:
                        pass  # Miejsce na ewentualne przyciski dla wiadomości użytkownika
            
            elif message["role"] == "assistant":
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**🤖 AI:** {message['content']}")
                        
                        # Wyświetl tłumaczenie jeśli istnieje
                        translation_key = f"translation_{i}"
                        if translation_key in st.session_state:
                            st.markdown(f"*🌍 Tłumaczenie na {language_out}:* {st.session_state[translation_key]}")
                    
                    with col2:
                        # Przyciski odtwarzania i tłumaczenia
                        if st.button("🔊", key=f"tts_{i}", help="Odtwórz tę odpowiedź"):
                            try:
                                audio_bytes = text_to_speech(message['content'], language_in)
                                st.audio(audio_bytes, format="audio/mp3")
                            except Exception as e:
                                st.error(f"Błąd TTS: {e}")
                        
                        if st.button("🌍", key=f"translate_{i}", help=f"Przetłumacz na {language_out}"):
                            try:
                                with st.spinner("Tłumaczę..."):
                                    translation_prompt = f"Przetłumacz następujący tekst z języka {language_in} na język {language_out}. Zachowaj naturalny ton i znaczenie:\n\n{message['content']}"
                                    
                                    response = client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        messages=[
                                            {"role": "system", "content": f"Jesteś profesjonalnym tłumaczem. Tłumacz tekst z {language_in} na {language_out} zachowując naturalny ton i kontekst rozmowy."},
                                            {"role": "user", "content": translation_prompt}
                                        ],
                                        max_tokens=300,
                                        temperature=0.3,
                                    )
                                    
                                    # Trackuj użycie tokenów dla tłumaczenia
                                    if response.usage:
                                        add_token_usage("dialog", response.usage.prompt_tokens, response.usage.completion_tokens)
                                    
                                    translation = response.choices[0].message.content
                                    translation = translation.strip() if translation else "Błąd tłumaczenia"
                                    
                                    # Zapisz tłumaczenie w session_state
                                    st.session_state[f"translation_{i}"] = translation
                                    st.rerun()
                                    
                            except Exception as e:
                                st.error(f"Błąd tłumaczenia: {e}")

    #st.divider()

    # Sekcja wprowadzania nowej wiadomości
    # st.subheader("✍️ Napisz wiadomość:")
    
    # Interfejs nagrywania
    recognized_text = show_recording_interface(language_in, "dialog_")
    
    # Input dla nowej wiadomości
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_message = st.text_area(
            f"Napisz w języku {language_in} lub {language_out}:",
            value=recognized_text,
            key="dialog_input_area",
            height=100,
            # placeholder=f"Przykład: Cześć! / Hello! / Hola!"
        )
    
    with col2:
        st.write("")  # Padding
        st.write("")  # Padding
        send_message = st.button("📤 Wyślij", type="primary", use_container_width=True)

    # Logika wysyłania wiadomości
    if send_message and user_message and user_message.strip():
        # Dodaj kontekst systemowy przy pierwszej wiadomości
        if not st.session_state.dialog_context_set:
            system_message = {
                "role": "system", 
                "content": f"""Jesteś native speakerem języka {language_in}. Prowadzisz naturalną rozmowę w scenariuszu: "{scenario}".

ZASADY:
- Odpowiadaj ZAWSZE w języku {language_in}
- Użytkownik może pisać w języku {language_in} lub {language_out} - rozumiesz oba
- Jeśli użytkownik popełni błąd językowy, delikatnie go popraw w naturalny sposób
- Dostosuj rozmowę do wybranego scenariusza
- Bądź pomocny, cierpliwy i zachęcający do nauki
- Używaj naturalnego, codziennego języka
- Jeśli scenariusz to "Swobodna rozmowa", rozmawiaj na dowolne tematy
- Jeśli scenariusz to "Jak powiedzieć", pomagaj użytkownikowi znaleźć odpowiednie zwroty i wyrażenia w języku {language_in} do różnych sytuacji"""
            }
            st.session_state.dialog_messages = [system_message]
            st.session_state.dialog_context_set = True

        # Dodaj wiadomość użytkownika
        st.session_state.dialog_messages.append({
            "role": "user",
            "content": user_message.strip()
        })

        # Generuj odpowiedź AI z pełnym kontekstem
        try:
            with st.spinner("AI myśli..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[  # type: ignore
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in st.session_state.dialog_messages
                    ],
                    max_tokens=300,
                    temperature=0.8,
                )
                
                # Trackuj użycie tokenów
                if response.usage:
                    add_token_usage("dialog", response.usage.prompt_tokens, response.usage.completion_tokens)
                
                ai_response = response.choices[0].message.content
                ai_response = ai_response.strip() if ai_response else "Przepraszam, nie mogę odpowiedzieć."
                
                # Dodaj odpowiedź AI do historii
                st.session_state.dialog_messages.append({
                    "role": "assistant", 
                    "content": ai_response
                })
                
                st.rerun()  # Odśwież interfejs
                
        except Exception as e:
            st.error(f"Błąd podczas generowania odpowiedzi: {e}")
    
    elif send_message and (not user_message or not user_message.strip()):
        st.warning("Proszę napisać wiadomość przed wysłaniem.")


        
    # Statystyki rozmowy
    if st.session_state.dialog_messages:
        user_messages = len([m for m in st.session_state.dialog_messages if m["role"] == "user"])
        ai_messages = len([m for m in st.session_state.dialog_messages if m["role"] == "assistant"])
        st.caption(f"📊 Długość dialogu: {user_messages} twoich wiadomości, {ai_messages} odpowiedzi AI")
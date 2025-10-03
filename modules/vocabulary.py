"""
Moduł do nauki słówek - fiszki, testy i zarządzanie słownictwem
"""
import streamlit as st
import json
import os
import random
from datetime import datetime, timedelta
from utils.config import client, add_token_usage, text_to_speech, language_code_map
from ai_handlers import get_ai_handler

# Plik z bazą słówek
VOCABULARY_FILE = "BASE/vocabulary_database.json"

# Gotowe zestawy słówek dla różnych języków
PREDEFINED_WORD_SETS = {
    "angielski": {
        "Podstawowe czasowniki": [
            "be", "have", "do", "say", "get", "make", "go", "know", "take", "see",
            "come", "think", "look", "want", "give", "use", "find", "tell", "ask", "work",
            "seem", "feel", "try", "leave", "call"
        ],
        "Podstawowe rzeczowniki": [
            "time", "person", "year", "way", "day", "thing", "man", "world", "life", "hand",
            "part", "child", "eye", "woman", "place", "work", "week", "case", "point", "government",
            "company", "number", "group", "problem", "fact"
        ],
        "Dom i rodzina": [
            "house", "home", "family", "mother", "father", "sister", "brother", "child", "baby", "parent",
            "kitchen", "bedroom", "bathroom", "living room", "table", "chair", "bed", "door", "window", "garden"
        ],
        "Jedzenie": [
            "food", "eat", "drink", "water", "bread", "meat", "fish", "chicken", "vegetable", "fruit",
            "apple", "banana", "orange", "milk", "coffee", "tea", "sugar", "salt", "lunch", "dinner"
        ],
        "Kolory i liczby": [
            "red", "blue", "green", "yellow", "black", "white", "brown", "pink", "orange", "purple",
            "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"
        ]
    },
    "niemiecki": {
        "Podstawowe czasowniki": [
            "sein", "haben", "werden", "können", "müssen", "sagen", "machen", "geben", "kommen", "sollen",
            "wollen", "gehen", "wissen", "sehen", "lassen", "stehen", "finden", "bleiben", "liegen", "heißen",
            "denken", "nehmen", "tun", "dürfen", "glauben"
        ],
        "Podstawowe rzeczowniki": [
            "Jahr", "Zeit", "Mensch", "Tag", "Hand", "Frau", "Teil", "Kind", "Auge", "Leben",
            "Welt", "Haus", "Fall", "Land", "Ende", "Arbeit", "Seite", "Platz", "Gruppe", "Problem",
            "Frage", "Recht", "Staat", "Krieg", "Geld"
        ],
        "Dom i rodzina": [
            "Haus", "Familie", "Mutter", "Vater", "Schwester", "Bruder", "Kind", "Baby", "Eltern", "Großmutter",
            "Küche", "Schlafzimmer", "Badezimmer", "Wohnzimmer", "Tisch", "Stuhl", "Bett", "Tür", "Fenster", "Garten"
        ],
        "Jedzenie": [
            "Essen", "trinken", "Wasser", "Brot", "Fleisch", "Fisch", "Huhn", "Gemüse", "Obst",
            "Apfel", "Banane", "Orange", "Milch", "Kaffee", "Tee", "Zucker", "Salz", "Mittagessen", "Abendessen"
        ],
        "Kolory i liczby": [
            "rot", "blau", "grün", "gelb", "schwarz", "weiß", "braun", "rosa", "orange", "lila",
            "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn"
        ]
    },
    "francuski": {
        "Podstawowe czasowniki": [
            "être", "avoir", "faire", "dire", "aller", "voir", "savoir", "prendre", "venir", "vouloir",
            "pouvoir", "falloir", "devoir", "croire", "trouver", "donner", "parler", "aimer", "porter", "laisser",
            "entendre", "demander", "rester", "passer", "regarder"
        ],
        "Podstawowe rzeczowniki": [
            "temps", "personne", "année", "jour", "main", "femme", "partie", "enfant", "œil", "vie",
            "monde", "maison", "cas", "pays", "fin", "travail", "côté", "place", "groupe", "problème",
            "question", "droit", "état", "guerre", "argent"
        ],
        "Dom i rodzina": [
            "maison", "famille", "mère", "père", "sœur", "frère", "enfant", "bébé", "parents", "grand-mère",
            "cuisine", "chambre", "salle de bain", "salon", "table", "chaise", "lit", "porte", "fenêtre", "jardin"
        ],
        "Jedzenie": [
            "nourriture", "manger", "boire", "eau", "pain", "viande", "poisson", "poulet", "légume", "fruit",
            "pomme", "banane", "orange", "lait", "café", "thé", "sucre", "sel", "déjeuner", "dîner"
        ],
        "Kolory i liczby": [
            "rouge", "bleu", "vert", "jaune", "noir", "blanc", "marron", "rose", "orange", "violet",
            "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix"
        ]
    },
    "hiszpański": {
        "Podstawowe czasowniki": [
            "ser", "estar", "tener", "hacer", "poder", "decir", "ir", "ver", "dar", "saber",
            "querer", "llegar", "pasar", "deber", "poner", "parecer", "quedar", "creer", "hablar", "llevar",
            "dejar", "seguir", "encontrar", "llamar", "venir"
        ],
        "Podstawowe rzeczowniki": [
            "tiempo", "persona", "año", "día", "mano", "mujer", "parte", "niño", "ojo", "vida",
            "mundo", "casa", "caso", "país", "fin", "trabajo", "lado", "lugar", "grupo", "problema",
            "pregunta", "derecho", "estado", "guerra", "dinero"
        ],
        "Dom i rodzina": [
            "casa", "familia", "madre", "padre", "hermana", "hermano", "niño", "bebé", "padres", "abuela",
            "cocina", "dormitorio", "baño", "sala", "mesa", "silla", "cama", "puerta", "ventana", "jardín"
        ],
        "Jedzenie": [
            "comida", "comer", "beber", "agua", "pan", "carne", "pescado", "pollo", "verdura", "fruta",
            "manzana", "plátano", "naranja", "leche", "café", "té", "azúcar", "sal", "almuerzo", "cena"
        ],
        "Kolory i liczby": [
            "rojo", "azul", "verde", "amarillo", "negro", "blanco", "marrón", "rosa", "naranja", "morado",
            "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"
        ]
    },
    "włoski": {
        "Podstawowe czasowniki": [
            "essere", "avere", "fare", "dire", "andare", "potere", "dovere", "volere", "sapere", "dare",
            "stare", "vedere", "uscire", "parlare", "arrivare", "portare", "mettere", "diventare", "partire", "tornare",
            "rimanere", "venire", "bere", "vivere", "morire"
        ],
        "Podstawowe rzeczowniki": [
            "tempo", "persona", "anno", "giorno", "mano", "donna", "parte", "bambino", "occhio", "vita",
            "mondo", "casa", "caso", "paese", "fine", "lavoro", "lato", "posto", "gruppo", "problema",
            "domanda", "diritto", "stato", "guerra", "soldi"
        ],
        "Dom i rodzina": [
            "casa", "famiglia", "madre", "padre", "sorella", "fratello", "bambino", "bambina", "genitori", "nonna",
            "cucina", "camera", "bagno", "salotto", "tavolo", "sedia", "letto", "porta", "finestra", "giardino"
        ],
        "Jedzenie": [
            "cibo", "mangiare", "bere", "acqua", "pane", "carne", "pesce", "pollo", "verdura", "frutta",
            "mela", "banana", "arancia", "latte", "caffè", "tè", "zucchero", "sale", "pranzo", "cena"
        ],
        "Kolory i liczby": [
            "rosso", "blu", "verde", "giallo", "nero", "bianco", "marrone", "rosa", "arancione", "viola",
            "uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove", "dieci"
        ]
    }
}

def initialize_language_pairs(db):
    """Inicjalizuje pary językowe z polskim (dla Polaków)"""
    from utils.config import supported_languages
    
    # Utwórz tylko pary z polskim jako jednym z języków
    for lang in supported_languages:
        if lang != "polski":
            # Polski → inne języki (nauka języków obcych)
            pair_key_out = f"polski_{lang}"
            if pair_key_out not in db["words"]:
                db["words"][pair_key_out] = []
            
            # Inne języki → polski (tłumaczenie na polski)
            pair_key_in = f"{lang}_polski"
            if pair_key_in not in db["words"]:
                db["words"][pair_key_in] = []
    
    return db

def load_vocabulary_database():
    """Ładuje bazę słówek z pliku JSON"""
    if os.path.exists(VOCABULARY_FILE):
        try:
            with open(VOCABULARY_FILE, 'r', encoding='utf-8') as f:
                db = json.load(f)
                # Inicjalizuj brakujące pary językowe
                db = initialize_language_pairs(db)
                return db
        except json.JSONDecodeError:
            st.error("Błąd odczytu bazy słówek. Tworzę nową bazę.")
    
    # Domyślna struktura bazy
    db = {
        "created_date": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "words": {},  # słownik: język_para -> lista słówek
        "statistics": {
            "words_added": 0,
            "tests_completed": 0,
            "correct_answers": 0,
            "total_answers": 0
        }
    }
    
    # Inicjalizuj wszystkie pary językowe
    db = initialize_language_pairs(db)
    return db

def save_vocabulary_database(db):
    """Zapisuje bazę słówek do pliku JSON"""
    db["last_updated"] = datetime.now().isoformat()
    with open(VOCABULARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_language_pair_key(lang_in, lang_out):
    """Tworzy klucz dla pary języków z walidacją"""
    from utils.config import supported_languages
    
    # Waliduj czy języki są obsługiwane
    if lang_in not in supported_languages:
        st.error(f"❌ Nieobsługiwany język źródłowy: {lang_in}")
        st.info(f"💡 Obsługiwane języki: {', '.join(supported_languages)}")
        return None
        
    if lang_out not in supported_languages:
        st.error(f"❌ Nieobsługiwany język docelowy: {lang_out}")  
        st.info(f"💡 Obsługiwane języki: {', '.join(supported_languages)}")
        return None
    
    return f"{lang_in}_{lang_out}"

def generate_word_conjugation(word, part_of_speech, language, polish_translation=""):
    """Generuje odmiany słówka używając specjalizowanych handlerów AI"""
    try:
        # Użyj specjalizowanego handlera AI dla danego języka
        ai_handler = get_ai_handler(language)
        return ai_handler.generate_word_conjugation(word, part_of_speech, polish_translation)
        
    except Exception as e:
        st.error(f"❌ Błąd generowania odmian: {str(e)}")
        return None

def generate_word_with_ai(word, lang_in, lang_out):
    """Generuje tłumaczenie i przykłady używając specjalizowanych handlerów AI"""
    try:
        # Użyj specjalizowanego handlera AI dla języka źródłowego
        ai_handler = get_ai_handler(lang_in)
        result = ai_handler.generate_word_translation(word, lang_in, lang_out)
        
        if result:
            # Dodaj oryginalne słowo do wyniku
            result["original"] = word
            
            # Sprawdź czy wynik ma wymagane pola
            required_fields = ["translation"]
            for field in required_fields:
                if field not in result:
                    st.error(f"❌ Brakuje pola '{field}' w odpowiedzi AI")
                    return None
                    
        return result
        
    except Exception as e:
        error_msg = f"❌ Błąd generowania słówka '{word}': {str(e)}"
        st.error(error_msg)
        
        # Wyświetl też w console dla debugowania
        print(f"ERROR in generate_word_with_ai: {error_msg}")
        
        # Pokaż szczegóły błędu w expander
        with st.expander("🔍 Szczegóły błędu (dla debugowania)"):
            st.code(str(e))
            
        return None

def add_word_to_database(word_data, lang_pair):
    """Dodaje słówko do bazy danych"""
    db = load_vocabulary_database()
    
    if lang_pair not in db["words"]:
        db["words"][lang_pair] = []
    
    # Dodaj metadata
    word_entry = {
        **word_data,
        "id": len(db["words"][lang_pair]) + 1,
        "added_date": datetime.now().isoformat(),
        "review_count": 0,
        "correct_count": 0,
        "last_reviewed": None,
        "next_review": datetime.now().isoformat(),  # od razu dostępne
        "mastery_level": 0  # 0-5, gdzie 5 = opanowane
    }
    
    db["words"][lang_pair].append(word_entry)
    db["statistics"]["words_added"] += 1
    
    save_vocabulary_database(db)
    return word_entry

def get_words_for_review(lang_pair, limit=10):
    """Pobiera słówka gotowe do powtórki"""
    db = load_vocabulary_database()
    
    if lang_pair not in db["words"]:
        return []
    
    now = datetime.now()
    words_ready = []
    
    for word in db["words"][lang_pair]:
        next_review = datetime.fromisoformat(word["next_review"])
        if next_review <= now:
            words_ready.append(word)
    
    # Sortuj według priorytetu (najdłużej nie powtarzane)
    words_ready.sort(key=lambda x: x["last_reviewed"] or "1900-01-01")
    
    return words_ready[:limit]

def update_word_performance(word_id, lang_pair, correct):
    """Aktualizuje statystyki słówka po odpowiedzi"""
    db = load_vocabulary_database()
    
    if lang_pair in db["words"]:
        for word in db["words"][lang_pair]:
            if word["id"] == word_id:
                word["review_count"] += 1
                word["last_reviewed"] = datetime.now().isoformat()
                
                if correct:
                    word["correct_count"] += 1
                    word["mastery_level"] = min(5, word["mastery_level"] + 1)
                    # Wydłuż interwał powtórki
                    days_delay = [1, 2, 5, 10, 20, 40][word["mastery_level"]]
                else:
                    word["mastery_level"] = max(0, word["mastery_level"] - 1)
                    # Skróć interwał
                    days_delay = 1
                
                # Ustaw następną powtórkę
                next_review = datetime.now() + timedelta(days=days_delay)
                word["next_review"] = next_review.isoformat()
                
                break
    
    save_vocabulary_database(db)

def quick_add_from_set(selected_words, lang_in, lang_out, lang_pair):
    """Szybko dodaje wybrane słówka z gotowego zestawu do bazy danych"""
    added_count = 0
    
    for word in selected_words:
        # Sprawdź czy słówko już istnieje
        db = load_vocabulary_database()
        if lang_pair in db["words"]:
            existing_words = [w["original"].lower() for w in db["words"][lang_pair]]
            if word.lower() in existing_words:
                continue
        
        # Wygeneruj dane słówka z AI
        with st.spinner(f"Generuję dane dla '{word}'..."):
            word_data = generate_word_with_ai(word, lang_in, lang_out)
            
            if word_data:
                add_word_to_database(word_data, lang_pair)
                added_count += 1
    
    return added_count

def get_words_for_learning(lang_pair, difficulty_filter=None, limit=20):
    """Pobiera słówka z bazy do nauki z filtrowaniem"""
    db = load_vocabulary_database()
    
    if lang_pair not in db["words"]:
        return []
    
    words = db["words"][lang_pair]
    
    # Filtruj według poziomu trudności jeśli podano
    if difficulty_filter and difficulty_filter != "wszystkie":
        words = [w for w in words if w.get("difficulty", "basic") == difficulty_filter]
    
    # Sortuj według poziomu opanowania (słabsze pierwsze) i daty dodania
    words.sort(key=lambda x: (x["mastery_level"], x["added_date"]))
    
    return words[:limit]

def conduct_learning_session(words, lang_pair, language_in, language_out):
    """Prowadzi sesję nauki słówek"""
    if "learning_session" not in st.session_state:
        st.session_state.learning_session = {
            "words": words.copy(),
            "current_index": 0,
            "correct_answers": 0,
            "show_translation": False,
            "show_examples": False,
            "show_conjugation": False,
            "user_answer": ""
        }
    
    session = st.session_state.learning_session
    
    if session["current_index"] < len(session["words"]):
        current_word = session["words"][session["current_index"]]
        
        # Progress bar
        progress = session["current_index"] / len(session["words"])
        st.progress(progress)
        
        st.write(f"**Słówko {session['current_index'] + 1}/{len(session['words'])}**")
        
        # Wyświetl słówko do nauki
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### 🔤 {current_word['original']}")
            
            # Informacje dodatkowe
            if current_word.get("part_of_speech"):
                st.caption(f"Część mowy: {current_word['part_of_speech']}")
            if current_word.get("difficulty"):
                st.caption(f"Poziom: {current_word['difficulty']}")
        
        with col2:
            if st.button("🔊 Wymów", key="pronounce"):
                try:
                    # Debug info
                    st.info(f"Wymawiam '{current_word['original']}' w języku: {language_in}")
                    audio_bytes = text_to_speech(current_word["original"], language_in)
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.error(f"❌ Błąd wymowy: {str(e)}")
                    st.info("💡 Sprawdź konfigurację OpenAI API lub połączenie internetowe")
        
        # Pole na odpowiedź użytkownika
        user_answer = st.text_input(
            f"Jak to się tłumaczy na {language_out}?",
            key="answer_input",
            placeholder="Wpisz tłumaczenie..."
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👁️ Pokaż tłumaczenie", key="show_trans"):
                session["show_translation"] = True
        
        with col2:
            if st.button("📝 Pokaż przykłady", key="show_ex"):
                session["show_examples"] = True
        
        with col3:
            if st.button("🔄 Odmiana", key="show_conjugation"):
                session["show_conjugation"] = True
        
        with col4:
            if st.button("⏭️ Pomiń słówko", key="skip"):
                session["current_index"] += 1
                session["show_translation"] = False
                session["show_examples"] = False
                session["show_conjugation"] = False
                st.rerun()
        
        # Pokaż tłumaczenie jeśli odkryte
        if session["show_translation"]:
            st.markdown(f"### ✅ {current_word['translation']}")
            
            if current_word.get("alternatives"):
                st.write(f"**Alternatywne tłumaczenia:** {', '.join(current_word['alternatives'])}")
            
            if current_word.get("pronunciation_tip"):
                st.info(f"💡 **Wymowa:** {current_word['pronunciation_tip']}")
            
            # Sprawdź odpowiedź użytkownika
            if user_answer.strip():
                correct_answers = [current_word['translation'].lower()]
                if current_word.get("alternatives"):
                    correct_answers.extend([alt.lower() for alt in current_word["alternatives"]])
                
                user_answer_lower = user_answer.lower().strip()
                is_correct = any(user_answer_lower in correct.lower() or correct.lower() in user_answer_lower 
                               for correct in correct_answers)
                
                if is_correct:
                    st.success("🎉 Świetna odpowiedź!")
                else:
                    st.warning("🤔 Spróbuj jeszcze raz lub sprawdź prawidłowe tłumaczenie")
            
            # Przyciski oceny zrozumienia
            st.write("**Jak dobrze znałeś to słówko?**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("😰 Wcale", key="not_known"):
                    update_word_performance(current_word["id"], lang_pair, False)
                    session["current_index"] += 1
                    session["show_translation"] = False
                    session["show_examples"] = False
                    session["show_conjugation"] = False
                    st.rerun()
            
            with col2:
                if st.button("🤔 Częściowo", key="partially"):
                    update_word_performance(current_word["id"], lang_pair, True)
                    session["current_index"] += 1
                    session["show_translation"] = False
                    session["show_examples"] = False
                    session["show_conjugation"] = False
                    st.rerun()
            
            with col3:
                if st.button("😊 Dobrze", key="well_known"):
                    update_word_performance(current_word["id"], lang_pair, True)
                    session["correct_answers"] += 1
                    session["current_index"] += 1
                    session["show_translation"] = False
                    session["show_examples"] = False
                    session["show_conjugation"] = False
                    st.rerun()
        
        # Pokaż przykłady jeśli odkryte
        if session["show_examples"] and current_word.get("examples"):
            st.write("**Przykłady użycia:**")
            for i, example in enumerate(current_word["examples"]):
                with st.expander(f"Przykład {i+1}", expanded=True):
                    st.write(f"**{current_word['original']}:** {example['original']}")
                    st.write(f"**Tłumaczenie:** {example['translated']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"🔊 Oryginał", key=f"ex_orig_{i}"):
                            try:
                                audio_bytes = text_to_speech(example["original"], language_in)
                                st.audio(audio_bytes, format="audio/mp3")
                            except Exception as e:
                                st.error(f"❌ Błąd wymowy: {str(e)}")
                    with col2:
                        if st.button(f"🔊 Tłumaczenie", key=f"ex_trans_{i}"):
                            try:
                                audio_bytes = text_to_speech(example["translated"], language_out)
                                st.audio(audio_bytes, format="audio/mp3")
                            except Exception as e:
                                st.error(f"❌ Błąd wymowy: {str(e)}")
        
        # Pokaż odmiany jeśli odkryte
        if session.get("show_conjugation", False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("**Odmiana słowa:**")
            with col2:
                if st.button("🔄 Regeneruj", key="regenerate_conjugation", help="Wygeneruj odmiany ponownie"):
                    conjugation_key = f"conjugation_{session['current_index']}_{language_in}"
                    if conjugation_key in st.session_state:
                        del st.session_state[conjugation_key]
                    st.rerun()
            
            # Sprawdź czy odmiana już została wygenerowana (uwzględnij język w kluczu)
            conjugation_key = f"conjugation_{session['current_index']}_{language_in}"
            if conjugation_key not in st.session_state:
                with st.spinner("Generuję odmiany słowa..."):
                    conjugation_data = generate_word_conjugation(
                        current_word["original"],
                        current_word.get("part_of_speech", ""),
                        language_in,
                        current_word.get("translation", "")
                    )
                    st.session_state[conjugation_key] = conjugation_data
            
            conjugation_data = st.session_state.get(conjugation_key)
            
            if conjugation_data and conjugation_data.get("conjugations"):
                for conj in conjugation_data["conjugations"]:
                    with st.expander(f"📚 {conj['form']}", expanded=True):
                        for example in conj.get("examples", []):
                            st.write(f"• {example}")
            else:
                st.warning("❌ Nie udało się wygenerować odmian dla tego słowa.")
                st.info(f"🔍 Słowo: '{current_word['original']}', część mowy: '{current_word.get('part_of_speech', 'brak')}'")
        
        
        # Przycisk do zakończenia sesji na dole
        #st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("❌ Zakończ sesję", key="end_session", 
                       type="secondary",
                       use_container_width=True,
                       help="Zakończy bieżącą sesję nauki"):
                del st.session_state.learning_session
                st.rerun()
    
    else:
        # Koniec sesji nauki
        st.success("🎉 Gratulacje! Ukończyłeś sesję nauki!")
        
        total_words = len(session["words"])
        correct_count = session["correct_answers"]
        percentage = (correct_count / total_words * 100) if total_words > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Słówek", total_words)
        with col2:
            st.metric("✅ Dobrze znanych", correct_count)
        with col3:
            st.metric("🎯 Wynik", f"{percentage:.0f}%")
        
        if percentage >= 80:
            st.balloons()
            st.success("🏆 Świetny wynik! Kontynuuj naukę!")
        elif percentage >= 60:
            st.info("👍 Dobry wynik! Jeszcze trochę praktyki!")
        else:
            st.warning("💪 Potrzebujesz więcej praktyki. Nie poddawaj się!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nowa sesja"):
                del st.session_state.learning_session
                st.rerun()
        with col2:
            if st.button("📊 Zobacz statystyki"):
                # Przełącz na tab statystyk - można to zaimplementować później
                st.info("Przejdź do zakładki 'Statystyki' aby zobaczyć szczegóły")

def show_vocabulary(language_in, language_out):
    """Główna funkcja modułu nauki słówek"""
    st.header("📚 Nauka słówek")
    
    # Instrukcja obsługi w expanderze
    with st.expander("ℹ️ Instrukcja obsługi modułu nauki słówek"):
        st.markdown("""
        ### 🎓 Jak korzystać z modułu nauki słówek:
        **🗣️ Wybierz język:**
        - **Język źródłowy:** Język, którego się uczysz
        - **Język docelowy:** Język, na który tłumaczysz (zazwyczaj polski)
                    
        **📋 Zakładki:**
        - **🎓 Nauka słówek** - Uczenie się słówek z Twojej bazy z inteligentnym systemem powtórek
        - **🎯 Wybierz słówko** - Dodawanie słówek z gotowych zestawów tematycznych
        - **➕ Dodaj słówko** - Ręczne dodawanie pojedynczych słówek lub całych list
        - **🔄 Powtórka** - Powtarzanie słówek, które wymagają utrwalenia
        - **🎯 Test** - Sprawdzenie wiedzy w formie quizu
        - **📊 Statystyki** - Przegląd postępów i statystyk nauki
        
        **💡 Wskazówki:**
        1. **Zacznij od zakładki 'Wybierz słówko'** - wybierz gotowe zestawy słówek z różnych tematów
        2. **Lub użyj 'Dodaj słówko'** - wpisz własne słówka lub całe listy
        3. **Przejdź do 'Nauka słówek'** - system będzie pokazywać Ci słówka do nauki
        4. **Używaj 'Powtórka'** - regularnie powtarzaj trudniejsze słówka
        5. **Testuj się** - sprawdzaj postępy w zakładce 'Test'
        
        **🎯 System nauki:**
        - Słówka są pokazywane według inteligentnego algorytmu
        - Trudniejsze słówka pojawiają się częściej
        - System pamięta Twoje odpowiedzi i dostosowuje trudność
        - Możesz filtrować według poziomu (podstawowy/średni/zaawansowany)
        """)
    
    # Sprawdź czy języki są obsługiwane
    lang_pair = get_language_pair_key(language_in, language_out)
    if lang_pair is None:
        st.stop()  # Zatrzymaj wykonywanie jeśli języki nieobsługiwane
    
    # Sprawdź czy zmienił się język i wyczyść cache odmian
    current_language_pair = f"{language_in}_{language_out}"
    if "current_language_pair" not in st.session_state:
        st.session_state.current_language_pair = current_language_pair
    elif st.session_state.current_language_pair != current_language_pair:
        # Język się zmienił - wyczyść cache odmian
        keys_to_remove = [key for key in st.session_state.keys() if isinstance(key, str) and key.startswith("conjugation_")]
        for key in keys_to_remove:
            del st.session_state[key]
        
        # Wyczyść też cache wygenerowanych słów i sesji
        if "generated_word" in st.session_state:
            del st.session_state.generated_word
            
        # Wyczyść aktywne sesje nauki i powtórki (mogą zawierać słówka w niewłaściwym języku)
        if "learning_session" in st.session_state:
            del st.session_state.learning_session
        if "review_session" in st.session_state:
            del st.session_state.review_session
            
        # Zaktualizuj aktualną parę językową
        st.session_state.current_language_pair = current_language_pair
    
    # Tabs dla różnych funkcji
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎓 Nauka słówek", "🎯 Wybierz słówko", "➕ Dodaj słówko", 
        "🔄 Powtórka", "🎯 Test", "📊 Statystyki"
    ])
    
    # TAB 1: Nauka słówek z bazy
    with tab1:
        st.subheader("🎓 Nauka słówek z Twojej bazy")
        
        # Sprawdź czy są słówka w bazie
        db = load_vocabulary_database()
        
        if lang_pair not in db["words"] or not db["words"][lang_pair]:
            st.warning("📭 Nie masz jeszcze słówek w bazie dla tej pary językowej!")
            st.info("💡 Przejdź do zakładki 'Wybierz słówko' lub 'Dodaj słówko' aby dodać pierwsze słówka.")
            
            # Pokaż statystyki ogólne
            total_words = sum(len(words) for words in db["words"].values())
            if total_words > 0:
                st.write(f"**Masz łącznie {total_words} słówek w innych parach językowych.**")
                
                # Pokaż dostępne pary
                st.write("**Dostępne pary językowe:**")
                for pair, words in db["words"].items():
                    if words:  # tylko niepuste
                        lang_from, lang_to = pair.split("_")
                        st.write(f"• {lang_from} → {lang_to}: {len(words)} słówek")
        else:
            words_in_pair = db["words"][lang_pair]
            st.success(f"🎯 Masz {len(words_in_pair)} słówek w parze {language_in} → {language_out}")
            
            # Opcje filtrowania
            col1, col2 = st.columns(2)
            
            with col1:
                difficulty_filter = st.selectbox(
                    "Filtruj według poziomu:",
                    ["wszystkie", "basic", "intermediate", "advanced"],
                    help="Wybierz poziom trudności słówek do nauki"
                )
            
            with col2:
                session_length = st.selectbox(
                    "Długość sesji:",
                    [5, 10, 15, 20, 25],
                    index=1,  # domyślnie 10
                    help="Ile słówek chcesz przećwiczyć w tej sesji"
                )
            
            # Pobierz słówka do nauki
            words_to_learn = get_words_for_learning(lang_pair, difficulty_filter, session_length)
            
            if not words_to_learn:
                if difficulty_filter != "wszystkie":
                    st.warning(f"🔍 Brak słówek na poziomie '{difficulty_filter}' w Twojej bazie.")
                    st.info("Spróbuj wybrać 'wszystkie' poziomy lub dodaj więcej słówek.")
                else:
                    st.info("🎉 Wszystkie Twoje słówka są już dobrze opanowane!")
            else:
                # Pokaż podgląd słówek
                with st.expander(f"👀 Podgląd słówek do nauki ({len(words_to_learn)})"):
                    for word in words_to_learn[:5]:  # Pokaż pierwsze 5
                        mastery_stars = "⭐" * word["mastery_level"]
                        st.write(f"• **{word['original']}** → {word['translation']} {mastery_stars}")
                    
                    if len(words_to_learn) > 5:
                        st.write(f"... i {len(words_to_learn) - 5} więcej")
                
                # Statystyki przed sesją
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_mastery = sum(w["mastery_level"] for w in words_to_learn) / len(words_to_learn)
                    st.metric("📊 Średni poziom", f"{avg_mastery:.1f}/5")
                
                with col2:
                    never_reviewed = sum(1 for w in words_to_learn if w["review_count"] == 0)
                    st.metric("🆕 Nowych słówek", never_reviewed)
                
                with col3:
                    if difficulty_filter != "wszystkie":
                        level_count = len([w for w in words_in_pair if w.get("difficulty", "basic") == difficulty_filter])
                        st.metric(f"📚 Poziom {difficulty_filter}", level_count)
                    else:
                        st.metric("📚 Wszystkie", len(words_to_learn))
                
                # Przycisk rozpoczęcia sesji
                #st.markdown("---")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button(f"🚀 Rozpocznij sesję nauki ({len(words_to_learn)} słówek)", 
                               type="primary", 
                               use_container_width=True):
                        
                        # Wyczyść poprzednią sesję jeśli istnieje i utwórz nową
                        if "learning_session" in st.session_state:
                            del st.session_state.learning_session
                        
                        # Utwórz nową sesję nauki
                        st.session_state.learning_session = {
                            "words": words_to_learn.copy(),
                            "current_index": 0,
                            "correct_answers": 0,
                            "show_translation": False,
                            "show_examples": False,
                            "user_answer": ""
                        }
                        
                        st.rerun()
                
                # Jeśli sesja jest aktywna, prowadź ją
                if "learning_session" in st.session_state:
                    #st.markdown("---")
                    conduct_learning_session(words_to_learn, lang_pair, language_in, language_out)
    
    # TAB 2: Wybór z gotowych zestawów
    with tab2:
        st.subheader("🎯 Wybierz z gotowych zestawów")
        st.info("💡 Wybierz zestaw podstawowych słówek, które chcesz dodać do swojej bazy do nauki.")
        
        # Sprawdź czy język ma dostępne zestawy
        if language_in not in PREDEFINED_WORD_SETS:
            st.warning(f"❌ Brak gotowych zestawów dla języka: {language_in}")
            st.info("💡 Dostępne języki z zestawami: " + ", ".join(PREDEFINED_WORD_SETS.keys()))
            st.info("🔧 Użyj zakładki 'Dodaj słówko' aby dodać słówka ręcznie.")
            return
        
        # Wybór zestawu dla wybranego języka
        available_sets = list(PREDEFINED_WORD_SETS[language_in].keys())
        selected_set = st.selectbox(
            f"Wybierz zestaw słówek ({language_in}):",
            available_sets,
            help="Każdy zestaw zawiera starannie dobrane słówka dla danej kategorii"
        )
        
        if selected_set:
            words_in_set = PREDEFINED_WORD_SETS[language_in][selected_set]
            st.write(f"**Zestaw '{selected_set}' zawiera {len(words_in_set)} słówek ({language_in}):**")
            
            # Pokaż słówka w zestawie
            with st.expander(f"👀 Zobacz słówka z zestawu '{selected_set}'"):
                # Wyświetl w kolumnach dla lepszej czytelności
                cols = st.columns(5)
                for i, word in enumerate(words_in_set):
                    with cols[i % 5]:
                        st.write(f"• {word}")
            
            # Opcje dodawania
            col1, col2 = st.columns(2)
            
            with col1:
                add_mode = st.radio(
                    "Sposób dodawania:",
                    ["🔥 Dodaj wszystkie słówka", "✋ Wybierz konkretne słówka"],
                    help="Wszystkie: dodaje cały zestaw\nWybrane: możesz zaznaczyć konkretne słówka"
                )
            
            with col2:
                # Sprawdź ile słówek już jest w bazie
                db = load_vocabulary_database()
                existing_count = 0
                if lang_pair in db["words"]:
                    existing_words = [w["original"].lower() for w in db["words"][lang_pair]]
                    existing_count = sum(1 for word in words_in_set if word.lower() in existing_words)
                
                if existing_count > 0:
                    st.warning(f"⚠️ {existing_count} słówek już jest w bazie")
                else:
                    st.success("✅ Wszystkie słówka są nowe")
            
            # Wybór konkretnych słówek jeśli wybrano tryb selekcji
            selected_words = []
            if add_mode == "✋ Wybierz konkretne słówka":
                st.write("**Zaznacz słówka do dodania:**")
                
                # Sprawdź które są już w bazie
                existing_words = []
                if lang_pair in db["words"]:
                    existing_words = [w["original"].lower() for w in db["words"][lang_pair]]
                
                # Checkbox dla każdego słówka
                cols = st.columns(3)
                for i, word in enumerate(words_in_set):
                    with cols[i % 3]:
                        is_existing = word.lower() in existing_words
                        disabled = is_existing
                        
                        if st.checkbox(
                            f"{word}" + (" ✅" if is_existing else ""), 
                            key=f"word_{i}",
                            disabled=disabled,
                            help="To słówko już jest w bazie" if is_existing else None
                        ):
                            selected_words.append(word)
            else:
                # Dodaj wszystkie (pomijając te które już są)
                if lang_pair in db["words"]:
                    existing_words = [w["original"].lower() for w in db["words"][lang_pair]]
                    selected_words = [word for word in words_in_set if word.lower() not in existing_words]
                else:
                    selected_words = words_in_set.copy()
            
            # Przycisk dodawania
            if selected_words:
                st.write(f"**Do dodania: {len(selected_words)} słówek**")
                
                col1, col2, col3 = st.columns(3)
                
                with col2:
                    if st.button(f"🚀 Dodaj {len(selected_words)} słówek", type="primary", use_container_width=True):
                        try:
                            with st.spinner(f"Dodaję {len(selected_words)} słówek do bazy..."):
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                success_count = 0
                                error_count = 0
                                
                                for i, word in enumerate(selected_words):
                                    try:
                                        status_text.text(f"Przetwarzam: {word} ({i+1}/{len(selected_words)})")
                                        progress_bar.progress((i + 1) / len(selected_words))
                                        
                                        word_data = generate_word_with_ai(word, language_in, language_out)
                                        if word_data:
                                            add_word_to_database(word_data, lang_pair)
                                            success_count += 1
                                        else:
                                            error_count += 1
                                            st.warning(f"⚠️ Nie udało się przetworzyć słówka: {word}")
                                            
                                    except Exception as word_error:
                                        error_count += 1
                                        st.error(f"❌ Błąd dla słówka '{word}': {str(word_error)}")
                                
                                progress_bar.empty()
                                status_text.empty()
                                
                                # Podsumowanie
                                if success_count > 0:
                                    st.success(f"✅ Pomyślnie dodano {success_count} słówek do bazy!")
                                    if success_count == len(selected_words):
                                        st.balloons()
                                
                                if error_count > 0:
                                    st.error(f"❌ Nie udało się dodać {error_count} słówek")
                                
                                if success_count > 0:  # Odśwież tylko jeśli coś zostało dodane
                                    st.rerun()
                                    
                        except Exception as general_error:
                            st.error(f"❌ Ogólny błąd podczas dodawania słówek: {str(general_error)}")
                            with st.expander("🔍 Szczegóły błędu"):
                                st.code(str(general_error))
            
            elif add_mode == "✋ Wybierz konkretne słówka":
                st.info("👆 Zaznacz słówka które chcesz dodać do bazy")
            else:
                st.info("✅ Wszystkie słówka z tego zestawu już są w bazie!")
    
    # TAB 3: Dodawanie słówek
    with tab3:
        st.subheader("Dodaj nowe słówko")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            new_word = st.text_input(
                f"Słowo/fraza w języku {language_in}:",
                placeholder="np. apple, good morning, I am hungry"
            )
        
        with col2:
            if st.button("🤖 Generuj z AI", disabled=not new_word):
                if new_word:
                    try:
                        with st.spinner("Generuję tłumaczenie i przykłady..."):
                            word_data = generate_word_with_ai(new_word, language_in, language_out)
                            
                            if word_data:
                                st.session_state.generated_word = word_data
                                st.session_state.generated_word["original"] = new_word
                                st.success(f"✅ Pomyślnie wygenerowano dane dla słówka '{new_word}'")
                            else:
                                st.error(f"❌ Nie udało się wygenerować danych dla słówka '{new_word}'")
                                
                    except Exception as e:
                        st.error(f"❌ Wystąpił błąd podczas generowania: {str(e)}")
                        with st.expander("🔍 Szczegóły błędu"):
                            st.code(str(e))
        
        # Wyświetl wygenerowane dane
        if "generated_word" in st.session_state:
            word_data = st.session_state.generated_word
            
            st.success("✅ Wygenerowano dane słówka:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{language_in}:** {word_data['original']}")
                st.write(f"**{language_out}:** {word_data['translation']}")
                
                if word_data.get("alternatives"):
                    st.write(f"**Alternatywy:** {', '.join(word_data['alternatives'])}")
                
                st.write(f"**Część mowy:** {word_data.get('part_of_speech', 'nieznana')}")
                st.write(f"**Poziom:** {word_data.get('difficulty', 'nieznany')}")
            
            with col2:
                if st.button("🔊 Wymów oryginał"):
                    try:
                        audio_bytes = text_to_speech(word_data["original"], language_in)
                        st.audio(audio_bytes, format="audio/mp3")
                    except Exception as e:
                        st.error(f"❌ Błąd wymowy: {str(e)}")
                
                if st.button("🔊 Wymów tłumaczenie"):
                    try:
                        audio_bytes = text_to_speech(word_data["translation"], language_out)
                        st.audio(audio_bytes, format="audio/mp3")
                    except Exception as e:
                        st.error(f"❌ Błąd wymowy: {str(e)}")
            
            # Przykłady
            if word_data.get("examples"):
                st.write("**Przykłady użycia:**")
                for i, example in enumerate(word_data["examples"]):
                    with st.expander(f"Przykład {i+1}"):
                        st.write(f"**{language_in}:** {example['original']}")
                        st.write(f"**{language_out}:** {example['translated']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"🔊 {language_in}", key=f"ex_orig_{i}"):
                                try:
                                    audio_bytes = text_to_speech(example["original"], language_in)
                                    st.audio(audio_bytes, format="audio/mp3")
                                except Exception as e:
                                    st.error(f"❌ Błąd wymowy: {str(e)}")
                        with col2:
                            if st.button(f"🔊 {language_out}", key=f"ex_trans_{i}"):
                                try:
                                    audio_bytes = text_to_speech(example["translated"], language_out)
                                    st.audio(audio_bytes, format="audio/mp3")
                                except Exception as e:
                                    st.error(f"❌ Błąd wymowy: {str(e)}")
            
            # Dodaj do bazy
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Dodaj do bazy słówek", type="primary"):
                    try:
                        word_entry = add_word_to_database(word_data, lang_pair)
                        st.success(f"✅ Dodano słówko do bazy! ID: {word_entry['id']}")
                        del st.session_state.generated_word
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Błąd dodawania do bazy: {str(e)}")
                        with st.expander("🔍 Szczegóły błędu"):
                            st.code(str(e))
            
            with col2:
                if st.button("🗑️ Odrzuć"):
                    del st.session_state.generated_word
                    st.rerun()
    
    # TAB 4: Powtórka
    with tab4:
        st.subheader("🔄 Powtórka słówek")
        
        words_to_review = get_words_for_review(lang_pair)
        
        if not words_to_review:
            st.info("🎉 Brak słówek do powtórki! Dodaj nowe słówka lub wróć później.")
        else:
            st.write(f"**Słówek do powtórki:** {len(words_to_review)}")
            
            # Inicjalizuj sesję powtórki
            if "review_session" not in st.session_state:
                st.session_state.review_session = {
                    "words": words_to_review.copy(),
                    "current_index": 0,
                    "correct_answers": 0,
                    "show_answer": False
                }
            
            session = st.session_state.review_session
            
            if session["current_index"] < len(session["words"]):
                current_word = session["words"][session["current_index"]]
                
                st.write(f"**Słówko {session['current_index'] + 1}/{len(session['words'])}**")
                
                # Pokaż słówko
                st.markdown(f"### 🔤 {current_word['original']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔊 Wymów"):
                        try:
                            audio_bytes = text_to_speech(current_word["original"], language_in)
                            st.audio(audio_bytes, format="audio/mp3")
                        except Exception as e:
                            st.error(f"❌ Błąd wymowy: {str(e)}")
                
                with col2:
                    if st.button("👁️ Pokaż odpowiedź"):
                        session["show_answer"] = True
                
                # Pokaż odpowiedź jeśli odkryta
                if session["show_answer"]:
                    st.markdown(f"### ✅ {current_word['translation']}")
                    
                    if current_word.get("alternatives"):
                        st.write(f"**Alternatywy:** {', '.join(current_word['alternatives'])}")
                    
                    # Przyciski oceny
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("❌ Źle", key="wrong"):
                            update_word_performance(current_word["id"], lang_pair, False)
                            session["current_index"] += 1
                            session["show_answer"] = False
                            st.rerun()
                    
                    with col2:
                        if st.button("⚡ Trudne", key="hard"):
                            update_word_performance(current_word["id"], lang_pair, True)
                            session["current_index"] += 1
                            session["show_answer"] = False
                            st.rerun()
                    
                    with col3:
                        if st.button("✅ Łatwe", key="easy"):
                            update_word_performance(current_word["id"], lang_pair, True)
                            session["correct_answers"] += 1
                            session["current_index"] += 1
                            session["show_answer"] = False
                            st.rerun()
            
            else:
                # Koniec sesji
                st.success("🎉 Gratulacje! Ukończyłeś sesję powtórki!")
                st.write(f"**Wynik:** {session['correct_answers']}/{len(session['words'])}")
                
                if st.button("🔄 Nowa sesja"):
                    del st.session_state.review_session
                    st.rerun()
    
    # TAB 5: Test
    with tab5:
        st.subheader("🎯 Test wiedzy")
        st.info("🚧 Tryb testowy będzie wkrótce dostępny!")
    
    # TAB 6: Statystyki
    with tab6:
        st.subheader("📊 Statystyki słówek")
        
        db = load_vocabulary_database()
        stats = db["statistics"]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📚 Słówka", stats["words_added"])
        
        with col2:
            if lang_pair in db["words"]:
                st.metric("🌍 W tej parze", len(db["words"][lang_pair]))
            else:
                st.metric("🌍 W tej parze", 0)
        
        with col3:
            ready_count = len(get_words_for_review(lang_pair, 1000))
            st.metric("🔄 Do powtórki", ready_count)
        
        with col4:
            if stats["total_answers"] > 0:
                accuracy = (stats["correct_answers"] / stats["total_answers"]) * 100
                st.metric("🎯 Celność", f"{accuracy:.1f}%")
            else:
                st.metric("🎯 Celność", "0%")
        
        # Lista słówek w tej parze języków
        if lang_pair in db["words"] and db["words"][lang_pair]:
            st.subheader(f"Słówka {language_in} → {language_out}")
            
            words = db["words"][lang_pair]
            
            for word in words[-10:]:  # Ostatnie 10
                with st.expander(f"{word['original']} → {word['translation']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Poziom opanowania:** {word['mastery_level']}/5")
                        st.write(f"**Powtórek:** {word['review_count']}")
                    
                    with col2:
                        if word["last_reviewed"]:
                            last = datetime.fromisoformat(word["last_reviewed"])
                            st.write(f"**Ostatnia powtórka:** {last.strftime('%d.%m.%Y')}")
                        else:
                            st.write("**Ostatnia powtórka:** Nigdy")
"""
Bazowy handler AI dla obsługi języków
Zawiera wspólne funkcjonalności dla wszystkich języków
"""
import json

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from utils.config import client, get_model
    from utils.ai_stats import add_token_usage
except ImportError:
    client = None
    add_token_usage = None


class BaseAIHandler:
    """
    Bazowa klasa dla handlerów AI różnych języków
    """
    
    def __init__(self, language_name):
        self.language_name = language_name
        try:
            self.model = get_model()
        except Exception:
            self.model = "gpt-4o-mini"
        self.temperature = 0.3
        
    def _make_ai_request(self, system_prompt, user_prompt, max_tokens=800):
        """
        Wykonuje zapytanie do AI z obsługą błędów
        """
        try:
            if not client:
                if st:
                    st.error("❌ Klient OpenAI nie jest skonfigurowany. Sprawdź plik .env")
                return None
                
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=max_tokens
            )
            
            if not response or not response.choices or len(response.choices) == 0:
                if st:
                    st.error("❌ Pusta odpowiedź z API OpenAI")
                return None
                
            content = response.choices[0].message.content
            if not content:
                if st:
                    st.error("❌ Pusta treść odpowiedzi z API")
                return None
            
            # Dodaj statystyki tokenów
            if hasattr(response, 'usage') and response.usage and add_token_usage:
                try:
                    add_token_usage("vocabulary", 
                                   response.usage.prompt_tokens, 
                                   response.usage.completion_tokens)
                except Exception:
                    pass
            
            return content
            
        except Exception as e:
            if st:
                st.error(f"❌ Błąd komunikacji z AI: {str(e)}")
            return None
    
    def _parse_json_response(self, content):
        """
        Parsuje odpowiedź JSON z lepszą obsługą błędów
        """
        try:
            # Wyczyść odpowiedź z markdown i białych znaków
            content = content.strip()
            
            # Usuń bloki markdown JSON jeśli istnieją
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            if not content:
                if st:
                    st.error("❌ Pusta odpowiedź JSON po wyczyszczeniu")
                return None
            
            return json.loads(content)
            
        except json.JSONDecodeError as json_error:
            if st:
                st.error(f"❌ Błąd parsowania JSON z AI: {json_error}")
                st.info(f"🔍 Treść do parsowania: '{content}'")
            return None
    
    def generate_word_translation(self, word, lang_in, lang_out):
        """
        Generuje tłumaczenie słowa - bazowa implementacja
        """
        system_prompt = "Jesteś ekspertem językowym. Odpowiadaj tylko w formacie JSON."
        
        user_prompt = f"""
Jestem aplikacją do nauki języków. Użytkownik podał słowo/frazę: "{word}" 
w języku: {lang_in}

Proszę o odpowiedź w formacie JSON:
{{
    "translation": "główne tłumaczenie na język {lang_out}",
    "alternatives": ["alternatywne tłumaczenie 1", "alternatywne tłumaczenie 2"],
    "examples": [
        {{"original": "przykład w języku {lang_in}", "translated": "tłumaczenie na {lang_out}"}},
        {{"original": "drugi przykład w języku {lang_in}", "translated": "tłumaczenie na {lang_out}"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "rzeczownik|czasownik|przymiotnik|etc",
    "pronunciation_tip": "wskazówka dotycząca wymowy (jeśli przydatna)"
}}

Odpowiedź tylko w formacie JSON, bez dodatkowych komentarzy.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt)
        if not content:
            return None
            
        return self._parse_json_response(content)
    
    def generate_word_conjugation(self, word, part_of_speech, polish_translation=""):
        """
        Generuje odmianę słowa - bazowa implementacja
        Do nadpisania w konkretnych handlerach językowych
        """
        system_prompt = "Jesteś ekspertem językowym. Odpowiadaj tylko w formacie JSON."
        
        polish_info = f" (znaczenie: {polish_translation})" if polish_translation else ""
        
        user_prompt = f"""
Przeanalizuj słowo "{word}" w języku {self.language_name} i określ jego część mowy, a następnie podaj odpowiednie formy gramatyczne.

Jeśli to czasownik - podaj koniugację (czas teraźniejszy, przeszły, przyszły).
Jeśli to rzeczownik - podaj deklinację (liczba pojedyncza i mnoga z przypadkami).
Jeśli to przymiotnik - podaj stopniowanie i formy rodzajowe.

Zwróć odpowiedź w formacie JSON:
{{
    "conjugations": [
        {{"form": "nazwa formy", "examples": ["przykład 1 - polskie tłumaczenie", "przykład 2 - polskie tłumaczenie", "przykład 3 - polskie tłumaczenie"]}},
        {{"form": "nazwa formy", "examples": ["przykład 1 - polskie tłumaczenie", "przykład 2 - polskie tłumaczenie", "przykład 3 - polskie tłumaczenie"]}}
    ]
}}

Słowo: "{word}"{polish_info}
Język: {self.language_name}

Odpowiedź tylko w formacie JSON, bez dodatkowych komentarzy.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt, max_tokens=600)
        if not content:
            return None
            
        return self._parse_json_response(content)
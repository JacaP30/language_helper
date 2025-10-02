"""
Handler AI specjalizowany dla języka angielskiego
Zawiera precyzyjne prompty dostosowane do specyfiki angielskiego
"""
from .base_ai_handler import BaseAIHandler


class EnglishAIHandler(BaseAIHandler):
    """
    Specjalizowany handler dla języka angielskiego
    """
    
    def __init__(self):
        super().__init__("angielski")
    
    def generate_word_conjugation(self, word, part_of_speech, polish_translation=""):
        """
        Generuje odmianę słowa angielskiego z precyzyjnymi promptami
        """
        system_prompt = """Jesteś ekspertem języka angielskiego dla Polaków. 
        Generuj TYLKO prawdziwe formy angielskie z dokładnymi polskimi tłumaczeniami.
        Odpowiadaj tylko w formacie JSON bez dodatkowych komentarzy."""
        
        polish_info = f" (znaczenie: {polish_translation})" if polish_translation else ""
        
        if part_of_speech and "czasownik" in part_of_speech.lower():
            user_prompt = f"""
Wygeneruj koniugację angielskiego czasownika "{word}"{polish_info} z prawdziwymi polskimi tłumaczeniami każdej formy:

{{
    "conjugations": [
        {{"form": "Present Simple", "examples": [
            "I {word} - ja ...", 
            "you {word} - ty ...", 
            "he/she/it {word}s - on/ona ...", 
            "we {word} - my ...", 
            "you {word} - wy ...", 
            "they {word} - oni/one ..."
        ]}},
        {{"form": "Past Simple", "examples": [
            "I {word}ed - ja ...", 
            "you {word}ed - ty ...", 
            "he/she/it {word}ed - on/ona ...", 
            "we {word}ed - my ...", 
            "you {word}ed - wy ...", 
            "they {word}ed - oni/one ..."
        ]}},
        {{"form": "Future Simple", "examples": [
            "I will {word} - ja będę ...", 
            "you will {word} - ty będziesz ...", 
            "he/she/it will {word} - on/ona będzie ...", 
            "we will {word} - my będziemy ...", 
            "you will {word} - wy będziecie ...", 
            "they will {word} - oni/one będą ..."
        ]}},
        {{"form": "Present Continuous", "examples": [
            "I am {word}ing - ja właśnie ...", 
            "you are {word}ing - ty właśnie ...", 
            "he/she/it is {word}ing - on/ona właśnie ..."
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe formy czasownika "{word}" w języku angielskim:
- Jeśli czasownik nieregularny (np. "go" → "went", "have" → "had"), użyj właściwych form
- Dla trzeciej osoby liczby pojedynczej w Present Simple dodaj -s/-es (he works, she goes)
- Sprawdź czy czasownik wymaga podwójnej spółgłoski (stop → stopped)
- Podaj dokładne polskie tłumaczenia każdej formy

Przykład dla "work":
"I work - ja pracuję", "he works - on pracuje", "I worked - ja pracowałem", "I will work - ja będę pracować"

Odpowiedź tylko w formacie JSON.
"""
        elif part_of_speech and "rzeczownik" in part_of_speech.lower():
            user_prompt = f"""
Dla angielskiego rzeczownika "{word}"{polish_info} podaj formy z polskimi objaśnieniami:

{{
    "conjugations": [
        {{"form": "Singular (liczba pojedyncza)", "examples": [
            "{word} - {polish_translation or '...'}", 
            "a {word} - jakiś/jakaś {polish_translation or '...'}", 
            "the {word} - ten/ta/to {polish_translation or '...'}"
        ]}},
        {{"form": "Plural (liczba mnoga)", "examples": [
            "{word}s - {polish_translation or '...'}y/i", 
            "the {word}s - te {polish_translation or '...'}y/i", 
            "some {word}s - jakieś {polish_translation or '...'}y/i"
        ]}},
        {{"form": "Possessive (dopełniacz)", "examples": [
            "the {word}'s - tego/tej {polish_translation or '...'}a", 
            "the {word}s' - tych {polish_translation or '...'}ów"
        ]}},
        {{"form": "Przykłady użycia", "examples": [
            "I have a {word} - mam {polish_translation or '...'}", 
            "The {word} is important - {polish_translation or 'rzeczownik'} jest ważny/a/e", 
            "I need some {word}s - potrzebuję {polish_translation or 'rzeczowników'}"
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe angielskie formy rzeczownika "{word}":
- Jeśli nieregularny (man → men, child → children), użyj właściwej formy mnogiej
- Jeśli kończy się na -y, zmień na -ies (city → cities)
- Jeśli kończy się na -s, -x, -z, -ch, -sh, dodaj -es (box → boxes)
- Podaj dokładne polskie tłumaczenia

Przykład dla "book":
"book - książka", "books - książki", "the book's - tej książki", "I have a book - mam książkę"

Odpowiedź tylko w formacie JSON.
"""
        else:
            # Automatyczne rozpoznanie części mowy
            user_prompt = f"""
Przeanalizuj angielskie słowo "{word}"{polish_info} i określ jego część mowy, następnie podaj odpowiednie formy gramatyczne.

Jeśli to czasownik:
- Present Simple (I work, he works)
- Past Simple (I worked)  
- Future Simple (I will work)
- Present Continuous (I am working)

Jeśli to rzeczownik:
- Singular/Plural (book/books)
- Possessive (book's, books')
- Przykłady użycia

Jeśli to przymiotnik:
- Positive (good)
- Comparative (better) 
- Superlative (the best)
- Przykłady użycia

Zwróć odpowiedź w formacie JSON:
{{
    "conjugations": [
        {{"form": "nazwa formy", "examples": ["forma angielska - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}},
        {{"form": "nazwa formy", "examples": ["forma angielska - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}}
    ]
}}

KRYTYCZNE: Użyj PRAWDZIWYCH angielskich form gramatycznych słowa "{word}" i dokładnych polskich tłumaczeń.
Sprawdź czy słowo jest regularne czy nieregularne.

Odpowiedź tylko w formacie JSON, bez dodatkowych komentarzy.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt, max_tokens=700)
        if not content:
            return None
            
        return self._parse_json_response(content)
    
    def generate_word_translation(self, word, lang_in, lang_out):
        """
        Specjalizowane tłumaczenie dla angielskiego
        """
        system_prompt = """Jesteś ekspertem języka angielskiego dla Polaków. 
        Podawaj precyzyjne tłumaczenia z uwzględnieniem kontekstu i użycia w zdaniach.
        Odpowiadaj tylko w formacie JSON."""
        
        if lang_in == "angielski":
            user_prompt = f"""
Przetłumacz angielskie słowo/frazę "{word}" na polski z pełnym kontekstem:

{{
    "translation": "główne polskie tłumaczenie",
    "alternatives": ["inne znaczenie 1", "inne znaczenie 2", "synonim"],
    "examples": [
        {{"original": "naturalne angielskie zdanie z '{word}'", "translated": "polskie tłumaczenie zdania"}},
        {{"original": "kolejne przykład z '{word}'", "translated": "polskie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}'", "translated": "polskie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "noun|verb|adjective|adverb|preposition|etc",
    "pronunciation_tip": "wskazówka wymowy po angielsku (jeśli trudne słowo)",
    "grammar_notes": "notatka gramatyczna (np. czasownik nieregularny, rzeczownik niepoliczalny)"
}}

KRYTYCZNE: Podaj dokładne polskie tłumaczenia i naturalne przykłady użycia.
Rozpoznaj czy słowo ma różne znaczenia w różnych kontekstach.

Odpowiedź tylko w formacie JSON.
"""
        else:  # tłumaczenie z polskiego na angielski
            user_prompt = f"""
Przetłumacz polskie słowo/frazę "{word}" na angielski z pełnym kontekstem:

{{
    "translation": "główne angielskie tłumaczenie",
    "alternatives": ["inne tłumaczenie 1", "synonim", "formalne/nieformalne warianty"],
    "examples": [
        {{"original": "naturalne polskie zdanie z '{word}'", "translated": "angielskie tłumaczenie zdania"}},
        {{"original": "kolejny przykład z '{word}'", "translated": "angielskie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}'", "translated": "angielskie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "noun|verb|adjective|adverb|preposition|etc",
    "pronunciation_tip": "wskazówka wymowy angielskiej",
    "grammar_notes": "notatka gramatyczna (np. irregular verb, uncountable noun, phrasal verb)"
}}

KRYTYCZNE: Podaj precyzyjne angielskie tłumaczenia i naturalne przykłady.
Sprawdź czy polskie słowo ma kilka angielskich odpowiedników w różnych kontekstach.

Odpowiedź tylko w formacie JSON.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt)
        if not content:
            return None
            
        return self._parse_json_response(content)
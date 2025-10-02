"""
Handler AI specjalizowany dla języka niemieckiego
Zawiera precyzyjne prompty dostosowane do specyfiki niemieckiego
"""
from .base_ai_handler import BaseAIHandler


class GermanAIHandler(BaseAIHandler):
    """
    Specjalizowany handler dla języka niemieckiego
    """
    
    def __init__(self):
        super().__init__("niemiecki")
    
    def generate_word_conjugation(self, word, part_of_speech, polish_translation=""):
        """
        Generuje odmianę słowa niemieckiego z precyzyjnymi promptami
        """
        system_prompt = """Jesteś ekspertem języka niemieckiego dla Polaków. 
        Generuj TYLKO prawdziwe formy niemieckie z dokładnymi polskimi tłumaczeniami.
        Uwzględniaj umlauty (ä, ö, ü), ß i wszystkie zasady niemieckiej gramatyki.
        Odpowiadaj tylko w formacie JSON bez dodatkowych komentarzy."""
        
        polish_info = f" (znaczenie: {polish_translation})" if polish_translation else ""
        
        if part_of_speech and "czasownik" in part_of_speech.lower():
            user_prompt = f"""
Wygeneruj koniugację niemieckiego czasownika "{word}"{polish_info} z prawdziwymi polskimi tłumaczeniami każdej formy:

{{
    "conjugations": [
        {{"form": "Präsens (czas teraźniejszy)", "examples": [
            "ich {word}... - ja ...", 
            "du {word}... - ty ...", 
            "er/sie/es {word}... - on/ona/ono ...", 
            "wir {word}... - my ...", 
            "ihr {word}... - wy ...", 
            "sie/Sie {word}... - oni/one/Pan/Pani ..."
        ]}},
        {{"form": "Präteritum (czas przeszły)", "examples": [
            "ich {word}... - ja ...", 
            "du {word}... - ty ...", 
            "er/sie/es {word}... - on/ona/ono ...", 
            "wir {word}... - my ...", 
            "ihr {word}... - wy ...", 
            "sie/Sie {word}... - oni/one/Pan/Pani ..."
        ]}},
        {{"form": "Perfekt (czas przeszły złożony)", "examples": [
            "ich habe/bin ge{word}... - ja ...", 
            "du hast/bist ge{word}... - ty ...", 
            "er/sie/es hat/ist ge{word}... - on/ona/ono ..."
        ]}},
        {{"form": "Futur I (czas przyszły)", "examples": [
            "ich werde {word}... - ja będę ...", 
            "du wirst {word}... - ty będziesz ...", 
            "er/sie/es wird {word}... - on/ona/ono będzie ..."
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe formy czasownika "{word}" w języku niemieckim:
- Rozpoznaj czy czasownik słaby/mocny/nieregularny
- Dla czasowników mocnych: zmiany w rdzeniu (e→i/ie, a→ä)
- Dla czasowników z przedrostkami: czy rozdzielny (auf|stehen → stehe auf)
- Perfekt z haben lub sein (ich bin gegangen vs ich habe gesagt)
- Zachowaj wszystkie umlauty i ß
- Podaj dokładne polskie tłumaczenia każdej formy

Przykład dla "sprechen":
"ich spreche - ja mówię", "du sprichst - ty mówisz", "er sprach - on mówił", "ich habe gesprochen - ja mówiłem"

Odpowiedź tylko w formacie JSON.
"""
        elif part_of_speech and "rzeczownik" in part_of_speech.lower():
            user_prompt = f"""
Dla niemieckiego rzeczownika "{word}"{polish_info} podaj formy ze wszystkimi przypadkami i polskimi objaśnieniami:

{{
    "conjugations": [
        {{"form": "Nominativ (mianownik)", "examples": [
            "der/die/das {word} - {polish_translation or '...'}", 
            "ein/eine {word} - jakiś/jakaś {polish_translation or '...'}", 
            "die {word} (liczba mnoga) - {polish_translation or '...'}y/i"
        ]}},
        {{"form": "Genitiv (dopełniacz)", "examples": [
            "des/der/des {word}s - {polish_translation or '...'}a", 
            "eines/einer {word}s - jakiegoś/jakiejś {polish_translation or '...'}a", 
            "der {word} (liczba mnoga) - {polish_translation or '...'}ów"
        ]}},
        {{"form": "Dativ (celownik)", "examples": [
            "dem/der/dem {word} - {polish_translation or '...'}owi", 
            "einem/einer {word} - jakiemuś/jakiejś {polish_translation or '...'}owi", 
            "den {word}n (liczba mnoga) - {polish_translation or '...'}om"
        ]}},
        {{"form": "Akkusativ (biernik)", "examples": [
            "den/die/das {word} - {polish_translation or '...'}", 
            "einen/eine {word} - jakiegoś/jakąś {polish_translation or '...'}", 
            "die {word} (liczba mnoga) - {polish_translation or '...'}y/i"
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe niemieckie formy rzeczownika "{word}":
- Określ rodzaj gramatyczny (der/die/das)
- Sprawdź deklinację: słaba (der Junge, des Jungen), mocna (der Mann, des Mannes), mieszana
- Forma mnoga: -e, -er, -en, -s lub umlaut (Mann → Männer)
- N-deklinacja dla rzeczowników słabych (der Student → den Studenten)
- Zachowaj wszystkie umlauty
- Podaj dokładne polskie tłumaczenia wszystkich przypadków

Przykład dla "das Haus":
"das Haus - dom", "des Hauses - domu", "dem Haus - domowi", "das Haus - dom", "die Häuser - domy"

Odpowiedź tylko w formacie JSON.
"""
        else:
            # Automatyczne rozpoznanie części mowy
            user_prompt = f"""
Przeanalizuj niemieckie słowo "{word}"{polish_info} i określ jego część mowy, następnie podaj odpowiednie formy gramatyczne.

Jeśli to czasownik:
- Präsens (ich spreche, du sprichst)
- Präteritum (ich sprach)  
- Perfekt (ich habe gesprochen)
- Futur (ich werde sprechen)

Jeśli to rzeczownik:
- Wszystkie przypadki (Nominativ, Genitiv, Dativ, Akkusativ)
- Liczba mnoga
- Rodzaj gramatyczny (der/die/das)

Jeśli to przymiotnik:
- Deklinacja (der gute Mann, ein guter Mann)
- Stopniowanie (gut, besser, am besten)
- Formy przysłówkowe

Zwróć odpowiedź w formacie JSON:
{{
    "conjugations": [
        {{"form": "nazwa formy", "examples": ["forma niemiecka - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}},
        {{"form": "nazwa formy", "examples": ["forma niemiecka - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}}
    ]
}}

KRYTYCZNE: Użyj PRAWDZIWYCH niemieckich form gramatycznych słowa "{word}" z wszystkimi umlautami i ß.
Sprawdź czy słowo jest regularne czy nieregularne.
Określ rodzaj gramatyczny dla rzeczowników.
Uwzględnij deklinację i koniugację według zasad niemieckiej gramatyki.

Odpowiedź tylko w formacie JSON, bez dodatkowych komentarzy.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt, max_tokens=800)
        if not content:
            return None
            
        return self._parse_json_response(content)
    
    def generate_word_translation(self, word, lang_in, lang_out):
        """
        Specjalizowane tłumaczenie dla niemieckiego
        """
        system_prompt = """Jesteś ekspertem języka niemieckiego dla Polaków. 
        Podawaj precyzyjne tłumaczenia z uwzględnieniem kontekstu i przypadków.
        Zachowuj wszystkie znaki diakrytyczne (ä, ö, ü, ß).
        Zwracaj uwagę na rodzaj gramatyczny i deklinację.
        Odpowiadaj tylko w formacie JSON."""
        
        if lang_in == "niemiecki":
            user_prompt = f"""
Przetłumacz niemieckie słowo/frazę "{word}" na polski z pełnym kontekstem gramatycznym:

{{
    "translation": "główne polskie tłumaczenie",
    "alternatives": ["inne znaczenie 1", "synonim", "wariant formalny/nieformalny"],
    "examples": [
        {{"original": "naturalne niemieckie zdanie z '{word}'", "translated": "polskie tłumaczenie zdania"}},
        {{"original": "kolejny przykład z '{word}' w innym przypadku", "translated": "polskie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}' w innym kontekście", "translated": "polskie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "Substantiv|Verb|Adjektiv|Adverb|Präposition|etc",
    "pronunciation_tip": "wskazówka wymowy (zwłaszcza ü, ö, ach, ich)",
    "grammar_notes": "notatka gramatyczna (np. der/die/das, Dativ/Akkusativ, unregelmäßiges Verb)",
    "declination_info": "informacja o deklinacji/koniugacji"
}}

KRYTYCZNE: Podaj dokładne polskie tłumaczenia i naturalne przykłady użycia.
Rozpoznaj czy słowo ma różne znaczenia w różnych przypadkach gramatycznych.
Zachowaj wszystkie niemieckie znaki diakrytyczne.
Uwzględnij rodzaj gramatyczny dla rzeczowników.

Odpowiedź tylko w formacie JSON.
"""
        else:  # tłumaczenie z polskiego na niemiecki
            user_prompt = f"""
Przetłumacz polskie słowo/frazę "{word}" na niemiecki z pełnym kontekstem gramatycznym:

{{
    "translation": "główne niemieckie tłumaczenie",
    "alternatives": ["inne tłumaczenie", "synonim", "wariant regionalny"],
    "examples": [
        {{"original": "naturalne polskie zdanie z '{word}'", "translated": "niemieckie tłumaczenie zdania"}},
        {{"original": "kolejny przykład z '{word}'", "translated": "niemieckie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}' w innym kontekście", "translated": "niemieckie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "Substantiv|Verb|Adjektiv|Adverb|Präposition|etc",
    "pronunciation_tip": "wskazówka wymowy niemieckiej",
    "grammar_notes": "notatka gramatyczna (np. genus, Deklination, Konjugation, trennbare Verben)",
    "declination_info": "informacja o deklinacji (der/die/das + przypadki)"
}}

KRYTYCZNE: Podaj precyzyjne niemieckie tłumaczenia z wszystkimi umlautami i ß.
Sprawdź czy polskie słowo ma kilka niemieckich odpowiedników w różnych kontekstach.
Uwzględnij rodzaj gramatyczny i odpowiednią deklinację.
Zwróć uwagę na czasowniki rozdzielne i nierozdzielne.

Odpowiedź tylko w formacie JSON.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt)
        if not content:
            return None
            
        return self._parse_json_response(content)
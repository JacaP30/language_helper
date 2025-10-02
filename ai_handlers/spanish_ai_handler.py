"""
Handler AI specjalizowany dla języka hiszpańskiego
Zawiera precyzyjne prompty dostosowane do specyfiki hiszpańskiego
"""
from .base_ai_handler import BaseAIHandler


class SpanishAIHandler(BaseAIHandler):
    """
    Specjalizowany handler dla języka hiszpańskiego
    """
    
    def __init__(self):
        super().__init__("hiszpański")
    
    def generate_word_conjugation(self, word, part_of_speech, polish_translation=""):
        """
        Generuje odmianę słowa hiszpańskiego z precyzyjnymi promptami
        """
        system_prompt = """Jesteś ekspertem języka hiszpańskiego dla Polaków. 
        Generuj TYLKO prawdziwe formy hiszpańskie z dokładnymi polskimi tłumaczeniami.
        Uwzględniaj akcenty, ñ i wszystkie znaki diakrytyczne.
        Odpowiadaj tylko w formacie JSON bez dodatkowych komentarzy."""
        
        polish_info = f" (znaczenie: {polish_translation})" if polish_translation else ""
        
        if part_of_speech and "czasownik" in part_of_speech.lower():
            user_prompt = f"""
Wygeneruj koniugację hiszpańskiego czasownika "{word}"{polish_info} z prawdziwymi polskimi tłumaczeniami każdej formy:

{{
    "conjugations": [
        {{"form": "Presente (czas teraźniejszy)", "examples": [
            "yo {word}... - ja ...", 
            "tú {word}... - ty ...", 
            "él/ella {word}... - on/ona ...", 
            "nosotros {word}... - my ...", 
            "vosotros {word}... - wy ...", 
            "ellos/ellas {word}... - oni/one ..."
        ]}},
        {{"form": "Pretérito perfecto simple (czas przeszły)", "examples": [
            "yo {word}... - ja ...", 
            "tú {word}... - ty ...", 
            "él/ella {word}... - on/ona ...", 
            "nosotros {word}... - my ...", 
            "vosotros {word}... - wy ...", 
            "ellos/ellas {word}... - oni/one ..."
        ]}},
        {{"form": "Futuro simple (czas przyszły)", "examples": [
            "yo {word}aré/eré/iré - ja będę ...", 
            "tú {word}arás/erás/irás - ty będziesz ...", 
            "él/ella {word}ará/erá/irá - on/ona będzie ..."
        ]}},
        {{"form": "Gerundio (imiesłów)", "examples": [
            "{word}ando/iendo - ...ąc", 
            "estar {word}ando/iendo - właśnie ..."
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe formy czasownika "{word}" w języku hiszpańskim:
- Rozpoznaj koniugację (-ar, -er, -ir)
- Jeśli czasownik nieregularny (ser, estar, tener, hacer), użyj właściwych form
- Uwzględnij zmiany w rdzeniu (e→ie, o→ue, e→i)
- Zachowaj wszystkie akcenty (está, tendrá, comió)
- Podaj dokładne polskie tłumaczenia każdej formy

Przykład dla "hablar":
"yo hablo - ja mówię", "tú hablas - ty mówisz", "él habla - on mówi"

Odpowiedź tylko w formacie JSON.
"""
        elif part_of_speech and "rzeczownik" in part_of_speech.lower():
            user_prompt = f"""
Dla hiszpańskiego rzeczownika "{word}"{polish_info} podaj formy z rodzajnikami i polskimi objaśnieniami:

{{
    "conjugations": [
        {{"form": "Singular masculino/feminino", "examples": [
            "el {word} / la {word} - {polish_translation or '...'}", 
            "un {word} / una {word} - jakiś/jakaś {polish_translation or '...'}", 
            "del {word} / de la {word} - z {polish_translation or '...'}a"
        ]}},
        {{"form": "Plural", "examples": [
            "los {word}s / las {word}s - {polish_translation or '...'}y/i", 
            "unos {word}s / unas {word}s - jakieś {polish_translation or '...'}y/i", 
            "de los {word}s / de las {word}s - z {polish_translation or '...'}ów"
        ]}},
        {{"form": "Con preposiciones (z przyimkami)", "examples": [
            "al {word} - do {polish_translation or '...'}a", 
            "en el {word} - w {polish_translation or '...'}ie", 
            "para el {word} - dla {polish_translation or '...'}a"
        ]}},
        {{"form": "Ejemplos de uso", "examples": [
            "Tengo un {word} - mam {polish_translation or '...'}", 
            "El {word} es importante - {polish_translation or 'rzeczownik'} jest ważny/a", 
            "Voy al {word} - idę do {polish_translation or '...'}a"
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe hiszpańskie formy rzeczownika "{word}":
- Określ czy słowo jest męskie (el) czy żeńskie (la)
- Formy množne: dodaj -s jeśli kończy się samogłoską, -es jeśli spółgłoską
- Uwzględnij kontrakcje: del (de + el), al (a + el)
- Zachowaj akcenty w liczbie mnogiej (nación → naciones)
- Podaj dokładne polskie tłumaczenia

Przykład dla "casa":
"la casa - dom", "las casas - domy", "de la casa - z domu", "en casa - w domu"

Odpowiedź tylko w formacie JSON.
"""
        else:
            # Automatyczne rozpoznanie części mowy
            user_prompt = f"""
Przeanalizuj hiszpańskie słowo "{word}"{polish_info} i określ jego część mowy, następnie podaj odpowiednie formy gramatyczne.

Jeśli to czasownik:
- Presente (hablo, hablas, habla)
- Pretérito (hablé, hablaste, habló)  
- Futuro (hablaré, hablarás, hablará)
- Gerundio (hablando)

Jeśli to rzeczownik:
- Singular con artículos (el/la palabra)
- Plural (las palabras)
- Con preposiciones (del, al)
- Przykłady użycia

Jeśli to przymiotnik:
- Masculino/Feminino (bueno/buena)
- Singular/Plural (buenos/buenas)
- Stopniowanie (más bueno, el mejor)

Zwróć odpowiedź w formacie JSON:
{{
    "conjugations": [
        {{"form": "nazwa formy", "examples": ["forma hiszpańska - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}},
        {{"form": "nazwa formy", "examples": ["forma hiszpańska - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}}
    ]
}}

KRYTYCZNE: Użyj PRAWDZIWYCH hiszpańskich form gramatycznych słowa "{word}" z wszystkimi akcentami i znakami.
Sprawdź czy słowo jest regularne czy nieregularne.
Określ rodzaj gramatyczny dla rzeczowników i przymiotników.

Odpowiedź tylko w formacie JSON, bez dodatkowych komentarzy.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt, max_tokens=700)
        if not content:
            return None
            
        return self._parse_json_response(content)
    
    def generate_word_translation(self, word, lang_in, lang_out):
        """
        Specjalizowane tłumaczenie dla hiszpańskiego
        """
        system_prompt = """Jesteś ekspertem języka hiszpańskiego dla Polaków. 
        Podawaj precyzyjne tłumaczenia z uwzględnieniem kontekstu regionalnego (Hiszpania vs Ameryka Łacińska).
        Zachowuj wszystkie znaki diakrytyczne (ñ, á, é, í, ó, ú).
        Odpowiadaj tylko w formacie JSON."""
        
        if lang_in == "hiszpański":
            user_prompt = f"""
Przetłumacz hiszpańskie słowo/frazę "{word}" na polski z pełnym kontekstem:

{{
    "translation": "główne polskie tłumaczenie",
    "alternatives": ["inne znaczenie 1", "wariant regionalny", "synonim"],
    "examples": [
        {{"original": "naturalne hiszpańskie zdanie z '{word}'", "translated": "polskie tłumaczenie zdania"}},
        {{"original": "kolejny przykład z '{word}'", "translated": "polskie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}' w innym kontekście", "translated": "polskie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "sustantivo|verbo|adjetivo|adverbio|preposición|etc",
    "pronunciation_tip": "wskazówka wymowy (zwłaszcza rr, ñ, j)",
    "grammar_notes": "notatka gramatyczna (np. verbo irregular, cambio de raíz, género)",
    "regional_notes": "różnice regionalne (Hiszpania vs Ameryka Łacińska)"
}}

KRYTYCZNE: Podaj dokładne polskie tłumaczenia i naturalne przykłady użycia.
Rozpoznaj czy słowo ma różne znaczenia lub różni się regionalnie.
Zachowaj wszystkie hiszpańskie znaki diakrytyczne.

Odpowiedź tylko w formacie JSON.
"""
        else:  # tłumaczenie z polskiego na hiszpański
            user_prompt = f"""
Przetłumacz polskie słowo/frazę "{word}" na hiszpański z pełnym kontekstem:

{{
    "translation": "główne hiszpańskie tłumaczenie",
    "alternatives": ["inne tłumaczenie", "wariant regionalny", "synonim"],
    "examples": [
        {{"original": "naturalne polskie zdanie z '{word}'", "translated": "hiszpańskie tłumaczenie zdania"}},
        {{"original": "kolejny przykład z '{word}'", "translated": "hiszpańskie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}' w innym kontekście", "translated": "hiszpańskie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "sustantivo|verbo|adjetivo|adverbio|preposición|etc",
    "pronunciation_tip": "wskazówka wymowy hiszpańskiej",
    "grammar_notes": "notatka gramatyczna (np. género, conjugación, uso con ser/estar)",
    "regional_notes": "czy słowo różni się między regionami hiszpańskojęzycznymi"
}}

KRYTYCZNE: Podaj precyzyjne hiszpańskie tłumaczenia z wszystkimi akcentami.
Sprawdź czy polskie słowo ma kilka hiszpańskich odpowiedników w różnych kontekstach.
Uwzględnij rodzaj gramatyczny i koniugację czasowników.

Odpowiedź tylko w formacie JSON.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt)
        if not content:
            return None
            
        return self._parse_json_response(content)
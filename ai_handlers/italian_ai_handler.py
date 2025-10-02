"""
Handler AI specjalizowany dla języka włoskiego
Zawiera precyzyjne prompty dostosowane do specyfiki włoskiego
"""
from .base_ai_handler import BaseAIHandler


class ItalianAIHandler(BaseAIHandler):
    """
    Specjalizowany handler dla języka włoskiego
    """
    
    def __init__(self):
        super().__init__("włoski")
    
    def generate_word_conjugation(self, word, part_of_speech, polish_translation=""):
        """
        Generuje odmianę słowa włoskiego z precyzyjnymi promptami
        """
        system_prompt = """Jesteś ekspertem języka włoskiego dla Polaków. 
        Generuj TYLKO prawdziwe formy włoskie z dokładnymi polskimi tłumaczeniami.
        Uwzględniaj wszystkie akcenty (à, è, é, ì, ò, ó, ù) i podwójne spółgłoski.
        Odpowiadaj tylko w formacie JSON bez dodatkowych komentarzy."""
        
        polish_info = f" (znaczenie: {polish_translation})" if polish_translation else ""
        
        if part_of_speech and "czasownik" in part_of_speech.lower():
            user_prompt = f"""
Wygeneruj koniugację włoskiego czasownika "{word}"{polish_info} z prawdziwymi polskimi tłumaczeniami każdej formy:

{{
    "conjugations": [
        {{"form": "Presente indicativo (czas teraźniejszy)", "examples": [
            "io {word}... - ja ...", 
            "tu {word}... - ty ...", 
            "lui/lei {word}... - on/ona ...", 
            "noi {word}... - my ...", 
            "voi {word}... - wy ...", 
            "loro {word}... - oni/one ..."
        ]}},
        {{"form": "Passato prossimo (czas przeszły złożony)", "examples": [
            "io ho/sono {word}... - ja ...", 
            "tu hai/sei {word}... - ty ...", 
            "lui/lei ha/è {word}... - on/ona ...", 
            "noi abbiamo/siamo {word}... - my ...", 
            "voi avete/siete {word}... - wy ...", 
            "loro hanno/sono {word}... - oni/one ..."
        ]}},
        {{"form": "Futuro semplice (czas przyszły)", "examples": [
            "io {word}... - ja będę ...", 
            "tu {word}... - ty będziesz ...", 
            "lui/lei {word}... - on/ona będzie ...", 
            "noi {word}... - my będziemy ...", 
            "voi {word}... - wy będziecie ...", 
            "loro {word}... - oni/one będą ..."
        ]}},
        {{"form": "Gerundio/Participio presente", "examples": [
            "{word}ando/endo - ...ąc", 
            "stare + gerundio - właśnie ...", 
            "participio presente - ... który ..."
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe formy czasownika "{word}" w języku włoskim:
- Rozpoznaj koniugację czasownika (-are, -ere, -ire)
- Czasowniki 1. koniugacji: -are (parlare → io parlo)
- Czasowniki 2. koniugacji: -ere (vedere → io vedo)  
- Czasowniki 3. koniugacji: -ire (finire → io finisco, partire → io parto)
- Czasowniki nieregularne (essere, avere, fare, dare, stare, andare, etc.)
- Passato prossimo z essere lub avere (sono andato vs ho mangiato)
- Zachowaj wszystkie akcenty i podwójne spółgłoski
- Podaj dokładne polskie tłumaczenia każdej formy

Przykład dla "parlare":
"io parlo - ja mówię", "tu parli - ty mówisz", "ho parlato - ja mówiłem", "parlerò - ja będę mówić"

Odpowiedź tylko w formacie JSON.
"""
        elif part_of_speech and "rzeczownik" in part_of_speech.lower():
            user_prompt = f"""
Dla włoskiego rzeczownika "{word}"{polish_info} podaj formy z rodzajnikami i polskimi objaśnieniami:

{{
    "conjugations": [
        {{"form": "Singolare maschile/femminile", "examples": [
            "il {word} / la {word} - {polish_translation or '...'}", 
            "un {word} / una {word} - jakiś/jakaś {polish_translation or '...'}", 
            "del {word} / della {word} - z {polish_translation or '...'}a"
        ]}},
        {{"form": "Plurale", "examples": [
            "i {word}... / le {word}... - {polish_translation or '...'}y/i", 
            "dei {word}... / delle {word}... - jakieś {polish_translation or '...'}y/i", 
            "alcuni {word}... / alcune {word}... - niektóre {polish_translation or '...'}y/i"
        ]}},
        {{"form": "Con preposizioni articolate", "examples": [
            "al {word} / alla {word} - do {polish_translation or '...'}a", 
            "nel {word} / nella {word} - w {polish_translation or '...'}ie", 
            "dal {word} / dalla {word} - od {polish_translation or '...'}a"
        ]}},
        {{"form": "Esempi d'uso", "examples": [
            "Ho un {word} - mam {polish_translation or '...'}", 
            "Il {word} è importante - {polish_translation or 'rzeczownik'} jest ważny/a", 
            "Vado al {word} - idę do {polish_translation or '...'}a"
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe włoskie formy rzeczownika "{word}":
- Określ czy słowo jest męskie (il/i) czy żeńskie (la/le)
- Formy mnogiej: -o→i, -a→e, -e→i (libro→libri, casa→case, cane→cani)
- Wyjątki: niektóre rzeczowniki nieregularne (uomo→uomini, mano→mani)
- Preposizioni articolate: del, nel, dal, al, sul, col (di+il=del, in+il=nel)
- Zachowaj wszystkie akcenty i podwójne spółgłoski
- Podaj dokładne polskie tłumaczenia

Przykład dla "casa":
"la casa - dom", "le case - domy", "della casa - z domu", "alla casa - do domu"

Odpowiedź tylko w formacie JSON.
"""
        else:
            # Automatyczne rozpoznanie części mowy
            user_prompt = f"""
Przeanalizuj włoskie słowo "{word}"{polish_info} i określ jego część mowy, następnie podaj odpowiednie formy gramatyczne.

Jeśli to czasownik:
- Presente (io parlo, tu parli)
- Passato prossimo (ho parlato)  
- Futuro semplice (parlerò)
- Gerundio (parlando)

Jeśli to rzeczownik:
- Maschile/Femminile (il/la parola)
- Singolare/Plurale (parole)
- Con preposizioni articolate (della, nella)
- Przykłady użycia

Jeśli to przymiotnik:
- Maschile/Femminile (bello/bella)
- Singolare/Plurale (belli/belle)
- Stopniowanie (più bello, il più bello)

Zwróć odpowiedź w formacie JSON:
{{
    "conjugations": [
        {{"form": "nazwa formy", "examples": ["forma włoska - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}},
        {{"form": "nazwa formy", "examples": ["forma włoska - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}}
    ]
}}

KRYTYCZNE: Użyj PRAWDZIWYCH włoskich form gramatycznych słowa "{word}" z wszystkimi akcentami i podwójnymi spółgłoskami.
Sprawdź czy słowo jest regularne czy nieregularne.
Określ rodzaj gramatyczny dla rzeczowników i przymiotników.
Uwzględnij koniugację czasowników i zgodność przymiotników.

Odpowiedź tylko w formacie JSON, bez dodatkowych komentarzy.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt, max_tokens=800)
        if not content:
            return None
            
        return self._parse_json_response(content)
    
    def generate_word_translation(self, word, lang_in, lang_out):
        """
        Specjalizowane tłumaczenie dla włoskiego
        """
        system_prompt = """Jesteś ekspertem języka włoskiego dla Polaków. 
        Podawaj precyzyjne tłumaczenia z uwzględnieniem kontekstu i użycia.
        Zachowuj wszystkie akcenty włoskie (à, è, é, ì, ò, ó, ù) i podwójne spółgłoski.
        Zwracaj uwagę na rodzaj gramatyczny i preposizioni articolate.
        Odpowiadaj tylko w formacie JSON."""
        
        if lang_in == "włoski":
            user_prompt = f"""
Przetłumacz włoskie słowo/frazę "{word}" na polski z pełnym kontekstem gramatycznym:

{{
    "translation": "główne polskie tłumaczenie",
    "alternatives": ["inne znaczenie 1", "synonim", "wariant regionalny"],
    "examples": [
        {{"original": "naturalne włoskie zdanie z '{word}'", "translated": "polskie tłumaczenie zdania"}},
        {{"original": "kolejny przykład z '{word}' z preposizioni", "translated": "polskie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}' w innym kontekście", "translated": "polskie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "sostantivo|verbo|aggettivo|avverbio|preposizione|etc",
    "pronunciation_tip": "wskazówka wymowy (zwłaszcza gli, gn, sc, podwójne spółgłoski)",
    "grammar_notes": "notatka gramatyczna (np. il/la, essere/avere, verbo irregolare)",
    "regional_info": "informacja o wariantach regionalnych (jeśli dotyczy)"
}}

KRYTYCZNE: Podaj dokładne polskie tłumaczenia i naturalne przykłady użycia.
Rozpoznaj czy słowo ma różne znaczenia w różnych kontekstach.
Zachowaj wszystkie włoskie akcenty i podwójne spółgłoski.
Uwzględnij rodzaj gramatyczny dla rzeczowników.
Zwróć uwagę na preposizioni articolate.

Odpowiedź tylko w formacie JSON.
"""
        else:  # tłumaczenie z polskiego na włoski
            user_prompt = f"""
Przetłumacz polskie słowo/frazę "{word}" na włoski z pełnym kontekstem gramatycznym:

{{
    "translation": "główne włoskie tłumaczenie",
    "alternatives": ["inne tłumaczenie", "synonim", "wariant formalny"],
    "examples": [
        {{"original": "naturalne polskie zdanie z '{word}'", "translated": "włoskie tłumaczenie zdania"}},
        {{"original": "kolejny przykład z '{word}'", "translated": "włoskie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}' w innym kontekście", "translated": "włoskie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "sostantivo|verbo|aggettivo|avverbio|preposizione|etc",
    "pronunciation_tip": "wskazówka wymowy włoskiej",
    "grammar_notes": "notatka gramatyczna (np. genere, coniugazione, accordo)",
    "preposition_info": "informacja o preposizioni articolate (del, nel, al, etc.)"
}}

KRYTYCZNE: Podaj precyzyjne włoskie tłumaczenia z wszystkimi akcentami i podwójnymi spółgłoskami.
Sprawdź czy polskie słowo ma kilka włoskich odpowiedników w różnych kontekstach.
Uwzględnij rodzaj gramatyczny i odpowiednią koniugację/zgodność.
Zwróć uwagę na preposizioni articolate.

Odpowiedź tylko w formacie JSON.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt)
        if not content:
            return None
            
        return self._parse_json_response(content)
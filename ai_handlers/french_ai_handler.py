"""
Handler AI specjalizowany dla języka francuskiego
Zawiera precyzyjne prompty dostosowane do specyfiki francuskiego
"""
from .base_ai_handler import BaseAIHandler


class FrenchAIHandler(BaseAIHandler):
    """
    Specjalizowany handler dla języka francuskiego
    """
    
    def __init__(self):
        super().__init__("francuski")
    
    def generate_word_conjugation(self, word, part_of_speech, polish_translation=""):
        """
        Generuje odmianę słowa francuskiego z precyzyjnymi promptami
        """
        system_prompt = """Jesteś ekspertem języka francuskiego dla Polaków. 
        Generuj TYLKO prawdziwe formy francuskie z dokładnymi polskimi tłumaczeniami.
        Uwzględniaj wszystkie akcenty (é, è, ê, ç, à, ù) i liaisonsy.
        Odpowiadaj tylko w formacie JSON bez dodatkowych komentarzy."""
        
        polish_info = f" (znaczenie: {polish_translation})" if polish_translation else ""
        
        if part_of_speech and "czasownik" in part_of_speech.lower():
            user_prompt = f"""
Wygeneruj koniugację francuskiego czasownika "{word}"{polish_info} z prawdziwymi polskimi tłumaczeniami każdej formy:

{{
    "conjugations": [
        {{"form": "Présent de l'indicatif (czas teraźniejszy)", "examples": [
            "je {word}... - ja ...", 
            "tu {word}... - ty ...", 
            "il/elle {word}... - on/ona ...", 
            "nous {word}... - my ...", 
            "vous {word}... - wy/Pan/Pani ...", 
            "ils/elles {word}... - oni/one ..."
        ]}},
        {{"form": "Passé composé (czas przeszły złożony)", "examples": [
            "j'ai/je suis {word}... - ja ...", 
            "tu as/tu es {word}... - ty ...", 
            "il/elle a/est {word}... - on/ona ...", 
            "nous avons/sommes {word}... - my ...", 
            "vous avez/êtes {word}... - wy/Pan/Pani ...", 
            "ils/elles ont/sont {word}... - oni/one ..."
        ]}},
        {{"form": "Futur simple (czas przyszły)", "examples": [
            "je {word}... - ja będę ...", 
            "tu {word}... - ty będziesz ...", 
            "il/elle {word}... - on/ona będzie ...", 
            "nous {word}... - my będziemy ...", 
            "vous {word}... - wy będziecie/Pan będzie ...", 
            "ils/elles {word}... - oni/one będą ..."
        ]}},
        {{"form": "Participe présent/Gérondif", "examples": [
            "{word}ant - ...ąc", 
            "en {word}ant - ...ąc, podczas gdy ..."
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe formy czasownika "{word}" w języku francuskim:
- Rozpoznaj grupę czasownika (1. grupa -er, 2. grupa -ir, 3. grupa nieregularne)
- Dla czasowników 1. grupy: zwykłe -er (parler → je parle)
- Dla czasowników 2. grupy: -ir z -iss- (finir → je finis, nous finissons)
- Dla czasowników 3. grupy: nieregularne (être, avoir, aller, faire, etc.)
- Passé composé z être lub avoir (je suis allé vs j'ai mangé)
- Zachowaj wszystkie akcenty (é, è, ê, ç, à, ù)
- Podaj dokładne polskie tłumaczenia każdej formy

Przykład dla "parler":
"je parle - ja mówię", "tu parles - ty mówisz", "j'ai parlé - ja mówiłem", "je parlerai - ja będę mówić"

Odpowiedź tylko w formacie JSON.
"""
        elif part_of_speech and "rzeczownik" in part_of_speech.lower():
            user_prompt = f"""
Dla francuskiego rzeczownika "{word}"{polish_info} podaj formy z rodzajnikami i polskimi objaśnieniami:

{{
    "conjugations": [
        {{"form": "Masculin/Féminin singulier", "examples": [
            "le {word} / la {word} - {polish_translation or '...'}", 
            "un {word} / une {word} - jakiś/jakaś {polish_translation or '...'}", 
            "du {word} / de la {word} - z {polish_translation or '...'}a (partitif)"
        ]}},
        {{"form": "Pluriel", "examples": [
            "les {word}s - {polish_translation or '...'}y/i", 
            "des {word}s - jakieś {polish_translation or '...'}y/i", 
            "de {word}s - z {polish_translation or '...'}ów"
        ]}},
        {{"form": "Avec prépositions", "examples": [
            "au {word} / à la {word} - do {polish_translation or '...'}a", 
            "dans le {word} - w {polish_translation or '...'}ie", 
            "pour le {word} - dla {polish_translation or '...'}a"
        ]}},
        {{"form": "Exemples d'usage", "examples": [
            "J'ai un {word} - mam {polish_translation or '...'}", 
            "Le {word} est important - {polish_translation or 'rzeczownik'} jest ważny/a", 
            "Je vais au {word} - idę do {polish_translation or '...'}a"
        ]}}
    ]
}}

KRYTYCZNE: Wypełnij prawdziwe francuskie formy rzeczownika "{word}":
- Określ czy słowo jest męskie (le) czy żeńskie (la)
- Formy množne: zwykle +s, ale uwzględnij wyjątki (eau → eaux, al → aux)
- Kontrakcje: du (de + le), au (à + le), des (de + les), aux (à + les)
- Partitifs: du/de la/des dla niepoliczalnych
- Zachowaj wszystkie akcenty
- Podaj dokładne polskie tłumaczenia

Przykład dla "maison":
"la maison - dom", "les maisons - domy", "de la maison - z domu", "à la maison - do domu"

Odpowiedź tylko w formacie JSON.
"""
        else:
            # Automatyczne rozpoznanie części mowy
            user_prompt = f"""
Przeanalizuj francuskie słowo "{word}"{polish_info} i określ jego część mowy, następnie podaj odpowiednie formy gramatyczne.

Jeśli to czasownik:
- Présent (je parle, tu parles)
- Passé composé (j'ai parlé)  
- Futur simple (je parlerai)
- Participe présent (parlant)

Jeśli to rzeczownik:
- Masculin/Féminin (le/la mot)
- Singulier/Pluriel (mots)
- Avec articles contractés (du, au)
- Przykłady użycia

Jeśli to przymiotnik:
- Masculin/Féminin (beau/belle)
- Singulier/Pluriel (beaux/belles)
- Stopniowanie (plus beau, le plus beau)

Zwróć odpowiedź w formacie JSON:
{{
    "conjugations": [
        {{"form": "nazwa formy", "examples": ["forma francuska - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}},
        {{"form": "nazwa formy", "examples": ["forma francuska - polskie tłumaczenie", "kolejna forma - tłumaczenie"]}}
    ]
}}

KRYTYCZNE: Użyj PRAWDZIWYCH francuskich form gramatycznych słowa "{word}" z wszystkimi akcentami.
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
        Specjalizowane tłumaczenie dla francuskiego
        """
        system_prompt = """Jesteś ekspertem języka francuskiego dla Polaków. 
        Podawaj precyzyjne tłumaczenia z uwzględnieniem kontekstu i użycia.
        Zachowuj wszystkie akcenty francuskie (é, è, ê, ç, à, ù, â, î, ô, û).
        Zwracaj uwagę na rodzaj gramatyczny i liaisons.
        Odpowiadaj tylko w formacie JSON."""
        
        if lang_in == "francuski":
            user_prompt = f"""
Przetłumacz francuskie słowo/frazę "{word}" na polski z pełnym kontekstem gramatycznym:

{{
    "translation": "główne polskie tłumaczenie",
    "alternatives": ["inne znaczenie 1", "synonim", "wariant formalny/nieformalny"],
    "examples": [
        {{"original": "naturalne francuskie zdanie z '{word}'", "translated": "polskie tłumaczenie zdania"}},
        {{"original": "kolejny przykład z '{word}' z liaisons", "translated": "polskie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}' w innym kontekście", "translated": "polskie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "nom|verbe|adjectif|adverbe|préposition|etc",
    "pronunciation_tip": "wskazówka wymowy (zwłaszcza e muet, liaisons, r français)",
    "grammar_notes": "notatka gramatyczna (np. le/la, COD/COI, verbe irrégulier)",
    "liaison_info": "informacja o liaisons i elisions (jeśli dotyczy)"
}}

KRYTYCZNE: Podaj dokładne polskie tłumaczenia i naturalne przykłady użycia.
Rozpoznaj czy słowo ma różne znaczenia w różnych kontekstach.
Zachowaj wszystkie francuskie akcenty.
Uwzględnij rodzaj gramatyczny dla rzeczowników.
Zwróć uwagę na liaisons i elisions.

Odpowiedź tylko w formacie JSON.
"""
        else:  # tłumaczenie z polskiego na francuski
            user_prompt = f"""
Przetłumacz polskie słowo/frazę "{word}" na francuski z pełnym kontekstem gramatycznym:

{{
    "translation": "główne francuskie tłumaczenie",
    "alternatives": ["inne tłumaczenie", "synonim", "wariant regionalny"],
    "examples": [
        {{"original": "naturalne polskie zdanie z '{word}'", "translated": "francuskie tłumaczenie zdania"}},
        {{"original": "kolejny przykład z '{word}'", "translated": "francuskie tłumaczenie"}},
        {{"original": "trzeci przykład z '{word}' w innym kontekście", "translated": "francuskie tłumaczenie"}}
    ],
    "difficulty": "basic|intermediate|advanced",
    "part_of_speech": "nom|verbe|adjectif|adverbe|préposition|etc",
    "pronunciation_tip": "wskazówka wymowy francuskiej",
    "grammar_notes": "notatka gramatyczna (np. genre, conjugaison, accord, COD/COI)",
    "liaison_info": "informacja o liaisons i elisions w kontekście"
}}

KRYTYCZNE: Podaj precyzyjne francuskie tłumaczenia z wszystkimi akcentami.
Sprawdź czy polskie słowo ma kilka francuskich odpowiedników w różnych kontekstach.
Uwzględnij rodzaj gramatyczny i odpowiednią koniugację/zgodność.
Zwróć uwagę na liaisons między słowami.

Odpowiedź tylko w formacie JSON.
"""
        
        content = self._make_ai_request(system_prompt, user_prompt)
        if not content:
            return None
            
        return self._parse_json_response(content)
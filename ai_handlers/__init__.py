"""
Moduły obsługi AI dla różnych języków
"""

from .base_ai_handler import BaseAIHandler
from .english_ai_handler import EnglishAIHandler
from .spanish_ai_handler import SpanishAIHandler
from .german_ai_handler import GermanAIHandler
from .french_ai_handler import FrenchAIHandler
from .italian_ai_handler import ItalianAIHandler

# Mapa języków do ich handlerów
LANGUAGE_HANDLERS = {
    "angielski": EnglishAIHandler,
    "hiszpański": SpanishAIHandler, 
    "niemiecki": GermanAIHandler,
    "francuski": FrenchAIHandler,
    "włoski": ItalianAIHandler
}

def get_ai_handler(language):
    """
    Zwraca odpowiedni handler AI dla danego języka
    """
    handler_class = LANGUAGE_HANDLERS.get(language.lower())
    if handler_class:
        return handler_class()
    else:
        # Fallback na bazowy handler
        return BaseAIHandler(language)
# ZASADY KODOWANIA DLA AI ASYSTENTA

## 🚨 PRZECZYTAJ TO NA POCZĄTKU KAŻDEJ SESJI! 🚨

### 1. JEDNA ZMIANA NA RAZ
- **NIE** rób kilku zmian jednocześnie
- Zrób jedną małą zmianę → przetestuj → czekaj na akceptację
- Dopiero po "OK" od użytkownika rób kolejną zmianę

### 2. PYTAJ PRZED KAŻDĄ ZMIANĄ
- Gdy użytkownik prosi o funkcję X, zapytaj: **"Czy mam zmienić TYLKO X czy też coś więcej?"**
- **NIE** dodawaj "ulepszeń" bez pytania
- **NIE** "poprawiaj" kodu który działa

### 3. JEŚLI COŚ DZIAŁA - NIE RUSZAJ!
- Gdy użytkownik mówi "to działa poprawnie" → **ZOSTAW BEZ ZMIAN**
- Dodawaj nowe funkcje **OBOK**, nie **ZAMIAST**
- Nie zmieniaj działających API calls, parametrów, logiki

### 4. ŚRODOWISKO TESTOWE
- **ZAWSZE** używaj odpowiedniego środowiska Python/conda
- Sprawdź `get_python_environment_details` przed uruchomieniem
- Używaj `conda run --name [ENV_NAME]` jeśli jest środowisko conda

### 4.1. PRACA Z TERMINALEM - KRYTYCZNE ZASADY!
- **NIE OTWIERAJ NOWYCH TERMINALI** bez powodu!
- Korzystaj z TEGO SAMEGO terminala dla całej sesji
- Gdy aktywujesz środowisko conda → używaj go dalej w TYM SAMYM terminalu
- **NIE** uruchamiaj `run_in_terminal` bez sprawdzenia aktualnego terminala
- Sprawdź `get_terminal_output` dla aktywnych terminali przed otwarciem nowego
- Jeśli masz aktywne środowisko w terminalu → KONTYNUUJ w nim
- Gdy uruchamiasz aplikację (streamlit/flask) → upewnij się że środowisko jest AKTYWNE w tym terminalu
- **PROBLEM**: otwieranie nowych terminali resetuje środowisko do 'base'
- **ROZWIĄZANIE**: jedna komenda łączona: `conda activate [ENV] && python script.py`

### 5. OBOWIĄZKOWY CHECKLIST
Przed każdą zmianą kodu zapytaj siebie:
- [ ] Czy zmieniam TYLKO to o co prosił użytkownik?
- [ ] Czy zostawiam resztę kodu bez zmian?
- [ ] Czy używam odpowiedniego środowiska do testów?
- [ ] Czy to jest minimalna możliwa zmiana?

### 6. STOP SŁOWA
Gdy użytkownik powie:
- **"STOP"**
- **"Za dużo zmian"** 
- **"Jedna rzecz na raz"**
- **"Nie ruszaj tego"**

→ **NATYCHMIAST** wracaj do poprzedniej wersji i zacznij małymi krokami

### 7. DOBRE vs ZŁE PODEJŚCIE

#### ❌ ZŁE:
```
Użytkownik: "Dodaj przycisk start/stop"
AI: *Przepisuje całą funkcję + dodaje debug + zmienia API + dodaje nowe funkcje*
```

#### ✅ DOBRE:
```
Użytkownik: "Dodaj przycisk start/stop" 
AI: "Czy mam dodać TYLKO przyciski start/stop, zostawiając resztę funkcji bez zmian?"
Użytkownik: "Tak"
AI: *Dodaje tylko 2 przyciski i zmienne session_state*
```

### 8. KOMUNIKACJA
- **Bądź konkretny** w pytaniach
- **Nie zakładaj** co użytkownik chce
- **Przyznaj się** do błędu zamiast dalej psuć
- **Poproś o przywrócenie** poprzedniej wersji gdy coś pójdzie nie tak

---

## 🎯 PAMIĘTAJ: UŻYTKOWNIK CHCE ROZWIĄZANIE PROBLEMU, NIE NOWY PROBLEM!

### Przykłady dobrych pytań:
- "Czy mam zmienić tylko sposób nagrywania, zostawiając API Whisper bez zmian?"
- "Czy dodać tę funkcję jako nową, czy zastąpić istniejącą?"
- "Czy przetestować w środowisku conda przed pokazaniem wyniku?"

### Gdy coś idzie źle:
1. **STOP** - nie rób więcej zmian
2. **PRZYZNAJ** - "Przepraszam, zrobiłem za dużo zmian"  
3. **ZAPYTAJ** - "Czy przywrócić poprzednią wersję i zacząć od nowa małymi krokami?"

---
**Ostatnia aktualizacja:** Wrzesień 2025  
**Powód utworzenia:** Zapobieganie nadmiernym zmianom w działającym kodzie
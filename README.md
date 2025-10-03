# 🗣️ PANJO - Personalny Asystent Nauki Języków Obcych z AI

Zaawansowana aplikacja webowa do nauki języków obcych wykorzystująca sztuczną inteligencję OpenAI.

## ✨ Funkcjonalności

### 🎓 **Nauka słówek**
- Inteligentny system fiszek z algorytmem powtórek
- Gotowe zestawy słówek tematycznych
- Dodawanie własnych słówek i list
- System poziomów trudności (podstawowy/średni/zaawansowany)
- Testy wiedzy i statystyki postępów
- Funkcja powtórki trudniejszych słówek

### 👨‍🏫 **Belfer - Sprawdzanie gramatyki**
- Analiza poprawności gramatycznej i składniowej
- Sprawdzanie pisowni i budowy zdań
- Szczegółowe wyjaśnienia błędów z poprawkami
- Tłumaczenie tekstu na język docelowy
- Synteza mowy dla wyjaśnień

### 💬 **Dialog z AI**
- Naturalne rozmowy z AI w wybranym języku
- Ciągła historia konwersacji
- Nagrywanie i rozpoznawanie mowy
- Synteza mowy dla odpowiedzi AI
- Różne tematy rozmów

### 🌍 **Translator**
- Tłumaczenie tekstu między obsługiwanymi językami
- Rozpoznawanie mowy (nagrywanie wypowiedzi)
- Synteza mowy dla tłumaczeń
- Obsługa wielu par językowych

## 🌐 Obsługiwane języki

- 🇵🇱 Polski
- 🇬🇧 Angielski  
- 🇩🇪 Niemiecki
- 🇫🇷 Francuski
- 🇪🇸 Hiszpański
- 🇮🇹 Włoski

## 🛠️ Wymagania techniczne

### Wymagane pakiety Python:
```
streamlit>=1.28.0
openai>=1.0.0
python-dotenv>=1.0.0
sounddevice>=0.4.6
scipy>=1.11.0
gtts>=2.3.0 (opcjonalne - dla darmowego TTS)
```

### Klucz API OpenAI:
- Wymagany klucz API od OpenAI
- Uzyskaj na: https://platform.openai.com/api-keys

## 🚀 Instalacja i uruchomienie

### 1. Klonowanie repozytorium:
```bash
git clone https://github.com/JacaP30/language_helper.git
cd language_helper
```

### 2. Instalacja zależności:
```bash
pip install -r requirements.txt
```

### 3. Konfiguracja klucza API:

**Opcja A - Plik .env (zalecana):**
```bash
# Utwórz plik .env i dodaj swój klucz:
OPENAI_API_KEY=sk-proj-twój-klucz-api
```

**Opcja B - Wpisywanie przy starcie:**
- Jeśli nie ma klucza w .env, aplikacja poprosi o jego wpisanie przy pierwszym uruchomieniu

### 4. Uruchomienie:
```bash
streamlit run app.py
```

Aplikacja będzie dostępna pod adresem: `http://localhost:8501`

## 📁 Struktura projektu

```
language_helper/
├── app.py                      # Główny plik aplikacji
├── background_styles.py        # Style CSS i tło
├── BASE/                       # Bazy danych (ignorowane w git)
│   ├── vocabulary_database.json
│   └── usage_database.json
├── modules/                    # Moduły funkcjonalności
│   ├── belfer.py              # Sprawdzanie gramatyki
│   ├── dialog.py              # Dialog z AI
│   ├── translator.py          # Tłumacz
│   └── vocabulary.py          # Nauka słówek
├── utils/                     # Narzędzia pomocnicze
│   └── config.py             # Konfiguracja i funkcje wspólne
├── .streamlit/               # Konfiguracja Streamlit
│   └── config.toml          # Wymuszenie trybu ciemnego
└── README.md                # Ten plik
```

## 💰 Koszty użytkowania

Aplikacja korzysta z płatnych API OpenAI:
- **GPT-4o-mini**: $0.15/1M tokenów wejściowych, $0.60/1M tokenów wyjściowych
- **TTS (synteza mowy)**: $15.00/1M znaków (opcjonalnie darmowe gTTS)
- **Whisper (rozpoznawanie mowy)**: $0.006/minutę

Aplikacja automatycznie śledzi użycie i koszty w interfejsie użytkownika.

## 🎨 Funkcje interfejsu

- 🌙 **Tryb ciemny** - automatycznie dla wszystkich użytkowników
- 🎨 **Kolorowe gradientowe nagłówki** 
- 📊 **Statystyki użycia** tokenów i kosztów
- 🔊 **Synteza mowy** (OpenAI TTS lub darmowe gTTS)
- 🎤 **Rozpoznawanie mowy** przez mikrofon
- ℹ️ **Instrukcje obsługi** w każdym module

## 🔧 Konfiguracja zaawansowana

### Tryb ciemny:
Konfiguracja w `.streamlit/config.toml` wymusza ciemny motyw dla wszystkich użytkowników.

### Bazy danych:
- `vocabulary_database.json` - słówka i statystyki nauki
- `usage_database.json` - statystyki użycia API i koszty

### Style wizualne:
Wszystkie style CSS w `background_styles.py` z obsługą tła, gradientów i przezroczystości.

## 📝 Instrukcja użytkowania

1. **Wybierz narzędzie** z menu bocznego
2. **Ustaw języki** źródłowy i docelowy
3. **Korzystaj z wybranej funkcji**:
   - Wpisuj tekst lub nagrywaj przez mikrofon
   - Używaj przycisków do odtwarzania audio
   - Sprawdzaj statystyki w menu bocznym

## 🤝 Wsparcie i rozwój

- **Autor**: JacaP30
- **Licencja**: MIT
- **Issues**: Zgłoś problemy przez GitHub Issues
- **Rozwój**: Pull requesty mile widziane!

## 🔒 Bezpieczeństwo

- Klucze API nie są przechowywane permanentnie
- Dane użytkownika pozostają lokalne
- Komunikacja z OpenAI przez szyfrowane API

---

**Miłej nauki języków z PANJO! 🚀**
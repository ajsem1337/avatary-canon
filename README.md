# Awatary z inicjałów

Skrypt do tworzenia prostych awatarów PNG, np. do profili użytkowników drukarki.
Podajesz inicjały, dostajesz obraz 256 × 256 px. Działa lokalnie, bez konta i bez
wysyłania danych do zewnętrznych usług.

## Instalacja

Wymagania: Python 3.9+ i Pillow 10.1+. Uruchom polecenia w katalogu repozytorium.

Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tworzenie_avatarow.py --user mc
```

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\tworzenie_avatarow.py --user mc
```

Skrypt wypisze ścieżkę do gotowego pliku:

```text
avatary/etg_MC.png
```

Na Windows ścieżka używa separatora `\`. Jeśli Linux zgłasza brak modułu `venv`,
zainstaluj pakiet udostępniający go w swojej dystrybucji.

## Użycie

Przykłady poniżej używają interpretera z linuksowego środowiska `.venv`.
Na Windows zastąp `.venv/bin/python` przez `.\.venv\Scripts\python.exe`.

```bash
.venv/bin/python tworzenie_avatarow.py --user "łż"
.venv/bin/python tworzenie_avatarow.py --user mc --outdir "gotowe awatary"
.venv/bin/python tworzenie_avatarow.py --help
```

| Argument | Działanie |
| --- | --- |
| `--user` | Wymagany. Tekst, z którego powstaną inicjały. |
| `--outdir` | Katalog wynikowy, domyślnie `avatary`. Tworzony automatycznie. |

Katalog wynikowy jest liczony względem bieżącego katalogu terminala.
Plik ma nazwę `etg_<INICJAŁY>.png`. **Istniejący plik o tej nazwie zostanie
nadpisany bez pytania.**

## Jak powstaje awatar

- Tekst jest zamieniany na wielkie litery. Spacje i znaki inne niż litery lub
  cyfry są usuwane; zostają pierwsze dwa znaki. `m-c` daje `MC`, `7` daje `7`.
- Skrypt nie wyciąga inicjałów z imienia i nazwiska: `Jan Kowalski` daje `JA`.
- Równoważne zapisy Unicode są ujednolicane przed filtrowaniem znaków.
- Kolor tła wynika ze skrótu SHA-256 inicjałów. Te same inicjały dają to samo tło.
- Tekst jest czarny albo biały, zależnie od tego, który kolor daje większy
  [kontrast względem tła](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum).
- Obraz jest zapisywany jako PNG w trybie RGB, bez przezroczystości.

Skrypt korzysta z wyszukiwania czcionek w Pillow: obsługuje katalogi systemowe
Linuxa, Windows i macOS oraz katalogi użytkownika i ustawienia XDG na Linuxie.
Próbuje kolejno DejaVu Sans Bold, Liberation Sans Bold, Noto Sans Bold,
Segoe UI Bold, Arial Bold i Calibri Bold, a następnie Arial Bold dla macOS.
Gdy ich nie znajdzie, korzysta z czcionki wbudowanej
w Pillow. Jej [skalowanie wymaga Pillow 10.1+](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.load_default).
Wbudowana czcionka ma ograniczony zestaw znaków; do polskich liter najlepiej
mieć jedną z wymienionych czcionek systemowych. Nie każdy znak przyjęty przez
`--user` musi być dostępny w wybranej czcionce.

Wygląd liter zależy od dostępnej czcionki i wersji Pillow. Pliki wygenerowane
na różnych komputerach mogą wyglądać inaczej mimo tych samych inicjałów.

## Błędy i testy

Kod zakończenia `0` oznacza sukces, `2` — błędne argumenty lub brak liter/cyfr
w `--user`, a `1` — błąd tworzenia obrazu albo zapisu. Sprawdź komunikat błędu,
ścieżkę katalogu i uprawnienia do zapisu.

Testy korzystają z `unittest` i nie wymagają dodatkowych bibliotek poza Pillow:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Obejmują normalizację inicjałów, kontrast, centrowanie i dopasowanie tekstu,
brak czcionek systemowych oraz działanie CLI, w tym nadpisywanie i błędy zapisu.

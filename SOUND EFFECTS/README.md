# SOUND EFFECTS: główny plik dla agenta

Biblioteka 126 efektów dźwiękowych (69 wav, 57 mp3) do filmów, rolek i przebitek. Wszedłeś do folderu? Przeczytaj ten plik, potem tylko to, czego potrzebujesz:

| Plik | Po co |
|---|---|
| `README.md` (ten) | zasady głośności, dobór dźwięku do sceny, komendy |
| `INDEX.md` | tabele wszystkich dźwięków wg kategorii: id, czas, szczyt, domyślny gain |
| `index.json` | to samo dla programów (przeszukuje je `studio.py sfx`) |
| pliki audio | oryginały, nie zmieniaj ich nazw, nie usuwaj |

## Zasady głośności (decyzja właściciela, obowiązują zawsze)

1. **Efekt nigdy na 100%.** Dźwięki w tej bibliotece są głośne (wiele ma szczyt 0 dB) i zagłuszają lektora oraz muzykę.
2. **Zakres 0.3 do 0.5, domyślnie 0.4.** Narzędzia odrzucają gain powyżej **0.5**.
3. Pod lektorem 0.25 do 0.35. Ambience (deszcz, wiatr) najwyżej 0.2 jako tło.
4. Efekt ma wzmacniać obraz, nie być słyszalny sam: jeśli po odsłuchu jest pierwszym, co słychać, zmniejsz gain.
5. Odsłuchaj finalny miks. Kategorie w indeksie wynikają z nazw plików i pomiarów, nikt ich nie odsłuchał.

## Dobór do sceny

| Zdarzenie w filmie | Kategoria | Jak |
|---|---|---|
| Hook, pierwsza sekunda, uderzenie tytułu | `impact` | jeden dźwięk na klatce, w której tytuł się zatrzymuje |
| Napięcie przed odsłonięciem | `riser` | koniec risera = moment uderzenia (start = czas uderzenia minus długość risera) |
| Cięcie, przejście sceny, wjazd elementu | `transition` | start 0.05 do 0.1 s przed ruchem, kierunek zgodny z ruchem |
| Pojawienie się liczby, ikony, przycisku, potwierdzenie | `ui` | krótki klik, ding, pop |
| Wpisywanie komendy, kod, czat | `typing` | tempo zgodne z liczbą znaków; przytnij długie nagrania (`duration`) |
| Zdjęcie, flash, zrzut ekranu, moment uchwycenia | `camera` | zsynchronizuj z błyskiem |
| Awaria, hologram, teleport, motyw tech | `glitch-tech` | razem z efektem `glitch` w obrazie |
| Szkło, papier, drzwi, mechanizm, serce | `foley` | tylko gdy to widać w kadrze |
| Atmosfera pod całą sceną | `ambience` | gain najwyżej 0.2, z fade |
| Żart, komedia | `meme` | tylko gdy ton marki na to pozwala |

Dobre praktyki: jeden dźwięk na zdarzenie wizualne; najwyżej jeden efekt na 1.5 s; ten sam dźwięk nie więcej niż dwa razy w filmie; nie kładź impactu i risera w tej samej chwili; przy lektorze zostaw ciszę wokół ważnego słowa.

## Komendy

```powershell
python -S studio.py sfx find whoosh --category transition --max-duration 2   # szukaj
python -S studio.py sfx find impact --limit 5
python -S studio.py sfx check                                                # czy indeks zna wszystkie pliki
python -S studio.py edit output/jobs/ID fx --asset a-xxxx --name sfx-v1 `
   --effect sfx:file=whoosh-cinematic,start=1.5 `
   --effect sfx:file=cinematic-impact,start=2.6,gain=0.4,duration=1.2
```

Parametry `sfx`: `file` (id z indeksu, nazwa pliku albo ścieżka), `start` (sekunda w osi wyniku), `gain` (0.0 do 0.5, 0 = domyślny z katalogu), `duration` (0 = cały plik), `fade` (wyciszenie końcówki, domyślnie 0.04 s). Efekt miksuje się z istniejącym audio (lektor, muzyka), a źródło bez audio dostaje samą ścieżkę efektów. Limiter chroni przed przesterowaniem.

## Utrzymanie

- Nowy plik: wrzuć do tego folderu i uruchom `python -S scripts/sfx_catalog.py build` (mierzy czas i głośność, nadaje id, odświeża INDEX.md i index.json). `check` wykrywa pliki bez wpisu.
- Workspace jest współdzielony: nie zmieniaj nazw ani nie usuwaj cudzych plików. Gdy ten sam dźwięk jest w wav i mp3, indeks wskazuje wav (`duplicate_of`).
- Nie edytuj `INDEX.md` ani `index.json` ręcznie: nadpisze je kolejny build. Reguły kategorii są w `scripts/sfx_catalog.py` (`RULES`).

## Prawa do użycia

Oryginalna biblioteka 126 plików została dołączona na wyraźne polecenie właściciela projektu, który 2026-10-23 potwierdził prawo do ich publicznej redystrybucji. Dokument lub źródło tego uprawnienia nie zostały jeszcze dołączone. Nie oznaczamy dźwięków licencją MIT ani CC0. Zasady ponownego wykorzystania poszczególnych nagrań pozostają zgodne z licencjami oryginalnych twórców; ta publikacja nie obiecuje nieograniczonego użycia komercyjnego. Szczegóły i status: ../docs/MEDIA_RIGHTS.md.

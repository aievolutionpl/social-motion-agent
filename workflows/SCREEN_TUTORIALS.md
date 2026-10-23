# Workflow: prawdziwy ekran → pokaz → tutorial

OpenScreen to główny silnik tej ścieżki. Ogólny proces filmu pozostaje w PRODUKCJA.md. Ten dokument dodaje capture i dydaktykę; bieżące wyniki faktycznych testów zapisuj w HANDOFF.md konkretnej produkcji.

## 1. Przygotuj lekcję

Pięć pytań dopasuj do celu nauki, odbiorcy, konkretnego narzędzia, formatu/czasu oraz sposobu narracji. Zachowaj odpowiedzi w intake. `showcase` koncentruje się na widocznym rezultacie i kilku kluczowych akcjach. `tutorial` pokazuje również wymagania, kroki, wyjaśnienie decyzji i kontrolę wyniku.

Sprawdź aktualny interfejs oraz oficjalną dokumentację narzędzia. Zapisz linki, datę i istotne warunki planu/konta. Nie generuj fałszywego UI zamiast nagrania. Przygotuj dane demonstracyjne i wybierz jeden jednoznacznie nazwany ekran aplikacji. Projekt filmu zakładaj zwykłym CLI:

```powershell
python -S studio.py new "Jak używać narzędzia AI" --kind tutorial --format 16:9 --duration 120 --language pl
python -S studio.py route tutorial
python -S scripts/openscreen.py doctor
python -S scripts/openscreen.py sources --output output/jobs/ID/notes/capture-sources.json
```

Lista źródeł może zawierać tytuły otwartych okien — jest lokalną notatką roboczą, nie materiałem do publikacji.

## 2. Storyboard i nagranie

Zapisz tabelę kroków: czas → działanie → stan interfejsu → tekst lektora → potrzebne zbliżenie. Pokaż efekt wcześnie. W tutorialu zostaw czas na odczytanie przycisku i potwierdzenie rezultatu. Okres oczekiwania modelu skróć lub oznacz przyspieszenie. Wycisz/wyłącz niepotrzebne wejścia; domyślnie wrapper nie włącza mikrofonu, audio systemu ani kamery.

```powershell
python -S scripts/openscreen.py record --window "UNIKALNY TYTUŁ OKNA" --duration 40 --project output/jobs/ID/source/capture/take-01.openscreen
```

`--mic`, `--system-audio`, `--camera` są opcjonalne. Zapisz rzeczywiste ścieżki zwrócone przez `done`; OpenScreen trzyma raw media w swoim katalogu nagrań. Sprawdź `screenVideoPath`, czas, właściwe okno i zawartość kadrów. Nie uruchamiaj równoległych nagrań do tej samej karty. Na Windows używaj `--duration` lub stdin `stop`; SIGTERM nie jest poprawną metodą zakończenia take'a.

Gdy stronę obsługuje skrypt/Playwright, zapisuj czas i współrzędne faktycznie wykonywanych akcji. Kliknięcie przez CDP nie tworzy fizycznego ruchu myszy. Bez telemetrii użyj manualnych zoomów w projekcie; podłączony MCP może przyjąć ślad przez `setPointerTrack`. Dodatkowe narracyjne plansze/robota można złożyć naszym rendererem motion i FFmpeg.

## 3. Montaż i lektor

W `.openscreen` zachowaj oryginalną skalę UI, usuń niepotrzebny setup, dodaj czytelne zbliżenia na działanie oraz krótkie podpisy kroków. Dla projektu v2 przykłady pól są w oficjalnym `tools/repos/openscreen/website/docs/cli.md`. Projekty zapisane przez edytor mają inny schemat — nie edytuj ich według przykładu v2.

```powershell
python -S scripts/openscreen.py info --project output/jobs/ID/source/capture/take-01.openscreen
python -S scripts/openscreen.py export --project output/jobs/ID/source/capture/take-01.openscreen --output output/jobs/ID/previews/demo-v1.mp4 --quality medium --fps 30
```

Polski lektor: istniejący ElevenLabs. Dostosuj nagranie do rzeczywistej długości wypowiedzi. Aby dodać gotowy VO, do export dołącz `--voiceover SCIEZKA.wav --audio-mode replace` albo świadome `mix`. OpenScreen captions czyta dźwięk źródłowego nagrania, nie VO dodany przy eksporcie; napisy z takiego VO przygotuj osobną sprawdzoną ścieżką. Nie deklaruj SRT z OpenScreen — jego napisy są wypalane w obrazie.

## 4. Master, QA i pliki do przejęcia

```powershell
python -S scripts/openscreen.py export --project output/jobs/ID/source/capture/take-01.openscreen --output output/jobs/ID/renders/tutorial-v1.mp4 --quality good --fps 60
python -S scripts/openscreen.py pack --project output/jobs/ID/source/capture/take-01.openscreen --output output/jobs/ID/source/capture/bundle-v1
python -S studio.py probe output/jobs/ID --render renders/tutorial-v1.mp4
python -S studio.py sheet output/jobs/ID --render renders/tutorial-v1.mp4
```

`pack` obsługuje v2; dla dokumentu edytora spisz i skopiuj wszystkie faktycznie referencjonowane media/VO/telemetrię. Zachowaj napisy SRT z naszego workflow, rozdziały, źródła i instrukcję wznowienia. Obejrzyj draft i finalne klatki; sprawdź pełne dekodowanie, zgodność kroków z bieżącym narzędziem, cursor/zoom, czytelność UI, brak prywatnych treści oraz synchronizację dźwięku. Dopiero wtedy wypełnij review i wykonaj `studio.py pack`. Publikacja wymaga osobnej zgody.

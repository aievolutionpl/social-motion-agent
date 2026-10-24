# Premium intro: 30 sekund, 16:9

[Obejrzyj gotowy film](../../docs/media/premium-intro.mp4).

Pokazówka Social Motion Agent: 1920 × 1080, 30 FPS, polski lektor, napisy, muzyka instrumentalna, generowana scenografia i autentyczne widoki skilli w Codexie.

## Odtwórz po pobraniu

W głównym katalogu repozytorium, z Pythonem 3.11+, Node 22+ i FFmpeg/ffprobe w PATH:

```bash
npm ci
python -S scripts/premium_intro.py --render
```

Skrypt tworzy nową produkcję w `output/jobs/`, kopiuje lokalne źródła, renderuje animację, dodaje gotowy miks stereo i sprawdza parametry MP4. Nie wymaga kont AI, kluczy API, submodułów ani ponownego generowania materiałów. Pierwsze uruchomienie może pobrać Chromium. Pliki istniejących produkcji pozostają bez zmian.

## Co jest w środku i jak edytować

| Plik | Rola |
| --- | --- |
| `source/index.html` | Cała kompozycja, scena po scenie, ruch GSAP i napisy w czasie |
| `source/frame-tokens.css` | Kolory, typografia, odstępy i bezpieczne pola |
| `source/media/` | Dwa tła imagegen, dwa prawdziwe zrzuty Codexa, font Inter i licencja OFL |
| `audio/voice.mp3` | Wygenerowana polska narracja |
| `audio/music.mp3` | Oryginalny wygenerowany instrumental |
| `audio/mix.wav` | Gotowy 30-sekundowy miks stereo używany przy odtwarzaniu |
| `audio/mix-filter.txt` | Filtr FFmpeg do odtworzenia miksu z osobnych ścieżek |
| `captions.srt`, `source/captions.json` | Napisy i ich znaczniki czasu |
| `narration.txt`, `storyboard.json` | Tekst lektora i plan dziesięciu scen |
| `voice-request.json`, `music-request.json`, `voice-alignment.json` | Parametry generowania bez danych dostępu i wyrównanie słów lektora |
| `provenance.json` | Pochodzenie materiałów i prompty generowania |

Po zmianie tekstu lektora trzeba wygenerować nowe audio i dopasować napisy. Gotowy plik nie wymaga takiej generacji. Zrzuty Codexa pokazują rzeczywiste dokumenty Social Motion Studio i Motion Effect Picker; najazdy i zmiana panelu są animacją zrzutów, a nie ciągłym nagraniem wykonania zadania przez agenta.

Miks można odtworzyć z tego katalogu:

```bash
ffmpeg -n -i audio/voice.mp3 -i audio/music.mp3 -filter_complex_script audio/mix-filter.txt -map "[out]" -c:a pcm_s24le audio/remix.wav
```

## Materiały i zgoda na publikację

Właściciel projektu zatwierdził publikację tego filmu i wszystkich jego źródeł na GitHubie 24 października 2026. Publikowany jest wynik syntezy głosu, nie model głosu, identyfikator konta ani dane uwierzytelniające. Kod ma licencję repozytorium; głos, muzyka, znaki i materiały generowane nie otrzymują automatycznie licencji MIT. Nie zakładaj prawa do klonowania osoby ani odsprzedaży ścieżek. Inter zachowuje SIL OFL, GSAP swoją licencję. Szczegóły: [prawa do mediów](../../docs/MEDIA_RIGHTS.md).

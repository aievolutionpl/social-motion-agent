# Kinetic Walk & Talk

Pionowa rolka z prezenterem idącym do kamery, małymi napisami prowadzącymi i dużymi
kinetycznymi hasłami. Tekst może przechodzić za sylwetką; krótkie zoomy, rozmycia
i punktowy dźwięk podkreślają znaczenie wypowiedzi. [Skill](../skills/kinetic-walk-talk/SKILL.md)
zawiera plan zdjęciowy, wariant AI, analizę referencji i biblię stylu.

## Rozpoczęcie

```bash
python -S studio.py route kinetic-walk-talk
python -S studio.py new "Moja rolka" --kind kinetic-walk-talk --format 9:16 --duration 30
# JOB to ścieżka zwrócona przez new
python -S studio.py walk-talk prepare JOB --mode footage
```

Tryby `footage`, `recording` i `ai` określają plan pozyskania ujęć. `prepare` tworzy
`source/walk-talk.json` i `source/walk-talk-plan.md`. Nie generuje filmów, nie
uruchamia płatnych usług i nie wypełnia odpowiedzi w briefie. Uzupełnij normalne
intake, research i storyboard rzeczywistymi informacjami. Znany styl jest już
kierunkiem wizualnym; nie trzeba zaczynać wyboru estetyki od nowa.

## Ujęcia, głos i sylwetka

**Nagranie realne:** kamera cofa się przed idącą osobą. Zachowaj pełną sylwetkę,
kontakt wzrokowy i przestrzeń nad głową. Nagraj bliski, wyraźny głos. Zmontuj bazę
przez istniejący workflow montażu do długości produkcji.

**AI:** skorzystaj z dostępnego, autoryzowanego dostawcy. Generuj krótkie ujęcia
tej samej osoby i stroju, bez napisów. Osobno kontroluj mowę, lip-sync i ciągłość
chodu. Prompty są w skillu; te lokalne komendy nie dostarczają generatora ani konta.

**Tekst za osobą:** przygotuj przezroczyste wycięcie postaci z identycznym pełnym
kadrem, długością, cropem i timingiem jak baza. Do ruchu używaj zgodnego z przeglądarką
wideo z alfą, np. sprawdzonego WebM; PNG z alfą nadaje się do scen nieruchomych.
`compose` nie segmentuje człowieka ani nie potwierdza jakości alfy. Obejrzyj włosy,
dłonie i nogi w ruchu. Obie warstwy dostają ten sam zoom, zachowując dopasowanie.

Zarejestruj pliki przez `asset-add`, np.:

```bash
python -S studio.py asset-add JOB --file base.mp4 --source "Własne nagranie" --rights "Własny materiał" --purpose "Baza spaceru"
python -S studio.py asset-add JOB --file presenter-alpha.webm --source "Wycięcie z własnej bazy" --rights "Własny materiał" --purpose "Sylwetka przed tekstem"
```

## Specyfikacja kompozycji

Edytuj `source/walk-talk.json`. Poniższe identyfikatory są opisowe; wstaw rzeczywiste
ID zwrócone przez `asset-add`. Przykładowe słowa i sekundy zastąp treścią oraz czasami
z końcowego głosu.

```json
{
  "schema_version": 1,
  "mode": "footage",
  "background_asset": "ID_BAZY",
  "foreground_asset": "ID_SYLWETKI",
  "audio_asset": null,
  "captions": [
    {"start": 0, "end": 0.8, "text": "Pokaż proces."},
    {"start": 0.8, "end": 1.7, "text": "Krok po kroku."}
  ],
  "accents": [
    {"start": 0.1, "end": 1.7, "text": "OD POMYSŁU\nDO FILMU", "color": "blue", "behind_subject": true, "x": 50, "y": 23, "size": 140}
  ],
  "punches": [{"start": 1.7, "end": 2.2, "zoom": 1.12}],
  "sound_cues": [{"start": 1.65, "end": 2.2, "note": "Krótki whoosh na zmianę skali; do wykonania w miksie"}]
}
```

`captions` są małe i białe. `accents` mogą występować z przodu lub z tyłu; kolory:
`white`, `black`, `orange`, `blue`, `cyan`. `x/y` są procentami, `size` to piksele
w kompozycji 1080×1920. Niezależne akcenty mogą się nakładać, gdy układ tego wymaga.
Podpisy i zoomy nie mogą nakładać się we własnej warstwie czasowej. Wszystkie czasy
muszą mieścić się w produkcji. Hasło za sylwetką wymaga `foreground_asset`.

```bash
python -S studio.py setup
python -S studio.py walk-talk compose JOB
python -S studio.py render-html JOB --name walk-talk-v1 --quality draft
python -S studio.py probe JOB --render renders/walk-talk-v1.mp4
python -S studio.py sheet JOB --render renders/walk-talk-v1.mp4
```

Komenda sprawdza ID, sumy plików, długość mediów i wymiary warstw. Kopiuje wybrane
media, font z licencją i przypięty GSAP do `source/`, tworząc edytowalne `index.html`.
Kompozycja ma deterministyczne `window.seek(t)` i pauzowaną oś GSAP dla HyperFrames.
Istniejące pliki kompozycji są zachowywane; przed ponownym compose przenieś poprzedni
`index.html` i zmieniane zależności do własnej wersji źródeł. Możesz też edytować HTML.

Nie są automatycznie wykonywane: zmiana pleneru dzień/noc, licznik dowodu, grafiki 3D,
segmentacja, wygenerowanie prezentera ani synteza muzyki. Agent może dodać je do
edycyjnych źródeł przy pomocy dostępnych narzędzi. Sam compose jest lokalnym etapem
kompozycji i nie zmienia bramek renderowania ani oceny produkcji.

## Dźwięk

Domyślnie film zachowuje oryginalną ścieżkę bazy. Jeżeli `audio_asset` wskazuje
zarejestrowany pełny miks, baza i sylwetka są wyciszane, a ten miks zastępuje audio.
Zapobiega to podwajaniu narracji. Przygotuj go z głosu, podkładu i wykonanych SFX.
`sound_cues` to wyłącznie notatki dla montażysty.

Wyszukaj lokalne próbki: `python -S studio.py sfx find whoosh --category transition`.
Stosuj [zasady biblioteki](../SOUND%20EFFECTS/README.md), w tym maksymalny gain 0.5.
Możesz dodać SFX do renderu przez istniejące `studio.py edit JOB fx`, zarejestrować
nowy wynik i sprawdzić finalny plik. Analiza oryginału nie ustaliła utworu ani BPM;
propozycja elektronicznego instrumentalu jest kierunkiem nowej muzyki.

## Kontrola i instalacja

Sprawdź maski w ruchu, synchronizację z rzeczywistą mową, polskie znaki, czytelność
na telefonie, CTA oraz końcowy miks. Normalny workflow wymaga recenzji tego samego
renderu i SHA przed `pack`. Bez odsłuchu nie wpisuj zatwierdzenia audio.

```bash
python -S scripts/install_skill.py --skill kinetic-walk-talk --agent codex
python -S scripts/install_skill.py --skill kinetic-walk-talk --agent codex --execute
```

Ten sam wybór działa z `--agent claude|hermes` i `--dest`. Instalator zachowuje
różniące się istniejące instalacje. Skill zawiera trzy referencje tekstowe; źródłowa
rolka i kadry użytkownika pozostają poza publiczną dystrybucją.

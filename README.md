<p align="center"><img src="docs/images/cover.png" alt="Social Motion Agent. Produkt AI EVOLUTION POLSKA." width="100%"></p>

<h1 align="center">Social Motion Agent</h1>
<p align="center"><strong>Od pomysłu do filmu. Z agentem AI, HyperFrames i kontrolą jakości.</strong></p>
<p align="center">Produkt <a href="https://www.aievolutionpolska.pl/">AI EVOLUTION POLSKA</a> · Open source · Local first</p>
<p align="center"><a href="https://github.com/aievolutionpl/social-motion-agent/actions/workflows/ci.yml"><img src="https://github.com/aievolutionpl/social-motion-agent/actions/workflows/ci.yml/badge.svg" alt="CI"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-7B5CFF" alt="MIT"></a> <a href="docs/README.en.md">English</a> · <a href="START_HERE.md">Start agenta</a> · <a href="docs/PRODUCTION.md">Produkcja</a></p>

**Twórz explainery, premiery produktów, Reels i filmy edukacyjne jako edytowalne projekty.** Agent pomaga przejść od briefu i researchu do scen, materiałów, renderu i sprawdzonego pakietu.

Social Motion Agent to narzędzie CLI i zestaw instrukcji dla agentów, a nie autonomiczny generator „jednym kliknięciem”. Działa z agentami potrafiącymi czytać pliki i wykonywać polecenia, np. Codex, Claude Code lub Cursor. Model AI wybierasz w swoim środowisku.

## Zobacz prawdziwy render

![Fragment demonstracyjnego filmu wyrenderowanego przez HyperFrames](docs/images/demo.gif)

*8-sekundowa, niema kompozycja HTML z repozytorium. GIF pokazuje rzeczywisty render; okładka i grafika procesu są ilustracjami koncepcyjnymi wygenerowanymi przez AI.*

## Kompletny warsztat w repozytorium

Dołączamy **126 oryginalnych efektów dźwiękowych**, **9 teł WebP**, **3 fonty z licencjami OFL**, **7 lokalnych skilli** oraz katalog **913 wpisów z 34 repozytoriów narzędziowych**. Katalog obejmuje również recipes, szablony i fixture testowe.

Media są bezpośrednio w `SOUND EFFECTS/` i `assets/`. Pełne źródła narzędzi znajdują się w `tools/repos/` jako submoduły Git, z przypiętymi wersjami i oryginalnymi licencjami.

```bash
# Pełna instalacja źródeł i materiałów
git clone --recurse-submodules https://github.com/aievolutionpl/social-motion-agent.git
cd social-motion-agent
npm ci
python -S scripts/bootstrap_library.py --check
python -S scripts/library_check.py
```

**Pobrałeś ZIP lub masz już zwykły klon?** Uruchom `python -S scripts/bootstrap_library.py`. GitHub ZIP zawiera media, ale nie zawartość submodułów; instalator uzupełni wszystkie źródła. Nie instaluje automatycznie zależności 34 narzędzi ani nie uruchamia ich kodu.

[Zawartość i pobieranie biblioteki](docs/LIBRARY.md) · [Katalog skilli](skills/INDEX.md) · [Narzędzia](tools/INDEX.md) · [Prawa do mediów](docs/MEDIA_RIGHTS.md)

## Pierwszy film

Wymagania: **Python 3.11+**, **Node.js 22+**, **FFmpeg i ffprobe** dostępne w PATH. Pythonowy rdzeń nie wymaga pakietów pip.

```bash
git clone https://github.com/aievolutionpl/social-motion-agent.git
cd social-motion-agent
npm ci
python -S studio.py doctor
python -S studio.py demo --render
```

Komenda zwraca katalog produkcji, ścieżkę MP4 i wynik kontroli technicznej. Pierwszy render może pobrać Chrome. Render demo nie wymaga kluczy API ani płatnej generacji.

```bash
# Wersja pionowa: 1080 × 1920
python -S studio.py demo --format 9:16 --render

# Podgląd edytowalnego przykładu w HyperFrames Studio
npm run preview
```

Pliki powstają w `output/jobs/<id>/`. Kolejne uruchomienie demo tworzy nową produkcję.

## Co dostajesz

| Potrzeba | Rozwiązanie |
| --- | --- |
| Piękny motion zamiast przypadkowych przejść | HyperFrames, lokalny GSAP, szablony typografii i instrukcje motion design |
| Agent rozumiejący etap pracy | Brief, research, storyboard, rejestr assetów i `resume` |
| Montaż własnych materiałów | FFmpeg: ujęcia, kadrowanie, lektor, muzyka, ducking i efekty |
| Wersje na różne kanały | Profile 16:9, 9:16, 4:5, 1:1; kompozycję należy sprawdzić w każdym formacie |
| Kontrola przed oddaniem filmu | Wymiary, FPS, długość, wymagane audio, SHA plików i dowody recenzji |
| Praca bez klientowskiego chaosu | Osobny katalog każdej produkcji, edytowalne źródła i HANDOFF.md |
| Własny głos i obrazy | Opcjonalny adapter ElevenLabs; obrazy i przebitki importowane z Twoich narzędzi |

## Jak działa

![Sześć etapów: brief, research, storyboard, compose, review, export](docs/images/workflow.png)

1. **Brief**: cel, widz, styl, audio i ograniczenia. Zapisujesz faktyczne odpowiedzi.
2. **Research**: źródła faktów, referencje wizualne i prawa do materiałów.
3. **Storyboard**: sceny, czas, tekst i rola każdego assetu.
4. **Compose**: agent pisze HTML/GSAP albo układa materiały na osi FFmpeg.
5. **Review**: oglądasz klatki, czytasz napisy, słuchasz miksu. Wynik jest przypisany do konkretnego pliku.
6. **Export**: pakiet zawiera master, źródła, rejestr materiałów i dowody kontroli.

Zmiana kompozycji unieważnia poprzednią kontrolę techniczną. Niezaakceptowany film nie przejdzie przez `pack`. Narzędzie sprawdza kompletność dowodów, ale nie zastępuje ludzkiego osądu jakości i praw do mediów.

## Daj zadanie agentowi

Otwórz repozytorium w swoim narzędziu AI i użyj:

> Przeczytaj AGENTS.md i START_HERE.md. Przygotuj 20-sekundowy explainer mojego produktu w formacie 9:16. Zacznij od briefu, zaproponuj kierunek wizualny, wykonaj research i storyboard. Użyj HyperFrames. Najpierw pokaż draft. Nie uruchamiaj płatnych usług ani nie publikuj bez mojej zgody.

```bash
python -S studio.py new "My product" --kind explainer --format 9:16 --duration 20
python -S studio.py route explainer
python -S studio.py resume output/jobs/JOB_ID
python -S studio.py check output/jobs/JOB_ID --stage assets
python -S studio.py render-html output/jobs/JOB_ID --name draft
python -S studio.py sheet output/jobs/JOB_ID --render renders/draft.mp4
```

`JOB_ID` zastąp nazwą zwróconego katalogu. Przed renderem uzupełnij plan i utwórz `source/index.html`. Szczegółowe kroki: [produkcja](docs/PRODUCTION.md), [HyperFrames](docs/HYPERFRAMES.md), [CLI](docs/CLI.md).

## Architektura

```mermaid
flowchart LR
    A[Agent + brief] --> B[Job JSON + storyboard]
    B --> C[HTML + GSAP]
    B --> D[Footage + timeline]
    C --> E[HyperFrames]
    D --> F[FFmpeg]
    E --> G[Probe + visual/audio review]
    F --> G
    G --> H[Local delivery package]
```

- `studio.py`: jeden punkt wejścia.
- `scripts/studio_core.py`: stan produkcji, pochodzenie materiałów, kontrola i pakiet.
- `scripts/hyperframes_adapter.py`: lokalny lint, render, log i probe.
- `skills/`: lokalne instrukcje do briefu, produkcji i projektowania ruchu.
- `examples/launch/`: działająca kompozycja do nauki i modyfikacji.
- `templates/`: tokeny wizualne i pomocnicze szablony.
- `sources.lock.json` i `.gitmodules`: dokładne wersje pełnych źródeł narzędziowych.

## Prywatność i integracje

Repozytorium zawiera kod, neutralne przykłady i publiczne oznaczenie autora produktu. Nie zawiera materiałów klientów, historii kampanii, prywatnych głosów ani połączeń kont.

Sekrety ustawiasz we własnym środowisku. `doctor` nie czyta kluczy i nie testuje kont w sieci. Dane produkcji pozostają w ignorowanym przez Git katalogu `output/`. Polecenia rdzenia nie publikują filmów.

[Providerzy i koszty](docs/PROVIDERS.md) · [Bezpieczeństwo](SECURITY.md) · [Licencje zależności](THIRD_PARTY_NOTICES.md)

## Testy i granice

```bash
python -S -B -m unittest discover -s tests -v
python -S scripts/smoke_test.py
python -S scripts/release_check.py
```

CI uruchamia testy na Pythonie 3.11 i 3.13, test montażu FFmpeg oraz rzeczywisty render HyperFrames. Testy skatalogowanych bibliotek uruchamiają się po pobraniu źródeł. Testy Playwright są pomijane, gdy przeglądarka pomiarowa nie jest zainstalowana.

- Demo i podstawowy montaż działają bez płatnych API.
- Płatne generowanie głosu wymaga Twojego konta i jawnego `--execute`.
- Źródła OpenScreen i katalogu ruchu są dołączone przez submoduły; runtime OpenScreen i dodatkowy adapter video-studio wymagają osobnej instalacji.
- Podgląd HyperFrames jest lokalnym edytorem; repo nie zawiera osobnej aplikacji SaaS.
- Spójność renderu między systemami zależy m.in. od fontów i przeglądarki; dla ściśle powtarzalnego środowiska użyj oficjalnej ścieżki Docker HyperFrames.

[Wyniki weryfikacji](docs/VALIDATION.md) · [Jak współtworzyć](CONTRIBUTING.md)

## AI EVOLUTION POLSKA

Budujemy praktyczne narzędzia do pracy z AI. Social Motion Agent łączy proces twórczy z kodem, który można sprawdzić, zmienić i uruchomić lokalnie.

[Strona AI EVOLUTION POLSKA](https://www.aievolutionpolska.pl/) · [GitHub](https://github.com/aievolutionpl)

Kod: [MIT](LICENSE). Zależności mają własne licencje. Projekt jest niezależny od HeyGen i nie sugeruje jego poparcia.

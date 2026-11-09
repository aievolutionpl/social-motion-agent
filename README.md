# Social Motion Agent

![Social Motion Agent — neonowy laptop z osią montażu](docs/images/social-motion-agent-neon.jpg)

Daj agentowi nagrania i opisz, jaki film chcesz zrobić. Agent zaproponuje styl, przygotuje montaż i pokaże ci podgląd MP4. Ty wybierasz kierunek i decydujesz, co poprawić.

[Szybki start](#szybki-start-z-agentem) · [Możliwości](#co-możesz-zrobić) · [Skille i efekty](#ile-jest-skilli-i-efektów) · [Współtworzenie](#autor-licencja-i-współtworzenie) · [English](docs/README.en.md)

## Szybki start z agentem

1. **Otwórz repo w agencie.** Skopiuj adres `https://github.com/aievolutionpl/social-motion-agent.git` i poproś Codexa, Claude Code lub Hermesa z terminalem o pobranie repo. Jeśli masz już kopię, otwórz jej folder.
2. **Daj mu materiały i zadanie.** Udostępnij nagrania w folderze projektu i wskaż ich ścieżkę. Powiedz, gdzie ma trafić film, ile ma trwać i czego potrzebujesz, np. polskich napisów.
3. **Wybierz styl i obejrzyj podgląd.** Agent proponuje 2–3 kierunki, jeśli styl jest jeszcze otwarty. Po wyborze przygotowuje plan scen i wersję MP4. Uwagi możesz podać z czasem, np. „w 00:04 powiększ napis”.

**Pierwszy prompt do wklejenia**

> Pobierz https://github.com/aievolutionpl/social-motion-agent.git, jeśli nie masz jeszcze kopii. Przeczytaj START_HERE.md i przygotuj narzędzia do lokalnego renderowania. Zmontuj 20-sekundową rolkę 9:16 z nagrań w folderze `media/`. Dodaj polskie napisy. Najpierw pokaż mi dwa pomysły na otwarcie filmu i poczekaj na mój wybór. Potem przygotuj podgląd MP4 i podaj ścieżkę do pliku.

Jeśli chcesz tylko sprawdzić, czy wszystko działa, uruchom próbny render na dołączonych materiałach. Możesz też zlecić ten krok agentowi. Potrzebujesz Pythona 3.11+, Node.js 22+ z npm oraz FFmpeg i ffprobe.

```bash
git clone https://github.com/aievolutionpl/social-motion-agent.git
cd social-motion-agent
python -S scripts/quickstart.py --browser --smoke
```

**Jak działa skill?** [Creative Director](skills/creative-director/SKILL.md) to instrukcja, z której agent korzysta, żeby dobrać narzędzia i poprowadzić pracę. Możesz zacząć z otwartej kopii repo. [Instalacja skilla w profilu agenta](#zainstaluj-przenośny-skill) przydaje się, gdy chcesz wywoływać go także z innych projektów.

**Brief → wybór stylu → plan scen → podgląd MP4 → twoje uwagi → gotowy film.**

[![Animowane demo procesu montażu](docs/images/editorial-loop.gif)](docs/media/editorial-loop.mp4)

[Obejrzyj demo · 8 s · bez dźwięku](docs/media/editorial-loop.mp4) · [Jak odtworzyć demo](examples/editorial-loop/README.md) · [Strona projektu](https://social-motion-agent-aiep.pages.dev/)

## Co możesz zrobić

| Zadanie | Przykładowy wynik |
| --- | --- |
| Zmontować własne ujęcia | Rolka lub Short z cięciami, napisami, muzyką i efektami dźwiękowymi |
| Zrobić teaser produktu | Motion graphics z dużą animowaną typografią, przejściami i ruchem zsynchronizowanym z muzyką |
| Przygotować tutorial lub demo aplikacji | Plan nagrania ekranu, podpisy i animowane wskazówki prowadzące widza po interfejsie |
| Zrobić rolkę z prezenterem | Napisy zsynchronizowane z mową, animowane hasła i tekst za sylwetką przy dostępnej masce alfa |
| Animować interfejs lub stronę | Działająca animacja w projekcie webowym albo pokaz produktu w MP4 |

HyperFrames renderuje lokalne kompozycje HTML/GSAP. Natywne projekty `.hype` wymagają osobnej instalacji Hypermotion. Generowanie ujęć AI, lektora lub masek zależy od dostępnych narzędzi i materiałów. Do synchronizacji napisów słowo po słowie potrzebujesz rzeczywistych znaczników czasu. [Instrukcja produkcji](docs/PRODUCTION.md) · [Providerzy](docs/PROVIDERS.md).

## Ile jest skilli i efektów

| Co liczysz | Ile | Co zawiera |
| --- | ---: | --- |
| Lokalne skille i punkty wejścia | **12** | 14 plików `SKILL.md`, w tym dwa dodatkowe odsyłacze do Creative Director i Kinetic Walk & Talk |
| Przypięte repozytoria rozszerzeń | **38** | Zewnętrzne paczki ze skillami, recepturami, szablonami i przykładami |
| Katalog efektów ruchu | **637 efektów i 11 receptur** | Zewnętrzny katalog do doboru efektów. Niektóre wpisy mają przykładowy klip i szablon HTML |
| Efekty dźwiękowe w repo | **126** | Pliki WAV i MP3. Przed wykorzystaniem sprawdź [status praw do mediów](docs/MEDIA_RIGHTS.md) |
| Lokalne presety i atlas stylów | **13 presetów Canvas i 14 stylów atlasu** | Presety pokazują ruch w przeglądarce, a atlas pomaga wybrać kierunek filmu |

Aby pobrać sam katalog efektów i znaleźć przykłady, uruchom z katalogu głównego repo:

```bash
git submodule update --init tools/repos/awesome-ai-motion
python -S studio.py motion find "zoom" --limit 5
python -S studio.py motion presets
python -S studio.py styles list
```

[Indeks skilli i rozszerzeń](skills/INDEX.md) · [Przegląd biblioteki](docs/LIBRARY.md)

## Ścieżki produkcji

| Zadanie | Proces | Wynik |
| --- | --- | --- |
| **Film**: Reels, Shorts, premiera, explainer, tutorial | Brief → kierunek → storyboard → kompozycja → render → recenzja | MP4, źródła, materiały i dowody kontroli |
| **Kinetic Walk & Talk**: pionowa rolka z prezenterem | Ujęcia → czasy słów → podpisy i hasła → sylwetka alpha → miks → render i recenzja | MP4 9:16, edytowalny HTML i plan produkcyjny |
| **Kinetic launch**: teaser i premiera z dużą typografią | Brief → beat sheet → spec.js → motion blur → kontrola ruchu i recenzja | MP4 16:9, edytowalna kompozycja, audio i dowody renderu |
| **Strona**: landing page, produkt, poprawa istniejącego projektu | Oferta → układ → typografia i obrazy → implementacja → przegląd w przeglądarce | Działający projekt w jego obecnym stacku |
| **UI motion**: pokaz produktu, animowana makieta, sekcja strony | Zgodność statyczna → akcja i rezultat → ruch → kontrola formatu | Animacja na stronie albo film zgodnie z briefem |

`creative-director` ma **12 modułów referencyjnych**: brief i kierunek, reżyserię wideo, **motion, nie slajdy**, style explainerów, web design, animację UI, receptury wizualne, **anti-slop**, **humanizer PL/EN**, dobór narzędzi, recenzję oraz źródła. Agent czyta tylko potrzebne moduły.

- **Kierunek przed kodem:** dwie lub trzy propozycje pokazują konkretny obraz, typografię, rytm i miejsce użycia; w razie potrzeby styleboard lub reprezentatywną scenę.
- **Pytania bez powtarzania:** znane odpowiedzi trafiają do briefu; pytania dotyczą brakujących decyzji. Drobna poprawka nie zaczyna produkcji od nowa.
- **Ruch z sensem:** akcja → zmiana stanu → czytelny rezultat. Osobne zasady dla strony i filmu.
- **Ludzki język:** konkrety, prawdziwe dowody i zachowany głos marki.
- **Retencja:** hook, dowód, payoff i warianty do porównania. Skill nie obiecuje wiralowości ani nie fabrykuje wyników.

## Sprawdzone źródła, przypięte wersje

Do explainerów dostępne są też dwa niezależne kierunki: **`isometric-line-art`** — izometryczny rysunek techniczny, montaż, przekroje i przepływy; **`flat-vector`** — ilustracje 2D, morfowanie kształtów i płynne zmiany stanu. Atlas ma teraz 14 stylów (12 źródłowych + 2 lokalne). Użyj `python -S studio.py styles recipe <slug>` i przeczytaj [zasady explainerów](skills/creative-director/references/explainer-styles.md). Dobieraj temat, format i audio w briefie filmu.

| Źródło | Wkład |
| --- | --- |
| [Elaya AI Design Skills](https://github.com/elayadesign/ai-design-skills) | Strategia landing page, zgodność statycznego UI i znaczący motion |
| [Taste Skill v2](https://github.com/Leonxlnx/taste-skill) | Art direction, typografia, kompozycja i ocena screenshotów |
| [Hypermotion](https://github.com/psiddharthdesign/hypermotion) | Profil marki, reżyseria explainera, edytowalne sceny `.hype` |
| [Scenario Kinetic Film](https://www.scenario.com/explorations/kinetic-film/) | Osobny, weryfikowany pakiet silnika: sceny na beat gridzie, kamera CSS 3D i motion blur; trasa `kinetic-launch` |
| [Unslop](https://github.com/heydamir/unslop) | 4-etapowy audyt redline (`Spacing`, `Color & icons`, `Type & copy`, `Details`), tinted neutral ramps, efekty Canvas i sceny Before→After (`unslop-story`) |
| [Opus 5.5 Video Styles](https://github.com/HiAPIAI/awesome-opus-5-5-video-styles) + [Opus 5.5 Videos](https://github.com/yihui-dev/awesome-opus5-5-videos) | 12 kanonicznych stylów wideo, 1128 promptów referencyjnych, fizyka sprężyn (`stepSpring`, `liquidSpan`) i kontrakt podagenta `<inputs>/<direction>/<structure>/<build>/<gotchas>` |
| Dotychczasowa biblioteka motion | Kinetic type, audio, mapy, wykresy, 3D, tutoriale i montaż |

Wersje i licencje: [sources.lock.json](sources.lock.json). Oryginalne licencje zostają zachowane. Brief, istniejąca marka i dostępność mają pierwszeństwo przed stylistycznymi domyślnościami upstream — bez obowiązkowych zakazów kolorów i liczby animacji.

## Przygotuj potrzebne skille

Do pobrania źródeł wystarczą Python 3.11+ i Git. Nie uruchamia to kodu upstream ani płatnych usług.

```bash
git clone https://github.com/aievolutionpl/social-motion-agent.git
cd social-motion-agent
python -S studio.py skills plan --mode video
python -S studio.py skills setup --mode video
python -S studio.py skills check --mode video
```

Tryby: `video`, `website`, `ui-motion`. Film przygotowuje Hypermotion i Elaya; strona — Elaya i Taste; UI motion — wszystkie trzy źródła. `check` działa offline i sprawdza źródła, **nie potwierdza działania rendererów ani kont**.

Cała biblioteka obejmuje **38 przypiętych repozytoriów**. Użyj `studio.py find`, `studio.py route`, `studio.py styles`, `studio.py unslop-story` i `studio.py motion`, aby dobrać specjalistę lub styl wideo. Pełne pobranie jest opcjonalne:

```bash
python -S scripts/bootstrap_library.py
python -S scripts/library_check.py
```

[Indeks skilli](skills/INDEX.md) · [Biblioteka](docs/LIBRARY.md) · [Wersje źródeł](docs/SOURCE_VERSIONS.md)

## Zainstaluj przenośny skill

Instalator kopiuje cały skill wraz z referencjami. Domyślnie pokazuje plan, zachowuje istniejące instalacje i nie łączy kont.

```bash
python -S scripts/install_skill.py --agent codex
python -S scripts/install_skill.py --agent codex --execute

# Wybierz środowisko, którego używasz
python -S scripts/install_skill.py --agent claude --execute
python -S scripts/install_skill.py --agent hermes --execute
```

Własny katalog skilli: `--dest`. Do filmów zainstalowany skill prowadzi do roboczej kopii Social Motion Agent; strony mogą korzystać z jego wskazówek bez renderera wideo. [Ścieżki profili i kompatybilność](docs/AGENT_SETUP.md).

## Wyrenderuj pierwszy film

Wymagania: **Python 3.11+, Node.js 22+, FFmpeg i ffprobe**. Pythonowy rdzeń nie wymaga pakietów pip.

```bash
python -S studio.py setup
python -S studio.py demo --format 9:16 --render

# Kinetic Film: najpierw oficjalny pakiet silnika i opcjonalne zależności
python -S studio.py kinetic setup --source /path/to/scenario-kinetic-film
python -m pip install -r requirements-kinetic.txt
python -S studio.py kinetic doctor
python -S studio.py kinetic demo --render --res 720 --samples 2
```

`setup` instaluje przypięte zależności przez `npm ci --ignore-scripts`. Pierwszy render może pobrać Chromium. Przykłady korzystają z dołączonych materiałów, bez płatnej generacji.

Kinetic Film jest opcjonalnym silnikiem pobieranym osobno od autora. `kinetic setup` sprawdza sumy plików i tworzy lokalny cache, a `render-kinetic` zachowuje karty produkcji, kontrolę dynamiki i dowody zgodności źródeł z MP4. Bieżące kompozycje Kinetic są poziome 16:9; pion wymaga osobnego układu. [Pełny workflow](docs/KINETIC_FILM.md).

**HyperFrames** renderuje lokalne HTML/GSAP. **Hypermotion** jest osobną aplikacją z projektami `.hype`, CLI i MCP. Agent pobiera jego skille, a przed natywnym eksportem sprawdza runtime i krótki render. Nie zamienia po cichu silnika wskazanego przez użytkownika. [Hypermotion — konfiguracja](docs/HYPERMOTION.md).

![Grafika koncepcyjna — oś montażu i pomarańczowa wstęga](docs/images/social-motion-agent-studio.jpg)

![Rzeczywisty fragment demonstracyjnego renderu](docs/images/demo.gif)

[Kinetic Film 30 s ze źródłami](examples/kinetic-launch/README.md) · [Showcase 36 s](examples/showcase/README.md) · [HyperFrames](docs/HYPERFRAMES.md)

<details>
<summary><strong>Katalog możliwości i ścieżek produkcji</strong></summary>

## Nowe style motion

**Kinetic Walk & Talk** dodaje rolki z chodzącym prezenterem, małymi podpisami i dużymi
animowanymi hasłami, także za sylwetką. Trasa `kinetic-walk-talk` obejmuje plan nagrania,
prompty do czystych ujęć AI, kompozycję warstw i plan dźwięku. Lokalne `walk-talk prepare`
i `walk-talk compose` tworzą edytowalne źródła HyperFrames z dostarczonych mediów;
generowanie ujęć i segmentacja korzystają z osobno dostępnych narzędzi.
[Skill](skills/kinetic-walk-talk/SKILL.md) · [Instrukcja i przykład JSON](docs/KINETIC_WALK_TALK.md).

**Motion, nie slajdy** — 13 deterministycznych stylów Canvas z `seek(t)` w laboratorium [examples/motion-styles](examples/motion-styles/README.md): Riso Print, Décollage, Optical Moiré oraz 10 nowych kierunków: **Grainy Gradient**, **Poster Color-Block**, **Flat Pop z wycinkami zdjęć**, **Visual Journalism**, **Vintage Sketch**, **Cartoon Collage**, **White Catalog**, **Brutalist Mono**, **Luxury Dark** i **Continuous Action**. Do tego:

- `python -S studio.py directions brief --for "aplikacja AI dla studentów"` — szkielet style briefu, 3 kandydackie koncepty z menu 19 konceptów openerów i 3 kierunki stylu z 10;
- `python -S studio.py directions compare "FP1" "FP2"` — czy nowy film różni się strukturą od poprzedniego (odcisk: koncept · sceny · obiekty · otwarcie · zakończenie);
- `python -S studio.py motion lint scena.html` — mechaniczny test „to film, nie prezentacja” i kontraktu renderu (losowość, zegar, `window.seek`, sekcje przełączane opacity, kicker+tytuł+body, autoplay wideo, przejścia CSS);
- moduł [Motion, not slides](skills/creative-director/references/motion-not-slides.md) oraz helpery kamery ujęć, żywego ziarna i asymetrycznego rytmu w `templates/motion-helpers.js`.

Idee zaadaptowane z [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion) (MIT), tekst i kod napisane od nowa. Presety to przykłady, nie gotowe kompozycje HyperFrames.

## Director Suite: 3 nowe ścieżki produkcji

Z [Explainroo](https://github.com/vincentsch/explainroo), [Argo](https://github.com/shreyaskarnik/argo) i [Huashu Motion](https://github.com/alchaincyf/huashu-motion) zaadaptowaliśmy praktyczne wzorce, bez kopiowania obcych silników do repo:

- **Explainer:** szkic Explainroo, lokalne napisy SRT i zdarzenia zsynchronizowane z **rzeczywistymi** czasami słów z alignera. Polski lektor wymaga nagrania lub zewnętrznego TTS.
- **Product demo:** szkic Playwright + Argo (manifest scen, markery narracji, overlay), do uzupełnienia prawdziwymi akcjami i uruchomienia w środowisku testowym.
- **Motion launch:** beat sheet, kontrola rytmu scen i komentarze do konkretnej sekundy oraz współrzędnych kadru. Handoff do Huashu Motion nie udaje gotowego projektu `om`.

```bash
# Po utworzeniu joba i zapisaniu jego storyboard.json
python -S studio.py director plan output/jobs/ID --profile launch
python -S studio.py director qa output/jobs/ID --profile launch
python -S studio.py director handoff output/jobs/ID --profile demo
python -S studio.py director captions output/jobs/ID --alignment source/alignment.json
python -S studio.py director feedback output/jobs/ID --at 4.2 --x 0.6 --y 0.3 --comment "Powiększ CTA"
```

Komendy przygotowują edytowalne źródła i kontrolę planu, **nie instalują generatorów wideo, nie renderują i nie zatwierdzają automatycznie jakości**. Dla eksportów używaj `--overwrite` tylko gdy chcesz zastąpić pliki z własnymi poprawkami.

[Pełna instrukcja i ograniczenia](docs/DIRECTOR_SUITE.md) · [Skill](skills/director-suite/SKILL.md).

</details>

## Jakość jako część procesu

Każdy film ma osobny katalog `output/jobs/<id>/`. Render jest powiązany z SHA pliku i stanem źródeł z chwili renderowania. Nowa kompozycja wymaga nowego renderu; ponowny `probe` nie zatwierdzi starych klatek jako nowego projektu. Kontrola długości obrazu zapobiega maskowaniu brakujących klatek przez audio.

`pack` wymaga kontroli i recenzji. Sprawdza zapisane dowody, ale nie zastępuje oglądania i odsłuchu. Dla stron agent sprawdza układ, klawiaturę, responsive, reduced motion i stany błędu. Bez narzędzia nie deklaruje wykonania testu.

```bash
python -S -B -m unittest discover -s tests -v
python -S scripts/smoke_test.py
python -S scripts/release_check.py
```

CI obejmuje Linux/Python 3.11 i 3.13, Windows, FFmpeg, rzeczywisty render HyperFrames oraz testy przeglądarkowe. [Produkcja](docs/PRODUCTION.md) · [CLI](docs/CLI.md) · [Weryfikacja](docs/VALIDATION.md)

## Materiały i wydania

126 efektów dźwiękowych, 9 teł, fonty z licencjami OFL i źródła pokazówek. Prawa do mediów są oddzielne od licencji kodu; dokumenty źródłowe licencji biblioteki SFX pozostają do uzupełnienia. [Prawa do mediów](docs/MEDIA_RIGHTS.md) · [Third-party notices](THIRD_PARTY_NOTICES.md).

Sekrety pochodzą z własnego środowiska, produkcje są ignorowane przez Git. Rdzeń nie publikuje filmów; generacje i publikacja wymagają właściwej autoryzacji. [Providerzy](docs/PROVIDERS.md) · [Bezpieczeństwo](SECURITY.md).

[Pełny ZIP v1.1.1](https://github.com/aievolutionpl/social-motion-agent/releases/download/v1.1.1/social-motion-agent-v1.1.1-full.zip) to archiwalne wydanie z 34 źródłami. **Nie zawiera Creative Director ani obecnych poprawek** — użyj aktualnego checkoutu. Nowy pełny ZIP wymaga osobnego zbudowania i publikacji.

## Autor, licencja i współtworzenie

Social Motion Agent stworzyło [AI Evolution Polska](https://www.aievolutionpolska.pl/). Kod udostępniamy na otwartej [licencji MIT](LICENSE). Możesz pobrać projekt, zrobić własny fork, dostosować kod do siebie i udostępniać ulepszenia z zachowaniem informacji o prawach autorskich i treści licencji. Media i zewnętrzne narzędzia mają [osobne warunki](docs/MEDIA_RIGHTS.md).

**Pull requesty są mile widziane.** Masz poprawkę, nowy efekt, preset albo przykład użycia? Zrób fork, wprowadź zmianę na osobnej gałęzi i otwórz pull request. Napisz krótko, co zmieniasz i jak to sprawdziłeś. Przy zmianie wizualnej dołącz podgląd na syntetycznych materiałach. [Zasady współtworzenia](CONTRIBUTING.md).

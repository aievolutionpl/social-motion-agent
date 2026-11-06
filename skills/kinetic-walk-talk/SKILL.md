---
name: kinetic-walk-talk
description: Twórz i montuj pionowe rolki w stylu chodzącego prezentera, kinetycznej typografii, napisów za sylwetką, szybkich zoomów i punktowego sound designu. Używaj przy prośbach o ten styl, kinetic walk and talk lub estetykę dostarczonej referencji; obejmuje nagranie realne, materiał AI i montaż gotowych ujęć.
---

# Kinetic Walk & Talk

Twórz film, w którym prezenter idzie do kamery, a typografia i grafiki wizualizują sens wypowiedzi. Zachowaj połączenie naturalnego nagrania z wyrazistą postprodukcją. Styl jest przenośny na różne osoby, branże i lokalizacje.

## Materiał odniesienia

Przed pierwszym projektem przeczytaj [biblię stylu](references/style-bible.md). Przy analizie podobieństwa używaj [rozpiski referencji](references/reference-breakdown.md). Źródłowy film i kadry nie są częścią publicznej paczki. Jeśli użytkownik je dostarczy, analizuj je w lokalnym katalogu produkcji. Parametry oznaczone jako propozycje są punktami startowymi do nowych produkcji, a nie pomiarami oryginału.

## W Social Motion Agent

Znajdź checkout po `studio.py` i `config/routes.json`; nie wyprowadzaj jego ścieżki z lokalizacji zainstalowanego skilla. Przeczytaj tam `AGENTS.md` i `docs/KINETIC_WALK_TALK.md`. Użyj `studio.py route kinetic-walk-talk`, utwórz produkcję `studio.py new "Tytuł" --kind kinetic-walk-talk --format 9:16 --duration 30` i uruchom `studio.py walk-talk prepare JOB --mode footage|recording|ai`.

Wpisz rzeczywiste znaczniki słów i ID z `asset-add` do `source/walk-talk.json`. `walk-talk compose JOB` tworzy edytowalny `source/index.html`: tło → hasła za sylwetką → dopasowana warstwa alpha → hasła z przodu i podpisy. Najpierw przygotuj bazowy film o długości całej produkcji. Przezroczysta sylwetka wymaga osobnego wycięcia i identycznych czasów oraz kadrowania; komenda nie segmentuje człowieka. Zachowaj oryginalny dźwięk bazy albo dostarcz jeden pełny miks jako `audio_asset`. `sound_cues` są opisem, nie syntezą dźwięku.

Wykorzystuj istniejące intake, brief, research i storyboard. Komendy prepare/compose nie wypełniają odpowiedzi ani nie zatwierdzają etapów. Renderuj przez `render-html`, potem wykonaj `probe`, `sheet`, recenzję i `pack`. Źródła i media pozostają w `output/jobs/<id>/`. Dla SFX z biblioteki stosuj `SOUND EFFECTS/README.md`, w tym limit gain 0.5. Generowanie ujęć AI odbywa się przez rzeczywiście dostępnego dostawcę w zakresie autoryzacji użytkownika.

## Rozpoczęcie zadania

Wykorzystaj temat, cel, CTA, materiały i preferencje podane przez użytkownika. Gdy brakuje treści filmu, zapytaj krótko o temat i oczekiwane działanie widza. Jeśli temat jest znany, przygotuj scenariusz bez ankiety. Domyślnie: język polski, pion 9:16, około 25–35 s, jedna osoba, jedna główna obietnica i jedno CTA. Dostosuj długość do treści i próbnego odczytu.

Dobierz tryb do materiału i prośby:

- **Nagranie realne:** przygotuj tekst do wypowiedzenia, plan zdjęciowy, miejsca na gesty i plan montażu.
- **Materiał AI:** utrzymaj tę samą osobę, ubranie i światło w krótkich ujęciach. Generuj czysty materiał bez napisów; osobno wykonaj kontrolowany głos/lip-sync oraz kompozycję tekstów.
- **Gotowe ujęcia:** zmierz materiał, przepisz faktyczną mowę i dopasuj efekty do istniejących gestów i pauz. Nie przepisuj nagranej wypowiedzi bez potrzeby.

Do szczegółowego planu nagrania, promptów i realizacji użyj [przepisu produkcyjnego](references/production-playbook.md).

## Reguły rozpoznawalności

1. Prezenter jest osią filmu: kontakt wzrokowy, naturalny chód, czytelne gesty; kamera cofa się, utrzymując go w centrum. Plan pełny lub amerykański zostawia miejsce na typografię.
2. Rozdziel napisy na **prowadzące** (małe białe słowa lub krótkie frazy blisko tułowia) i **akcentowe** (duże hasło, liczba lub puenta). Nie powiększaj każdego słowa.
3. Stosuj biały i czarny tekst, błękit/cyjan oraz pomarańcz. Buduj hierarchię rozmiarem i grubością, czasem lekkim pochyleniem. Kolory dostosuj do marki na prośbę użytkownika.
4. W wybranych momentach umieszczaj duże litery za sylwetką: tło → tekst/grafiki → wycięta postać. Sprawdź maskę włosów, palców i nóg w ruchu.
5. Wizualizuj sens: liczbę pokaż licznikiem, proces ikonami, rezultat kartą. Używaj rzeczywistych, dostarczonych danych; referencyjne wyniki i dane kontaktowe nie należą do nowego projektu.
6. Łącz krótkie zoomy, kierunkowy blur, punktowy flash i zdecydowane wejścia tekstu. Zachowuj spokojniejsze odcinki ze zwykłymi napisami, żeby duże akcenty miały siłę.
7. Montaż prowadzi wypowiedź. Najpierw zsynchronizuj słowa, gesty i momenty akcentów; podkład i SFX dopasuj do tych zdarzeń.

## Realizacja

Przygotuj scenariusz i roboczą oś czasu zawierającą: czas, wypowiedź, kadr/ruch, napisy prowadzące, akcent typograficzny, przejście i cue dźwiękowy. W planie wystarczą orientacyjne czasy. Po nagraniu lub wygenerowaniu głosu dopasuj montaż do rzeczywistych znaczników słów.

Jeśli użytkownik zamawia gotowy film, przejdź do realizacji dostępnymi narzędziami, a nie wyłącznie do napisania promptów. Dobierz aktualnie dostępny generator do wymagań ujęcia i użyj edytora/kompozytora do napisów, masek i miksu. Nie wpisuj na stałe modeli, identyfikatorów głosów, cen ani funkcji konkretnego dostawcy. Zachowaj preferowane przez użytkownika narzędzie. Jeżeli brakuje wykonawcy potrzebnego etapu, wskaż dokładnie brak i dostarcz wykonalną część projektu; nie nazywaj planu wyrenderowanym filmem.

Nie próbuj uzyskać całego filmu z doskonałą typografią, polskim tekstem i precyzyjnymi cue z jednego promptu text-to-video. Wariant minimum może używać czystych cięć, ręcznych masek na krótkich akcentach i prostszych grafik. Każde uproszczenie oceniaj względem rozpoznawalnych cech stylu.

## Dźwięk

Prowadź energiczną, wyraźną mowę na pierwszym planie. Zachowaj naturalne oddechy potrzebne dla rytmu. Podkład traktuj jako warstwę wspierającą, a krótkie whooshe, kliknięcia/popy i uderzenia jako akcenty wybranych zdarzeń. Konkretne próbki i muzykę dobieraj dla nowego filmu; nie deklaruj, że zidentyfikowano oryginalny utwór lub BPM. Ograniczenia analizy źródła opisano w rozpisce referencji.

Cue sheet to plan dźwięku. Dopiero użycie rzeczywistych plików i odsłuch miksu potwierdzają wykonanie sound designu. Bez odsłuchu nie deklaruj sprawdzenia czytelności mowy ani jakości miksu.

## Sprawdzenie i dostarczenie

- Obejrzyj film w ruchu: czy kamera i maski nie skaczą, twarz pozostaje czytelna, litery nie przenikają przez postać, ruch nóg i dłoni jest spójny.
- Sprawdź napisy z rzeczywistą mową oraz polskie znaki. Duże słowo powinno dać się odczytać także bez zatrzymywania filmu.
- Sprawdź wersję na ekranie telefonu i marginesy dla interfejsu docelowej platformy. Nie ukrywaj CTA przy dolnej krawędzi.
- Odsłuchaj mowę, muzykę i SFX razem; sprawdź piki oraz wyeksportowany plik, nie tylko podgląd projektu.
- Przy gotowym filmie dostarcz plik i krótko opisz istotne ograniczenia. Przy zleceniu planu dostarcz scenariusz, shot list, timeline napisów, cue sheet oraz prompty potrzebne w wybranym trybie.

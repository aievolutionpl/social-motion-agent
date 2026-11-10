# 30 promptów do HyperFrames

Baza offline zaadaptowana z pliku użytkownika `30_promptow_Remotion.md`. To briefy implementacyjne, nie gotowe animacje. Opisy oznaczone w źródle jako „Inspiracja” nie są przedstawiane jako zweryfikowany cytat z Ultra Skills. Załącznik nie zawierał obrazów; link do publicznej okładki nie jest zestawem referencji efektów.

## Kontrakt wspólny

Wklej ten kontrakt razem z wybranym promptem; CLI `prompts show` zwraca je już połączone.

```text
Zbuduj tę scenę dla HyperFrames jako source/index.html istniejącego joba. Użyj HTML/CSS/SVG/Canvas i lokalnego GSAP; przy wymaganym prawdziwym 3D użyj lokalnego Three.js, po sprawdzeniu dostępności zależności. Nie dodawaj React ani Remotion. Zachowaj format, fps i długość zatwierdzonego joba; jeśli nie ustalono inaczej, zaproponuj 1080×1920, 30 fps i czas z briefu. Teksty, dane, paletę i ścieżki lokalnych assetów umieść w jednym obiekcie CONFIG. Brak materiału oznacz jako placeholder; nie wymyślaj danych ani praw do assetów.
Utwórz gsap.timeline({paused:true}) i zarejestruj go jako window.__timelines.main. Zdefiniuj window.seek(t), które ogranicza czas do długości sceny i odtwarza cały stan niezależnie od historii wywołań. Przy Canvas/Three.js samodzielnie oblicz pełny stan z t; do osi GSAP dodaj onUpdate wywołujący tę samą funkcję renderAt(tl.time()), aby capture HyperFrames i ręczne seek dawały ten sam obraz. Zarejestruj data-composition-id="main", data-start="0", data-duration, data-width, data-height i data-fps zgodne z jobem. Zablokuj start do załadowania lokalnych fontów, tekstur i modeli.
Przedziały klatek w briefie są inkluzywne przy 30 fps; start=f/30, koniec=(f+1)/30. Przy innym fps zachowaj czas w sekundach. Ostatnie 10 klatek przy 30 fps pozostaw nieruchome; jeśli tekst nie mieści się w czasie czytania, zaproponuj dłuższą scenę zamiast przyspieszać go bez pytania. Wszystkie przejścia licz z czasu; bez autoplay, CSS transitions, setTimeout, requestAnimationFrame jako zegara eksportu, Date.now ani losowania w pętli renderu. Losowy układ wylicz raz ze stałym seedem.
Pracuj na zatwierdzonym kierunku albo pokaż użytkownikowi warianty i zaczekaj na wybór; jawna delegacja wystarcza. Nie dodawaj muzyki ani SFX bez źródła. Renderuj przez python -S studio.py render-html JOB --name NOWA_WERSJA; zachowaj istniejące intake, storyboard, assety i bramki jakości. Sprawdź klatki 0, środek, ostatnią oraz fazy przejść; sprawdź seek w kolejności 0 → środek → koniec → 0. Obejrzyj rzeczywisty MP4, dopiero potem opisz wynik. Nie deklaruj zgodności na podstawie samego HTML.
```

## Katalog

| ID | Efekt | Technika | Czas bazowy |
|---|---|---|---|
| hf-01 | Makieta miasta | Three.js + GSAP + HyperFrames | 3 s |
| hf-02 | Globus połączeń | Three.js + GSAP + HyperFrames | 3 s |
| hf-03 | Hologram produktu | Three.js + GSAP + HyperFrames | 3 s |
| hf-04 | Obrót produktu | Three.js + GSAP + HyperFrames | 2 s |
| hf-05 | Papierowy paragon | Three.js + GSAP + HyperFrames | 2 s |
| hf-06 | Góra lodowa | Three.js + GSAP + HyperFrames | 2 s |
| hf-07 | Rozłożony produkt | Three.js + GSAP + HyperFrames | 2 s |
| hf-08 | Warstwowy teren | Three.js + GSAP + HyperFrames | 2 s |
| hf-09 | Robot składa się z modułów | Three.js + GSAP + HyperFrames | 2 s |
| hf-10 | Portal z ramą | Three.js + GSAP + HyperFrames | 2 s |
| hf-11 | Wstęga przez szklane klatki | Three.js + GSAP + HyperFrames | 2 s |
| hf-12 | Stos pudełek | Three.js + GSAP + HyperFrames | 2 s |
| hf-13 | Widok przez obiektyw | Three.js + GSAP + HyperFrames | 2 s |
| hf-14 | Połączenie dwóch modułów | Three.js + GSAP + HyperFrames | 2 s |
| hf-15 | Składająca się gazeta | HTML/SVG/Canvas + GSAP + HyperFrames | 3 s |
| hf-16 | Szwajcarski plakat | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-17 | Rysunek techniczny jedną linią | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-18 | Flipbook | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-19 | Malowanie tuszem | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-20 | Kolaż z wycinanek | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-21 | Pieczątka na papierze | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-22 | Wykres wyrasta poza skalę | HTML/SVG/Canvas + GSAP + HyperFrames | 3 s |
| hf-23 | Rój pomocników | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-24 | Kalendarz 30 dni | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-25 | Tablica odlotów | HTML/SVG/Canvas + GSAP + HyperFrames | 3 s |
| hf-26 | Suwak przed i po | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-27 | Ekran blokady | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-28 | Typografia z impaktem | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-29 | Słowo z pyłu | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |
| hf-30 | Terminal w landing page | HTML/SVG/Canvas + GSAP + HyperFrames | 2 s |

## hf-01 — Makieta miasta

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: CEL, START

```text
Zbuduj efekt „Makieta miasta”. Czas bazowy: 3 s (90 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Na kremowej makiecie z matowymi budynkami narysuj kobaltową trasę od [START] do [CEL]. Klatki 0–19 najazd kamery, 20–65 rysowanie trasy po krzywej, 66–79 pinezka i etykieta. Prowadź linię tuż nad ulicą.

Adaptacja i kontrola: Krzywą trasy oblicz raz; reveal przez drawRange lub shader uniform. Sprawdź kolizję z ulicą i czy podpis celu pozostaje w kadrze.
```

## hf-02 — Globus połączeń

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: MIASTA, ZASIĘG

```text
Zbuduj efekt „Globus połączeń”. Czas bazowy: 3 s (90 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Zbuduj grafitowy globus z konturami lądów i punktami [MIASTA]. Klatki 0–19 obrót globu, 20–65 rysowanie łuków od miasta bazowego, 66–79 podpis [ZASIĘG]. Chowaj etykiety punktów za kulą.

Adaptacja i kontrola: Pozycje miast wyznacz z rzeczywistych współrzędnych. Ukrywaj podpis, gdy normalna punktu jest odwrócona od kamery; nie rysuj połączeń przez wnętrze kuli.
```

## hf-03 — Hologram produktu

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: MODEL

```text
Zbuduj efekt „Hologram produktu”. Czas bazowy: 3 s (90 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Pokaż [MODEL] nad czarną podstawą z błękitnym światłem. Klatki 0–19 uruchom podstawę, 20–58 skanuj bryłę od dołu do góry, 59–79 wyświetl trzy opisane punkty. W razie braku modelu użyj bryły zastępczej.

Adaptacja i kontrola: Skanowanie steruj uniformem wysokości. Utrzymaj opis na osobnej warstwie czytelnego DOM; placeholder musi być podpisany jako model zastępczy.
```

## hf-04 — Obrót produktu

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: MODEL, NAZWA

```text
Zbuduj efekt „Obrót produktu”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Umieść [MODEL] na neutralnej podstawce. Klatki 0–10 oświetl bryłę, 11–42 obróć produkt o 120°, 43–49 pokaż [NAZWA]. Zatrzymaj produkt na ujęciu trzy czwarte.

Adaptacja i kontrola: Kąt obrotu wylicz bez akumulacji znormalizowanym postępem; orbit controls wyłącz na czas capture. W ostatnich klatkach zatrzymaj też światło.
```

## hf-05 — Papierowy paragon

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: POZYCJE, SUMA

```text
Zbuduj efekt „Papierowy paragon”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Wysuń z drukarki kremową taśmę z [POZYCJE] i [SUMA]. Klatki 0–12 zapal kontrolkę, 13–36 wysuń papier i odsłaniaj tekst wraz z nim, 37–49 wygnij koniec i podświetl sumę. Użyj tekstury na deformowanej siatce.

Adaptacja i kontrola: Deformuj siatkę zawsze względem zachowanych pozycji bazowych, nigdy względem poprzedniej klatki. Teksturę paragonu generuj z CONFIG raz po załadowaniu fontu.
```

## hf-06 — Góra lodowa

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: UKRYTE, WIDOCZNE

```text
Zbuduj efekt „Góra lodowa”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Zbuduj lodową bryłę z dwiema strefami i półprzezroczystą taflą. Klatki 0–13 pokaż wierzchołek [WIDOCZNE], 14–37 zjedź kamerą pod wodę, 38–49 odsłoń [UKRYTE]. Nadaj obu strefom odrębne odcienie.

Adaptacja i kontrola: Kamera, poziom wody i odsłonięcie obu podpisów muszą wynikać z tej samej osi czasu. Sprawdź sortowanie przezroczystości; czytelność ważniejsza od fizycznej refrakcji.
```

## hf-07 — Rozłożony produkt

Etykieta w dostarczonym pliku: Autorski. Wejścia: PRODUKT

```text
Zbuduj efekt „Rozłożony produkt”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Podziel [PRODUKT] na warstwy. Klatki 0–10 pokaż złożoną bryłę, 11–36 rozsuń części wzdłuż jednej osi, 37–49 połącz trzy części z etykietami. Utrzymaj wspólną oś i stały kąt kamery.

Adaptacja i kontrola: Dla części modelu zapisz pozycje bazowe i odległości rozsunięcia. Etykiety prowadź do rzutowanych środków części; nie sugeruj prawdziwej konstrukcji bez danych.
```

## hf-08 — Warstwowy teren

Etykieta w dostarczonym pliku: Autorski. Wejścia: OBSZAR, PUNKT

```text
Zbuduj efekt „Warstwowy teren”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Zbuduj cztery warstwy terenu o wspólnym konturze [OBSZAR]. Klatki 0–12 unieś podstawę, 13–35 dosuń poziomice, 36–49 wysuń znacznik [PUNKT]. Użyj ortograficznego widoku pod kątem.

Adaptacja i kontrola: Poziomice muszą zachować wspólny kontur; jeżeli obszar jest fikcyjny, nazwij go schematem. Użyj kamery ortograficznej i stabilnego rzutu.
```

## hf-09 — Robot składa się z modułów

Etykieta w dostarczonym pliku: Autorski. Wejścia: KOLOR, NAZWA

```text
Zbuduj efekt „Robot składa się z modułów”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Użyj prostych brył dla korpusu, kół i ramienia. Klatki 0–11 wprowadź podstawę, 12–30 dołącz korpus i ramię, 31–49 rozświetl oko i wykonaj krótki ukłon. Udostępnij [KOLOR] i [NAZWA].

Adaptacja i kontrola: Każdy moduł ma bazowy transform i własny przedział wejścia. Ukłon wylicz analitycznie; finał bez niekończącego się pulsowania.
```

## hf-10 — Portal z ramą

Etykieta w dostarczonym pliku: Autorski. Wejścia: OBRAZ

```text
Zbuduj efekt „Portal z ramą”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Ustaw grafitową ramę, w której pojawi się [OBRAZ]. Klatki 0–12 narysuj obwód, 13–35 przesuń kamerę ku otworowi, 36–49 rozszerz obraz na cały kadr. Zsynchronizuj krawędzie maski z ramą.

Adaptacja i kontrola: Obraz portalu i maskę podłącz do wspólnego postępu; kontroluj piksele krawędzi w połowie przejścia, nie tylko na początku i końcu.
```

## hf-11 — Wstęga przez szklane klatki

Etykieta w dostarczonym pliku: Autorski. Wejścia: LOGO

```text
Zbuduj efekt „Wstęga przez szklane klatki”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Rozmieść trzy szklane ramki w głębi. Klatki 0–10 pokaż ich krawędzie, 11–40 poprowadź kobaltową wstęgę po krzywej przez wszystkie ramki, 41–49 zatrzymaj kamerę na [LOGO]. Zachowaj odstęp wstęgi od szkła.

Adaptacja i kontrola: Próbkuj krzywą raz, oblicz stałe ramy wstęgi, a następnie odsłaniaj geometrię. Sprawdź kolejność szkła oraz wstęgi w środku ruchu.
```

## hf-12 — Stos pudełek

Etykieta w dostarczonym pliku: Autorski. Wejścia: ETYKIETY

```text
Zbuduj efekt „Stos pudełek”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Zbuduj trzy matowe pudełka z [ETYKIETY]. Klatki 0–12 wprowadź podstawę, 13–35 ustaw pozostałe pudełka ze sprężystym dojazdem, 36–49 obróć kamerę, by ujawnić etykiety. Każde pudełko ma osobny kolor.

Adaptacja i kontrola: Zastosuj deterministyczną sprężynę analityczną albo GSAP back.out zamiast symulacji fizyki. Nie dopuść do przenikania pudełek podczas dojazdu.
```

## hf-13 — Widok przez obiektyw

Etykieta w dostarczonym pliku: Autorski. Wejścia: OBRAZ

```text
Zbuduj efekt „Widok przez obiektyw”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Ułóż pierścienie obiektywu wokół [OBRAZ]. Klatki 0–13 przesuń kamerę między pierścieniami, 14–34 domknij i otwórz sześciolistkową przysłonę, 35–49 wyostrz obraz. Zgraj ostrość z otwarciem przysłony.

Adaptacja i kontrola: Listki przysłony i fokus mają wspólny parametr. Ogranicz blur do obrazu, nie etykiet; sprawdź render WebGL bez GPU, jeśli tak działa środowisko.
```

## hf-14 — Połączenie dwóch modułów

Etykieta w dostarczonym pliku: Autorski. Wejścia: SYSTEM A, SYSTEM B

```text
Zbuduj efekt „Połączenie dwóch modułów”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Three.js osadzony w HTML HyperFrames, bez React. Ustaw dwie ceramiczne bryły opisane [SYSTEM A] i [SYSTEM B]. Klatki 0–15 obróć bryły, 16–35 zsuń złącza po jednej osi, 36–49 poprowadź impuls świetlny przez styk. Utrzymaj podgląd połączenia w finale.

Adaptacja i kontrola: Pozycja złączy na końcu ma być dokładnie zgodna, bez snapu. Impuls to osobna maska lub emisyjny obiekt sterowany czasem.
```

## hf-15 — Składająca się gazeta

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: TYTUŁ, ZDJĘCIE

```text
Zbuduj efekt „Składająca się gazeta”. Czas bazowy: 3 s (90 klatek przy 30 fps).
SVG i CSS. Użyj kremowego papieru i trzykolumnowej siatki. Klatki 0–18 rozłóż arkusze, 19–42 wsuń kolumny, 43–62 odsłoń [ZDJĘCIE], 63–79 złóż [TYTUŁ] słowo po słowie. Dodaj subtelną fakturę druku.

Adaptacja i kontrola: Użyj wrapperów overflow:hidden i transform-origin na grzbietach. Faktura papieru ma stałą pozycję, a tekst i zdjęcie wymagają lokalnych źródeł.
```

## hf-16 — Szwajcarski plakat

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: DATA, MIEJSCE, TYTUŁ

```text
Zbuduj efekt „Szwajcarski plakat”. Czas bazowy: 2 s (60 klatek przy 30 fps).
SVG i CSS. Zbuduj asymetryczną siatkę na jasnym tle. Klatki 0–12 wprowadź czerwony moduł, 13–35 przesuń [TYTUŁ] pod maską, 36–49 dosuń [DATA] i [MIEJSCE] do linii siatki. Zachowaj duże marginesy.

Adaptacja i kontrola: Pozycje wylicz z jednej siatki. Animuj transform wrappera tytułu, nie font-size; sprawdź polskie znaki i zawijanie przy docelowym formacie.
```

## hf-17 — Rysunek techniczny jedną linią

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: OBIEKT

```text
Zbuduj efekt „Rysunek techniczny jedną linią”. Czas bazowy: 2 s (60 klatek przy 30 fps).
SVG. Przygotuj ciągłą ścieżkę obrysu [OBIEKT] na granatowym papierze. Klatki 0–32 odsłaniaj linię przez stroke-dashoffset, 33–42 dorysuj linie wymiarowe, 43–49 pokaż oznaczenia. Długości opisów podaj w CONFIG.

Adaptacja i kontrola: Zmierz getTotalLength po gotowości SVG; ustaw dasharray i dashoffset od stanu bazowego przy każdym seek. Nie fabrykuj wymiarów obiektu.
```

## hf-18 — Flipbook

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: OBIEKT

```text
Zbuduj efekt „Flipbook”. Czas bazowy: 2 s (60 klatek przy 30 fps).
CSS 3D. Ułóż papierowe kartki z sześcioma fazami ruchu [OBIEKT]. Klatki 0–10 pokaż okładkę, 11–42 przewracaj kartki wokół grzbietu, 43–49 odsłoń końcową ilustrację. Ukryj tył każdej kartki podczas obrotu.

Adaptacja i kontrola: Każda kartka ma stały indeks, z-index i kąt wyliczany z czasu. Użyj backface-visibility:hidden; sprawdź przewijanie wstecz i seam przy 90 stopniach.
```

## hf-19 — Malowanie tuszem

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: MOTYW

```text
Zbuduj efekt „Malowanie tuszem”. Czas bazowy: 2 s (60 klatek przy 30 fps).
SVG. Przygotuj pociągnięcia dla [MOTYW]. Klatki 0–14 pokaż pierwszą plamę, 15–38 odsłoń kreski maskami, 39–49 dodaj drobne rozlania i czerwony podpis. Trzymaj fakturę nieruchomo względem papieru.

Adaptacja i kontrola: Maski tuszu buduj z ustalonych ścieżek. Fakturę i rozlania generuj raz; nie zmieniaj szumu co klatkę.
```

## hf-20 — Kolaż z wycinanek

Etykieta w dostarczonym pliku: Autorski. Wejścia: HASŁO, ZDJĘCIE

```text
Zbuduj efekt „Kolaż z wycinanek”. Czas bazowy: 2 s (60 klatek przy 30 fps).
CSS i SVG. Zbuduj trzy papierowe kształty i wycięty obrys [ZDJĘCIE]. Klatki 0–12 rozłóż tło, 13–33 wsuwaj warstwy z różnych kierunków, 34–49 przyklej [HASŁO] na taśmie. Cienie prowadź pod jednym kątem.

Adaptacja i kontrola: Przytnij przezroczyste marginesy assetu i zapisz punkt zaczepienia. Zachowaj jedną logikę światła; nie animuj samego elementu video, jeśli materiał jest klipem.
```

## hf-21 — Pieczątka na papierze

Etykieta w dostarczonym pliku: Autorski. Wejścia: NAPIS

```text
Zbuduj efekt „Pieczątka na papierze”. Czas bazowy: 2 s (60 klatek przy 30 fps).
SVG i CSS. Ustaw [NAPIS] na drewnianej pieczątce. Klatki 0–17 przybliż pieczątkę do papieru, 18–23 odciśnij napis i lekko odkształć kartkę, 24–49 podnieś pieczątkę, zostawiając ślad z ubytkami tuszu.

Adaptacja i kontrola: Odcisk pojawia się wyłącznie w momencie kontaktu. Ubytki tuszu są stałe; deformacja papieru wraca do neutralnej pozycji przed finałem.
```

## hf-22 — Wykres wyrasta poza skalę

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: DANE

```text
Zbuduj efekt „Wykres wyrasta poza skalę”. Czas bazowy: 3 s (90 klatek przy 30 fps).
SVG. Wykreśl [DANE] jako słupki. Klatki 0–20 wprowadź skalę, 21–55 podnieś pierwsze słupki, 56–79 przeskaluj oś i wszystkie słupki, gdy ostatnia wartość przekroczy dotychczasowe maksimum. Pokaż wartość bez zaokrąglania.

Adaptacja i kontrola: Oś i każdy słupek używają tej samej funkcji skali w każdej klatce. Zachowaj prawdziwe jednostki, wartości i punkt odniesienia; nie przycinaj danych.
```

## hf-23 — Rój pomocników

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: AGENTY, ZADANIE

```text
Zbuduj efekt „Rój pomocników”. Czas bazowy: 2 s (60 klatek przy 30 fps).
SVG. Umieść [ZADANIE] pośrodku, a wokół niego ikony [AGENTY]. Klatki 0–12 rozprosz punkty, 13–34 sprowadź je po krzywych, 35–49 zmieniaj statusy z pracy na gotowe. Zastosuj stały seed dla układu.

Adaptacja i kontrola: Rozkład początkowy wynika ze stałego seeda; ścieżki i statusy wylicz z CONFIG i czasu. To ilustracja procesu, nie dowód wykonania zadań przez agentów.
```

## hf-24 — Kalendarz 30 dni

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: DNI UKOŃCZONE

```text
Zbuduj efekt „Kalendarz 30 dni”. Czas bazowy: 2 s (60 klatek przy 30 fps).
SVG lub CSS Grid. Ułóż dni 1–30 w siatce siedmiu kolumn. Klatki 0–11 pokaż siatkę, 12–43 zaznaczaj kolejne pozycje z [DNI UKOŃCZONE], 44–49 pokaż licznik wynikający z danych. Dodaj etykietę stanu oprócz koloru.

Adaptacja i kontrola: Licznik oblicz z unikalnych prawidłowych dni 1–30. Stan opisuj ikoną/tekstem obok koloru; powtórne seek nie może zwiększać licznika.
```

## hf-25 — Tablica odlotów

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: CEL, GODZINA, STATUS

```text
Zbuduj efekt „Tablica odlotów”. Czas bazowy: 3 s (90 klatek przy 30 fps).
CSS 3D. Zbuduj wiersze [GODZINA], [CEL], [STATUS] ze znaków podzielonych na połówki. Klatki 0–14 pokaż stan początkowy, 15–65 obracaj połówki od lewej do prawej, 66–79 podświetl finalny status. Użyj fontu monospace.

Adaptacja i kontrola: Przygotuj wszystkie połówki znaków z góry. Indeks znaku i fazę obrotu wylicz z czasu, nie z interwału; sprawdź znikanie tylnych powierzchni.
```

## hf-26 — Suwak przed i po

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: PO, PRZED

```text
Zbuduj efekt „Suwak przed i po”. Czas bazowy: 2 s (60 klatek przy 30 fps).
CSS. Nałóż [PRZED] i [PO] w identycznym kadrze. Klatki 0–10 pokaż pierwszy obraz, 11–49 przesuń separator od 85% do 15% szerokości, odsłaniając drugi przez clip-path. Przesuwaj uchwyt i maskę tą samą wartością.

Adaptacja i kontrola: Wspólna zmienna postępu steruje uchwytem i clip-path; oba obrazy muszą mieć identyczny fit i crop. Podpisz PRZED/PO oraz źródła.
```

## hf-27 — Ekran blokady

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: GODZINA, POWIADOMIENIE, TAPETA

```text
Zbuduj efekt „Ekran blokady”. Czas bazowy: 2 s (60 klatek przy 30 fps).
CSS. Na tle [TAPETA] pokaż [GODZINA] i kartę [POWIADOMIENIE]. Klatki 0–13 rozświetl ekran, 14–35 wprowadź kartę sprężystym ruchem, 36–49 pokaż jej drugi wiersz. Użyj ciemnego półprzezroczystego tła pod tekstem.

Adaptacja i kontrola: Godzinę odczytaj z CONFIG, nie z zegara systemu. Zbuduj ilustrację powiadomienia bez prywatnych danych; nie udawaj prawdziwego systemowego zrzutu.
```

## hf-28 — Typografia z impaktem

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: DOPISEK, HASŁO

```text
Zbuduj efekt „Typografia z impaktem”. Czas bazowy: 2 s (60 klatek przy 30 fps).
CSS. Ułóż maksymalnie trzy słowa [HASŁO] dużą, zwartą czcionką. Wprowadź słowa w klatkach 6, 16 i 26. Każde ląduje z krótkim przekroczeniem docelowej skali i powrotem. W 38–49 odsłoń [DOPISEK].

Adaptacja i kontrola: Overshoot nie może obcinać liter poza kadrem. Każde słowo otrzymuje stabilny stan początkowy; dopisek potrzebuje rzeczywistego czasu czytania.
```

## hf-29 — Słowo z pyłu

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: SŁOWO

```text
Zbuduj efekt „Słowo z pyłu”. Czas bazowy: 2 s (60 klatek przy 30 fps).
Canvas lub SVG. Wyznacz punkty docelowe z maski [SŁOWO]. Klatki 0–12 pokaż rozproszone cząstki, 13–39 sprowadź je do liter po zakrzywionych torach, 40–49 dołóż pełny tekst pod maską. Rozmieszczenie cząstek ma być powtarzalne.

Adaptacja i kontrola: Poczekaj na font, rasteryzuj maskę słowa raz, zapisz punkty i startowe pozycje z seedem. Pozycje wylicz analitycznie; finał zastąp ostrą warstwą tekstu.
```

## hf-30 — Terminal w landing page

Etykieta w dostarczonym pliku: Inspiracja. Wejścia: CTA, KOMENDA, NAGŁÓWEK, OBRAZ

```text
Zbuduj efekt „Terminal w landing page”. Czas bazowy: 2 s (60 klatek przy 30 fps).
CSS i SVG. Klatki 0–17 wpisz [KOMENDA] w terminalu, 18–34 przekształć ramę w okno przeglądarki, 35–49 odsłoń [NAGŁÓWEK], [OBRAZ] i [CTA]. Trzymaj wspólną ramkę obu stanów, żeby przejście było płynne.

Adaptacja i kontrola: Zachowaj jeden wrapper ramy; indeks wpisywanego znaku i reveal UI zależą od czasu. Komenda jest tekstem ilustracji, nigdy poleceniem do wykonania.
```

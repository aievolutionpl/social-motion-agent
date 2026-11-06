# Przepis produkcyjny

## Scenariusz, który daje się zmontować

Zaprojektuj wypowiedź do konkretnego tematu. Każdy większy efekt powinien mieć słowo lub gest, który go uzasadnia. Dla filmu około 30 s użyteczny jest taki układ; proporcje zmieniaj po próbnym odczycie:

| Odcinek roboczy | Zadanie wypowiedzi | Możliwy akcent |
|---|---|---|
| 0–4 s | Obietnica lub problem, który widz rozumie od razu | Dwu-/trzypoziomowy nagłówek i jedno duże hasło |
| 4–10 s | Dowód, demonstracja albo konkretny przykład | Liczba, porównanie, karta lub miniatura własnego materiału |
| 10–15 s | Dlaczego to działa lub co zmienia | Duże słowo za sylwetką, potem spokojny fragment |
| 15–22 s | Krótki proces i korzyść | Dwie/trzy kolejno wchodzące ikony lub karty |
| 22–30 s | Jedno proste CTA | Gest wskazania, czytelny komunikat i hold |

Jeśli użytkownik nie dostarczył wyniku, pokaż demonstrację albo proces. Nie uzupełniaj scenariusza zmyśloną liczbą. Dla polskiej wypowiedzi zacznij orientacyjnie od 70–95 słów na 30 s, a następnie sprawdź odczyt; krótszy, wyraźny tekst ma pierwszeństwo przed arbitralną liczbą słów. Tempo angielskiej referencji jest bardzo szybkie i nie przekłada się mechanicznie na polski.

Oddziel tekst mówiony od instrukcji. Oznacz tylko potrzebne gesty: `[wskazanie karty]`, `[otwarcie dłoni]`, `[krótka pauza na liczbę]`. Unikaj stałego wskazywania palcem w każdym zdaniu.

## Plan nagrania realnego

Przygotuj 2–3 spokojne odcinki trasy z podobnym światłem i różnym tłem. Można też wykorzystać jeden dłuższy spacer. Wybierz tło dające przestrzeń na typografię i widoczną paralaksę. Referencja nie wymaga wody ani ulicy.

Nagraj wypowiedź w segmentach po jednej myśli, z około sekundą zapasu przed i po. Utrzymuj podobne tempo chodu i położenie postaci. Zostaw wolne miejsce w kadrze po tej stronie, którą prezenter będzie wskazywał. Nagraj krótki fragment czystego tła, jeśli planowany kompozyt tego potrzebuje. Sprawdź głos i wiatr przed właściwymi dublami.

Przy kontakcie wzrokowym nie kieruj wzroku stale nad obiektyw do wielkiego tekstu na prompterze. Dobierz sposób podpowiedzi do naturalnej mowy. Plan pełny pozostawia miejsce na nogi i gesty; cyfrowy punch-in może później zmieniać odczucie odległości.

## Materiał AI

Twórz kilka krótkich ujęć zamiast jednego długiego spaceru przez wiele lokalizacji. Długości dopasuj do dostępnego modelu oraz fraz mowy. Zachowuj tę samą osobę, ubiór, proporcje, porę dnia i kierunek światła. Kontroluj ręce, stopy, ruch ust i cofanie kamery.

Jeśli potrzebna jest nowa tożsamość, opracuj spójny wygląd postaci. Jeśli użytkownik dostarczył własną postać lub materiały, wykorzystaj je zgodnie z briefem. Nie bierz automatycznie twarzy osoby ze źródłowej rolki.

Przykładowa konstrukcja promptu do **czystego ujęcia**; zastąp pola rzeczywistymi ustaleniami:

```text
Vertical 9:16 live-action style shot. [Presenter description and consistent wardrobe]
walks naturally toward the camera along [location], looks directly into the lens,
speaks with confident conversational energy, and makes [specific modest gesture].
The camera tracks backward smoothly at matching walking speed. Full-body to
three-quarter framing, centered subject, generous headroom for later typography,
clear background with natural parallax. [Lighting direction and time of day].
Continuous believable footsteps, stable identity and hands, realistic proportions.
Clean footage for compositing: no captions, floating letters, logos, UI or graphics.
```

To opis zamierzonego ujęcia, nie gwarancja obsługi przez dowolny model. Wstaw mowę tylko w pole/tryb rzeczywiście obsługiwany przez wybrany generator. Jeżeli potrzebny jest osobny lip-sync, dopasuj gotowy głos do ujęcia i sprawdź rezultat. Nie zostawiaj przypadkowej mowy wygenerowanej natywnie pod docelową narracją.

## Montaż i napisy

1. Zbuduj najpierw płynną wypowiedź i spacer. Usuń zbędne przerwy oraz duble. Sprawdź, czy narracja działa bez ozdobników.
2. Wygeneruj lub popraw transkrypcję z czasami słów. Te czasy stają się źródłem synchronizacji, a nie czasy z wcześniejszego scenariusza.
3. Dodaj małe podpisy prowadzące. Duże akcenty zaprojektuj osobno: inne wielkości, wybrane kolory, maska i ruch. Popraw ręcznie łamanie polskich wyrazów.
4. Wykonaj wycięcie sylwetki tam, gdzie hasło przechodzi za osobą. Dodaj śledzenie, jeśli potrzebne. Obejrzyj maskę w ruchu, zwłaszcza przy dłoniach i włosach.
5. Dodaj wybrane zoomy, rozmycia, grafiki i przejścia. Prędkość efektu dobieraj do słowa i ciężaru znaczenia, nie tylko do siatki muzycznej.
6. Dodaj miks dźwięku i wykonaj eksport. Osobno zachowaj projekt lub strukturę pozwalającą zmienić tekst, jeśli użyte narzędzie to umożliwia.

Przykład wiersza osi czasu po nagraniu:

| In–out | Wypowiedź | Obraz | Podpis | Akcent | SFX |
|---|---|---|---|---|---|
| Z czasu rzeczywistej mowy | Konkretna fraza użytkownika | Prezenter wskazuje miejsce na lewo | Krótkie słowa przy tułowiu | Karta wchodzi obok dłoni, nie na twarz | Pop w chwili zatrzymania karty |

Przy planie bez nagrania używaj orientacyjnych sekund. Przy projekcie do renderu określ klatkaż i precyzyjne czasy; nie nazywaj orientacyjnej tabeli gotowym plikiem montażowym.

## Projekt dźwięku

**Głos:** najpierw uzyskaj wyraźną, pewną wypowiedź. Naturalny, własny głos lub nowy dobrany głos zgodny z briefem; barwa osoby z referencji nie jest warunkiem podobieństwa. Nie podbijaj energii samym przyspieszeniem całej ścieżki.

**Propozycja promptu do podkładu:**

```text
Instrumental bed for a confident walk-and-talk social reel. Light modern electronic
pulse, restrained bass and clean percussion, simple repeating motif, space in the
midrange for fast speech, no vocals. Support the speaker rather than dominate.
Clear short ending at [duration]. [Mood appropriate to the actual topic].
```

To kierunek nowej muzyki, nie opis rozpoznanego utworu. Zastosuj rzeczywisty plik muzyczny z dostępnego źródła lub generatora. Sama instrukcja nie dodaje muzyki do filmu.

**Przykładowe cue do nowego filmu:**

| Zdarzenie obrazu | Projektowany dźwięk | Dopasowanie |
|---|---|---|
| Pierwsze duże hasło | Krótki miękki hit/pop | Akcent w chwili osiągnięcia docelowej skali |
| Szybkie odsunięcie/zbliżenie | Zwięzły whoosh | Początek ruchu → koniec ruchu, bez przykrycia słowa |
| Licznik lub informacja liczbowa | Subtelny narastający tick i lekki hit | Hit przy wartości docelowej; bez długiego efektu kasowego |
| Sekwencja ikon procesu | Dwa/trzy delikatne kliknięcia | Każde przy wejściu kolejnej ikony |
| Karta korzyści/kontaktu | Dyskretny pop lub potwierdzenie | Zatrzymanie karty i gest prezentera |
| Koniec CTA | Krótkie domknięcie podkładu | Bez urwania środka sylaby lub długiego ogona |

Nie przypisuj efektu każdemu słowu. Najpierw odsłuchaj głos z muzyką, potem dołóż SFX i sprawdź całość na cichym głośniku telefonu oraz słuchawkach. Kontrola techniczna LUFS/peak nie zastępuje odsłuchu.

## Weryfikacja rezultatu

Porównuj film z referencją na poziomie zachowania: spacer i cofanie kamery, napisy o dwóch skalach, celowo użyta głębia warstw, zróżnicowany rytm, czytelny CTA. Nie porównuj podobieństwa krajobrazu lub osoby.

Sprawdź ruch całej sekwencji oraz reprezentatywne klatki przed akcentem, w jego kulminacji i po przejściu. Obejrzyj wyeksportowany MP4 od początku do końca. Dla domyślnego pionowego wydania można użyć H.264, 1080×1920, źródłowego/docelowego 25 lub 30 fps i AAC; dopasuj parametry do narzędzia i wymagań użytkownika.

Przy nowym renderze nie twierdź, że kontrolowano dźwięk, jeśli dostępna była wyłącznie analiza tekstowa. Wskaż konkretnie, co zostało sprawdzone obrazem, pomiarem lub odsłuchem.

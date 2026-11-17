# Trzy wersje filmu i opinie

`studio.py plan "20-sekundowa rolka z idącym prezenterem i tekstem za sylwetką"` dobiera istniejącą ścieżkę, źródła, brakujące materiały i kolejne polecenia. Dodaj `--job JOB`, aby uwzględnić stan produkcji. Polecenie `new` może też dobrać ścieżkę z tytułu lub `--brief`. Podane samodzielnie format, czas i `--kind` mają pierwszeństwo.

## Wybór wypowiedzi i otwarcia

Zarejestruj nagranie przez `asset-add`. Zastąp `JOB` ścieżką zwróconą przez `new`, a `ASSET_ID` identyfikatorem nagrania. Zaimportuj czasy wypowiedzi z programu Whisper albo uruchom lokalny `whisper-cli` na nagraniu.

```bash
python -S studio.py selects JOB --asset ASSET_ID --transcript notes/whisper.json --query "cena produktu"
python -S studio.py selects JOB --asset ASSET_ID --model /path/to/ggml-model.bin --query "cena produktu"
python -S studio.py variants openings JOB --query "cena produktu"
```

Wynik zawiera do trzech różnych cytatów, czas wejścia i wyjścia, powód doboru oraz wpis do `timeline.json`. Sprawdź sens wypowiedzi w kontekście. Odsłuchaj otwarcia z oryginalnym dźwiękiem. Mają do trzech sekund każde. Bez transkrypcji agent dostaje próbki nagrania oznaczone jako wybór wizualny. Jeśli użytkownik poprosił o wybór przed produkcją, pokaż mu te otwarcia i zaczekaj.

## Pełne wersje

Polecenia `render-assembly`, `render-html`, `render-hype`, `render-kinetic`, edycja z poprawnym eksportem i `demo --render` zwracają ścieżkę `variants.gallery`. W jednym katalogu są trzy pełne MP4 i przenośny plik `index.html`. Wersja autorska zachowuje montaż źródłowy, kinetyczna dodaje rytmiczne ruchy kamery, a studyjna pokazuje cały obraz na oddzielnym, miękko poruszającym się planie. Każda zachowuje długość i dźwięk mastera. Przy ponowieniu renderu istniejące galerie pozostają dostępne.

```bash
python -S studio.py variants build JOB --render renders/master.mp4
python -S studio.py variants serve JOB --collection GALLERY_ID
```

Agent uruchamia polecenie `serve` zwrócone z galerią, przekazuje lokalny adres użytkownikowi i pozostawia proces na czas oceny. Odtwarzacze obsługują przewijanie. Gwiazdki 1–5 zapisują się po kliknięciu, komentarz po wybraniu „Zapisz opinię”. Pole „Uwagi do całego filmu” służy do przekazania wskazówek wspólnych dla trzech wersji. Przy otwarciu HTML jako pliku można pobrać opinie w JSON. Skopiuj plik do katalogu produkcji i zaimportuj go. Do przeniesienia podglądu na inne urządzenie skopiuj cały katalog galerii.

```bash
python -S studio.py variants import JOB --collection GALLERY_ID --source notes/feedback.json
python -S studio.py variants rate JOB --collection GALLERY_ID --style studio --stars 5 --note "Zachowaj szeroki kadr"
python -S studio.py variants rate JOB --collection GALLERY_ID --note "Zostaw dłuższe pauzy między wypowiedziami"
python -S studio.py variants prefer JOB
python -S studio.py variants use JOB --collection GALLERY_ID --style studio
```

Uwaga przekazana w rozmowie może zawierać sam tekst. Zapisuj rzeczywiste słowa użytkownika i ocenę tylko wtedy, kiedy ją podał. Polecenie `use` wskazuje pełny render do dalszej recenzji i pakowania. Dotychczasowe etapy weryfikacji i akceptacji nadal obowiązują.

## Jak agent korzysta z opinii

Domyślny profil `local` służy osobie korzystającej z danej kopii studia. Na wspólnej instalacji przy tworzeniu filmu podaj odrębny `--profile` dla osoby lub serii. Oceny i komentarze są zapisywane w lokalnej bazie SQLite w ignorowanym katalogu produkcji. Ponowny zapis aktualizuje ocenę tej samej wersji. Profil porządkuje kierunki na podstawie dotychczasowych gwiazdek i udostępnia agentowi ostatnie komentarze przy `plan`, `new` i `variants prefer`. Przy nowym filmie zastosuj zapisane wskazówki w montażu, o ile pasują do bieżącego briefu.

W kolejnym filmie renderer automatycznie stosuje też kilka dosłownych wskazówek. „Mniej zbliżeń” i „więcej zbliżeń” zmieniają siłę i rytm ruchu kamery w wersji kinetycznej. „Większy kadr” i „mniejszy kadr” zmieniają rozmiar obrazu w wersji studyjnej. Pozostałe uwagi, np. o pauzach, muzyce czy napisach, agent dostaje w oryginalnym brzmieniu podczas planowania montażu.

## Edytowalne sceny ShotCraft

`shotcraft list` oznacza przepisy dostępne w `compose`. Utwórz JSON w produkcji. Dla `flying-words` użyj np. `{"words":["Ruch","i","światło"]}`. Dla `carousel-3d` podaj `assets` z identyfikatorami 2–6 zarejestrowanych obrazów. Dla `before-after-slider-scrub` podaj dwa obrazy w kolejności przed i po. Opcjonalne pola to `background`, `foreground`, `accent` w formacie `#RRGGBB` i `audio` z identyfikatorem pliku dźwiękowego.

```bash
python -S studio.py shotcraft compose flying-words --job JOB --spec source/scene.json
python -S studio.py render-html JOB --name tytul
```

Scena korzysta z wymiarów, klatkażu i długości produkcji. Animację i lokalne media można edytować w `source/`. Do zastąpienia istniejącej kompozycji służy `--overwrite`.

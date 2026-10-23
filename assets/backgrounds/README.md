# Tła: główny plik dla agenta

9 gotowych teł (pionowe, 1024x1792, webp) do rolek, przebitek, scen z tekstem i przejść. Przeczytaj ten plik, potem `INDEX.md` (tabela z opisem, jasnością i spokojnymi strefami każdego tła).

| Plik | Po co |
|---|---|
| `README.md` (ten) | zasady użycia i komendy |
| `INDEX.md`, `index.json` | opis, nastrój, zastosowanie, jasność, zajętość, strefy na tekst |
| `bg-0N-*.webp` | oryginały, nie nadpisuj |

## Które tło do czego

| Potrzeba | Tła |
|---|---|
| Domyślne tło pod tekst, liczby, wykresy | `bg-02-navy-glow` (najspokojniejsze), `bg-03-amber-arc` |
| AI, technologia, explainer | `bg-04-blue-wires-orange` (środek pusty na tekst) |
| Premium, luksus, finanse, cytat | `bg-05-gold-glow-silk`, `bg-06-gold-ring` (puste koło na logo lub liczbę) |
| Hook, intro, energia | `bg-01-silk-purple-orange`, `bg-08-iridescent-glass-swirl` |
| Wybuch, flash na uderzenie dźwięku, przejście | `bg-07-neon-shard-burst`, `bg-09-blue-orange-glitch` |

## Zasady

1. **Marka decyduje.** Przeczytaj lokalny brief marki w produkcji: kolory tła mają pasować do palety (złote tła do marek premium, niebieskie do technologii). Nie mieszaj dwóch różnych temperatur kolorów w jednej scenie bez powodu.
2. **Tekst a gęstość.** Tła spokojne (`navy-glow`, `amber-arc`, `gold-*`, `blue-wires`) przyjmują tekst w strefach z indeksu. Tła gęste i barwne (`silk`, `iridescent`, `shard-burst`, `glitch`) wymagają panelu lub pilla pod tekstem (`.panel`, `.pill-caption` z `templates/frame-tokens.css`). Sprawdź `studio.py polish`.
3. **Ruch jest delikatny.** Najazd lub dryf 8 do 15% w czasie sceny. Gęste tła (`shard-burst`, `glitch`) trzymaj krótko (do 3 s), potem wróć do spokojnego.
4. **Pionowe z natury.** Do 9:16 i 4:5 pasują bez przycinania. Do 16:9 i 1:1 narzędzie przycina kadr z środka i powiększa (miękko, tła są rozmyte); przy 16:9 sprawdź, czy ważny element nie wypadł.
5. **Nie przekraczaj rozdzielczości.** Źródło ma 1024 px szerokości; do 1080x1920 skala 1.05x jest niezauważalna, większe powiększenia (najazd + crop) dodawaj z umiarem.

## Komenda: tło jako klip

```powershell
python -S studio.py background assets/backgrounds/bg-02-navy-glow.webp output/jobs/ID/assets/bg-hook.mp4 --duration 8 --format 9:16 --motion push
```

`--motion push` (płynny najazd z ease in/out), `drift` (przesuw w bok), `none`; `--amount` 0 do 0.5 (domyślnie 0.12); `--format` 16:9, 9:16, 4:5, 1:1. Wynik zarejestruj w produkcji przez `studio.py asset-add` (pochodzenie: dostarczone przez właściciela, tło własne).

## Utrzymanie

Nowe tło: wrzuć plik, dopisz opis w `META` w `scripts/backgrounds_catalog.py` i uruchom `python -I scripts/backgrounds_catalog.py build`. `check` wykrywa pliki bez wpisu.


Pochodzenie: materiały dostarczone przez właściciela projektu i opublikowane na jego polecenie. Zasady mediów: ../../docs/MEDIA_RIGHTS.md.

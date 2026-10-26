# Pełna biblioteka skilli

Uruchom `python -S scripts/bootstrap_library.py`, aby pobrać wszystkie 36 przypięte źródła. Lokalny rdzeń działa również bez rozszerzeń. Katalog zawiera oryginalne skille, recipes, szablony i fixtures, nie tylko samodzielne integracje.

## Punkty wejścia agenta

Nadrzędny skill: `skills/creative-director/SKILL.md` (film, strona, UI motion; 10 modułów czytanych na żądanie). Dobór i przygotowanie źródeł: `studio.py skills plan/setup/check --mode video|website|ui-motion`.

Dotychczasowy skill filmowy: `.agents/skills/social-motion-studio/SKILL.md`. Mapę zadań pokaże `studio.py map`; właściwe ścieżki wybierze `studio.py route TYP`. Dodatkowo pobrano `remotion-official-skills` i `motion-video-skill`; sprawdzono renderowanie HTML. Brief ma pięć kategorii; pytaj tylko o brakujące decyzje. Reguły są w skills/intake/SKILL.md.

| Zadanie | Źródło i ścieżka od `tools/repos/` |
|---|---|
| Dopracowanie kodowanych ramek (wygląd nie-generowany, bezpieczne pola, bramka pomiarowa) | Lokalnie `.agents/skills/motion-ui-polish/SKILL.md`; doktryna upstream `ux-ui-agent-skills/taste/design-taste.md`; trasa `polish`; komenda `studio.py polish` |
| Dobór efektów ruchu z katalogu 637 efektów i 11 receptur | Lokalnie `.agents/skills/motion-effect-picker/SKILL.md`; upstream `awesome-ai-motion/SKILL.md`; trasa `motion`; komenda `studio.py motion find/show/recipe` |
| Nagrania stron/aplikacji i tutoriale AI | Lokalnie `.agents/skills/screen-tutorials/SKILL.md`; upstream `openscreen/plugin/skills/openscreen-demo/SKILL.md`; trasy `showcase` i `tutorial` |
| Profil marki dla Hypermotion | `hypermotion/skills/hypermotion-brand-profile/SKILL.md` |
| Reżyseria i produkcja explainera Hypermotion | `hypermotion/skills/hypermotion-explainer-director/SKILL.md` |
| Ilustracje i mechanizmy techniczne | `anatomy/SKILL.md` |
| Dobór animacji z biblioteki Motion Anything | `motion-anything/skills/motion-anything/SKILL.md`; przepisy w `recipes/` |
| Scenariusze, hooki, montaże i shorty | `video-agent-skills/skills/`; zacznij od `editing/` lub `studio-script/` |
| Napisy i operacje OpenClip | `openclip-agent-skills/skills/openclip/SKILL.md` oraz 9 wyspecjalizowanych skilli |
| Reguły motion, SFX i kontrola klatek | `claude-motion/.claude/skills/`: `motion-design`, `review-loop`, `sound-design`, `web-sims` |
| Film HTML, frame-by-frame i beat sync | `claude-motion-design/skill/motion-design/SKILL.md` |
| Planowanie, kierowanie produkcją i audyt | `awesome-motion-design-agent-skills/skills/`: `motion-director`, `remotion-video-agent`, `generative-media-director`, `web-motion-auditor`, `site-motion-excellence-director` |
| OpenDesign: motion i film | `open-design/skills/motion-design/`, `motion-lab/`, `video-hyperframes/`, `remotion/`; szablony `design-templates/hyperframes/`, `motion-frames/`, `video-shortform/` |

## Paczki iart

Każda paczka znajduje się w `tools/repos/iart-<nazwa-paczki>/`. Wymagania i instrukcje sprawdzamy w wybranym skillu, bez ładowania wszystkich paczek do kontekstu.

| Obszar | Paczki |
|---|---|
| Social, nagrania, reklamy | `tiktok-video-skills`, `text-message-video-skills`, `youtube-video-skills`, `ecommerce-video-skills`, `ad-video-skills`, `b-roll-skills` |
| Narracja i informacja | `explainer-video-skills`, `data-animation-skills`, `map-animation-skills`, `kinetic-typography-skills` |
| Warsztat motion | `motion-design-skills`, `freelance-motion-skills`, `lower-thirds-skills` |
| Kod, 3D i animacja | `web-animation-skills`, `webgl-animation-skills`, `manim-skills`, `generative-illustration-skills`, `javascript-animation-skills` |

## Zasady wyboru

- Dla pojedynczego filmu wybierz jeden główny silnik i mały zestaw uzupełniających skilli.
- Wskazuj zawsze repozytorium i pełną ścieżkę. Nazwy `motion-design` i `motion-director` występują w różnych źródłach; nie nadpisuj ich wspólną instalacją.
- `catalog.json` rozróżnia skille, recipes, szablony i fixture testowe; liczb plików nie traktuj jako liczby gotowych integracji.
- Skille publikacji, kont zewnętrznych i usług płatnych uruchamiaj tylko w zakresie aktualnego polecenia użytkownika. Ten etap obejmuje zebranie biblioteki.

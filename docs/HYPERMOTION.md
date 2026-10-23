# Hypermotion: opcjonalny edytor

Źródło przyjęte na podstawie nazwy i kontekstu: [psiddharthdesign/hypermotion](https://github.com/psiddharthdesign/hypermotion). Lokalne źródła: `tools/repos/hypermotion/`; commit zapisano w `sources.lock.json`.

## Co bierzemy do systemu

- Natywne, edytowalne sceny `.hype`, layout, keyframes, kamerę i eksport.
- CLI `hypermotion` oraz MCP `hypermotion-mcp` jako przyszły interfejs automatyzacji.
- Dwa skille: profil marki i reżyser explainera.
- Rozdzielenie planowania scen od deterministycznego budowania i renderowania.

Dokumentacja pobranej wersji wskazuje aplikację `0.1.18` w fazie research preview oraz pakiet CLI `0.1.2`. To osobne wersje komponentów.

## Co trzeba potwierdzić przed pierwszym filmem

1. Sprawdzić właściwy build aplikacji na Windows i uruchomienie desktopu. README opisuje instalator Windows, ale pobrany AGENTS.md nadal twierdzi, że build Windows nie jest wydawany. To rozbieżność w źródłach, nie potwierdzenie dostępności działającego instalatora.
2. Uruchomić CLI w środowisku projektu. CLI wymaga Node 20+ i korzysta z aplikacji desktop do renderowania; sam pakiet CLI nie zastępuje silnika renderującego.
3. Sprawdzić utworzenie i ponowne otwarcie prostej sceny `.hype`.
4. Wykonać krótki eksport i sprawdzić MP4 przez ffprobe oraz obejrzenie klatek.
5. Dopiero po tym połączyć profil marki, storyboard i pełny film.

Nie instalowano aplikacji, CLI ani MCP w ramach zebrania źródeł. Instrukcje i skille dostępne są lokalnie do następnego etapu.

Źródła szczegółów: `tools/repos/hypermotion/README.md`, `AGENTS.md`, `package.json`, `cli/package.json`, `skills/`.

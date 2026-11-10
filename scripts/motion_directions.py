"""Menu kierunków „motion, nie slajdy”: style, koncepty openerów, tryby explainerów, tło i przejścia.

Dane: config/motion-directions.json (oryginalne opisy, idee z bangtutorial/bang-motion, MIT).
Wszystko jest deterministyczne i offline. Menu to propozycje do briefu, nie limity ani zakazy:
marka i jawne decyzje użytkownika mają pierwszeństwo.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from studio_core import ROOT

DATA = ROOT / "config/motion-directions.json"
MENUS = ("style_directions", "explainer_modes", "opener_concepts", "background_motion", "surfaces",
         "render_families", "transitions", "openings", "endings", "canonical_components")
FINGERPRINT_PARTS = ("concept", "scenes", "objects", "opening", "ending")


@lru_cache(maxsize=1)
def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def _tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", text.casefold()) if len(t) > 1}


def list_menus(menu: str | None = None) -> dict:
    data = load()
    if menu is None:
        return {"source": data["source"], "note": data["note"],
                "menus": {name: len(data[name]) for name in MENUS},
                "usage": "studio.py directions list MENU · show SLUG · brief --for 'product, audience' · compare FP1 FP2"}
    if menu not in MENUS:
        raise ValueError(f"Nieznane menu {menu!r}; dostępne: {', '.join(MENUS)}")
    return {"menu": menu, "items": data[menu]}


def show(slug: str) -> dict:
    data = load()
    for menu in MENUS:
        for item in data[menu]:
            if isinstance(item, dict) and (item.get("slug") == slug or (menu == "opener_concepts" and str(item.get("id")) == slug)):
                result = {"menu": menu, **item}
                preset = item.get("preset")
                if preset:
                    result["example"] = "examples/motion-styles/index.html?style=" + preset
                return result
    raise ValueError(f"Nie ma pozycji {slug!r}; użyj: studio.py directions list MENU")


def _rank(items: list[dict], wanted: set[str], keys: tuple[str, ...], limit: int) -> list[dict]:
    ranked = []
    for index, item in enumerate(items):
        tags = set()
        for key in keys:
            value = item.get(key, "")
            tags |= _tokens(" ".join(value) if isinstance(value, list) else str(value))
        score = len(tags & wanted)
        ranked.append((-score, index, item, score))
    ranked.sort(key=lambda r: r[:2])
    return [{**r[2], "match": r[3]} for r in ranked[:limit]]


def brief(subject: str, kind: str = "opener", previous: str | None = None) -> dict:
    """Szkielet style briefu: trzy kandydackie koncepty + kierunki dobrane po słowach z briefu.

    Dopasowanie jest leksykalne i jawne (pole `match`); to punkt startu do rozmowy z
    użytkownikiem, nie automatyczna decyzja kreatywna.
    """
    if not subject.strip():
        raise ValueError("Podaj --for 'produkt, odbiorca, nastrój', np. 'fintech app for students'")
    if kind not in ("opener", "explainer"):
        raise ValueError("kind: opener albo explainer")
    data, wanted = load(), _tokens(subject)
    result = {"subject": subject, "kind": kind,
              "fields": data["style_brief_fields"],
              "fingerprint_template": " · ".join(FINGERPRINT_PARTS),
              "checks": ["Show the brief and rundown before code; wait for a requested approval",
                         "Every palette color states its brand source or 'derived: reason'",
                         "At most two canonical components, each demanded by the concept",
                         "Run studio.py motion lint on the built HTML, then inspect real frames"]}
    if kind == "opener":
        result["concept_candidates"] = _rank(data["opener_concepts"], wanted, ("good_for", "premise", "name"), 3)
        result["canonical_components"] = data["canonical_components"]
    else:
        result["explainer_modes"] = _rank(data["explainer_modes"], wanted, ("best_for", "look", "name"), 3)
    result["direction_candidates"] = _rank(data["style_directions"], wanted, ("good_for", "name"), 3)
    if previous:
        result["previous_fingerprint"] = parse_fingerprint(previous)
        result["novelty_rule"] = "new concept, or at least 3 of 5 fingerprint parts different (studio.py directions compare)"
    return result


def parse_fingerprint(text: str) -> dict:
    parts = [p.strip() for p in re.split(r"\s*[·|]\s*", text.strip()) if p.strip()]
    if len(parts) != len(FINGERPRINT_PARTS):
        raise ValueError("Odcisk struktury ma 5 części: " + " · ".join(FINGERPRINT_PARTS))
    return dict(zip(FINGERPRINT_PARTS, parts))


def _same(a: str, b: str) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return a.strip().casefold() == b.strip().casefold()
    return len(ta & tb) / len(ta | tb) >= 0.6


def compare(first: str, second: str) -> dict:
    """Porównaj dwa odciski struktury; nowy film to inny koncept albo ≥3 z 5 różnych części."""
    a, b = parse_fingerprint(first), parse_fingerprint(second)
    different = [part for part in FINGERPRINT_PARTS if not _same(a[part], b[part])]
    concept_changed = "concept" in different
    return {"first": a, "second": b, "different": different, "different_count": len(different),
            "concept_changed": concept_changed,
            "distinct": concept_changed or len(different) >= 3,
            "rule": "distinct = different concept, or >= 3 of 5 parts different; lexical check, review the rundown too"}


def session(subject: str, kind: str = "footage") -> dict:
    """Offline discussion packet, not an approved plan or automated media analysis."""
    if not subject.strip():
        raise ValueError("Podaj temat filmu przez --for")
    profiles = {
        "footage": [
            ("Historia z materiałów", "Najmocniejszy autentyczny moment", "Rough cut dialogu, J/L cuts i B-roll zakrywający cięcia", "Głos i atmosfera; muzyka poniżej mowy", "Potrzebuje dobrych ujęć i selekcji; mniej dekoracyjnych efektów"),
            ("Editorial collage", "Detal produktu z krótkim podpisem", "Wycinanki, match cuts, maski i typografia prowadząca uwagę", "Rytm muzyki, pojedyncze akcenty cięć", "Wymaga zdjęć lub klipów o odpowiedniej rozdzielczości"),
            ("Kinetic teaser", "Jedna mocna fraza powiązana z ujęciem", "Kontrast skali, kontrolowane przyspieszenia, pauza na rezultat", "Akcent kulminacji i przestrzeń na końcową informację", "Więcej energii kosztem szczegółowego wyjaśnienia")],
        "product": [
            ("Prawdziwe demo", "Problem widoczny w istniejącym interfejsie", "Akcja użytkownika → zmiana stanu → czytelny rezultat", "Dyskretne potwierdzenia akcji, opcjonalna narracja", "Wymaga nagrania lub dostępu do aplikacji"),
            ("Ilustracja produktu", "Duży charakterystyczny fragment UI", "Stały obiekt, zmiana danych i kadru bez skoków tekstu", "Minimalny motyw z jednym akcentem rezultatu", "Mockup trzeba oznaczyć jako ilustrację, nie działający produkt"),
            ("Historia korzyści", "Konkretna sytuacja odbiorcy", "Kontekst → funkcja → jej praktyczny efekt", "Narracja prowadzi montaż; muzyka wspiera emocję", "Potrzebuje potwierdzonych informacji i materiałów kontekstowych")],
        "explainer": [
            ("Mechanizm krok po kroku", "Przedmiot lub proces do wyjaśnienia", "Elementy pozostają w scenie i pokazują związki przyczynowe", "Narracja z pauzami na zrozumienie", "Wymaga weryfikacji faktów i czytelnych etykiet"),
            ("Visual journalism", "Pytanie oraz źródłowy obraz lub dane", "Zdjęcia, zaznaczenia i porównania na wspólnej osi", "Spokojny podkład, pierwszeństwo głosu", "Potrzebne źródła danych i prawa do zdjęć"),
            ("Flat vector story", "Jedna wizualna metafora tematu", "Obiekty transformują się, zamiast znikać między slajdami", "Lekki rytm i celowe efekty obiektów", "Metafora nie może zniekształcać faktów")]
    }
    if kind not in profiles:
        raise ValueError("Tryb sesji: footage, product lub explainer")
    return {
        "schema_version": 1, "subject": subject.strip(), "mode": kind,
        "status": "proposal", "approval": None,
        "note": "To menu rozmowy. Agent dopasowuje sceny do materiałów; komenda nie ogląda plików ani nie wybiera za użytkownika.",
        "questions_if_unknown": ["Dla kogo i jaki rezultat?", "Długość, format i miejsce publikacji?", "Materiały, marka i referencje?", "Głos, muzyka, napisy i preferencje dźwięku?", "Który kierunek wybierasz lub czy delegujesz wybór?"],
        "options": [dict(id=str(i+1), name=n, first_frame=f, editing=m, audio=a, tradeoff=t)
                    for i, (n,f,m,a,t) in enumerate(profiles[kind])],
        "recommendation": "Agent rekomenduje jedną opcję po sprawdzeniu briefu i dostępnych materiałów, podając powód.",
        "working_files": ["direction.md", "edit-plan.md", "audio-cues.md", "feedback.md"],
        "edit_plan_columns": ["timeline_in", "timeline_out", "source_asset", "source_in", "source_out", "purpose", "action_and_result", "transition", "audio_cue", "acceptance"],
        "preview_steps": ["Zatwierdzony kierunek lub jawna delegacja", "Reprezentatywna scena i próbka dźwięku", "Rough cut całej historii", "Motion i miks", "Nowy render, kontrola obrazu/dźwięku, feedback", "Akceptacja konkretnej wersji i istniejące bramki pack"],
        "feedback": {"version_sha": None, "keep": [], "change": [], "ratings_optional": ["style", "pacing", "clarity"], "acceptance": None},
        "checks": ["Nie wymyślaj timecode ani analizy mediów", "Nie oznaczaj placeholderów jako gotowych assetów", "Nie traktuj cue sheet jako gotowego miksu", "Nie renderuj całego filmu w oczekiwaniu na wybór", "Zachowaj poprzednią wersję i odnotuj zakres zmian"]
    }

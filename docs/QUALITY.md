# Kontrola gotowego filmu

`probe` zapisuje technical.json powiązany z SHA mastera i fingerprintem specyfikacji. Zmiana briefu, researchu, scenariusza, storyboardu, assetów, timeline lub profilu wymaga nowej kontroli. Zmiana renderu wymaga także aktualnego review.

W review.json zapisz `render_sha256`, recenzenta i lokalne `evidence` (np. contact sheet). Każdy `pass` wymaga konkretnej notatki; `na` wymaga uzasadnienia i nie zastępuje wymaganych napisów lub audio.

| Kontrola | Co sprawdzić |
|---|---|
| visual | Czytelność na telefonie, kadry, marginesy, polskie znaki, ciągłość produktu/osoby, timing, przejścia i błyski |
| audio | Odsłuch, wymowa, muzyka pod głosem, cięcia, przestery i synchronizacja |
| captions | Nazwy, liczby, sens, timing i bezpieczne położenie napisów |
| facts | Claims zgodne z odczytanymi źródłami, przykładowe dane oznaczone |
| rights | Pochodzenie mediów i warunki użycia w konkretnym filmie |
| platform | Proporcje i kompozycja, pierwszy kadr, cover i interfejs platformy |

Gdy oględziny lub odsłuch są niedostępne, zapisz ograniczenie i pozostaw punkt `pending`. `pack` sprawdza kompletność zapisanych dowodów, nie prawdziwość deklaracji recenzenta. Nie publikuje filmu.

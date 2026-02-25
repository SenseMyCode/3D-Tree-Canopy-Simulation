1. Pobierz repozytorium

git clone <URL>
cd project

2. (Opcjonalnie) Utwórz wirtualne środowisko

python -m venv venv
venv\Scripts\activate      # Windows

3. Zainstaluj zależności

pip install -r requirements.txt

🧪 4. Uruchamianie eksperymentów
Eksperyment 1 — kompensacja wzrostu (2 drzewa + wizualizacja)
Kod

python presentation.py

python exp1.py

Otworzy się okno Vispy z animacją wzrostu drzew.
Eksperyment 2 — wpływ położenia słońca (symulacje + CSV)
Kod

python exp2.py

Wyniki zostaną zapisane do:

    exp2_results.csv

    exp2_summary.csv

Eksperyment 2 — wizualizacja 3D
Kod

python exp2_visualize.py

Wyświetla kolejne sceny dla różnych pozycji słońca.
Eksperyment 3 — konkurencja drzew w lesie (symulacje + CSV)
Kod

python exp3.py

Wyniki:

    exp3_results.csv

    exp3_summary.csv

Eksperyment 3 — wizualizacja lasów
Kod

python exp3_visualize_trees.py

Wyświetla sceny z 1, 4, 9 i 16 drzewami.
🎨 5. Wizualizacje (Vispy)

Projekt używa Vispy z backendem OpenGL.
Jeśli pojawią się problemy z backendem, zainstaluj:
Kod

pip install PyQt5

lub
Kod

pip install glfw

Vispy automatycznie wybierze dostępny backend.

🧰 Wymagania wstępne

Zanim zaczniesz, upewnij się, że masz:

    Python 3.8–3.11 (najlepiej 3.10 lub 3.11)

    pip (instalator pakietów)

    git

    System:

        Windows 10/11

        macOS

        Linux (Ubuntu/Debian/Fedora)

    Najtrudniejszym elementem jest instalacja Mayavi, bo wymaga bibliotek graficznych VTK. Poniżej masz gotowe instrukcje dla każdego systemu.

📦 1. Pobranie projektu

Otwórz terminal i wpisz:
bash

git clone https://github.com/SenseMyCode/3D-Tree-Canopy-Simulation.git
cd 3D-Tree-Canopy-Simulation

🏗️ 2. Utworzenie środowiska wirtualnego (zalecane)
Windows
bash

python -m venv venv
venv\Scripts\activate

macOS / Linux
bash

python3 -m venv venv
source venv/bin/activate

📚 3. Instalacja zależności
🔵 3.1. Instalacja NumPy i Matplotlib (proste)
bash

pip install numpy matplotlib

🔵 3.2. Instalacja Mayavi (najważniejsze)
Windows

Najprościej przez wheel z nieoficjalnego repozytorium:

    Wejdź na:
    https://www.lfd.uci.edu/~gohlke/pythonlibs/#mayavi (lfd.uci.edu in Bing)

    Pobierz plik mayavi‑<wersja>‑cp<python>‑win_amd64.whl

    Zainstaluj:

bash

pip install mayavi‑...whl

macOS
bash

brew install vtk
pip install mayavi

Linux (Ubuntu)
bash

sudo apt-get install python3-pyqt5 python3-pyqt5.qtopengl
sudo apt-get install python3-vtk7
pip install mayavi

▶️ 4. Uruchomienie projektu

W repozytorium znajduje się główny skrypt symulacji, zwykle:
bash

python main.py

lub jeśli projekt ma inny punkt startowy:
bash

python simulation.py

Jeśli nie jesteś pewien — daj mi znać, sprawdzę strukturę repozytorium i wskażę dokładny plik startowy.
🧪 5. Test działania

Po uruchomieniu powinno otworzyć się okno 3D z wizualizacją korony drzewa.
Jeśli pojawią się błędy typu:

    ImportError: No module named mayavi

    VTK not found

    Qt backend missing

— napisz, a pomogę je rozwiązać (Mayavi bywa kapryśne).
📁 6. (Opcjonalnie) Instalacja wszystkich zależności z pliku

Jeśli repozytorium zawiera requirements.txt, możesz zrobić:
bash

pip install -r requirements.txt

Jeśli go nie ma — mogę przygotować go dla Ciebie na podstawie kodu.

import os

# Foldery tworzone automatycznie – POMIJAMY
POMINIETE_FOLDERY = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "build"
}

# Rozszerzenia plików z kodem
DOZWOLONE_ROZSZERZENIA = {
    ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h",
    ".html", ".css", ".scss",
    ".json", ".yml", ".yaml",
    ".md", ".txt"
}

def polacz_pliki_rekurencyjnie(folder, plik_wyjsciowy="wynik.txt"):
    with open(plik_wyjsciowy, "w", encoding="utf-8") as out:
        for root, dirs, files in os.walk(folder):
            # USUWAMY foldery techniczne (os.walk ich nie odwiedzi)
            dirs[:] = [d for d in dirs if d not in POMINIETE_FOLDERY]

            for nazwa_pliku in files:
                rozszerzenie = os.path.splitext(nazwa_pliku)[1].lower()
                if rozszerzenie not in DOZWOLONE_ROZSZERZENIA:
                    continue

                sciezka = os.path.join(root, nazwa_pliku)
                sciezka_rel = os.path.relpath(sciezka, folder)

                out.write(f"{sciezka_rel}\n")

                try:
                    with open(sciezka, "r", encoding="utf-8") as f:
                        out.write(f.read())
                except UnicodeDecodeError:
                    out.write("[Nie można odczytać pliku – zła enkodacja]")

                out.write("\n\n")

# URUCHOMIENIE
polacz_pliki_rekurencyjnie(
    "C:/Users/torna/OneDrive/Desktop/Visual studio code/3D-Tree-Canopy-Simulation"
)

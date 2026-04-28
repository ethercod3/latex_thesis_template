# Прогоняет mmdc по всем рисункам в папке mermaid

from pathlib import Path
from os import system

DST = "figures"
SRC = "mermaid"

files = [f for f in Path(SRC).iterdir() if f.is_file()]

for f in files:
    basename = f.stem
    system(f"mmdc -i {str(f)} -o {DST}\\{basename}.pdf -f ")
    print(f"{basename} done")
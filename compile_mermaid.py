# Прогоняет mmdc по всем рисункам в папке mermaid

from pathlib import Path
import subprocess

SRC = Path("mermaid")
DST = Path("figures")

DST.mkdir(parents=True, exist_ok=True)

for f in SRC.iterdir():
    if not f.is_file():
        continue

    output_file = DST / f"{f.stem}.pdf"

    try:
        subprocess.run(
            f'mmdc -i "{f}" -o "{output_file}" -f',
            check=True,
            shell=True
        )    
        print(f"{f.name} -> {output_file.name} done")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {f.name}: {e}")
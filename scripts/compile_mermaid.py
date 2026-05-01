from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

SRC = Path("mermaid")
DST = Path("figures")

DST.mkdir(parents=True, exist_ok=True)

def process_file(f: Path):
    if not f.is_file():
        return None

    output_file = DST / f"{f.stem}.pdf"

    cmd = f'mmdc -i "{f}" -o "{output_file}" -f'

    try:
        subprocess.run(
            cmd,
            check=True,
            shell=True
        )
        return f"{f.name} -> {output_file.name} done"
    except subprocess.CalledProcessError as e:
        return f"Error processing {f.name}: {e}"


files = list(SRC.iterdir())

MAX_WORKERS = min(4, len(files))

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(process_file, f) for f in files]

    for future in as_completed(futures):
        result = future.result()
        if result:
            print(result)
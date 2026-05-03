import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC = PROJECT_DIR / "mermaid"
DST = PROJECT_DIR / "figures"

EXTENSIONS = {".mmd", ".mermaid", ".mmdc"}
MAX_WORKERS_LIMIT = 4
TIMEOUT_SECONDS = 60

def find_mmdc() -> str:
    mmdc = shutil.which("mmdc") or shutil.which("mmdc.cmd")

    if mmdc is None:
        raise RuntimeError("mmdc or mmdc.cmd was not found in PATH")

    return mmdc


def process_file(f: Path, mmdc: str) -> str | None:
    if not f.is_file():
        return None

    if f.suffix.lower() not in EXTENSIONS:
        return None

    output_file = DST / f"{f.stem}.pdf"

    cmd = [mmdc, "-i", str(f), "-o", str(output_file), "-f"]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        return f"[OK] {f.name} -> {output_file.name}"

    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] {f.name}: exceeded {TIMEOUT_SECONDS}s"

    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else "no stdout"
        stderr = e.stderr.strip() if e.stderr else "no stderr"

        return (
            f"[ERROR] {f.name}\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}"
        )


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(f"Source directory does not exist: {SRC}")

    mmdc = find_mmdc()

    files = [
        f for f in SRC.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSIONS
    ]

    if not files:
        print(f"No Mermaid files found in {SRC}")
        return

    max_workers = min(MAX_WORKERS_LIMIT, len(files))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_file, f, mmdc): f
            for f in files
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    print(result)
            except Exception as e:
                f = futures[future]
                print(f"[ERROR] {f.name}: unexpected error: {e}")


if __name__ == "__main__":
    DST.mkdir(parents=True, exist_ok=True)
    main()

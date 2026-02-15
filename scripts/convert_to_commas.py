# Script: convert_to_commas.py
# Scans Data/ for .csv files, detects delimiter, creates a .bak backup,
# and rewrites the file using comma (,) as delimiter.

import csv
from pathlib import Path
import shutil

DATA_DIR = Path(__file__).resolve().parents[1] / 'Data'
POSSIBLE_DELIMITERS = [',', '\t', ';', '|']

def detect_delimiter(sample: str) -> str:
    # Try csv.Sniffer first, fallback to heuristic
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample, delimiters=POSSIBLE_DELIMITERS)
        return dialect.delimiter
    except Exception:
        if '\t' in sample:
            return '\t'
        if ';' in sample:
            return ';'
        if '|' in sample:
            return '|'
        return ','


def normalize_file(path: Path) -> bool:
    text_sample = path.read_text(encoding='utf-8', errors='replace')[:8192]
    delim = detect_delimiter(text_sample)
    if delim == ',':
        print(f"SKIP: {path.name} already comma-separated")
        return False

    bak = path.with_suffix(path.suffix + '.bak')
    shutil.copy(path, bak)

    rows = []
    with path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter=delim)
        for row in reader:
            rows.append(row)

    # Write to a temp file then replace
    tmp = path.with_suffix('.tmp')
    with tmp.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for r in rows:
            writer.writerow(r)

    tmp.replace(path)
    print(f"CONVERTED: {path.name} (backup -> {bak.name})")
    return True


def main():
    if not DATA_DIR.exists():
        print(f"Data directory not found: {DATA_DIR}")
        return

    changed = []
    for p in sorted(DATA_DIR.glob('*.csv')):
        try:
            if normalize_file(p):
                changed.append(p.name)
        except Exception as e:
            print(f"ERROR: {p.name} -> {e}")

    print('\nSummary:')
    print(f"Files converted: {len(changed)}")
    for n in changed:
        print(' -', n)

if __name__ == '__main__':
    main()

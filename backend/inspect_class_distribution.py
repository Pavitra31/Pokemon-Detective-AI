
import csv
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "datasets" / "pokemon_clean_manifest.csv"


def main():
    with MANIFEST_PATH.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        rows = list(csv.DictReader(file))

    counts = Counter(row["pokemon"] for row in rows)
    frequencies = list(counts.values())

    print("========== CLASS DISTRIBUTION ==========")
    print("Total images:", len(rows))
    print("Total classes:", len(counts))
    print("Minimum images per class:", min(frequencies))
    print("Maximum images per class:", max(frequencies))
    print(
        "Average images per class:",
        round(sum(frequencies) / len(frequencies), 2),
    )

    for threshold in (10, 20, 30, 50, 80, 100):
        print(
            f"Classes with fewer than {threshold} images:",
            sum(count < threshold for count in frequencies),
        )

    print("\n10 classes with the fewest images:")
    for name, count in sorted(counts.items(), key=lambda item: item[1])[:10]:
        print(f"  {name}: {count}")

    print("\n10 classes with the most images:")
    for name, count in counts.most_common(10):
        print(f"  {name}: {count}")

    print("========================================")


if __name__ == "__main__":
    main()

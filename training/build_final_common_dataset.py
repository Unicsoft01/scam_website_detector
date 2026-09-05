from pathlib import Path
import pandas as pd


BASE = Path("data/processed")

OUTPUT = Path(
    "data/experiments/v1_1/final_common_dataset.csv"
)


def main():

    heuristic = pd.read_csv(
        BASE / "heuristic_dataset.csv"
    )

    behavioural = pd.read_csv(
        BASE / "behavioural_dataset.csv"
    )

    hybrid = pd.read_csv(
        BASE / "hybrid_dataset.csv"
    )


    key = "registrable_domain"


    common = (
        set(heuristic[key])
        &
        set(behavioural[key])
        &
        set(hybrid[key])
    )


    print("==============================")
    print("FINAL COMMON DATASET")
    print("==============================")

    print(
        "Common URLs:",
        len(common)
    )


    final = hybrid[
        hybrid[key].isin(common)
    ].copy()


    final.to_csv(
        OUTPUT,
        index=False
    )


    print()
    print("Saved:")
    print(OUTPUT)


if __name__ == "__main__":
    main()
    
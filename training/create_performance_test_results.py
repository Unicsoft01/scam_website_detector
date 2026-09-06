from pathlib import Path
import pandas as pd


INPUT = Path(
    "data/interim/feature_extraction_log.csv"
)

OUTPUT = Path(
    "data/experiments/v1_1/performance_test_results.csv"
)



def main():

    if not INPUT.exists():
        raise FileNotFoundError(
            INPUT
        )


    df = pd.read_csv(INPUT)


    required = [
        "heuristic_duration_ms",
        "behavioural_duration_ms",
        "total_duration_ms",
        "heuristic_success",
        "behavioural_success",
        "hybrid_success",
    ]


    missing = [
        c for c in required
        if c not in df.columns
    ]


    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )


    performance = df[
        [
            "url",
            "registrable_domain",
            "heuristic_duration_ms",
            "behavioural_duration_ms",
            "total_duration_ms",
            "heuristic_success",
            "behavioural_success",
            "hybrid_success",
        ]
    ].copy()


    performance["completion_status"] = (
        (
            performance["hybrid_success"]
            == True
        )
        .astype(int)
    )


    performance["timeout_status"] = (
        (
            performance["behavioural_success"]
            == False
        )
        .astype(int)
    )


    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    performance.to_csv(
        OUTPUT,
        index=False
    )


    print(
        "Created:"
    )

    print(
        OUTPUT
    )

    print()

    print(
        performance.head()
    )


if __name__ == "__main__":
    main()
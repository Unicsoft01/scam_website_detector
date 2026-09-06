from pathlib import Path
import pandas as pd


INPUT = Path(
    "data/experiments/v1_1/performance_test_results.csv"
)

OUTPUT = Path(
    "data/experiments/v1_1/performance_test_results.csv"
)


def main():

    df = pd.read_csv(INPUT)


    df["validation_time_ms"] = 0


    df["heuristic_time_ms"] = (
        df["heuristic_duration_ms"]
    )


    df["behavioural_time_ms"] = (
        df["behavioural_duration_ms"]
    )


    df["hybrid_scan_time_ms"] = (
        df["total_duration_ms"]
    )


    df["response_time_ms"] = (
        df["total_duration_ms"]
    )


    df.to_csv(
        OUTPUT,
        index=False
    )


    print(
        "Updated performance columns"
    )

    print(
        df.columns.tolist()
    )


if __name__ == "__main__":
    main()
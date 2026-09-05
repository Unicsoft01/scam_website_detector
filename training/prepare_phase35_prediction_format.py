from pathlib import Path
import pandas as pd


INPUT = Path(
    "data/experiments/v1_1/final_test_predictions.csv"
)

OUTPUT = Path(
    "data/experiments/v1_1/final_test_predictions.csv"
)


def main():

    df = pd.read_csv(INPUT)


    # Rename RF outputs
    df["heuristic_prediction"] = (
        df["RF-H_prediction"]
    )

    df["heuristic_probability"] = (
        df["RF-H_probability"]
    )


    df["behavioural_prediction"] = (
        df["RF-B_prediction"]
    )

    df["behavioural_probability"] = (
        df["RF-B_probability"]
    )


    # Temporary hybrid fusion
    # Alpha = 0.5 because no calibration has been performed yet

    df["hybrid_probability"] = (
        (
            df["heuristic_probability"]
            +
            df["behavioural_probability"]
        )
        /
        2
    )


    df["hybrid_prediction"] = (
        df["hybrid_probability"]
        >=
        0.5
    ).astype(int)


    df.to_csv(
        OUTPUT,
        index=False
    )


    print(
        "Updated:"
    )

    print(
        OUTPUT
    )

    print()

    print(
        "Added columns:"
    )

    for c in [
        "heuristic_prediction",
        "behavioural_prediction",
        "hybrid_prediction",
        "heuristic_probability",
        "behavioural_probability",
        "hybrid_probability",
    ]:
        print(c)


if __name__ == "__main__":
    main()
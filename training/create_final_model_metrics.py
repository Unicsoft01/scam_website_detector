from pathlib import Path
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)


INPUT = Path(
    "data/experiments/v1_1/final_test_predictions.csv"
)

OUTPUT = Path(
    "data/experiments/v1_1/final_model_metrics.csv"
)


def calculate_metrics(
    model_name,
    actual,
    predicted
):

    return {
        "model": model_name,
        "accuracy": round(
            accuracy_score(actual, predicted),
            4
        ),
        "precision": round(
            precision_score(
                actual,
                predicted,
                zero_division=0
            ),
            4
        ),
        "recall": round(
            recall_score(
                actual,
                predicted,
                zero_division=0
            ),
            4
        ),
        "f1": round(
            f1_score(
                actual,
                predicted,
                zero_division=0
            ),
            4
        ),
    }



def main():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing file: {INPUT}"
        )


    df = pd.read_csv(INPUT)


    required = [
        "binary_label",
        "heuristic_prediction",
        "behavioural_prediction",
        "hybrid_prediction",
    ]


    missing = [
        c for c in required
        if c not in df.columns
    ]


    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )


    results = []


    results.append(
        calculate_metrics(
            "RF-H",
            df["binary_label"],
            df["heuristic_prediction"]
        )
    )


    results.append(
        calculate_metrics(
            "RF-B",
            df["binary_label"],
            df["behavioural_prediction"]
        )
    )


    results.append(
        calculate_metrics(
            "Hybrid",
            df["binary_label"],
            df["hybrid_prediction"]
        )
    )


    metrics = pd.DataFrame(results)


    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    metrics.to_csv(
        OUTPUT,
        index=False
    )


    print(
        "FINAL MODEL METRICS CREATED"
    )

    print()

    print(metrics)

    print()

    print(
        "Saved:"
    )

    print(
        OUTPUT
    )


if __name__ == "__main__":
    main()
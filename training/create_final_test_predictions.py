from pathlib import Path
import pandas as pd
import joblib


BASE = Path(
    "data/experiments/v1_1"
)

MODEL_DIR = Path(
    "models"
)


def prepare_features(df):

    drop_cols = [
        "registrable_domain",
        "url",
        "original_url",
        "final_url",
        "scam_category",
        "source",
        "source_category",
        "original_label",
        "submitted_url",
        "normalized_url",
        "audit_timestamp",
    ]

    X = df.drop(
        columns=[
            c for c in drop_cols
            if c in df.columns
        ]
        + ["binary_label"],
        errors="ignore"
    )

    return X.select_dtypes(
        include=["number"]
    )


def main():

    test = pd.read_csv(
        BASE / "final_test.csv"
    )


    X_test = prepare_features(
        test
    )


    models = {
        "RF-H":
        MODEL_DIR /
        "rf_heuristic.joblib",

        "RF-B":
        MODEL_DIR /
        "rf_behavioural.joblib",
    }


    output = test.copy()


    for name, path in models.items():

        model = joblib.load(
            path
        )

        output[
            f"{name}_prediction"
        ] = model.predict(
            X_test
        )

        output[
            f"{name}_probability"
        ] = model.predict_proba(
            X_test
        )[:,1]


    output.to_csv(
        BASE /
        "final_test_predictions.csv",
        index=False
    )


    print(
        "Created:"
    )

    print(
        BASE /
        "final_test_predictions.csv"
    )


if __name__ == "__main__":
    main()
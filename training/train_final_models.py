from pathlib import Path
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


BASE = Path(
    "data/experiments/v1_1"
)

MODEL_DIR = Path(
    "models"
)

MODEL_DIR.mkdir(
    exist_ok=True
)


def train_model(
    train_file,
    test_file,
    dataset_name,
    model_file,
    prediction_file
):

    train = pd.read_csv(
        BASE / train_file
    )

    test = pd.read_csv(
        BASE / test_file
    )


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


    X_train = train.drop(
        columns=[
            c for c in drop_cols
            if c in train.columns
        ]
        + ["binary_label"]
    )


    y_train = train["binary_label"]


    X_test = test.drop(
        columns=[
            c for c in drop_cols
            if c in test.columns
        ]
        + ["binary_label"]
    )


    y_test = test["binary_label"]


    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

      # Keep only numeric machine-learning features
    X_train = X_train.select_dtypes(
      include=["number"]
      )

    X_test = X_test.select_dtypes(
      include=["number"]
      )

    model.fit(
        X_train,
        y_train
    )


    predictions = model.predict(
        X_test
    )


    probabilities = model.predict_proba(
        X_test
    )[:,1]


    output = test.copy()

    output["prediction"] = predictions
    output["probability"] = probabilities


    output.to_csv(
        BASE / prediction_file,
        index=False
    )


    joblib.dump(
        model,
        MODEL_DIR / model_file
    )


    metrics = {

        "model": dataset_name,

        "accuracy":
        accuracy_score(
            y_test,
            predictions
        ),

        "precision":
        precision_score(
            y_test,
            predictions,
            zero_division=0
        ),

        "recall":
        recall_score(
            y_test,
            predictions,
            zero_division=0
        ),

        "f1":
        f1_score(
            y_test,
            predictions,
            zero_division=0
        )
    }


    return metrics



def main():

    results=[]


    results.append(
        train_model(
            "final_train.csv",
            "final_test.csv",
            "RF-H",
            "rf_heuristic.joblib",
            "heuristic_test_predictions.csv"
        )
    )


    results.append(
        train_model(
            "final_train.csv",
            "final_test.csv",
            "RF-B",
            "rf_behavioural.joblib",
            "behavioural_test_predictions.csv"
        )
    )


    pd.DataFrame(
        results
    ).to_csv(
        BASE /
        "final_model_metrics.csv",
        index=False
    )


    print(
        "FINAL MODELS TRAINED"
    )

    print(
        pd.DataFrame(results)
    )


if __name__ == "__main__":
    main()
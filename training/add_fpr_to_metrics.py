from pathlib import Path
import pandas as pd
from sklearn.metrics import confusion_matrix


INPUT = Path(
    "data/experiments/v1_1/final_test_predictions.csv"
)

OUTPUT = Path(
    "data/experiments/v1_1/final_model_comparison.csv"
)



def calculate_fpr(
    y_true,
    y_pred
):

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred
    ).ravel()

    return round(
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0,
        4
    )



def main():

    predictions = pd.read_csv(INPUT)


    rows = []


    models = {
        "RF-H": "heuristic_prediction",
        "RF-B": "behavioural_prediction",
        "Hybrid": "hybrid_prediction",
    }


    for name, column in models.items():

        rows.append(
            {
                "model": name,
                "fpr": calculate_fpr(
                    predictions["binary_label"],
                    predictions[column]
                )
            }
        )


    fpr_df = pd.DataFrame(rows)


    existing = pd.read_csv(OUTPUT)


    merged = existing.merge(
        fpr_df,
        on="model",
        how="left"
    )


    merged.to_csv(
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

    print(merged)



if __name__ == "__main__":
    main()
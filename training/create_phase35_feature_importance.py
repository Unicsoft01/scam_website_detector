from pathlib import Path
import pandas as pd
import joblib


MODEL_DIR = Path("models")

OUTPUT_DIR = Path(
    "data/processed/model_training"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def generate(model_file, output_file):

    model_path = MODEL_DIR / model_file

    print(
        "Loading:",
        model_path
    )

    model = joblib.load(
        model_path
    )


    if not hasattr(
        model,
        "feature_names_in_"
    ):
        raise RuntimeError(
            "Model does not contain feature names."
        )


    features = list(
        model.feature_names_in_
    )


    importances = list(
        model.feature_importances_
    )


    print(
        "Features:",
        len(features)
    )

    print(
        "Importances:",
        len(importances)
    )


    importance_df = pd.DataFrame(
        {
            "feature": features,
            "importance": importances
        }
    )


    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False
    )


    output_path = OUTPUT_DIR / output_file


    importance_df.to_csv(
        output_path,
        index=False
    )


    print(
        "Created:",
        output_path
    )



def main():

    generate(
        "rf_heuristic.joblib",
        "heuristic_feature_importance.csv"
    )


    generate(
        "rf_behavioural.joblib",
        "behavioural_feature_importance.csv"
    )



if __name__ == "__main__":
    main()
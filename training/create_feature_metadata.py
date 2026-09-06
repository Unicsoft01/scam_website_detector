from pathlib import Path
import pandas as pd


OUTPUT = Path(
    "models/runtime/v1.1.0"
)


def save_features(
    dataset,
    filename
):

    df = pd.read_csv(dataset)

    drop_columns = [
        "url",
        "original_url",
        "registrable_domain",
        "source",
        "source_category",
        "binary_label",
        "scam_category",
        "original_label"
    ]


    features = [
        c for c in df.columns
        if c not in drop_columns
    ]


    pd.DataFrame(
        {
            "feature": features
        }
    ).to_csv(
        OUTPUT / filename,
        index=False
    )


    print(
        "Created:",
        OUTPUT / filename
    )



def main():

    OUTPUT.mkdir(
        parents=True,
        exist_ok=True
    )


    save_features(
        "data/processed/heuristic_dataset.csv",
        "rf_heuristic_features.csv"
    )


    save_features(
        "data/processed/behavioural_dataset.csv",
        "rf_behavioural_features.csv"
    )


if __name__ == "__main__":
    main()
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


INPUT = Path(
    "data/experiments/v1_1/final_common_dataset.csv"
)

OUTPUT = Path(
    "data/experiments/v1_1"
)


def main():

    df = pd.read_csv(INPUT)

    print("==============================")
    print("FINAL DATASET SPLIT")
    print("==============================")

    print("Total records:", len(df))


    train, test = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["binary_label"]
    )


    train, validation = train_test_split(
        train,
        test_size=0.25,
        random_state=42,
        stratify=train["binary_label"]
    )


    train.to_csv(
        OUTPUT / "final_train.csv",
        index=False
    )

    validation.to_csv(
        OUTPUT / "final_validation.csv",
        index=False
    )

    test.to_csv(
        OUTPUT / "final_test.csv",
        index=False
    )


    print()
    print("TRAIN:", len(train))
    print("VALIDATION:", len(validation))
    print("TEST:", len(test))

    print()
    print("Saved:")
    print("final_train.csv")
    print("final_validation.csv")
    print("final_test.csv")


if __name__ == "__main__":
    main()
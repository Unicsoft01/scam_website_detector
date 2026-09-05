from pathlib import Path
import pandas as pd


BASE = Path(
    "data/experiments/v1_1"
)


def main():

    files = [
        "final_train.csv",
        "final_validation.csv",
        "final_test.csv",
    ]

    datasets = {}

    print("==============================")
    print("FINAL SPLIT INTEGRITY CHECK")
    print("==============================")


    for file in files:

        path = BASE / file

        df = pd.read_csv(path)

        datasets[file] = df

        print()
        print(file)
        print("Rows:", len(df))

        print(
            "Label distribution:"
        )

        print(
            df["binary_label"]
            .value_counts()
            .to_dict()
        )


    print()
    print("==============================")
    print("OVERLAP CHECK")
    print("==============================")


    train_domains = set(
        datasets["final_train.csv"]
        ["registrable_domain"]
    )

    val_domains = set(
        datasets["final_validation.csv"]
        ["registrable_domain"]
    )

    test_domains = set(
        datasets["final_test.csv"]
        ["registrable_domain"]
    )


    print(
        "Train-Val overlap:",
        len(train_domains & val_domains)
    )

    print(
        "Train-Test overlap:",
        len(train_domains & test_domains)
    )

    print(
        "Val-Test overlap:",
        len(val_domains & test_domains)
    )


if __name__ == "__main__":
    main()
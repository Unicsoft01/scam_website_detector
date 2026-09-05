import pandas as pd


FILE = (
    "data/experiments/v1_1/"
    "final_dataset_split_manifest.csv"
)


def domains_for(dataframe, split):
    return set(
        dataframe.loc[
            dataframe["split"] == split,
            "registrable_domain",
        ]
        .dropna()
        .astype(str)
        .str.lower()
    )


def main():
    data = pd.read_csv(FILE)

    train = domains_for(
        data,
        "training",
    )

    validation = domains_for(
        data,
        "validation",
    )

    test = domains_for(
        data,
        "testing",
    )

    train_validation = (
        train & validation
    )

    train_test = (
        train & test
    )

    validation_test = (
        validation & test
    )

    print(
        "TRAIN DOMAINS:",
        len(train),
    )

    print(
        "VALIDATION DOMAINS:",
        len(validation),
    )

    print(
        "TEST DOMAINS:",
        len(test),
    )

    print(
        "\nTRAIN/VALIDATION OVERLAP:",
        len(train_validation),
    )

    print(
        "TRAIN/TEST OVERLAP:",
        len(train_test),
    )

    print(
        "VALIDATION/TEST OVERLAP:",
        len(validation_test),
    )

    if (
        train_validation
        or train_test
        or validation_test
    ):
        raise RuntimeError(
            "DOMAIN LEAKAGE DETECTED."
        )

    print(
        "\nFINAL SPLIT INTEGRITY: PASS"
    )


if __name__ == "__main__":
    main()
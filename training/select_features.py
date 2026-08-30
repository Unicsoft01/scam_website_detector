import json
from hashlib import sha256
from pathlib import Path

import pandas as pd

from app.ml.feature_selection import (
    calculate_mi_ranking,
    choose_best_candidate,
    evaluate_candidate_counts,
    prepare_train_validation_features,
)


SPLIT_ROOT = Path(
    "data/splits"
)

OUTPUT_ROOT = Path(
    "data/processed/"
    "feature_selection"
)


CONFIGURATIONS = {
    "heuristic": {
        "training":
            SPLIT_ROOT
            / "heuristic"
            / "training.csv",

        "validation":
            SPLIT_ROOT
            / "heuristic"
            / "validation.csv",
    },

    "behavioural": {
        "training":
            SPLIT_ROOT
            / "behavioural"
            / "training.csv",

        "validation":
            SPLIT_ROOT
            / "behavioural"
            / "validation.csv",
    },
}


def _read_dataset(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():

        raise FileNotFoundError(
            (
                "Required Phase 16 split "
                f"does not exist: {path}"
            )
        )

    try:

        dataframe = pd.read_csv(
            path
        )

    except pd.errors.EmptyDataError:

        raise ValueError(
            f"Dataset is empty: {path}"
        )

    if dataframe.empty:

        raise ValueError(
            f"Dataset has no rows: {path}"
        )

    return dataframe


def _sha256(
    path: Path,
) -> str:

    digest = sha256()

    with path.open(
        "rb"
    ) as file:

        for block in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):

            digest.update(
                block
            )

    return digest.hexdigest()


def process_configuration(
    feature_type: str,
    configuration: dict,
) -> dict:

    print()

    print(
        "=" * 72
    )

    print(
        f"{feature_type.upper()} FEATURE SELECTION"
    )

    print(
        "=" * 72
    )

    training_path = (
        configuration[
            "training"
        ]
    )

    validation_path = (
        configuration[
            "validation"
        ]
    )

    training = _read_dataset(
        training_path
    )

    validation = _read_dataset(
        validation_path
    )

    print(
        f"Training rows: "
        f"{len(training)}"
    )

    print(
        f"Validation rows: "
        f"{len(validation)}"
    )

    prepared = (
        prepare_train_validation_features(
            training=training,

            validation=validation,

            feature_type=feature_type,
        )
    )

    print(
        "Usable candidate features: "
        f"{prepared.x_train.shape[1]}"
    )

    print(
        "All-missing training features excluded: "
        f"{len(prepared.excluded_all_missing)}"
    )

    ranking = (
        calculate_mi_ranking(
            prepared.x_train,
            prepared.y_train,
        )
    )

    candidate_results = (
        evaluate_candidate_counts(
            prepared,
            ranking,
        )
    )

    best_count = (
        choose_best_candidate(
            candidate_results
        )
    )

    selected_features = (
        ranking[
            "feature"
        ]
        .head(
            best_count
        )
        .tolist()
    )

    ranking[
        "selected_candidate"
    ] = ranking[
        "feature"
    ].isin(
        selected_features
    )

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    ranking_path = (
        OUTPUT_ROOT
        / (
            f"{feature_type}"
            "_mi_ranking.csv"
        )
    )

    candidate_path = (
        OUTPUT_ROOT
        / (
            f"{feature_type}"
            "_candidate_results.csv"
        )
    )

    selected_path = (
        OUTPUT_ROOT
        / (
            f"{feature_type}"
            "_selected_features.json"
        )
    )

    ranking.to_csv(
        ranking_path,
        index=False,
    )

    candidate_results.to_csv(
        candidate_path,
        index=False,
    )

    selected_payload = {
        "feature_type":
            feature_type,

        "selection_method":
            "mutual_info_classif",

        "primary_validation_metric":
            "f1",

        "tie_breaker_1":
            "recall",

        "tie_breaker_2":
            "fewer_features",

        "selected_feature_count":
            best_count,

        "selected_features":
            selected_features,

        "training_medians":
            prepared.medians,

        "all_missing_training_features_excluded":
            prepared.excluded_all_missing,

        "training_file":
            str(
                training_path
            ),

        "validation_file":
            str(
                validation_path
            ),

        "training_sha256":
            _sha256(
                training_path
            ),

        "validation_sha256":
            _sha256(
                validation_path
            ),
    }

    selected_path.write_text(
        json.dumps(
            selected_payload,
            indent=2,
        ),

        encoding="utf-8",
    )

    best_row = (
        candidate_results[
            candidate_results[
                "feature_count"
            ]
            == best_count
        ]
        .iloc[
            0
        ]
    )

    print()

    print(
        f"Selected feature count: "
        f"{best_count}"
    )

    print(
        "Validation F1: "
        f"{best_row['validation_f1']:.4f}"
    )

    print(
        "Validation precision: "
        f"{best_row['validation_precision']:.4f}"
    )

    print(
        "Validation recall: "
        f"{best_row['validation_recall']:.4f}"
    )

    print()

    print(
        "Selected features:"
    )

    for index, feature in enumerate(
        selected_features,
        start=1,
    ):

        score = float(
            ranking.loc[
                ranking[
                    "feature"
                ]
                == feature,

                "mutual_information",
            ].iloc[0]
        )

        print(
            (
                f"{index:>3}. "
                f"{feature:<45} "
                f"MI={score:.6f}"
            )
        )

    print()

    print(
        f"Ranking saved: "
        f"{ranking_path}"
    )

    print(
        f"Candidate results saved: "
        f"{candidate_path}"
    )

    print(
        f"Selected features saved: "
        f"{selected_path}"
    )

    return {
        "feature_type":
            feature_type,

        "selected_count":
            best_count,

        "training_sha256":
            _sha256(
                training_path
            ),

        "validation_sha256":
            _sha256(
                validation_path
            ),
    }


def main():

    print()

    print(
        "PHASE 17 — MUTUAL INFORMATION "
        "FEATURE SELECTION"
    )

    print(
        "=" * 72
    )

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest_entries = []

    for (
        feature_type,
        configuration,
    ) in CONFIGURATIONS.items():

        result = process_configuration(
            feature_type,
            configuration,
        )

        manifest_entries.append(
            result
        )

    manifest_lines = [
        "PHASE 17 FEATURE SELECTION MANIFEST",
        "=" * 72,

        (
            "Method: "
            "sklearn.feature_selection."
            "mutual_info_classif"
        ),

        "Ranking data: training partition only",

        (
            "Candidate feature-count evaluation: "
            "validation partition only"
        ),

        (
            "Final test set used during "
            "feature selection: NO"
        ),

        (
            "Primary candidate-selection metric: "
            "validation F1"
        ),

        (
            "Tie-breakers: validation recall, "
            "then fewer features"
        ),

        (
            "Heuristic and behavioural features "
            "selected separately"
        ),

        "",
    ]

    for entry in manifest_entries:

        manifest_lines.extend(
            [
                (
                    f"{entry['feature_type']} "
                    f"selected count: "
                    f"{entry['selected_count']}"
                ),

                (
                    f"{entry['feature_type']} "
                    "training SHA256: "
                    f"{entry['training_sha256']}"
                ),

                (
                    f"{entry['feature_type']} "
                    "validation SHA256: "
                    f"{entry['validation_sha256']}"
                ),

                "",
            ]
        )

    manifest_path = (
        OUTPUT_ROOT
        / "feature_selection_manifest.txt"
    )

    manifest_path.write_text(
        "\n".join(
            manifest_lines
        ),

        encoding="utf-8",
    )

    print()

    print(
        "=" * 72
    )

    print(
        "FEATURE SELECTION COMPLETE"
    )

    print(
        "=" * 72
    )

    print(
        f"Manifest saved: "
        f"{manifest_path}"
    )


if __name__ == "__main__":
    main()
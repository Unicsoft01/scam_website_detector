def test_heuristic_and_behavioural_probabilities_fuse():

    heuristic_probability = 0.80
    behavioural_probability = 0.60
    alpha = 0.50

    hybrid_probability = (
        alpha * heuristic_probability
        + (1 - alpha)
        * behavioural_probability
    )

    assert (
        round(
            hybrid_probability,
            2,
        )
        == 0.70
    )
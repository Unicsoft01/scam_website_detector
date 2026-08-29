from datetime import (
    datetime,
    timezone,
)

from app.collectors.browser_environment import (
    observe_public_url,
)

from app.features.behavioural_features import (
    extract_behavioural_features,
)


def build_behavioural_observation(
    url: str,
    observation_time_ms: int = 2000,
) -> dict:
    """
    Build behavioural observation X_B.

    This function gathers and structures evidence only.
    It does not classify the website.
    """

    collection_timestamp = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    observation = (
        observe_public_url(
            url,
            observation_time_ms=(
                observation_time_ms
            ),
        )
    )

    if not observation.success:
        return {
            "success": False,

            "submitted_url":
                url,

            "collection_timestamp":
                collection_timestamp,

            "features": None,

            "metadata": {
                "error_type":
                    observation.error_type,

                "error_message":
                    observation.error_message,

                "final_url":
                    observation.final_url,
            },
        }

    x_b = (
        extract_behavioural_features(
            observation
        )
    )

    metadata = {
        "initial_url":
            observation.initial_url,

        "final_url":
            observation.final_url,

        "main_status_code":
            observation.main_status_code,

        "redirect_chain":
            observation.redirect_chain,

        "navigation_urls":
            observation.navigation_urls,

        "automatic_navigation_urls":
            observation.automatic_navigation_urls,

        "request_urls":
            observation.request_urls,

        "blocked_requests":
            observation.blocked_requests,

        "failed_requests":
            observation.failed_requests,

        "page_errors":
            observation.page_errors,
    }

    return {
        "success": True,

        "submitted_url":
            url,

        "collection_timestamp":
            collection_timestamp,

        "features":
            x_b,

        "metadata":
            metadata,
    }
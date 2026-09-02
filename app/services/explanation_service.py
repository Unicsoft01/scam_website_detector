from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvidenceIndicator:

    code: str

    title: str

    description: str

    category: str

    severity: str

    source: str

    observed_value: Any


class ExplanationService:
    """
    Converts recorded heuristic and behavioural
    observations into human-readable evidence
    summaries.

    These indicators describe observations only.

    They must not be interpreted as proof that
    a single feature caused the model prediction
    or independently proves that a website is
    fraudulent.
    """

    def explain(
        self,
        heuristic_features: dict | None,
        behavioural_features: dict | None,
        max_indicators: int = 10,
    ) -> list[EvidenceIndicator]:

        indicators: list[
            EvidenceIndicator
        ] = []

        if isinstance(
            heuristic_features,
            dict,
        ):

            indicators.extend(
                self._heuristic_indicators(
                    heuristic_features
                )
            )

        if isinstance(
            behavioural_features,
            dict,
        ):

            indicators.extend(
                self._behavioural_indicators(
                    behavioural_features
                )
            )

        indicators = (
            self._remove_duplicates(
                indicators
            )
        )

        indicators = sorted(
            indicators,
            key=self._severity_order,
        )

        return indicators[
            :max_indicators
        ]

    # -------------------------------------------------
    # Heuristic evidence
    # -------------------------------------------------

    def _heuristic_indicators(
        self,
        features: dict,
    ) -> list[EvidenceIndicator]:

        indicators = []

        # ---------------------------------------------
        # Suspicious URL structure
        # ---------------------------------------------

        suspicious_url_keys = [
            "h_ip_address_in_url",
            "ip_address_in_url",
            "h_ip_literal",
            "ip_literal",
            "h_suspicious_url",
            "suspicious_url",
        ]

        if self._any_positive(
            features,
            suspicious_url_keys,
        ):

            indicators.append(
                EvidenceIndicator(
                    code=(
                        "suspicious_url_structure"
                    ),
                    title=(
                        "Suspicious URL structure "
                        "detected"
                    ),
                    description=(
                        "The URL contains structural "
                        "characteristics associated "
                        "with elevated website risk."
                    ),
                    category="URL",
                    severity="medium",
                    source="Heuristic",
                    observed_value=True,
                )
            )

        # ---------------------------------------------
        # Long URL
        # ---------------------------------------------

        url_length = self._first_numeric(
            features,
            [
                "h_url_length",
                "url_length",
            ],
        )

        if (
            url_length is not None
            and url_length >= 100
        ):

            indicators.append(
                EvidenceIndicator(
                    code="long_url",
                    title=(
                        "Unusually long URL observed"
                    ),
                    description=(
                        "The submitted address is "
                        "relatively long and therefore "
                        "contains more URL components "
                        "than a typical short address."
                    ),
                    category="URL",
                    severity="low",
                    source="Heuristic",
                    observed_value=url_length,
                )
            )

        # ---------------------------------------------
        # Multiple subdomains
        # ---------------------------------------------

        subdomain_count = (
            self._first_numeric(
                features,
                [
                    "h_subdomain_count",
                    "subdomain_count",
                    "h_num_subdomains",
                    "num_subdomains",
                ],
            )
        )

        if (
            subdomain_count is not None
            and subdomain_count >= 3
        ):

            indicators.append(
                EvidenceIndicator(
                    code=(
                        "multiple_subdomains"
                    ),
                    title=(
                        "Multiple subdomains detected"
                    ),
                    description=(
                        "The hostname contains several "
                        "subdomain levels."
                    ),
                    category="URL",
                    severity="low",
                    source="Heuristic",
                    observed_value=(
                        subdomain_count
                    ),
                )
            )

        # ---------------------------------------------
        # Domain age unavailable
        # ---------------------------------------------

        domain_age = self._first_value(
            features,
            [
                "h_domain_age_days",
                "domain_age_days",
            ],
        )

        domain_age_available = (
            self._first_value(
                features,
                [
                    "h_domain_age_available",
                    "domain_age_available",
                    "h_rdap_available",
                    "rdap_available",
                ],
            )
        )

        if (
            self._is_missing(
                domain_age
            )
            or domain_age_available
            in (0, False)
        ):

            indicators.append(
                EvidenceIndicator(
                    code=(
                        "domain_registration_unavailable"
                    ),
                    title=(
                        "Domain registration "
                        "information unavailable"
                    ),
                    description=(
                        "The system could not obtain "
                        "usable domain-registration "
                        "age information during "
                        "analysis."
                    ),
                    category="Domain",
                    severity="info",
                    source="Heuristic",
                    observed_value=None,
                )
            )

        # ---------------------------------------------
        # Young domain
        # ---------------------------------------------

        if (
            domain_age is not None
            and self._is_numeric(
                domain_age
            )
            and float(
                domain_age
            ) >= 0
            and float(
                domain_age
            ) < 90
        ):

            indicators.append(
                EvidenceIndicator(
                    code="young_domain",
                    title=(
                        "Recently registered domain "
                        "observed"
                    ),
                    description=(
                        "Available registration data "
                        "indicates that the domain is "
                        "relatively young."
                    ),
                    category="Domain",
                    severity="medium",
                    source="Heuristic",
                    observed_value=(
                        domain_age
                    ),
                )
            )

        # ---------------------------------------------
        # TLS unavailable / failure
        # ---------------------------------------------

        tls_available = (
            self._first_value(
                features,
                [
                    "h_tls_available",
                    "tls_available",
                    "h_ssl_available",
                    "ssl_available",
                ],
            )
        )

        if tls_available in (
            0,
            False,
        ):

            indicators.append(
                EvidenceIndicator(
                    code="tls_unavailable",
                    title=(
                        "TLS information unavailable"
                    ),
                    description=(
                        "The system could not obtain "
                        "usable TLS certificate "
                        "information for the analysed "
                        "website."
                    ),
                    category="TLS",
                    severity="medium",
                    source="Heuristic",
                    observed_value=False,
                )
            )

        # ---------------------------------------------
        # External form action
        # ---------------------------------------------

        if self._any_positive(
            features,
            [
                "h_external_form_action",
                "external_form_action",
                "h_off_domain_form_action",
                "off_domain_form_action",
                "h_external_form_count",
                "external_form_count",
            ],
        ):

            indicators.append(
                EvidenceIndicator(
                    code=(
                        "external_form_action"
                    ),
                    title=(
                        "External form action detected"
                    ),
                    description=(
                        "At least one observed form "
                        "appears to submit information "
                        "to a different domain."
                    ),
                    category="Forms",
                    severity="high",
                    source="Heuristic",
                    observed_value=True,
                )
            )

        # ---------------------------------------------
        # Password field
        # ---------------------------------------------

        if self._any_positive(
            features,
            [
                "h_password_field",
                "password_field",
                "h_password_input_count",
                "password_input_count",
            ],
        ):

            indicators.append(
                EvidenceIndicator(
                    code="password_field",
                    title=(
                        "Password input field detected"
                    ),
                    description=(
                        "The analysed webpage contains "
                        "a field intended to receive "
                        "password information."
                    ),
                    category="Forms",
                    severity="info",
                    source="Heuristic",
                    observed_value=True,
                )
            )

        # ---------------------------------------------
        # Payment field
        # ---------------------------------------------

        if self._any_positive(
            features,
            [
                "h_payment_field",
                "payment_field",
                "h_credit_card_field",
                "credit_card_field",
                "h_payment_input_count",
                "payment_input_count",
            ],
        ):

            indicators.append(
                EvidenceIndicator(
                    code="payment_field",
                    title=(
                        "Payment-related input "
                        "detected"
                    ),
                    description=(
                        "Payment-related webpage "
                        "elements were observed during "
                        "static analysis."
                    ),
                    category="Forms",
                    severity="info",
                    source="Heuristic",
                    observed_value=True,
                )
            )

        # ---------------------------------------------
        # High external-link ratio
        # ---------------------------------------------

        external_ratio = (
            self._first_numeric(
                features,
                [
                    "h_external_link_ratio",
                    "external_link_ratio",
                ],
            )
        )

        if (
            external_ratio is not None
            and external_ratio >= 0.70
        ):

            indicators.append(
                EvidenceIndicator(
                    code=(
                        "high_external_link_ratio"
                    ),
                    title=(
                        "High proportion of external "
                        "links observed"
                    ),
                    description=(
                        "A substantial proportion of "
                        "the analysed page links point "
                        "outside the website's own "
                        "domain."
                    ),
                    category="Page Structure",
                    severity="low",
                    source="Heuristic",
                    observed_value=(
                        external_ratio
                    ),
                )
            )

        return indicators

    # -------------------------------------------------
    # Behavioural evidence
    # -------------------------------------------------

    def _behavioural_indicators(
        self,
        features: dict,
    ) -> list[EvidenceIndicator]:

        indicators = []

        # ---------------------------------------------
        # Cross-domain redirects
        # ---------------------------------------------

        redirects = self._first_numeric(
            features,
            [
                "b_cross_domain_redirect_count",
                "cross_domain_redirect_count",
                "b_external_redirect_count",
                "external_redirect_count",
            ],
        )

        if (
            redirects is not None
            and redirects >= 2
        ):

            indicators.append(
                EvidenceIndicator(
                    code=(
                        "multiple_cross_domain_redirects"
                    ),
                    title=(
                        "Multiple cross-domain "
                        "redirects observed"
                    ),
                    description=(
                        "The controlled browser "
                        "observed navigation across "
                        "multiple external domains."
                    ),
                    category="Navigation",
                    severity="high",
                    source="Behavioural",
                    observed_value=redirects,
                )
            )

        elif (
            redirects is not None
            and redirects == 1
        ):

            indicators.append(
                EvidenceIndicator(
                    code=(
                        "cross_domain_redirect"
                    ),
                    title=(
                        "Cross-domain redirect "
                        "observed"
                    ),
                    description=(
                        "The browser was redirected "
                        "from the analysed site to a "
                        "different domain."
                    ),
                    category="Navigation",
                    severity="medium",
                    source="Behavioural",
                    observed_value=redirects,
                )
            )

        # ---------------------------------------------
        # Automatic navigation
        # ---------------------------------------------

        auto_navigation = (
            self._first_numeric(
                features,
                [
                    "b_automatic_navigation_count",
                    "automatic_navigation_count",
                    "b_auto_navigation_count",
                    "auto_navigation_count",
                ],
            )
        )

        if (
            auto_navigation is not None
            and auto_navigation > 0
        ):

            indicators.append(
                EvidenceIndicator(
                    code=(
                        "automatic_navigation"
                    ),
                    title=(
                        "Automatic navigation "
                        "activity observed"
                    ),
                    description=(
                        "The page initiated navigation "
                        "without an explicit user "
                        "navigation action during the "
                        "controlled observation period."
                    ),
                    category="Navigation",
                    severity="medium",
                    source="Behavioural",
                    observed_value=(
                        auto_navigation
                    ),
                )
            )

        # ---------------------------------------------
        # Popups
        # ---------------------------------------------

        popup_count = (
            self._first_numeric(
                features,
                [
                    "b_popup_count",
                    "popup_count",
                    "b_new_page_count",
                    "new_page_count",
                ],
            )
        )

        if (
            popup_count is not None
            and popup_count > 0
        ):

            indicators.append(
                EvidenceIndicator(
                    code="popup_activity",
                    title=(
                        "JavaScript popup activity "
                        "observed"
                    ),
                    description=(
                        "One or more popup or new-page "
                        "events were observed during "
                        "controlled browser execution."
                    ),
                    category="Browser Behaviour",
                    severity="medium",
                    source="Behavioural",
                    observed_value=popup_count,
                )
            )

        # ---------------------------------------------
        # JavaScript dialogs
        # ---------------------------------------------

        dialog_count = (
            self._first_numeric(
                features,
                [
                    "b_dialog_count",
                    "dialog_count",
                    "b_js_dialog_count",
                    "js_dialog_count",
                ],
            )
        )

        if (
            dialog_count is not None
            and dialog_count > 0
        ):

            indicators.append(
                EvidenceIndicator(
                    code="javascript_dialog",
                    title=(
                        "JavaScript dialog activity "
                        "observed"
                    ),
                    description=(
                        "The webpage attempted to open "
                        "one or more JavaScript dialog "
                        "messages during controlled "
                        "execution."
                    ),
                    category="Browser Behaviour",
                    severity="medium",
                    source="Behavioural",
                    observed_value=dialog_count,
                )
            )

        # ---------------------------------------------
        # Download attempts
        # ---------------------------------------------

        downloads = (
            self._first_numeric(
                features,
                [
                    "b_download_attempt_count",
                    "download_attempt_count",
                    "b_download_count",
                    "download_count",
                ],
            )
        )

        if (
            downloads is not None
            and downloads > 0
        ):

            indicators.append(
                EvidenceIndicator(
                    code="download_attempt",
                    title=(
                        "Automatic download activity "
                        "observed"
                    ),
                    description=(
                        "The controlled browser "
                        "observed a download attempt. "
                        "The scanner's collection "
                        "environment should intercept "
                        "such downloads."
                    ),
                    category="Browser Behaviour",
                    severity="high",
                    source="Behavioural",
                    observed_value=downloads,
                )
            )

        # ---------------------------------------------
        # Dynamic form destination changes
        # ---------------------------------------------

        form_changes = (
            self._first_numeric(
                features,
                [
                    "b_form_action_change_count",
                    "form_action_change_count",
                    "b_dynamic_form_action_count",
                    "dynamic_form_action_count",
                ],
            )
        )

        if (
            form_changes is not None
            and form_changes > 0
        ):

            indicators.append(
                EvidenceIndicator(
                    code=(
                        "form_action_changed"
                    ),
                    title=(
                        "Form destination changed "
                        "during execution"
                    ),
                    description=(
                        "The destination associated "
                        "with a webpage form changed "
                        "during controlled browser "
                        "analysis."
                    ),
                    category="Forms",
                    severity="high",
                    source="Behavioural",
                    observed_value=form_changes,
                )
            )

        # ---------------------------------------------
        # DOM changes
        # ---------------------------------------------

        dom_changes = (
            self._first_numeric(
                features,
                [
                    "b_dom_change_count",
                    "dom_change_count",
                    "b_dom_mutation_count",
                    "dom_mutation_count",
                ],
            )
        )

        if (
            dom_changes is not None
            and dom_changes > 0
        ):

            indicators.append(
                EvidenceIndicator(
                    code="dom_changes",
                    title=(
                        "Dynamic page changes "
                        "observed"
                    ),
                    description=(
                        "The webpage modified its "
                        "document structure during the "
                        "controlled observation period."
                    ),
                    category="Page Behaviour",
                    severity="info",
                    source="Behavioural",
                    observed_value=dom_changes,
                )
            )

        return indicators

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    @staticmethod
    def _first_value(
        features: dict,
        names: list[str],
    ):

        for name in names:

            if name in features:
                return features[name]

        return None

    def _first_numeric(
        self,
        features: dict,
        names: list[str],
    ) -> float | None:

        value = self._first_value(
            features,
            names,
        )

        if not self._is_numeric(
            value
        ):
            return None

        return float(value)

    @staticmethod
    def _is_numeric(
        value,
    ) -> bool:

        if isinstance(
            value,
            bool,
        ):
            return False

        try:
            float(value)
            return True

        except (
            TypeError,
            ValueError,
        ):
            return False

    @staticmethod
    def _is_missing(
        value,
    ) -> bool:

        if value is None:
            return True

        if isinstance(
            value,
            str,
        ):

            return (
                value.strip().lower()
                in {
                    "",
                    "none",
                    "null",
                    "nan",
                    "unknown",
                    "unavailable",
                }
            )

        return False

    def _any_positive(
        self,
        features: dict,
        names: list[str],
    ) -> bool:

        for name in names:

            if name not in features:
                continue

            value = features[name]

            if isinstance(
                value,
                bool,
            ):

                if value:
                    return True

                continue

            if self._is_numeric(
                value
            ):

                if float(value) > 0:
                    return True

        return False

    @staticmethod
    def _remove_duplicates(
        indicators: list[
            EvidenceIndicator
        ],
    ) -> list[
        EvidenceIndicator
    ]:

        seen = set()

        unique = []

        for indicator in indicators:

            if indicator.code in seen:
                continue

            seen.add(
                indicator.code
            )

            unique.append(
                indicator
            )

        return unique

    @staticmethod
    def _severity_order(
        indicator:
            EvidenceIndicator,
    ):

        order = {
            "high": 0,
            "medium": 1,
            "low": 2,
            "info": 3,
        }

        return order.get(
            indicator.severity,
            4,
        )
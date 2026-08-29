import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from app.core.url_security import (
    get_registrable_domain,
)


LOGIN_TERMS = {
    "login",
    "log in",
    "sign in",
    "signin",
    "username",
    "password",
    "verify account",
    "verification",
    "authenticate",
    "authentication",
}


PAYMENT_TERMS = {
    "payment",
    "pay now",
    "credit card",
    "debit card",
    "card number",
    "cvv",
    "cvc",
    "billing",
    "bank account",
    "account number",
    "checkout",
    "make payment",
}


CRYPTO_TERMS = {
    "bitcoin",
    "btc",
    "ethereum",
    "eth",
    "cryptocurrency",
    "crypto wallet",
    "wallet address",
    "usdt",
    "tether",
    "blockchain",
}


URGENCY_TERMS = {
    "urgent",
    "immediately",
    "act now",
    "limited time",
    "expires today",
    "account suspended",
    "account locked",
    "verify now",
    "confirm now",
    "final warning",
}


SUSPICIOUS_TERMS = {
    "claim prize",
    "you have won",
    "guaranteed profit",
    "guaranteed return",
    "double your money",
    "risk free",
    "risk-free",
    "free gift",
    "security alert",
    "unusual activity",
    "verify your identity",
}


PAYMENT_FIELD_TOKENS = {
    "card",
    "cardnumber",
    "card_number",
    "creditcard",
    "credit_card",
    "debitcard",
    "debit_card",
    "cvv",
    "cvc",
    "expiry",
    "expiration",
    "billing",
    "accountnumber",
    "account_number",
}


def _parse_html(
    html: str
) -> BeautifulSoup:
    """
    Parse HTML using BeautifulSoup with the lxml parser.
    """

    return BeautifulSoup(
        html or "",
        "lxml",
    )


def _visible_page_text(
    soup: BeautifulSoup
) -> str:
    """
    Extract textual page content while excluding script/style code.
    """

    for element in soup(
        [
            "script",
            "style",
            "noscript",
            "template",
        ]
    ):
        element.decompose()

    text = soup.get_text(
        " ",
        strip=True,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.lower()


def _count_terms(
    text: str,
    terms: set[str],
) -> int:
    """
    Count occurrences of phrase/token indicators.

    This is evidence extraction only.
    """

    total = 0

    for term in terms:
        pattern = (
            r"(?<!\w)"
            + re.escape(term)
            + r"(?!\w)"
        )

        total += len(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
        )

    return total


def _is_hidden_element(
    element
) -> bool:
    """
    Identify common static HTML hiding mechanisms.

    This does not detect CSS rules from external stylesheets.
    """

    if element.has_attr(
        "hidden"
    ):
        return True

    aria_hidden = (
        element.get(
            "aria-hidden",
            ""
        )
        .strip()
        .lower()
    )

    if aria_hidden == "true":
        return True

    style = (
        element.get(
            "style",
            ""
        )
        .replace(" ", "")
        .lower()
    )

    hidden_styles = (
        "display:none",
        "visibility:hidden",
        "opacity:0",
    )

    return any(
        marker in style
        for marker in hidden_styles
    )


def _input_descriptor(
    element
) -> str:
    """
    Combine useful input attributes for lexical field inspection.
    """

    values = [
        element.get(
            "name",
            ""
        ),
        element.get(
            "id",
            ""
        ),
        element.get(
            "placeholder",
            ""
        ),
        element.get(
            "autocomplete",
            ""
        ),
        element.get(
            "aria-label",
            ""
        ),
    ]

    return " ".join(
        str(value).lower()
        for value in values
        if value
    )


def _is_payment_field(
    element
) -> bool:
    descriptor = (
        _input_descriptor(
            element
        )
    )

    compact = re.sub(
        r"[^a-z0-9_]+",
        "",
        descriptor,
    )

    for token in (
        PAYMENT_FIELD_TOKENS
    ):
        if (
            token in descriptor
            or token in compact
        ):
            return True

    return False


def _is_http_link(
    value: str
) -> bool:
    """
    Determine whether a resolved link is HTTP/HTTPS.
    """

    try:
        scheme = (
            urlsplit(
                value
            )
            .scheme
            .lower()
        )

        return scheme in {
            "http",
            "https",
        }

    except Exception:
        return False


def _classify_link(
    page_url: str,
    href: str,
) -> str:
    """
    Return:
        internal
        external
        ignored
    """

    href = (
        href
        or ""
    ).strip()

    if not href:
        return "ignored"

    lowered = (
        href.lower()
    )

    if (
        lowered.startswith("#")
        or lowered.startswith(
            "javascript:"
        )
        or lowered.startswith(
            "mailto:"
        )
        or lowered.startswith(
            "tel:"
        )
        or lowered.startswith(
            "data:"
        )
    ):
        return "ignored"

    resolved = urljoin(
        page_url,
        href,
    )

    if not _is_http_link(
        resolved
    ):
        return "ignored"

    page_domain = (
        get_registrable_domain(
            page_url
        )
    )

    target_domain = (
        get_registrable_domain(
            resolved
        )
    )

    if (
        page_domain
        and target_domain
        and page_domain
        == target_domain
    ):
        return "internal"

    return "external"


def _analyse_form_action(
    page_url: str,
    action: str,
) -> dict:
    """
    Analyse a form action without making any network request.
    """

    action = (
        action
        or ""
    ).strip()

    if not action:
        return {
            "empty": 1,
            "javascript": 0,
            "external": 0,
            "suspicious": 0,
        }

    lowered = (
        action.lower()
    )

    if lowered.startswith(
        "javascript:"
    ):
        return {
            "empty": 0,
            "javascript": 1,
            "external": 0,
            "suspicious": 1,
        }

    resolved = urljoin(
        page_url,
        action,
    )

    parsed = urlsplit(
        resolved
    )

    if parsed.scheme.lower() not in {
        "http",
        "https",
    }:
        return {
            "empty": 0,
            "javascript": 0,
            "external": 0,
            "suspicious": 1,
        }

    page_domain = (
        get_registrable_domain(
            page_url
        )
    )

    action_domain = (
        get_registrable_domain(
            resolved
        )
    )

    external = int(
        bool(
            page_domain
            and action_domain
            and page_domain
            != action_domain
        )
    )

    suspicious_tokens = {
        "verify",
        "password",
        "credential",
        "login",
        "account",
        "wallet",
        "payment",
    }

    action_text = (
        resolved.lower()
    )

    suspicious = int(
        external == 1
        or any(
            token in action_text
            for token in suspicious_tokens
        )
    )

    return {
        "empty": 0,
        "javascript": 0,
        "external": external,
        "suspicious": suspicious,
    }


def extract_html_features(
    page_url: str,
    html: str,
) -> dict:
    """
    Extract static HTML heuristic features.

    No network requests are performed here.
    """

    soup = _parse_html(
        html
    )

    # --------------------------
    # FORMS AND INPUTS
    # --------------------------

    forms = soup.find_all(
        "form"
    )

    inputs = soup.find_all(
        "input"
    )

    password_fields = [
        element
        for element in inputs
        if (
            element.get(
                "type",
                ""
            )
            .strip()
            .lower()
            == "password"
        )
    ]

    hidden_inputs = [
        element
        for element in inputs
        if (
            element.get(
                "type",
                ""
            )
            .strip()
            .lower()
            == "hidden"
        )
    ]

    payment_fields = [
        element
        for element in inputs
        if _is_payment_field(
            element
        )
    ]

    # --------------------------
    # IFRAMES / SCRIPTS
    # --------------------------

    iframes = soup.find_all(
        "iframe"
    )

    scripts = soup.find_all(
        "script"
    )

    # --------------------------
    # HIDDEN ELEMENTS
    # --------------------------

    hidden_elements = [
        element
        for element in soup.find_all(
            True
        )
        if (
            _is_hidden_element(
                element
            )
        )
    ]

    # --------------------------
    # LINKS
    # --------------------------

    links = soup.find_all(
        "a"
    )

    internal_link_count = 0
    external_link_count = 0

    for link in links:
        classification = (
            _classify_link(
                page_url,
                link.get(
                    "href",
                    ""
                ),
            )
        )

        if classification == (
            "internal"
        ):
            internal_link_count += 1

        elif classification == (
            "external"
        ):
            external_link_count += 1

    analysed_link_count = (
        internal_link_count
        + external_link_count
    )

    external_link_ratio = (
        external_link_count
        / analysed_link_count
        if analysed_link_count
        else 0.0
    )

    # --------------------------
    # FORM ACTIONS
    # --------------------------

    form_action_count = 0
    empty_form_action_count = 0
    javascript_form_action_count = 0
    external_form_action_count = 0
    suspicious_form_action_count = 0

    for form in forms:
        form_action_count += 1

        result = (
            _analyse_form_action(
                page_url,
                form.get(
                    "action",
                    ""
                ),
            )
        )

        empty_form_action_count += (
            result["empty"]
        )

        javascript_form_action_count += (
            result["javascript"]
        )

        external_form_action_count += (
            result["external"]
        )

        suspicious_form_action_count += (
            result["suspicious"]
        )

    # --------------------------
    # META REFRESH
    # --------------------------

    meta_refresh_count = 0

    for meta in soup.find_all(
        "meta"
    ):
        http_equiv = (
            meta.get(
                "http-equiv",
                ""
            )
            .strip()
            .lower()
        )

        if http_equiv == "refresh":
            meta_refresh_count += 1

    # --------------------------
    # PAGE TEXT
    # --------------------------

    page_text = (
        _visible_page_text(
            soup
        )
    )

    login_keyword_count = (
        _count_terms(
            page_text,
            LOGIN_TERMS,
        )
    )

    payment_keyword_count = (
        _count_terms(
            page_text,
            PAYMENT_TERMS,
        )
    )

    crypto_keyword_count = (
        _count_terms(
            page_text,
            CRYPTO_TERMS,
        )
    )

    urgency_keyword_count = (
        _count_terms(
            page_text,
            URGENCY_TERMS,
        )
    )

    suspicious_keyword_count = (
        _count_terms(
            page_text,
            SUSPICIOUS_TERMS,
        )
    )

    return {
        "form_count": len(
            forms
        ),

        "password_field_count": len(
            password_fields
        ),

        "payment_field_count": len(
            payment_fields
        ),

        "hidden_input_count": len(
            hidden_inputs
        ),

        "iframe_count": len(
            iframes
        ),

        "script_count": len(
            scripts
        ),

        "hidden_element_count": len(
            hidden_elements
        ),

        "link_count": len(
            links
        ),

        "internal_link_count": (
            internal_link_count
        ),

        "external_link_count": (
            external_link_count
        ),

        "external_link_ratio": round(
            external_link_ratio,
            6,
        ),

        "form_action_count": (
            form_action_count
        ),

        "empty_form_action_count": (
            empty_form_action_count
        ),

        "javascript_form_action_count": (
            javascript_form_action_count
        ),

        "external_form_action_count": (
            external_form_action_count
        ),

        "suspicious_form_action_count": (
            suspicious_form_action_count
        ),

        "meta_refresh_count": (
            meta_refresh_count
        ),

        "has_meta_refresh": int(
            meta_refresh_count > 0
        ),

        "suspicious_keyword_count": (
            suspicious_keyword_count
        ),

        "urgency_keyword_count": (
            urgency_keyword_count
        ),

        "crypto_keyword_count": (
            crypto_keyword_count
        ),

        "login_keyword_count": (
            login_keyword_count
        ),

        "payment_keyword_count": (
            payment_keyword_count
        ),

        "has_password_field": int(
            len(
                password_fields
            )
            > 0
        ),

        "has_payment_field": int(
            len(
                payment_fields
            )
            > 0
        ),

        "has_iframe": int(
            len(
                iframes
            )
            > 0
        ),

        "has_external_form_action": int(
            external_form_action_count
            > 0
        ),
    }
from app.collectors.browser_environment import (
    observe_synthetic_html,
)


HTML = """
<!doctype html>
<html>
    <body>
        <h1>
            Synthetic Download Test
        </h1>
    </body>
</html>
"""


JAVASCRIPT = """
() => {
    const link =
        document.createElement("a");

    link.href =
        "data:text/plain,"
        + encodeURIComponent(
            "Synthetic research test"
        );

    link.download =
        "synthetic-test.txt";

    document.body.appendChild(
        link
    );

    link.click();
}
"""


result = (
    observe_synthetic_html(
        HTML,
        javascript=JAVASCRIPT,
        observation_time_ms=1000,
    )
)


print(
    "\nDOWNLOAD INTERCEPTION TEST"
)

print(
    "=" * 60
)

print(
    f"success: "
    f"{result.success}"
)

print(
    f"download_count: "
    f"{result.download_count}"
)

print(
    f"error_type: "
    f"{result.error_type}"
)

print(
    f"error_message: "
    f"{result.error_message}"
)
from app.collectors.browser_environment import (
    observe_synthetic_html,
)


HTML = """
<!doctype html>
<html>
    <head>
        <title>
            Synthetic Behaviour Test
        </title>
    </head>

    <body>
        <h1>
            Safe synthetic test
        </h1>
    </body>
</html>
"""


JAVASCRIPT = """
() => {
    setTimeout(() => {
        alert("Synthetic dialog test");
    }, 50);

    setTimeout(() => {
        window.open(
            "about:blank",
            "_blank"
        );
    }, 100);
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
    "\nSYNTHETIC BROWSER TEST"
)

print(
    "=" * 60
)

print(
    f"success: "
    f"{result.success}"
)

print(
    f"dialog_count: "
    f"{result.dialog_count}"
)

print(
    f"popup_count: "
    f"{result.popup_count}"
)

print(
    f"download_count: "
    f"{result.download_count}"
)

print(
    f"page_error_count: "
    f"{result.page_error_count}"
)

print(
    f"error_type: "
    f"{result.error_type}"
)

print(
    f"error_message: "
    f"{result.error_message}"
)
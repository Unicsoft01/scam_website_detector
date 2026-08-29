from app.collectors.browser_environment import (
    observe_synthetic_html,
)


HTML = """
<!doctype html>

<html>
    <body>
        <div id="timer">
            30
        </div>

        <script>
            let remaining = 30;

            setInterval(
                () => {
                    remaining--;

                    document
                        .getElementById(
                            "timer"
                        )
                        .textContent =
                            remaining;
                },
                400
            );
        </script>
    </body>
</html>
"""


result = (
    observe_synthetic_html(
        HTML,
        observation_time_ms=500,
    )
)


print(
    "\nCOUNTDOWN TEST"
)

print(
    "=" * 60
)

print(
    f"success: "
    f"{result.success}"
)

print(
    f"countdown_detected: "
    f"{result.countdown_detected}"
)
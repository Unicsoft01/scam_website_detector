from app.collectors.browser_environment import (
    observe_synthetic_html,
)

from app.features.behavioural_features import (
    extract_behavioural_features,
)


HTML = """
<!doctype html>

<html>
    <head>
        <title>
            Original Title
        </title>
    </head>

    <body>
        <h1>
            Synthetic behavioural test
        </h1>

        <form
            id="test-form"
            action="/original"
        >
            <input
                name="username"
            >
        </form>

        <div id="container">
        </div>
    </body>
</html>
"""


JAVASCRIPT = """
() => {

    setTimeout(() => {

        document.title =
            "Changed Title";

        const form =
            document.getElementById(
                "test-form"
            );

        form.setAttribute(
            "action",
            "/changed"
        );

        const newForm =
            document.createElement(
                "form"
            );

        newForm.action =
            "/dynamic-submit";

        document
            .getElementById(
                "container"
            )
            .appendChild(
                newForm
            );

        const newElement =
            document.createElement(
                "div"
            );

        newElement.textContent =
            "Dynamic content";

        document.body.appendChild(
            newElement
        );

    }, 100);
}
"""


observation = (
    observe_synthetic_html(
        HTML,
        javascript=JAVASCRIPT,
        observation_time_ms=1000,
    )
)


features = (
    extract_behavioural_features(
        observation
    )
)


print(
    "\nDYNAMIC BEHAVIOUR TEST"
)

print(
    "=" * 70
)


for name, value in (
    features.items()
):
    print(
        f"{name}: {value}"
    )
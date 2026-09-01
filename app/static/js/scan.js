document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "scanForm"
            );

        if (!form) {
            return;
        }

        const urlInput =
            document.getElementById(
                "urlInput"
            );

        const button =
            document.getElementById(
                "analyseButton"
            );

        const loadingPanel =
            document.getElementById(
                "loadingPanel"
            );

        const errorPanel =
            document.getElementById(
                "errorPanel"
            );

        const errorMessage =
            document.getElementById(
                "errorMessage"
            );


        function setLoading(
            isLoading
        ) {

            button.disabled =
                isLoading;

            urlInput.disabled =
                isLoading;

            if (isLoading) {

                loadingPanel
                    .classList
                    .remove("d-none");

            } else {

                loadingPanel
                    .classList
                    .add("d-none");
            }
        }


        function showError(
            message
        ) {

            errorMessage.textContent =
                message;

            errorPanel
                .classList
                .remove("d-none");
        }


        function clearError() {

            errorMessage.textContent =
                "";

            errorPanel
                .classList
                .add("d-none");
        }


        form.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();

                clearError();

                const url =
                    urlInput
                        .value
                        .trim();

                if (!url) {

                    showError(
                        "Please enter a website URL."
                    );

                    return;
                }

                setLoading(true);

                try {

                    const response =
                        await fetch(
                            "/api/scans",
                            {
                                method:
                                    "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify(
                                        {
                                            url: url
                                        }
                                    )
                            }
                        );


                    let data = null;

                    try {

                        data =
                            await response.json();

                    } catch (error) {

                        data = null;
                    }


                    if (!response.ok) {

                        let message =
                            "The website could not be analysed.";

                        if (data) {

                            if (
                                typeof data.message
                                === "string"
                            ) {

                                message =
                                    data.message;

                            } else if (
                                typeof data.detail
                                === "string"
                            ) {

                                message =
                                    data.detail;
                            }
                        }

                        throw new Error(
                            message
                        );
                    }


                    if (!data.scan_id) {

                        throw new Error(
                            "The server did not return a scan identifier."
                        );
                    }


                    window.location.href =
                        `/results/${data.scan_id}`;

                } catch (error) {

                    showError(
                        error.message
                        ||
                        "An unexpected error occurred."
                    );

                } finally {

                    setLoading(false);
                }
            }
        );
    }
);
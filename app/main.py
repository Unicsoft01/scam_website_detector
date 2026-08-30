from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)

from fastapi.exceptions import (
    RequestValidationError,
)

from fastapi.responses import (
    JSONResponse,
)

from app.api.routes import (
    router,
)


app = FastAPI(
    title=(
        "Real-Time Scam Website "
        "Detection System"
    ),

    description=(
        "A web-based scam website "
        "detection system using "
        "heuristic and behavioural "
        "analysis."
    ),

    version="1.0.0",

    docs_url="/docs",

    redoc_url="/redoc",

    openapi_url=(
        "/openapi.json"
    ),
)


app.include_router(
    router
)


@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):

    return JSONResponse(
        status_code=422,

        content={
            "error": (
                "request_validation_error"
            ),

            "message": (
                "The submitted request "
                "could not be validated."
            ),

            "details": exc.errors(),
        },
    )


@app.exception_handler(
    HTTPException
)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):

    return JSONResponse(
        status_code=(
            exc.status_code
        ),

        content={
            "error": (
                "http_error"
            ),

            "message": exc.detail,
        },
    )


@app.exception_handler(
    Exception
)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):

    # Do not return internal traceback
    # details to the client.

    return JSONResponse(
        status_code=500,

        content={
            "error": (
                "internal_server_error"
            ),

            "message": (
                "An unexpected internal "
                "error occurred."
            ),
        },
    )
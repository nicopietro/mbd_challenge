from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from py_challenge_data_service import __version__
from py_challenge_data_service.routes import animals

app = FastAPI(
    title="py_challenge Data Service",
    description="A REST API application to obtain the data required to complete the py_challenge proposed at [https://github.com/jfaldanam/py_challenge](https://github.com/jfaldanam/py_challenge)",
    version=__version__,
)


@app.get(
    "/",
    response_class=HTMLResponse,
    summary="Beautiful front page for the data service",
    description="This is the front page of the data service. It provides a welcome message and a link to the API documentation.",
    tags=["front-page"],
)
async def root_page():
    return """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>py_challenge Data Service</title>
    </head>
    <body>
        <h1>Welcome to py_challenge Data Service</h1>
        <p>This service provides data for solving the python challenge presented at the github repository <a href="https://github.com/jfaldanam/py_challenge">https://github.com/jfaldanam/py_challenge</a>.</p>
        <p>For more information, check the API documentation <a href="/docs">/docs</a></p>
    </body>
</html>"""


app.include_router(
    animals.router,
    prefix="/api/v1/animals",
)

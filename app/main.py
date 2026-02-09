from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.web.pages import router as page_router

app = FastAPI(
    title="Computing Place",
    description="Environmental and Cultural Dimensions of Place",
    version="0.1"
)

app.include_router(api_router)
app.include_router(page_router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)
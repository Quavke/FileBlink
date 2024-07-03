from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from starlette.responses import RedirectResponse

from src.user_files.router import router as router_files
# from src.config import REDIS_HOST, REDIS_PORT
from src.pages.router import router as router_pages
app = FastAPI(
    title="FileBlink",
)


app.mount("/src/static/", StaticFiles(directory="src/static"), name="static")


app.include_router(router_files, tags=['Files'])
app.include_router(router_pages, tags=["Pages"])


@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/upload_file")

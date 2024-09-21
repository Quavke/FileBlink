from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from starlette.responses import RedirectResponse

from src.user_files.router import router as router_files
from fastapi.middleware.cors import CORSMiddleware
from src.pages.router import router as router_pages
app = FastAPI(
    title="FileBlink",
    docs_url=None,
    redoc_url=None
)

origins = [
    "http://localhost:9999",
    "http://127.0.0.1:9999",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

#app.mount("/src/static/", StaticFiles(directory="src/static"), name="static")


app.include_router(router_files, tags=['Files'])
app.include_router(router_pages, tags=["Pages"])


@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/upload_file/")

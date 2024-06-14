from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from starlette.responses import RedirectResponse

from src.database import get_async_session
from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserCreate, UserRead
from src.user_files.router import router as router_files
# from src.config import REDIS_HOST, REDIS_PORT
from src.tasks.tasks import delete_expired_files
from src.pages.router import router as router_pages
app = FastAPI(
    title="FileBlink",
)


app.mount("/src/static/", StaticFiles(directory="src/static"), name="static")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"]
)


app.include_router(router_files, tags=['Files'])
app.include_router(router_pages, tags=["Pages"])


@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")


# @app.on_event("startup")
# async def startup_event():
#     delete_expired_files.apply_async()

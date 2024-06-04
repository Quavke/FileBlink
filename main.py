from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserCreate, UserRead
from src.user_files.router import router as router_files
from src.config import REDIS_HOST, REDIS_PORT
from src.pages.router import router as router_pages
app = FastAPI(title="PaperDrop")


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

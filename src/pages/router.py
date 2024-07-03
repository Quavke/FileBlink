from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from src.database import get_async_session
from src.user_files.router import get_password
from sqlalchemy.ext.asyncio import AsyncSession
router = APIRouter(
)

templates = Jinja2Templates(directory="src/templates/")


@router.get("/get_file/{uuid_}")
async def get_file_page(request: Request, uuid_: str, session: AsyncSession = Depends(get_async_session)):
    file_url = f"http://127.0.0.1:8000/files/get_file_download_link/{uuid_}"
    password_check = await get_password(uuid_, session)
    password_check_url = f"http://127.0.0.1:8000/files/password_check/?uuid_={uuid_}&password="
    if not password_check:
        return templates.TemplateResponse("getfile_not_pass.html", {"request": request, "get_file_url": file_url})
    else:
        return templates.TemplateResponse("getfile_pass.html", {"request": request, "api_url": password_check_url})


@router.get("/upload_file/")
async def create_file_page(request: Request):
    return templates.TemplateResponse("upload_file.html", {"request": request})

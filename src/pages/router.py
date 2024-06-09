from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session

router = APIRouter(
)

templates = Jinja2Templates(directory="src/templates/")


@router.get("/getfile/{uuid_}")
async def get_file_page(request: Request, uuid_: str, session: AsyncSession = Depends(get_async_session)):
    file_url = f"http://127.0.0.1:8000/files/get_file_download_link/{uuid_}"
    return templates.TemplateResponse("getfile.html", {"request": request, "get_file_url": file_url})

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from src.user_files.router import get_file_download_link

router = APIRouter(
)

templates = Jinja2Templates(directory="src/templates/")


@router.get("/jopa")
def get_page(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@router.get("/getfile/{uuid_}")
def get_file_page(request: Request, getfile=Depends(get_file_download_link)):
    return templates.TemplateResponse("getfile.html", {"request": request, "get_file_url": getfile["request"]})

from datetime import datetime, timedelta, timezone
from tempfile import NamedTemporaryFile
from typing import Optional
from pydantic import BaseModel
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File


class MyFileBase(BaseModel):
    id: int
    file: UploadFile


class Will_del(BaseModel):
    day_week: bool
    day_14: bool
    day_free: timedelta


def get_file_name(file: UploadFile) -> Optional[str]:
    return file.filename


class MyFileUpload(MyFileBase):
    name: Optional[str] = None
    will_del: Will_del = Will_del(
        day_week=True, day_14=False, day_free=timedelta(days=0))
    create_at: datetime = datetime.now(timezone.utc)

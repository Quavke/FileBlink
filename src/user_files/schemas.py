from pydantic import BaseModel


class BaseUpload(BaseModel):
    ...


class UploadParams(BaseUpload):
    day_week: bool = True,
    day_14: bool = False,
    day_free: int = 0,
    download_count_del: int = 0,
    password_bool: bool = False,

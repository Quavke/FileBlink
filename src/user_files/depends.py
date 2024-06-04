from fastapi import File, Query
from fastapi.datastructures import UploadFile


def get_upload_file_dependencies(
    file: UploadFile = File(...),
    name: str = "N/A",
    day_week: bool = Query(True),
    day_14: bool = Query(False),
    day_free: bool = Query(False),
):
    name_1 = file.filename
    return {"file": file, "name": name_1, "day_week": day_week, "day_14": day_14, "day_free": day_free}


import datetime
import os
import re
import uuid

import logging
from fastapi.responses import FileResponse
from sqlalchemy import select, update
from fastapi import Depends, APIRouter, File, UploadFile

from starlette.background import BackgroundTask

from src.auth.base_config import current_user
from src.auth.models import User
from src.database import get_async_session

from src.user_files.crypt import encrypt_file, decrypt_file
from src.config import VT_API
from sqlalchemy.ext.asyncio import AsyncSession


from src.user_files.utils import get_delta, name_checker, get_by_value_from_db_scalar
from src.user_files.models import File as File_U
from src.user_files.models import UserFiles as User_Files
from src.user_files.vt_check import vt_check_func
router = APIRouter(prefix="/files", tags=['Files'])

params = {"apikey": VT_API}


# score = 0
# Эндпоинт для загрузки файлов


@router.post("/uploadfile/")
async def create_upload_file(u_file: UploadFile = File(...),
                             name: str = "N/A",
                             day_week: bool = True,
                             day_14: bool = False,
                             day_free: int = 0,
                             session: AsyncSession = Depends(get_async_session), user: User = Depends(current_user)):

    file_size = len(await u_file.read())
    await u_file.seek(0)
    if file_size >= 32 * 1024 * 1024:
        return {"error": "File too large", "status": "error", "message": "File larger than 32 MB"}
    # Отправляем файл на сканирование в VirusTotal
    m_count = await vt_check_func(u_file)
    await u_file.seek(0)
    # return  {"data": m_count}
    # Считаем предупреждения
    # m_count = 1
    print(m_count)
    if m_count > 5:
        return {
            "error": "the file is too suspicious",
            "status": "error",
            'message': 'the file is too suspicious. Try another file'}
    else:
        # сделаем вид что это отправка не в БД, а в s3 хранилище
        # Шифрование файла
        try:
            delta = get_delta(day_week, day_14, day_free)
            id = uuid.uuid1()
            uuid_ = id.hex

            en_file = encrypt_file(u_file)

            base_name, extension = await name_checker(session, name, u_file.filename)
            new_file = File_U(name=base_name, created_at=datetime.datetime.utcnow(),
                              will_del_at=datetime.datetime.utcnow() + datetime.timedelta(days=delta), file=en_file, uuid_=uuid_, file_extension=extension)

            session.add(new_file)
            query = select(File_U.id).where(File_U.name == new_file.name,
                                            File_U.created_at == new_file.created_at,
                                            File_U.will_del_at == new_file.will_del_at,
                                            File_U.file == new_file.file)
            new_relationship = User_Files(user_id=user.id, file_id=query)
            session.add(new_relationship)
            await session.commit()
            return {"error": None,
                    "status": "ok",
                    "message": "file was uploaded successfully",
                    "url": f"http://127.0.0.1:8000/getfile/{uuid_}"}
        except Exception as e:
            logging.error(str(e))
            return {"error": "Server error",
                    "status": "error",
                    'message': 'an error occurred on the server. Please wait or try another file'
                    }


def delete_file(file_path: str):
    os.remove(file_path)


@router.get("/get_file/{uuid_}")
def get_file_id(uuid_: str):
    return {"url": f"http://127.0.0.1:8000/files/get_file_download_link/{uuid_}"}


@router.get("/get_file_download_link/{uuid_}")
async def get_file_download_link(uuid_: str, session: AsyncSession = Depends(get_async_session)):
    # получение зашифрованного файла
    file_encrypted = await get_by_value_from_db_scalar(
        File_U.file, File_U.uuid_, uuid_, session)
    # query = select(File_U.file).where(File_U.uuid_ == uuid_)
    # result = await session.execute(query)
    # file_encrypted = result.scalar()
    # print(str(file_encrypted))

    # получение имени файла
    file_name = await get_by_value_from_db_scalar(File_U.name, File_U.uuid_, uuid_, session)
    # query = select(File_U.name).where(File_U.uuid_ == uuid_)
    # result = await session.execute(query)
    # file_name = result.scalar()
    pattern = r'\(\d+--\)$'
    file_name = re.sub(pattern, '', file_name)

    # получение расширения файла
    file_extension = await get_by_value_from_db_scalar(
        File_U.file_extension, File_U.uuid_, uuid_, session)
    # query = select(File_U.file_extension).where(File_U.uuid_ == uuid_)
    # result = await session.execute(query)
    # file_extension = result.scalar()
    if file_extension is None:
        file_extension = ''
    download_count = await get_by_value_from_db_scalar(
        File_U.download_count, File_U.uuid_, uuid_, session)
    # query = select(File_U.download_count).where(File_U.uuid_ == uuid_)
    # result = await session.execute(query)
    # download_count = result.scalar()
    print(download_count)
    download_count = download_count + 1
    query = update(File_U).where(
        File_U.uuid_ == uuid_).values(download_count=download_count)
    await session.execute(query)
    await session.commit()
    if file_encrypted:
        file_decrypted = decrypt_file(file_encrypted)

        with open(file_name, 'wb') as f:
            f.write(file_decrypted)

        file_path = os.path.abspath(file_name)
        # with open(file_path, 'rb') as f:
        #     file_data = f.read()

        # response = Response(content=file_data,
        #                     media_type='application/octet-stream')
        # response.headers['Content-Disposition'] = f'attachment; filename={file_name}{file_extension}'
        response = FileResponse(
            path=file_path, media_type='application/octet-stream', filename=f"{file_name}{file_extension}", background=BackgroundTask(delete_file, file_path))

        try:
            return response
        finally:
            # os.remove(file_path)
            pass

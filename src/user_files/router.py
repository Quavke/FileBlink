
import datetime
from base64 import b64encode, encode
from urllib.parse import quote

from sqlalchemy import update
import os

import re
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse

import uuid

from fastapi import Depends, APIRouter, File, Response, UploadFile
from src.database import get_async_session

from src.user_files.crypt import encrypt_file, decrypt_file
from src.config import VT_API
from sqlalchemy.ext.asyncio import AsyncSession
from src.user_files.models import File as File_U
from src.user_files.utils import get_delta, get_by_value_from_db_scalar, delete_expired_files, password_create, password_decrypt
from src.user_files.vt_check import vt_check_func
from icecream import ic

router = APIRouter(prefix="/files", tags=['Files'])

response_200 = Response.status_code = 200


def check_string(s):
    pattern = r'^[a-zA-Z0-9\s\!\@\#\$\%\^\&\*$$$$\_\+\-\=$$$$\{\}\|\;\'\:\,\.\/\<\>\/]+$'
    return bool(re.match(pattern, s))
# Эндпоинт для загрузки файлов


@router.post("/uploadfile/")
async def create_upload_file(u_file: UploadFile = File(...),
                             day_week: bool = True,
                             day_14: bool = False,
                             day_free: int = 0,
                             download_count_del: int = 0,
                             password_bool: bool = False,
                             session: AsyncSession = Depends(get_async_session), response: Response = response_200):
    await delete_expired_files(session)
    name_latin_check_file = check_string(u_file.filename)
    # if not name_latin_check_file:
    #     response.status_code = 400
    #     return {"error": "Not latin characters",
    #             "status": "error",
    #             "message": "The file name must be in English"}

    if download_count_del < 0:
        return {"error": "Number less than zero",
                "status": "error",
                "message": "The number of downloads cannot be less than zero"}

    # TODO раскомментировать проверку на вирусы
    file_size = len(await u_file.read())
    await u_file.seek(0)
    if file_size >= 32 * 1024 * 1024:
        return {"error": "File too large", "status": "error", "message": "File larger than 32 MB", "url": "file too large"}
    # Отправляем файл на сканирование в VirusTotal
    m_count = await vt_check_func(u_file)
    await u_file.seek(0)
    # Считаем предупреждения
    # m_count = 1
    # print(m_count)
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
            UUID_ = id.hex
            en_file = encrypt_file(u_file)
            password_en, password = password_create(password_bool)
            new_file = File_U(name=u_file.filename, created_at=datetime.datetime.utcnow(),
                              will_del_at=datetime.datetime.utcnow() + datetime.timedelta(days=delta),
                              file=en_file, uuid_=UUID_, mime_type=u_file.content_type,
                              download_count_del=download_count_del, password_bytea=password_en
                              )
            session.add(new_file)
            await session.commit()
            return {"error": None,
                    "status": "ok",
                    "message": "file was uploaded successfully",
                    "url": f"http://127.0.0.1:8000/get_file/{UUID_}",
                    "password": password}
        except Exception as e:
            ic(e)
            return {"error": "Server error",
                    "status": "error",
                    'message': 'an error occurred on the server. Please wait or try another file'
                    }


def delete_file(file_path: str):
    os.remove(file_path)


response_200 = Response.status_code = 200


async def get_password(uuid_: str, session):
    password = await get_by_value_from_db_scalar(File_U.password_bytea, File_U.uuid_, uuid_, session)
    print(str(password))
    if password is not None:
        return True
    else:
        return False


@router.get("/test/")
async def test(uuid_, session: AsyncSession = Depends(get_async_session)):
    password = await get_by_value_from_db_scalar(File_U.name, File_U.uuid_, uuid_, session)


@router.post("/password_check/")
async def password_check(uuid_: str, password, session: AsyncSession = Depends(get_async_session)):
    try:
        if password is not None:
            password_en = await get_by_value_from_db_scalar(File_U.password_bytea, File_U.uuid_, uuid_, session)
            password_de = password_decrypt(password_en)
            if password == password_de:
                return {"status": 2,
                        "download_url": f"http://127.0.0.1:8000/files/get_file_download_link/{uuid_}"}
            else:
                return {"status": 1}
        else:
            return {"status": 0}
    except Exception as e:
        ic(e)


@router.get("/get_file_download_link/{uuid_}")
async def get_file_download_link(uuid_: str, session: AsyncSession = Depends(get_async_session), response: Response = response_200, ):
    await delete_expired_files(session)

    try:
        file_encrypted = await get_by_value_from_db_scalar(
            File_U.file, File_U.uuid_, uuid_, session)

        # получение имени файла
        file_name = await get_by_value_from_db_scalar(File_U.name, File_U.uuid_, uuid_, session)
        pattern = r'\(\d+--\)$'
        file_name = re.sub(pattern, '', file_name)
        # получение расширения файла
        download_count = await get_by_value_from_db_scalar(
            File_U.download_count, File_U.uuid_, uuid_, session)
        # получение MIME type
        mime_type = await get_by_value_from_db_scalar(File_U.mime_type, File_U.uuid_, uuid_, session)
        # print("download count:", download_count, "| name:",
        #   file_name, "| ext:", file_extension)
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
            print(str(type(file_decrypted)))
            response = FileResponse(
                path=file_path, media_type='application/octet-stream', filename=file_name, background=BackgroundTask(delete_file, file_path), headers={
                    "Content-Disposition": f"attachment; filename={quote(file_name, safe='/', encoding='utf-8')}",
                    'X-Content-Type-Options': 'nosniff'
                })
            try:
                return response
            except Exception as e:
                ic(e)
                return {"error": "unknown",
                        "status": "error",
                        "message": "file doesn't exists"}
            # try:
            #     return StreamingResponse(
            #         iter([file_decrypted]),
            #         media_type=f"{mime_type}",
            #         headers={
            #             "Content-Disposition": f"attachment; filename={quote(file_name)}",
            #             'X-Content-Type-Options': 'nosniff'
            #         },
            #     )
            # except Exception as e:
            #     print(e)
            #     response.status_code = 404
            #     return {"error": "unknown",
            #             "status": "error",
            #             "message": "file-doesn't exists"}
    except Exception as e:
        print(e)
        response.status_code = 404
        return {"error": "unknown",
                "status": "error",
                "message": "file-doesn't exists"}

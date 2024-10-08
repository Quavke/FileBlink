
import datetime
from urllib.parse import quote

from sqlalchemy import update
import os

from sqlmodel import false
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse

import uuid
from typing import Optional
from fastapi import Depends, APIRouter, File, Request, Response, UploadFile
from src.database import get_async_session

from src.user_files.crypt import encrypt_file, decrypt_file
from sqlalchemy.ext.asyncio import AsyncSession
from src.user_files.models import File as File_U
from src.user_files.utils import get_delta, get_by_value_from_db_scalar, delete_expired_files, password_create, password_decrypt
from src.user_files.vt_check import vt_check_func
from icecream import ic

router = APIRouter(tags=['Files'])

response_200 = Response.status_code = 200


@router.post("/file_check/")
async def file_check(u_file: UploadFile = File(...), response: Response = response_200) -> dict:
    file_size = len(await u_file.read())
    await u_file.seek(0)
    if file_size >= 650 * 1024 * 1024:
        response.status_code = 404
        return {"error": "File too large", "status": "error", "message": "File larger than 32 MB", "url": "file too large"}
    # Отправляем файл на сканирование в VirusTotal
    m_count = await vt_check_func(u_file, file_size)
    print(m_count)
    await u_file.seek(0)
    # Считаем предупреждения
    # m_count = 1
    if m_count > 5:
        response.status_code = 404
        return {
            "error": "the file is too suspicious",
            "status": "error",
            'message': 'the file is too suspicious. Try another file'}
    else:
        return {
            "error": None,
            "status": "OK",
            'message': 'file check passed'}


@router.post("/uploadfile/")
async def create_upload_file(request: Request,
                             u_file: UploadFile = File(...),
                             day_week: bool = True,
                             day_14: bool = False,
                             day_free: int = 0,
                             download_count_del: int = 0,
                             password_bool: bool = False,
                             session: AsyncSession = Depends(get_async_session), response: Response = response_200):
    await delete_expired_files(session)
    if download_count_del < 0:
        response.status_code = 404
        return {"error": "Number less than zero",
                "status": "error",
                "message": "The number of downloads cannot be less than zero"}
        # сделаем вид что это отправка не в БД, а в s3 хранилище
        # Шифрование файла
    try:
        delta = get_delta(day_week,
                          day_14, day_free)
        id = uuid.uuid4()
        UUID = id.hex
        slice = round(len(UUID)/2)
        UUID = UUID[:slice]
        id_ = uuid.uuid4()
        SECRET_UUID = id_.hex
        print(1, str(type(u_file)))
        en_file = encrypt_file(u_file)
        print(2)
        password_en, password = password_create(password_bool)
        new_file = File_U(name=u_file.filename, created_at=datetime.datetime.utcnow(),
                          will_del_at=datetime.datetime.utcnow() + datetime.timedelta(days=delta),
                          file=en_file, uuid_=UUID, mime_type=u_file.content_type,
                          download_count_del=download_count_del, password_bytea=password_en, secret_uuid=SECRET_UUID, file_size=len(await u_file.read()))  # , file_size=len(await u_file.read()
        session.add(new_file)
        await session.commit()
        return {"error": None,
                "status": "ok",
                "message": "file was uploaded successfully",
                "url": f"{request.url.scheme}://{request.url.netloc}/get_file/{UUID}",
                "password": password}
    except Exception as e:
        ic(e)
        ic("/uploadfile/")
        response.status_code = 404
        return {"error": "Server error",
                "status": "error",
                'message': 'an error occurred on the server. Please wait or try another file'
                }


def delete_file(file_path: str):
    os.remove(file_path)


async def get_password(uuid_: str, session):
    password = await get_by_value_from_db_scalar(File_U.password_bytea, File_U.uuid_, uuid_, session)
    print(str(password))
    if password is not None:
        return True
    else:
        return False


@router.post("/password_check/")
async def password_check(uuid_: str, request: Request, password: Optional[str], session: AsyncSession = Depends(get_async_session)):
    try:
        base_url = f"{request.url.scheme}://{request.url.netloc}/"
        if password:
            password_en = await get_by_value_from_db_scalar(File_U.password_bytea, File_U.uuid_, uuid_, session)
            password_de = password_decrypt(password_en)
            if password == password_de:
                secret_uuid = await get_by_value_from_db_scalar(File_U.secret_uuid, File_U.uuid_, uuid_, session)
                # file_size = await get_by_value_from_db_scalar(File_U.file_size, File_U.uuid_, uuid_, session)
                # return {"status": 2,
                #         "download_url": f"http://127.0.0.1:8000/files/{secret_uuid}",
                #         "file_size": file_size}
                return {"status": 2,
                        "download_url": f"{base_url}{secret_uuid}"}
            else:
                return {"status": 1}
        else:
            password_exist_check = await get_by_value_from_db_scalar(File_U.password_bytea, File_U.uuid_, uuid_, session)
            if password_exist_check is not None:
                return {"status": 0}
            secret_uuid = await get_by_value_from_db_scalar(File_U.secret_uuid, File_U.uuid_, uuid_, session)
            return {"status": 2,
                    "download_url": f"{base_url}{secret_uuid}"}
    except Exception as e:
        ic(e)
        return {"status": 0}


@router.get("/{secret_uuid}")
async def get_file_download_link(secret_uuid: str, session: AsyncSession = Depends(get_async_session), response: Response = response_200, ):
    await delete_expired_files(session)

    try:
        file_encrypted = await get_by_value_from_db_scalar(
            File_U.file, File_U.secret_uuid, secret_uuid, session)

        # получение имени файла
        file_name = await get_by_value_from_db_scalar(File_U.name, File_U.secret_uuid, secret_uuid, session)
        # получение расширения файла
        download_count = await get_by_value_from_db_scalar(
            File_U.download_count, File_U.secret_uuid, secret_uuid, session)
        # получение MIME type
        mime_type = await get_by_value_from_db_scalar(File_U.mime_type, File_U.secret_uuid, secret_uuid, session)
        # обновление счетчика
        download_count = download_count + 1
        query = update(File_U).where(
            File_U.secret_uuid == secret_uuid).values(download_count=download_count)
        await session.execute(query)
        await session.commit()
        if file_encrypted:
            file_decrypted = decrypt_file(file_encrypted)
            with open(file_name, 'wb') as f:
                f.write(file_decrypted)
            file_path = os.path.abspath(file_name)
            print(str(type(file_decrypted)))
            response = FileResponse(
                path=file_path, media_type=mime_type, filename=file_name, background=BackgroundTask(delete_file, file_path), headers={
                    "Content-Disposition": f"attachment; filename={quote(file_name, safe='/', encoding='utf-8')}",
                    'X-Content-Type-Options': 'nosniff'
                })
            try:
                return response
            except Exception as e:
                ic(e)
                response.status_code = 404
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
                "message": "file doesn't exists"}

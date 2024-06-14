
import datetime
import os
import re
import uuid

import logging
from fastapi.responses import StreamingResponse
from sqlalchemy import or_, select, update
from fastapi import Depends, APIRouter, File, UploadFile

from src.tasks.tasks import delete_expired_files
from src.auth.base_config import current_user
from src.auth.models import User
from src.database import get_async_session

from src.user_files.crypt import encrypt_file, decrypt_file
from src.config import VT_API
from sqlalchemy.ext.asyncio import AsyncSession

from src.user_files.utils import get_delta, name_checker, get_by_value_from_db_scalar
from src.user_files.models import File as File_U, UserFiles
from src.user_files.models import UserFiles as User_Files
from src.user_files.vt_check import vt_check_func
from icecream import ic
from src.tasks.tasks import delete_expired_files
router = APIRouter(prefix="/files", tags=['Files'])

params = {"apikey": VT_API}


# Эндпоинт для загрузки файлов

@router.post("/uploadfile/")
async def create_upload_file(u_file: UploadFile = File(...),
                             name: str = "N/A",
                             day_week: bool = True,
                             day_14: bool = False,
                             day_free: int = 0,
                             download_count_del: int = 0,
                             session: AsyncSession = Depends(get_async_session), user: User = Depends(current_user)):
    delete_expired_files.delay()
    if download_count_del < 0:
        return {"error": "Number less than zero",
                "status": "error",
                "message": "The number of downloads cannot be less than zero"}

    # TODO раскомментировать проверку на вирусы
    file_size = len(await u_file.read())
    await u_file.seek(0)
    if file_size >= 32 * 1024 * 1024:
        return {"error": "File too large", "status": "error", "message": "File larger than 32 MB"}
    # Отправляем файл на сканирование в VirusTotal
    # m_count = await vt_check_func(u_file)
    await u_file.seek(0)
    # Считаем предупреждения
    m_count = 1
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
            UUID_ = id.hex

            en_file = encrypt_file(u_file)

            base_name, extension = await name_checker(session, name, u_file.filename)
            new_file = File_U(name=base_name, created_at=datetime.datetime.utcnow(),
                              will_del_at=datetime.datetime.utcnow() + datetime.timedelta(days=delta),
                              file=en_file, uuid_=UUID_, file_extension=extension, mime_type=u_file.content_type,
                              download_count_del=download_count_del
                              )

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
                    "url": f"http://127.0.0.1:8000/getfile/{UUID_}"}
        except Exception as e:
            logging.error(str(e))
            return {"error": "Server error",
                    "status": "error",
                    'message': 'an error occurred on the server. Please wait or try another file'
                    }


def delete_file(file_path: str):
    os.remove(file_path)


@router.get("/get_file_download_link/{uuid_}")
async def get_file_download_link(uuid_: str, session: AsyncSession = Depends(get_async_session)):
    # delete_expired_files.delay()
    result = delete_expired_files.delay()
    # ic(str(task))
    return {"task_id": str(result.result), "message": "Task to delete expired files has been triggered."}
    # получение зашифрованного файла
    try:
        file_encrypted = await get_by_value_from_db_scalar(
            File_U.file, File_U.uuid_, uuid_, session)

        # получение имени файла
        file_name = await get_by_value_from_db_scalar(File_U.name, File_U.uuid_, uuid_, session)
        pattern = r'\(\d+--\)$'
        file_name = re.sub(pattern, '', file_name)

        # получение расширения файла
        file_extension = await get_by_value_from_db_scalar(
            File_U.file_extension, File_U.uuid_, uuid_, session)

        if file_extension is None:
            file_extension = ''
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

            # with open(file_name, 'wb') as f:
            #     f.write(file_decrypted)

            # file_path = os.path.abspath(file_name)
            # print(str(type(file_decrypted)))
            # response = FileResponse(
            #     path=file_path, media_type='application/octet-stream', filename=f"{file_name}{file_extension}", background=BackgroundTask(delete_file, file_path))
            # try:
            #     return response
            # except Exception as e:
            #     return {"error": "unknown",
            #             "status": "error",
            #             "message": e}
            try:
                return StreamingResponse(
                    iter([file_decrypted]),
                    media_type=f"{mime_type}",
                    headers={
                        "Content-Disposition": f"attachment; filename={file_name}{file_extension}",
                        'X-Content-Type-Options': 'nosniff'
                    },
                )
            except Exception as e:
                return {"error": "unknown",
                        "status": "error",
                        "message": e}
    except Exception as e:
        return {"error": "unknown",
                "status": "error",
                "message": e}

# utc = timezone('UTC')


@ router.get("/test-celery")
async def test_celery(session: AsyncSession = Depends(get_async_session), user: User = Depends(current_user)):
    try:
        query = select(File_U.id).where(File_U.name == 'test')
        result = await session.execute(query)
        file_ids = result.scalars().all()

        for file_id in file_ids:
            # Find user files to delete
            query = select(UserFiles.id).where(UserFiles.file_id == file_id)
            result = await session.execute(query)
            user_file_ids = result.scalars().all()

            for user_file_id in user_file_ids:
                # Delete each UserFiles entry
                user_file = await session.get(UserFiles, user_file_id)
                if user_file:
                    await session.delete(user_file)

            # Delete the File_U entry
            file_entry = await session.get(File_U, file_id)
            if file_entry:
                await session.delete(file_entry)

        await session.commit()
    except Exception as e:
        print(e)

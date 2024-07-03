import base64
from datetime import datetime
import uuid
import pytz
from sqlalchemy import and_, or_, select
from src.user_files.models import File as File_U
from cryptography.fernet import Fernet


# def separate_file_name_and_extension(file_name):
#     extensions_list = []
#     base_name = file_name
#     s = file_name.split('.')
#     with open('file_extensions_complete.txt', 'r') as f:
#         extensions = [line.strip() for line in f.readlines()]
#         for i in s:
#             # print("s:", s, "\n")
#             i = "." + i
#             for k in extensions:
#                 if i.lower() == k:
#                     # print("i:", i, "\n", "k:", k)
#                     extensions_list.append(i)
#                     break
#     for value in extensions_list:
#         base_name = base_name.replace(value, "")
#     extensions_str = ''
#     for j in extensions_list:
#         extensions_str = extensions_str + j
#     if extensions_str == '':
#         extensions_str = None
#     return base_name, extensions_str


# async def name_checker(session, name, filename):
#     base_name, extension = separate_file_name_and_extension(filename)
#     base_name = base_name
#     if name != "N/A":
#         base_name = name

#     query = select(File_U.name).where(File_U.name == base_name)
#     result = await session.execute(query)
#     filename_db = result.scalar()  # Get the first element of the first row
#     # print(filename_db, type(filename_db))  # Should print a str

#     query = select(File_U.count).where(File_U.name == base_name)
#     result = await session.execute(query)
#     filecount_db = result.scalar()  # Get the first element of the first row
#     # print(filecount_db, type(filecount_db))  # Should print an int

#     if filename_db:
#         # print("Count:", filecount_db)
#         filecount_db_new = filecount_db + 1
#         filename_db = f"{filename_db}({filecount_db_new}--)"

#         query = update(File_U).where(
#             File_U.name == base_name).values(count=filecount_db_new)
#         await session.execute(query)
#         await session.commit()
#         u_name = filename_db
#     else:
#         u_name = base_name
#     return u_name, extension.lower()


def get_delta(day_week, day_14, day_free):
    if day_week:
        delta = 7
    if day_14:
        delta = 14
    if day_free != 0:
        delta = day_free
    return delta


async def get_by_value_from_db_scalar(field, where, value, session):
    query = select(field).where(where == value)
    result = await session.execute(query)
    result_scalar = result.scalar()
    return result_scalar


async def delete_expired_files(session):
    now = datetime.now(pytz.utc)
    naive_now = now.replace(tzinfo=None)
    query = select(File_U.id).where(
        or_(
            and_(File_U.download_count_del != 0,
                 File_U.download_count >= File_U.download_count_del),
            File_U.will_del_at <= naive_now
        )
    )
    try:
        result = await session.execute(query)
        file_ids = result.scalars().all()
        for file_id in file_ids:
            # Delete the File_U entry
            file_entry = await session.get(File_U, file_id)
            if file_entry:
                await session.delete(file_entry)

        await session.commit()
    except Exception as e:
        print(e)


def password_create(password_bool: bool):
    if password_bool:
        with open("key_pass.key", "rb") as key_file:
            key = key_file.read()
        cipher = Fernet(key)
        id = uuid.uuid1()
        password = id.bytes
        password_b64 = base64.b64encode(password)
        en_password = cipher.encrypt(password_b64)
        password_b64_decode = base64.b64encode(password).decode('utf-8')
        password_str = password_b64_decode.replace("+", "")
        password_str = password_str.replace("=", "")
        return en_password, password_str
    else:
        return None, None


def password_decrypt(en_password: str):
    with open("key_pass.key", "rb") as key_file:
        key = key_file.read()
    cipher = Fernet(key)
    cipher = Fernet(key)
    decrypt_pass = cipher.decrypt(en_password)
    de_pass = decrypt_pass.decode('utf-8')
    password_str = de_pass.replace("+", "")
    password_str = password_str.replace("=", "")
    return password_str

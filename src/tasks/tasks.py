# import datetime
# from celery import Celery
# from pytz import timezone
# from sqlalchemy import or_, select
# from src.user_files.models import File as File_U
# from src.user_files.models import UserFiles
# from icecream import ic
# from src.database import async_session_maker


# celery = Celery('tasks', broker='redis://localhost:6379')
# utc = timezone('UTC')


# async def delete_expired_files_async():
#     async def delete_value(id):
#     async with async_session_maker() as session:
#         now = datetime.datetime.now(utc)
#         # query = select(File_U.id).where(or_(File_U.download_count >=
#         #                                     File_U.download_count_del, File_U.will_del_at <= now))
#         try:
#             query = select(File_U.id).where(File_U.name == 'test')
#             result = await session.execute(query)
#             file_ids = result.scalars().all()
#             ic(file_ids)
#             for file_id in file_ids:
#                 # Find user files to delete
#                 query = select(UserFiles.id).where(
#                     UserFiles.file_id == file_id)
#                 result = await session.execute(query)
#                 user_file_ids = result.scalars().all()

#                 for user_file_id in user_file_ids:
#                     # Delete each UserFiles entry
#                     user_file = await session.get(UserFiles, user_file_id)
#                     if user_file:
#                         await session.delete(user_file)

#                 # Delete the File_U entry
#                 file_entry = await session.get(File_U, file_id)
#                 if file_entry:
#                     await session.delete(file_entry)
#             await asyncio.gather(*[delete_expired_files_async()])

#             await session.commit()
#         except Exception as e:
#             print(e)


# @celery.task()
# async def delete_expired_files():
#     ic("MESSAGE")
#     async with async_session_maker() as session:
#         now = datetime.datetime.now(utc)
#         # query = select(File_U.id).where(or_(File_U.download_count >=
#         #                                     File_U.download_count_del, File_U.will_del_at <= now))
#         try:
#             query = select(File_U.id).where(File_U.name == 'test')
#             result = await session.execute(query)
#             file_ids = result.scalars().all()
#             ic(file_ids)
#             for file_id in file_ids:
#                 # Find user files to delete
#                 query = select(UserFiles.id).where(
#                     UserFiles.file_id == file_id)
#                 result = await session.execute(query)
#                 user_file_ids = result.scalars().all()

#                 for user_file_id in user_file_ids:
#                     # Delete each UserFiles entry
#                     user_file = await session.get(UserFiles, user_file_id)
#                     if user_file:
#                         await session.delete(user_file)

#                 # Delete the File_U entry
#                 file_entry = await session.get(File_U, file_id)
#                 if file_entry:
#                     await session.delete(file_entry)

#             await session.commit()
#         except Exception as e:
#             print(e)


# @celery.task
# async def delete_expired_files(session: AsyncSession = Depends(get_async_session)):
#     now = datetime.datetime.now(utc)
#     query = select(File_U).where(or_(File_U.download_count >=
#                                      File_U.download_count_del, File_U.will_del_at <= now))
#     result = await session.execute(query)
#     records_to_delete = result.scalars().all()

#     for record in records_to_delete:
#         await session.delete(record)

#     await session.commit()

#     return

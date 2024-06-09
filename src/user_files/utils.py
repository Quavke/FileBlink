from sqlalchemy import select, update
from src.user_files.models import File as File_U


def separate_file_name_and_extension(file_name):
    extensions_list = []
    base_name = file_name
    s = file_name.split('.')
    with open('file_extensions_complete.txt', 'r') as f:
        extensions = [line.strip() for line in f.readlines()]
        for i in s:
            # print("s:", s, "\n")
            i = "." + i
            for k in extensions:
                if i.lower() == k:
                    # print("i:", i, "\n", "k:", k)
                    extensions_list.append(i)
                    break
    for value in extensions_list:
        base_name = base_name.replace(value, "")
    extensions_str = ''
    for j in extensions_list:
        extensions_str = extensions_str + j
    if extensions_str == '':
        extensions_str = None
    return base_name, extensions_str


a, b = separate_file_name_and_extension("Circle.PnG")


async def name_checker(session, name, filename):
    base_name, extension = separate_file_name_and_extension(filename)
    base_name = base_name
    if name != "N/A":
        base_name = name

    query = select(File_U.name).where(File_U.name == base_name)
    result = await session.execute(query)
    filename_db = result.scalar()  # Get the first element of the first row
    # print(filename_db, type(filename_db))  # Should print a str

    query = select(File_U.count).where(File_U.name == base_name)
    result = await session.execute(query)
    filecount_db = result.scalar()  # Get the first element of the first row
    # print(filecount_db, type(filecount_db))  # Should print an int

    if filename_db:
        # print("Count:", filecount_db)
        filecount_db_new = filecount_db + 1
        filename_db = f"{filename_db}({filecount_db_new}--)"

        query = update(File_U).where(
            File_U.name == base_name).values(count=filecount_db_new)
        await session.execute(query)
        await session.commit()
        print(str(filename_db), str(base_name))
        u_name = filename_db
    else:
        u_name = base_name
    return u_name, extension.lower()


# async def file_exists_checker(session, file):
#     file = select(File_U).filter(File_U.file == file)
#     result = await session.execute(file)
#     file_row = result.scalars().first()  # Используем first() вместо one_or_none()

#     if file_row is not None:
#         return file_row
#     else:
#         return None

    # file_row = result.scalars().one_or_none()
    # return file_row is not None


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

from datetime import datetime, timedelta
import pytz
from sqlalchemy import DateTime, Integer, MetaData, String, LargeBinary


from sqlalchemy_file import FileField
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, DeclarativeMeta
from sqlmodel import null


my_metadata = MetaData()


Base: DeclarativeMeta = declarative_base(metadata=my_metadata)


class File(Base):
    __tablename__ = "file"

    name: Mapped[str] = mapped_column(String, index=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(pytz.utc))
    will_del_at: Mapped[datetime] = mapped_column(DateTime, default=(
        datetime.now(pytz.utc) + timedelta(days=7)))
    file: Mapped[FileField] = mapped_column(LargeBinary)

    uuid_: Mapped[str] = mapped_column(
<<<<<<< HEAD
        String, default="1abc", index=True,  primary_key=True)
    # count: Mapped[int] = mapped_column(Integer, default=0) TODO вернуть каунт
=======
        String, default="1abc", index=True, primary_key=True)
    # count: Mapped[int] = mapped_column(Integer, default=0)
>>>>>>> cd838a31c7ad5cc0c114ed14ca194cb21d08e57f
    # file_extension: Mapped[str] = mapped_column(String)
    mime_type: Mapped[str] = mapped_column(String)
    download_count_del: Mapped[int] = mapped_column(
        Integer, default=None, nullable=True)
    password_bytea: Mapped[LargeBinary] = mapped_column(
        LargeBinary, nullable=True)
    secret_uuid: Mapped[str] = mapped_column(
        String, index=True, nullable=False)

    file_size: Mapped[int] = mapped_column(Integer, nullable=True)

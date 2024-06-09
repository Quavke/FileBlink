import datetime
from email.policy import default
from pytz import timezone
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, MetaData, String, LargeBinary


from sqlalchemy_file import FileField
from src.auth.models import User
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, DeclarativeMeta


utc = timezone('UTC')


# FIXME исправить метадату для таблиц, отношения между ними, создание юзера БЕЗ ЕБАНЫХ БАГОВ


my_metadata = MetaData()


Base: DeclarativeMeta = declarative_base(metadata=my_metadata)


class File(Base):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.now(utc))
    will_del_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=(
        datetime.datetime.now(utc) + datetime.timedelta(days=7)))
    file: Mapped[FileField] = mapped_column(LargeBinary)
    # user = sqlalchemy.orm.relationship("UserFiles", back_populates='file',
    #                                    primaryjoin='and_(File.owner_id == User.id)')
    uuid_: Mapped[str] = mapped_column(
        String, default="1abc", index=True, nullable=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    file_extension: Mapped[str] = mapped_column(String)
    mime_type: Mapped[str] = mapped_column(String, nullable=True)
    download_count_del: Mapped[int] = mapped_column(
        Integer, default=None, nullable=True)


class UserFiles(Base):
    __tablename__ = "userfiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    file_id = Column(Integer, ForeignKey(File.id))
    # user = sqlalchemy.orm.relationship('User', back_populates='files')
    # file = sqlalchemy.orm.relationship('File', back_populates='users')

# UserFiles = Table(
#     "userfiles",
#     Base.metadata,
#     id = Column(Integer, primary_key=True),
#     user_id = Column(Integer, ForeignKey(User.id), primary_key=True),
#     file_id = Column(Integer, ForeignKey(File.id), ,
# )

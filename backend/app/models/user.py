from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import LargeBinary, String

import app.config as config
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(config.USER_EMAIL_LENGTH), unique=True, index=True
    )
    password_salt: Mapped[bytes] = mapped_column(
        LargeBinary(config.PASSWORD_SALT_LENGTH)
    )
    password_key: Mapped[bytes] = mapped_column(LargeBinary(config.PASSWORD_KEY_LENGTH))
    is_active: Mapped[bool] = mapped_column(default=True)
    creation_date: Mapped[date] = mapped_column(server_default=func.now())
    display_name: Mapped[str] = mapped_column(String(config.USER_DISPLAY_NAME_LENGTH))

    articles = relationship("Article", back_populates="author")

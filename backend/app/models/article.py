from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import String

import app.config as config
from app.db import Base
from app.schemas.article_blocks import ArticleBlock


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    author = relationship("User", back_populates="articles")
    creation_time: Mapped[datetime] = mapped_column(server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(
        server_default=func.now(), server_onupdate=func.now()
    )
    title: Mapped[str] = mapped_column(String(config.ARTICLE_TITLE_LENGTH))
    body: Mapped[list[ArticleBlock]] = mapped_column(JSON(), default=[])
    is_published: Mapped[bool] = mapped_column(default=False)
    views_count: Mapped[int] = mapped_column(default=0)
    likes_count: Mapped[int] = mapped_column(default=0)

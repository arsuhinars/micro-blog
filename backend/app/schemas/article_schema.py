from datetime import datetime

from pydantic import BaseModel, constr

import app.config as config
from app.schemas.article_blocks import ArticleBlock


class ArticleSchema(BaseModel):
    id: int | None
    author_id: int | None
    creation_time: datetime | None
    update_time: datetime | None
    title: constr(max_length=config.ARTICLE_TITLE_LENGTH)
    body: list[ArticleBlock]
    is_published: bool

    class Config:
        orm_mode = True

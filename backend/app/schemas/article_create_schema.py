from pydantic import BaseModel, constr

import app.config as config


class ArticleCreateSchema(BaseModel):
    title: constr(min_length=1, max_length=config.ARTICLE_TITLE_LENGTH)

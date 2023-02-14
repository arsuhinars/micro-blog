from typing import Literal

from pydantic import BaseModel, HttpUrl, conint, constr

import app.config as config


class ArticleHeader(BaseModel):
    type: Literal["header"]
    heading_level: conint(ge=1, le=6)
    content: constr(max_length=config.ARTICLE_HEADER_LENGTH)


class ArticleParagraph(BaseModel):
    type: Literal["paragraph"]
    content: constr(max_length=config.ARTICLE_PARAGRAPH_LENGTH)


class ArticleQuote(BaseModel):
    type: Literal["quote"]
    content: constr(max_length=config.ARTICLE_QUOTE_LENGTH)


class ArticleList(BaseModel):
    type: Literal["list"]
    list_type: Literal["ordered", "unordered"]
    content: list[constr(max_length=config.ARTICLE_LIST_ITEM_LENGTH)]


class ArticleHorizontalRule(BaseModel):
    type: Literal["horizontal_rule"]


class ArticleImage(BaseModel):
    type: Literal["image"]
    url: HttpUrl | list[HttpUrl]
    margin: Literal["narrow", "middle", "wide"]


ArticleBlock = (
    ArticleHeader
    | ArticleParagraph
    | ArticleQuote
    | ArticleList
    | ArticleHorizontalRule
    # | ArticleImage
)

from typing import Literal

from pydantic import BaseModel, HttpUrl, conint


class ArticleHeader(BaseModel):
    type: Literal["header"]
    heading_level: conint(ge=1, le=6)
    content: str


class ArticleParagraph(BaseModel):
    type: Literal["paragraph"]
    content: str


class ArticleQuote(BaseModel):
    type: Literal["quote"]
    content: str


class ArticleList(BaseModel):
    type: Literal["list"]
    list_type: Literal["ordered", "unordered"]
    content: list[str]


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
    | ArticleImage
)

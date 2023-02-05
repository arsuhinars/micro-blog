from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    email: str
    password: str
    display_name: str

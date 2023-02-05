from datetime import date

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: int | None
    email: EmailStr | None
    creation_date: date | None
    display_name: str

    class Config:
        orm_mode = True

from datetime import date

from pydantic import BaseModel, EmailStr, constr

import app.config as config


class UserSchema(BaseModel):
    id: int | None
    email: EmailStr | None
    creation_date: date | None
    display_name: constr(
        strip_whitespace=True,
        min_length=1,
        max_length=config.USER_DISPLAY_NAME_LENGTH
    )

    class Config:
        orm_mode = True

from pydantic import BaseModel, constr

import app.config as config


class UserCreateSchema(BaseModel):
    email: constr(max_length=config.USER_EMAIL_LENGTH)
    password: constr(
        min_length=config.USER_PASSWORD_MIN_LENGTH,
        max_length=config.USER_PASSWORD_MAX_LENGTH
    )
    display_name: constr(
        strip_whitespace=True,
        min_length=1,
        max_length=config.USER_DISPLAY_NAME_LENGTH
    )

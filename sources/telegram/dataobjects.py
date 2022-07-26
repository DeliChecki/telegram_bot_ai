from typing import Optional, Union

from sqlmodel import Field, SQLModel


# create class User with id, telegram_id, login and password
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int
    login: str
    password: str
    created_at: int
    registered: bool = Field(default=False)
    invited_by: Union[int, None] = Field(default=None)

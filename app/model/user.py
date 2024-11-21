from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from app.model.assesment import Assessment


class UserRoleEnum(Enum):
    admin = "admin"
    coach = "coach"
    user  = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    id: Optional[str] = Field(None, max_length=36, min_length=36)
    username: str
    email: str
    password: str = Field(..., min_length=12, max_length=128)
    role: UserRoleEnum


class UserUpdate(BaseModel):
    id: Optional[str] = Field(None, max_length=36, min_length=36)
    username: str
    email: str
    password: Optional[str] = Field(None, min_length=12, max_length=128)
    role: UserRoleEnum

class User(BaseModel):
    id: Optional[str] = Field(..., max_length=36, min_length=36)
    username: str
    email: str
    hash: str
    role: UserRoleEnum

    def can_grant_roles(self) -> list:
        if self.role == UserRoleEnum.admin:
            return ["admin", "coach", "user"]
        if self.role == UserRoleEnum.coach:
            return ["coach", "user"]
        else:
            return []

    def can_create_user(self, new_user) -> bool:
        if self.role == UserRoleEnum.admin:
            return True
        if self.role == UserRoleEnum.coach:
            if new_user.role == UserRoleEnum.coach:
                return True
            if new_user.role == UserRoleEnum.user:
                return True
        else:
            return False
        return False

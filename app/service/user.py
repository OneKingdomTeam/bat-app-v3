from app.config import  DEFAULT_USER, \
        DEFAULT_EMAIL, DEFAULT_PASSWORD

from app.data import user as data
from app.exception.database import RecordNotFound
from app.exception.service import Unauthorized
from app.service.auth import get_password_hash
from app.model.user import User, UserCreate, UserRoleEnum
from uuid import uuid4

# -------------------------------
#   Add default user
# -------------------------------

def add_default_user():

    new_uuid = str(uuid4())

    username = DEFAULT_USER
    email = DEFAULT_EMAIL
    password = DEFAULT_PASSWORD
    hash: str = ""

    if username is not None and email is not None and password is not None:
        hash = get_password_hash(password)
    else:
        print("Default values for username, admin or password not defined")
        return 

    user_object = User(
        id=new_uuid,
        username=username,
        email=email,
        hash=hash,
        role=UserRoleEnum.admin
        )

    new_user = data.create(user_object)

    return new_user


# -------------------------------
#   Basic CRUD operations
# -------------------------------

def create(user: UserCreate, current_user: User) -> User:

    if not current_user.can_create_user(user):
        raise Unauthorized(msg="You cannot create this user")

    new_uuid = str(uuid4())

    new_user = data.create(User(
            id=new_uuid,
            username=user.username,
            email=user.email,
            hash=get_password_hash(user.password),
            role=user.role
            ))

    return new_user


def get(id: str, current_user: User) -> User:
    user = data.get_one(id)
    return user


def get_all(current_user: User) -> list[User]:

    if current_user.role != UserRoleEnum.admin and current_user.role != UserRoleEnum.coach:
        raise Unauthorized(msg="You cannot list all users, insufficient rights")

    users = data.get_all()
    return users


def delete(uuid: str, current_user: User) -> User:

    user_for_deletion: User = data.get_one(uuid)
    if current_user.can_delete_user(user_for_deletion):
        deleted_user = data.delete(uuid)
    else:
        raise Unauthorized(msg="You cannot perform this action")

    return deleted_user


def update(uuid: str, user: UserCreate, current_user: User) -> User:

    return ""
    if (uuid != user.uuid):
        raise EndpointDataMismatch(msg="Endpoint UUID and data UUID are not matching. Something fishy? Or try contacting your admin.")

    if not current_user.can_modify_user(user):
        raise Unauthorized(msg="You cannot modify this user")

    current_data: User = data.get_one(uuid)

    if user.password:
        password_hash = get_password_hash(user.password)
    else:
        password_hash = current_data.hash

    updated_data = User(
            uuid=user.uuid,
            username=user.username,
            email=user.email,
            hash=password_hash,
            role=user.role,
            )

    modified_user = data.modify(uuid, updated_data)
    return modified_user



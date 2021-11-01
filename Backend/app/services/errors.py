from typing import Callable, Union

from fastapi import HTTPException, status

not_found_error: HTTPException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
)
scope_denied: HTTPException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough scopes"
)
permission_denied: HTTPException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions"
)
something_bad_happened: HTTPException = HTTPException(
    detail="something is wrong", status_code=status.HTTP_400_BAD_REQUEST
)
user_not_found: HTTPException = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="User with this id didn't exist"
)
data_not_acceptable = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Data isn't acceptable"
)
not_author_not_sudo = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="You are not the author of this post"
)
session_error: HTTPException = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Session error"
)

incorrect_username_or_password = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)
inactive_user = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="This User is Disabled"
)
open_registration_forbidden = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Open user registration is forbidden on this server",
)
username_exist = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The user with this username already exists in the system.",
)
email_exist = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The user with this email already exists in the system.",
)
user_not_exist_username = HTTPException(
    status_code=404,
    detail="The user with this username does not exist in the system",
)
user_not_exist_id = HTTPException(
    detail="There no user with this id !", status_code=status.HTTP_400_BAD_REQUEST
)
two_password_didnt_match = HTTPException(
    detail="two passwords are different", status_code=status.HTTP_400_BAD_REQUEST
)
token_didnt_created = HTTPException(
    detail="token created but it's not  saved !", status_code=status.HTTP_409_CONFLICT
)
user_have_not_active_token = HTTPException(
    detail="This user didn't have any active token",
    status_code=status.HTTP_404_NOT_FOUND,
)


def credentials_exception(
    headers=None,
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
):
    if headers:
        headers = {"WWW-Authenticate": headers}
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers,
    )


def func(status_code, detail, headers):
    return HTTPException(status_code=status_code, detail=detail, headers=headers)


def not_validate_credential(headers):
    return func(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers=headers,
    )


not_validate_credential_with_headers = not_validate_credential(headers="Bearer")


def create_exception(detail: Union[str, dict]) -> Callable:
    def inner_status(status_code: status) -> HTTPException:
        return HTTPException(detail=detail, status_code=status_code)

    return inner_status


not_found_exception: Callable = create_exception(detail="item not found")
not_found_status: HTTPException = not_found_exception(
    status_code=status.HTTP_404_NOT_FOUND
)
conflict_status: HTTPException = not_found_exception(
    status_code=status.HTTP_409_CONFLICT
)

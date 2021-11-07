import typing
import pydantic.main as py_fields
import services.scopes as s_service


class ScopeBase(py_fields.BaseModel):
    code: typing.Optional[s_service.ScopeTypes] = None
    description: typing.Optional[str] = None

    class Config:
        orm_mode = True


class ScopeIn(ScopeBase):
    code: s_service.ScopeTypes
    description: str


class ScopeOut(ScopeBase):
    id: int
    code: s_service.ScopeTypes
    description: str


class ScopeUser(py_fields.BaseModel):
    username: str
    id: int
    email: typing.Any

    class Config:
        orm_mode = True


class ScopeOutWithUsers(ScopeOut):
    users: typing.List[ScopeUser]

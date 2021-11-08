import typing
import core.database.session as base_ses
import fastapi.param_functions as fast_params
import fastapi.routing as fast_router
import sqlalchemy.orm.session as sql_ses
import sqlalchemy.sql as sql_select
import services.errors as my_errors
import services.security_service as sec_ser
import apps.users.models as u_models
import apps.scopes.schemas as scope_schemas
import apps.scopes.models as scope_models


scope_api = fast_router.APIRouter()


@scope_api.get(
	"/",
	response_model=typing.List[scope_schemas.ScopeOut],
	dependencies=[fast_params.Depends(sec_ser.get_current_active_user)],
)
async def scope_list(
	session: sql_ses.Session = fast_params.Depends(base_ses.get_session),
):
	"""scope lists with super_user"""
	scopes = session.execute(sql_select.select(scope_models.Scope))
	return scopes.scalars().all()


@scope_api.get(
	"/{scope_id}",
	dependencies=[fast_params.Depends(sec_ser.get_current_active_superuser)],
)
async def scope_detail(
	scope_id: int,
	session: sql_ses.Session = fast_params.Depends(base_ses.get_session),
):
	"""scopes details  with super_user"""
	return session.get(scope_models.Scope, scope_id)


@scope_api.post("/", description="Adding new permission to authentication system")
async def add_new_scope(
	scope: scope_schemas.ScopeIn,
	session: sql_ses.Session = fast_params.Depends(base_ses.get_session),
	current_user: u_models.User = fast_params.Depends(
		sec_ser.get_current_active_superuser
	),
):
	"""creating new scopes with super_user"""
	new_scope = scope_models.Scope()
	new_scope.code = scope.code
	new_scope.description = scope.description
	session.add(new_scope)
	session.commit()
	session.refresh(new_scope)
	return new_scope


@scope_api.get("/users/{scope}", response_model=scope_schemas.ScopeOutWithUsers)
async def scope_users(
	scope: int,
	session: sql_ses.Session = fast_params.Depends(base_ses.get_session),
	current_user: u_models.User = fast_params.Depends(
		sec_ser.get_current_active_superuser
	),
):
	statement = sql_select.select(scope_models.Scope).where(
		scope_models.Scope.id == scope
	)
	scope = session.execute(statement=statement).scalar_one_or_none()
	if not scope:
		raise my_errors.not_found_error()
	return scope


@scope_api.delete("/{scope_id}")
async def delete_scope(
	scope_id: int,
	session: sql_ses.Session = fast_params.Depends(base_ses.get_session),
	current_user: u_models.User = fast_params.Depends(
		sec_ser.get_current_active_superuser
	),
):
	"""deleting scopes with super_user, please be caution"""
	wanted_scope = session.get(scope_models.Scope, scope_id).one
	if not wanted_scope:
		raise my_errors.not_found_error()
	session.delete(wanted_scope)
	session.commit()
	return {
		"msg": f"Scope with code:{wanted_scope.code} and id:{wanted_scope.id} was deleted"
	}

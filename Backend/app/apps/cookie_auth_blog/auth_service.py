from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import status
from fastapi import HTTPException
from fastapi.security import OAuth2
from fastapi import Request
from typing import Optional


class OAuth2PasswordBearerCookie(OAuth2):
	def __init__(
			self,
			tokenUrl: str,
			scheme_name: str = None,
			scopes: dict = None,
			auto_error: bool = True,
	):
		if not scopes:
			scopes = {}
		flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
		super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)
	
	async def __call__(self, request: Request) -> Optional[str]:
		header_authorization: str = request.headers.get("Authorization")
		cookie_authorization: str = request.cookies.get("Authorization")
		
		header_scheme, header_param = get_authorization_scheme_param(
				header_authorization
		)
		cookie_scheme, cookie_param = get_authorization_scheme_param(
				cookie_authorization
		)
		
		if header_scheme.lower() == "bearer":
			authorization = True
			scheme = header_scheme
			param = header_param
		
		elif cookie_scheme.lower() == "bearer":
			authorization = True
			scheme = cookie_scheme
			param = cookie_param
		
		else:
			authorization = False
		
		if not authorization or scheme.lower() != "bearer":
			if self.auto_error:
				raise HTTPException(
						status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
				)
			else:
				return None
		return param


oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/token")

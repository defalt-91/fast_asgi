from fastapi.middleware.cors import CORSMiddleware

from configurations.settings_env import settings

CORS = {
		"middleware_class"  : CORSMiddleware,
		"allow_origins"     : settings.ALLOWED_ORIGINS,
		"allow_methods"     : settings.ALLOWED_METHODS,
		"allow_headers"     : settings.ALLOWED_HEADERS,
		"allow_credentials" : bool(settings.ALLOWED_CREDENTIALS),
		"allow_origin_regex": '',
		"expose_headers"    : '',
		"max_age"           : ''
}

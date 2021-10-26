from core.base_router import api_router
from core.base_settings import settings
from fastapi import FastAPI, responses
from fastapi.middleware import cors, gzip, trustedhost, httpsredirect, wsgi
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from services.exception_services import rate_limit_exceeded_handler
from services.security_service import limiter
from starlette_csrf import CSRFMiddleware

some_file_path = "/home/defalt91/User_Authentication.mkv"
app = FastAPI(
	debug=settings.DEBUG,
	title=settings.PROJECT_NAME,
	version='1',
	docs_url="/docs",
	redoc_url="/redoc",
	openapi_url="/openapi.json",
	# root_path="/api/v1"  # for behind proxy
)

app.include_router(api_router)

app.add_middleware(
	middleware_class=cors.CORSMiddleware,
	allow_origins=settings.ALLOWED_ORIGINS,
	allow_methods=settings.ALLOWED_METHODS,
	allow_headers=settings.ALLOWED_HEADERS,
	allow_credentials=bool(settings.ALLOWED_CREDENTIALS),
	# allow_headers=["*"],
	# expose_headers='',
	max_age=3600,
)
# app.add_middleware(httpsredirect.HTTPSRedirectMiddleware)
app.add_middleware(
	trustedhost.TrustedHostMiddleware,
	allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(
	CSRFMiddleware,
	secret=settings.CSRF_TOKEN_SECRET,
	cookie_name=settings.CSRF_TOKEN_COOKIE_NAME,
	cookie_path=settings.CSRF_TOKEN_COOKIE_PATH,
	# for triggering the csrf check when detecting this cookie in safe methods
	sensitive_cookies=settings.TOKEN_SENSITIVE_COOKIES,
	cookie_domain=settings.FRONTEND_DOMAIN,
	header_name=settings.CSRF_TOKEN_HEADER_NAME,
)
app.add_middleware(gzip.GZipMiddleware, minimum_size=1000)
app.add_middleware(SlowAPIMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


@app.get("/")
async def home():
	return {"hello": "world"}


# asynchronous
@app.get("/video")
async def main():
	return responses.FileResponse(
		some_file_path
		, media_type="video/mp4"
	)


# synchronous
@app.get("/video2")
def main2():
	def iterfile():
		with open(some_file_path, mode="rb") as file_like:
			yield from file_like
	
	return responses.StreamingResponse(iterfile())

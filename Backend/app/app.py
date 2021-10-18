from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from core.base_router import api_router
from core.base_settings import settings
from utils.cors_middleware import CORS
from fastapi.middleware.gzip import GZipMiddleware

some_file_path = "/home/defalt91/User_Authentication.mkv"
app = FastAPI(
		# docs_url=None,
		# redoc_url=None,
		# openapi_url=None
)  # root_path="/"  for behind proxy

app.include_router(api_router)
app.add_middleware(**CORS)
# app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(GZipMiddleware, minimum_size=1000)



@app.get("/")
async def home():
	return {"hello": "world"}


# asyncronous
@app.get("/video")
async def main():
	return FileResponse(
			some_file_path
			, media_type="video/mp4"
	)


# syncronous
@app.get("/video2")
def main():
	def iterfile():
		with open(some_file_path, mode="rb") as file_like:
			yield from file_like
	
	return StreamingResponse(iterfile())

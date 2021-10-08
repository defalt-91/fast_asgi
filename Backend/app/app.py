from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from apps.routers import api_router
from configurations.settings_env import settings
from utils.cors_middleware import CORS
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

some_file_path = "/home/defalt91/User_Authentication.mkv"

app = FastAPI()  # root_path="/"  for behind proxy

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

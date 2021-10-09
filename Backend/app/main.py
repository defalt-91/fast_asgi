from uvicorn.main import run
# from .configurations.settings_json import read_json


if __name__ == '__main__':
	# read_json()
	run(
			app="app:app",
			port=8000,
			use_colors=True,
			log_level="info",
			reload=True,
			workers=1,
			host="127.0.0.1",
	)

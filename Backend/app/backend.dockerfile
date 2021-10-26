FROM fastasgi_python_ready

COPY dependencies.txt .
RUN pip install -r dependencies.txt
WORKDIR /app/

#ENTRYPOINT ["gunicorn","-c","python:gunicorn_conf"]

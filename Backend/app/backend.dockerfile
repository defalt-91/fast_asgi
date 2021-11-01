FROM fastasgi_python_ready:latest

COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app/

#ENTRYPOINT ["gunicorn","-c","python:gunicorn_conf"]

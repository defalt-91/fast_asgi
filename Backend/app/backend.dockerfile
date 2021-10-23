FROM python:3.9

WORKDIR /app/
#USER gunicorn
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY ./Pipfile ./Pipfile.lock  /app/
RUN pip install pipenv && pipenv install --system
#CMD ["gunicorn","-c","python:configurations.gunicorn_conf"]
#COPY . /app/
#CMD python
#ENTRYPOINT ["gunicorn","-c","python:gunicorn_conf"]

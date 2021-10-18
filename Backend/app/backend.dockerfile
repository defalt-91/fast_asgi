FROM python:3.9

#USER gunicorn

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY Pipfile Pipfile.lock  /app/
WORKDIR /app
RUN pip install pipenv && pipenv install --system
#CMD ["gunicorn","-c","python:configurations.gunicorn_conf"]
COPY . /app/
#CMD python
#ENTRYPOINT ["gunicorn","-c","python:gunicorn_conf"]

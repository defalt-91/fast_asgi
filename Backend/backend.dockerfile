FROM fastasgi_python_ready:v1

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
HEALTHCHECK --interval=5m --timeout=3s --start-period=3s --retries=4 CMD curl -f http://localhost/ || exit 1
WORKDIR /fast_asgi_app/app
COPY ./app/requirements.txt /fast_asgi_app/app

#RUN bash -c if [ $INSTALL_DEPENDECIES == 'true' ]; then pip install -r requirements.txt ; fi
#RUN bash -c "if [ $INSTALL_DEPENDECIES == 'true' ]; then pip install -r requirements.txt ; fi"
#CMD ["gunicorn","--reload","-c","gunicorn_conf.py"]
ENV PYTHONPATH=/fast_asgi_app/app
ENTRYPOINT ["bash", "start.sh"]

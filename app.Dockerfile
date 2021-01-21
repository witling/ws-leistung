FROM python:3.9-slim AS base

ADD requirements.txt /tmp/requirements.txt
RUN python -m pip install -r /tmp/requirements.txt

EXPOSE 5000
WORKDIR /app
#COPY ./app /app
ENV FLASK_APP "/app/__main__.py"
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
#CMD python -m flask run --host=0.0.0.0

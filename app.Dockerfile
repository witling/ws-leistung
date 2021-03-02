FROM python:3.9-slim AS base

ADD requirements.txt /tmp/requirements.txt
RUN python -m pip install -r /tmp/requirements.txt

EXPOSE 5000
WORKDIR /app

ENV PYTHONPATH=/common
RUN python -c "import sys; print(sys.path)"

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]

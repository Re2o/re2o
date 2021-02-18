FROM python:3
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends gettext-base libpq-dev
WORKDIR /code
COPY requirements.txt /code/
COPY postgresql-requirements.txt /code/
COPY dev-requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install -r postgresql-requirements.txt
RUN pip install -r dev-requirements.txt
COPY . /code/
CMD ./docker/docker-entrypoint.sh
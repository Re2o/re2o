FROM python:3.6-alpine

# Django code will be in /usr/src/app/
# During development you should mount the git code there,
# During production you should copy the code in the image.
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies via pipenv
ADD Pipfile* ./
RUN apk update && apk add gcc musl-dev postgresql-dev
RUN pip install --upgrade pip==18.0
RUN pip install pipenv==2018.7.1
RUN pipenv install --deploy --system --dev

# Pass only port 8080
EXPOSE 8080

# Set entrypoint : make migrations and collect statics
COPY entrypoint.sh ./
ENTRYPOINT [ "./entrypoint.sh" ]

# Start Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]


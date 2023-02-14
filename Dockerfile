FROM python:3.9

RUN addgroup -S nonroot \
    && adduser -S nonroot -G nonroot

USER nonroot

COPY ./skillstrainer ./skillstrainer
COPY ./quiz ./quiz

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# running migrations
RUN python manage.py migrate

# gunicorn
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]


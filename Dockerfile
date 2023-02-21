FROM python:3.9-alpine

WORKDIR /skills-trainer

RUN addgroup -S nonroot \
    && adduser -S nonroot -G nonroot

USER nonroot

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /skills-trainer/

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY . /skills-trainer/

# running migrations
RUN python manage.py migrate

EXPOSE 5000

# gunicorn
# CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]


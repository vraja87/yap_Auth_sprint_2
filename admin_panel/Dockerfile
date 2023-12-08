FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY uwsgi/uwsgi.ini uwsgi.ini
COPY requirements.txt requirements.txt

RUN  mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --no-cache-dir --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["uwsgi", "--strict", "--ini", "uwsgi.ini"]
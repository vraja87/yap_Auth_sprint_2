FROM python:3.10

WORKDIR /auth

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT [ "sh", "-c", "\
    if [ \"$PROJECT_IS_DEV_MODE\" = 1 ]; \
    then \
        uvicorn main:app --host 0.0.0.0 --port 8000; \
    else \
        alembic upgrade head && python create_admin.py && gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app; \
    fi" ]

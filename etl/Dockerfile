FROM python:3.10

WORKDIR /etl

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir \
     && mkdir "log" \
     && mkdir "cache" \
     && touch "./log/etl.log"

COPY . .

ENTRYPOINT ["python", "./main.py"]

FROM python:3.9

RUN mkdir /file_blink

WORKDIR /file_blink

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x Docker/*.sh

RUN alembic upgrade head

CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000  --log-level app:app

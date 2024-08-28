FROM python:3.12-alpine

WORKDIR /app

RUN python -m pip install -r requirements.txt

COPY . .

RUN alembic upgrade head

CMD ["python", "-m", "anadeabot"]

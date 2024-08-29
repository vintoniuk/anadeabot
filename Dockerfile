FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

RUN --mount=type=secret,id=POSTGRES_URI \
    --mount=type=secret,id=OPENAI_API_KEY \
    POSTGRES_URI="$(cat /run/secrets/POSTGRES_URI)" \
    OPENAI_API_KEY="$(cat /run/secrets/OPENAI_API_KEY)" \
    alembic upgrade head

CMD ["python", "-m", "anadeabot"]

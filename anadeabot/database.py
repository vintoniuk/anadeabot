from typing import TypedDict

from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_postgres import PGVector

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from anadeabot.settings import settings
from anadeabot.schemas import DesignChoice
from anadeabot.models import User, Order, Request

engine = create_engine(settings.POSTGRES_URI)

embeddings = OpenAIEmbeddings(
    model=settings.embedding_model,
    api_key=settings.OPENAI_API_KEY,
    dimensions=settings.dimensionality
)

faq_vectorstore = PGVector(
    embeddings=embeddings,
    connection=settings.POSTGRES_URI,
    embedding_length=settings.dimensionality,
    collection_name='faq',
    use_jsonb=True,
)

grounding_vectorstore = PGVector(
    embeddings=embeddings,
    connection=settings.POSTGRES_URI,
    embedding_length=settings.dimensionality,
    collection_name='grounding',
    use_jsonb=True,
)


def create_user(telegram_id: str | int, *, session: Session) -> User:
    user = User(telegram_id=telegram_id)
    session.add(user)
    session.flush()
    return user


def get_user(telegram_id: str | int, *, session: Session) -> User | None:
    return session.scalar(sa.select(User).filter_by(telegram_id=str(telegram_id)))


def delete_user(user: User, *, session: Session) -> None:
    session.delete(user)
    session.flush()


def place_order(user: User, design: DesignChoice, *, session: Session) -> Order:
    order = Order(
        user_id=user.id,
        color=design.color,
        size=design.size,
        style=design.style,
        gender=design.gender,
        printing=design.printing
    )
    session.add(order)
    session.flush()
    return order


def make_request(user: User, details: str, *, session: Session) -> Request:
    request = Request(user_id=user.id, details=details)
    session.add(request)
    session.flush()
    return request


class FAQ(TypedDict):
    question: str
    answer: str


def create_faq(questions_and_answers: list[FAQ]) -> list[str]:
    documents = [
        Document(qa['question'], metadata={'answer': qa['answer']}) for qa in questions_and_answers
    ]
    return faq_vectorstore.add_documents(documents)


def add_facts(documents: list[str]) -> list[str]:
    return grounding_vectorstore.add_documents([Document(d) for d in documents])

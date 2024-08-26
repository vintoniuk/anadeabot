from typing import TypedDict

from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_postgres import PGVector

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from anadeabot.settings import settings
from anadeabot.schemas import DesignChoice
from anadeabot.models import User, Order

engine = create_engine(settings.POSTGRES_URI)

embeddings = OpenAIEmbeddings(
    model=settings.embedding_model,
    api_key=settings.OPENAI_API_KEY,
    dimensions=settings.dimensionality
)

vectorstore = PGVector(
    embeddings=embeddings,
    connection=settings.POSTGRES_URI,
    embedding_length=settings.dimensionality,
    collection_name='faq',
    use_jsonb=True,
)


class FAQ(TypedDict):
    question: str
    answer: str


def create_faq(questions_and_answers: list[FAQ]) -> list[str]:
    documents = [Document(qa['question'], metadata={'answer': qa['answer']}) for qa in questions_and_answers]
    return vectorstore.add_documents(documents)


def create_user(telegram_id: int, *, session: Session) -> User:

        user = User(telegram_id=telegram_id)
        session.add(user)
        return user


def get_user(telegram_id: int) -> User | None:
    with Session(engine, expire_on_commit=False) as session, session.begin():
        return session.scalar(sa.select(User).filter_by(telegram_id=telegram_id))


def place_order(user: User, design: DesignChoice):
    with Session(engine, expire_on_commit=False) as session, session.begin():
        order = Order(
            user_id=user.id,
            color=design.color,
            size=design.size,
            style=design.style,
            gender=design.gender,
            printing=design.printing
        )
        session.add(order)
        return order

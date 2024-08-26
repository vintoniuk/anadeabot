from typing import TypedDict

from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_postgres import PGVector

from anadeabot.settings import settings

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

from typing import Sequence, Union
import csv

from alembic import op
import sqlalchemy as sa

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import ChatOpenAI

from anadeabot import database
from anadeabot.settings import settings

# revision identifiers, used by Alembic.
revision: str = '1c8f58aec392'
down_revision: Union[str, None] = '4ae9e5a27fc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

grounding_prompt = PromptTemplate.from_template("""
    Given a question and its answer, COMPOSE them together into a single piece
    of knowledge, something like: "to do this, you have to do this" or "it works
    in this way" or just as a fact and REPHRASE the piece of knowledge to be
    complete and self-contained.\n\nQuestion:\n{question}\n\nAnswer:\n{answer} 
""")


def upgrade() -> None:
    llm = ChatOpenAI(model=settings.model, api_key=settings.OPENAI_API_KEY)
    chain = (grounding_prompt | llm | StrOutputParser())

    with open('data/qa.csv', newline='') as file:
        questions_answers = list(csv.DictReader(file))

    database.create_faq(questions_answers)

    facts = chain.batch([
        {'question': qa['question'], 'answer': qa['answer']} for qa in questions_answers
    ])
    database.add_facts(facts)


def downgrade() -> None:
    op.drop_table('langchain_pg_embedding')
    op.drop_table('langchain_pg_collection')

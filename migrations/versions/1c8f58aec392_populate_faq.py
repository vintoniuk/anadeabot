"""populate faq

Revision ID: 1c8f58aec392
Revises: 4ae9e5a27fc6
Create Date: 2024-08-26 12:43:03.251293

"""
from typing import Sequence, Union
import csv

from alembic import op
import sqlalchemy as sa

from anadeabot.database import create_faq, FAQ, vectorstore

# revision identifiers, used by Alembic.
revision: str = '1c8f58aec392'
down_revision: Union[str, None] = '4ae9e5a27fc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with open('data/qa.csv', newline='') as file:
        data = csv.DictReader[FAQ](file)
        create_faq([qa for qa in data], vectorstore)


def downgrade() -> None:
    op.drop_table('langchain_pg_embedding')
    op.drop_table('langchain_pg_collection')

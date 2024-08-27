"""add memory

Revision ID: 4d3f81bcfcc1
Revises: 1c8f58aec392
Create Date: 2024-08-27 14:57:24.144900

"""
from typing import Sequence, Union

from alembic import op
from psycopg import Connection
import sqlalchemy as sa

from langgraph.checkpoint.postgres import PostgresSaver

from anadeabot.settings import settings

# revision identifiers, used by Alembic.
revision: str = '4d3f81bcfcc1'
down_revision: Union[str, None] = '1c8f58aec392'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with PostgresSaver.from_conn_string(settings.POSTGRES_URI) as memory:
        memory.setup()

    for table in ['checkpoints', 'checkpoint_blobs', 'checkpoint_writes']:
        op.create_foreign_key(
            f'{table}_user_telegram_id_fkey',
            source_table=table,
            referent_table='user',
            local_cols=['thread_id'],
            remote_cols=['user_telegram_id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    op.drop_table('checkpoints')
    op.drop_table('checkpoint_blobs')
    op.drop_table('checkpoint_writes')
    op.drop_table('checkpoint_migrations')

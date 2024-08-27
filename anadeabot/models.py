import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Uuid, Text, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, MappedAsDataclass


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column('user_id', Uuid, primary_key=True, insert_default=uuid.uuid4, init=False)
    telegram_id: Mapped[str] = mapped_column('user_telegram_id', Text, nullable=False)
    personality: Mapped[Optional[str]] = mapped_column('user_personality', Text, nullable=True, default=None)

    orders: Mapped[list['Order']] = relationship(default_factory=list, cascade='all, delete', passive_deletes=True,
                                                 lazy='select')
    requests: Mapped[list['Request']] = relationship(default_factory=list, cascade='all, delete', passive_deletes=True,
                                                     lazy='select')


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[uuid.UUID] = mapped_column('order_id', Uuid, primary_key=True, insert_default=uuid.uuid4, init=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'))
    color: Mapped[str] = mapped_column('order_color', String, nullable=False)
    size: Mapped[str] = mapped_column('order_size', String, nullable=False)
    style: Mapped[str] = mapped_column('order_style', String, nullable=False)
    gender: Mapped[str] = mapped_column('order_gender', String, nullable=False)
    printing: Mapped[str] = mapped_column('order_printing', String, nullable=False)
    placed_at: Mapped[datetime] = mapped_column('order_placed_at', server_default=func.CURRENT_TIMESTAMP(), init=False)


class Request(Base):
    __tablename__ = 'request'

    id: Mapped[uuid.UUID] = mapped_column('req_id', Uuid, primary_key=True, insert_default=uuid.uuid4, init=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'))
    details: Mapped[str] = mapped_column('req_details', Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column('req_submitted_at', server_default=func.CURRENT_TIMESTAMP(),
                                                   init=False)

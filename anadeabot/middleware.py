import logging
import functools
from dataclasses import dataclass
from collections.abc import Callable

import sqlalchemy.exc
from pyrogram import Client
from pyrogram.types import Message

from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.postgres import PostgresSaver

from anadeabot import graph
from anadeabot import database
from anadeabot.models import User
from anadeabot.settings import settings


@dataclass
class RequestContext:
    user: User
    session: Session
    memory: BaseCheckpointSaver
    agent: CompiledStateGraph
    config: graph.ConfigSchema


def handle(func: Callable, client: Client, message: Message):
    with Session(database.engine) as session, session.begin():
        if not (user := database.get_user(message.chat.id, session=session)):
            user = database.create_user(message.chat.id, session=session)
    with (
        Session(database.engine) as session, session.begin(),
        PostgresSaver.from_conn_string(settings.POSTGRES_URI) as memory
    ):
        user = session.merge(user)
        agent = graph.create_graph(memory)
        llm = ChatOpenAI(model=settings.model, api_key=settings.OPENAI_API_KEY)
        config = graph.ConfigSchema(thread_id=str(message.chat.id), llm=llm, session=session)
        context = RequestContext(user, session, memory, agent, config)
        return func(client, message, context)


def contextualize(func):
    @functools.wraps(func)
    def wrapper(client: Client, message: Message):
        try:
            try:
                return handle(func, client, message)
            except sqlalchemy.exc.OperationalError as exc:
                logging.warning(exc, exc_info=True)
                return handle(func, client, message)
        except Exception as exc:
            logging.critical(exc, exc_info=True)
            client.send_message(message.chat.id, 'Sorry, something went wrong! Try again later, please.')

    return wrapper

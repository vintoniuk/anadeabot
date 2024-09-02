import logging
import functools
from dataclasses import dataclass
from collections.abc import Callable

import sqlalchemy.exc
from pyrogram import Client
from pyrogram.types import Message

from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI
from langchain_core.tracers import LangChainTracer
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.postgres import PostgresSaver

from langsmith import Client

from anadeabot import database
from anadeabot.models import User
from anadeabot.settings import settings
from anadeabot.graph import create_graph, ConfigSchema


@dataclass
class RequestContext:
    user: User
    session: Session
    memory: BaseCheckpointSaver
    agent: CompiledStateGraph
    tracer: LangChainTracer
    config: ConfigSchema


def handle(func: Callable, client: Client, message: Message):
    with Session(database.engine) as session, session.begin():
        if not (user := database.get_user(message.chat.id, session=session)):
            user = database.create_user(message.chat.id, session=session)
    with (
        Session(database.engine) as session, session.begin(),
        PostgresSaver.from_conn_string(settings.POSTGRES_URI) as memory
    ):
        user = session.merge(user)
        agent = create_graph(memory)
        langsmith_client = Client(api_key=settings.LANGCHAIN_API_KEY)
        tracer = LangChainTracer(project_name='TeeCustomizer', client=langsmith_client)
        llm = ChatOpenAI(model=settings.model, api_key=settings.OPENAI_API_KEY, temperature=0.1)
        config = ConfigSchema(thread_id=str(message.chat.id), llm=llm, session=session)
        context = RequestContext(user, session, memory, agent, tracer, config)
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

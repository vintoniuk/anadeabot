from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters

from langchain_core.messages import HumanMessage

from anadeabot.app import App
from anadeabot import prompts
from anadeabot import database
from anadeabot.middleware import contextualize, RequestContext


@App.on_message(filters.command('start'))
@contextualize
def start_handler(client: Client, message: Message, context: RequestContext):
    state = context.agent.invoke({
        'messages': [prompts.start_agent_system_prompt, prompts.greeting_prompt]
    }, config={'configurable': context.config, 'callbacks': [context.tracer]})
    client.send_message(message.chat.id, state['messages'][-1].content)


@App.on_message(filters.text & (~filters.command(['start', 'stop'])))
@contextualize
def message_handler(client: Client, message: Message, context: RequestContext):
    state = context.agent.invoke({
        'messages': HumanMessage(message.text)
    }, config={'configurable': context.config, 'callbacks': [context.tracer]})
    client.send_message(message.chat.id, state['messages'][-1].content)


@App.on_message(filters.command('stop'))
@contextualize
def stop_handler(client: Client, message: Message, context: RequestContext):
    state = context.agent.invoke({
        'messages': [prompts.say_goodbye_user_prompt]
    }, config={'configurable': context.config, 'callbacks': [context.tracer]})
    database.delete_user(context.user, session=context.session)
    client.send_message(message.chat.id, state['messages'][-1].content)

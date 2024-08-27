import os

from pyrogram import Client

from anadeabot.settings import settings


class App(Client):
    def __init__(self):
        super().__init__(
            name='TeeCustomizer',
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            bot_token=settings.BOT_TOKEN,
            plugins={'root': os.path.basename(os.path.dirname(__file__))}
        )

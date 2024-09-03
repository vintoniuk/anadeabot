import yaml
from typing import Optional

from langchain_core.pydantic_v1 import BaseModel, ConfigDict

from anadeabot.schemas import DesignChoice


class State(BaseModel):
    model_config = ConfigDict(extra='ignore')

    design: Optional[DesignChoice]


class Turn(BaseModel):
    user_message: str
    expected_state: Optional[State]


class Conversation(BaseModel):
    turns: list[Turn]


class Dataset(BaseModel):
    conversations: list[Conversation]


def load_dataset(path: str) -> Dataset:
    with open(path, 'r') as file:
        dataset = Dataset(**yaml.safe_load(file))
    return dataset

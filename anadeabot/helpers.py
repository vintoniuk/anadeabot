from enum import Enum
from pydantic import BaseModel

from anadeabot.schemas import UserIntent, ExpectedIntent


def enum_to_list(enumeration: type[Enum]) -> list[str]:
    return [member.value for member in enumeration]


def missing_attributes(model: BaseModel) -> list[str]:
    return [attr for attr, value in model if value is None]


def resolve_intent(detected: UserIntent, expected: ExpectedIntent, default='agent') -> str:
    active = [intent for intent, active in detected if active]
    weighted = [(intent, expectancy) for intent, expectancy in expected if intent in active]
    likely = max(weighted, key=lambda intent: intent[1], default=None)
    return likely[0] if likely else default

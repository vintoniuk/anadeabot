from enum import Enum
from collections.abc import Iterable
from pydantic import BaseModel


def enum_to_list(enumeration: type[Enum]) -> list[str]:
    return [member.value for member in enumeration]


def missing_attributes(model: BaseModel) -> list[str]:
    return [attr for attr, value in model if value is None]


def first[T](iterable: Iterable[T]) -> T:
    return next(iter(iterable))

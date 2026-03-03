from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Success(Generic[T]):
    data: T
    is_success: bool = True


@dataclass(frozen=True)
class Failure(Generic[E]):
    error: E
    is_success: bool = False


Result = Union[Success[T], Failure[E]]


def success(data: T) -> Success[T]:
    return Success(data=data)


def failure(error: E) -> Failure[E]:
    return Failure(error=error)

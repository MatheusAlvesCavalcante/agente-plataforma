import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


@dataclass(frozen=True)
class Tool:
    name: str
    description: str                 
    parameters: dict[str, Any]       
    input_model: type[BaseModel]    
    executor: Callable[[sqlite3.Connection, Any], dict[str, Any]]
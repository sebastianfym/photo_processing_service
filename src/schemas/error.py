from pydantic.dataclasses import dataclass as pydantic_dataclass

@pydantic_dataclass
class ErrorException(Exception):
    status_code: int
    detail: str
    message: str
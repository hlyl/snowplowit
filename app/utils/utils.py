# app/utils.py

from datetime import datetime
from typing import Union


def str_to_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def date_to_str(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


def handle_date(date: Union[str, datetime]) -> datetime:
    if isinstance(date, str):
        return str_to_date(date)
    return date

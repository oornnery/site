from __future__ import annotations

from typing import TypeVar

from fastapi import Request
from pydantic import BaseModel, ValidationError
from starlette.datastructures import FormData

T = TypeVar("T", bound=BaseModel)


async def parse_form(request: Request, model: type[T]) -> tuple[T | None, dict[str, str]]:
    form = await request.form()
    data = form_to_dict(form)
    try:
        return model(**data), {}
    except ValidationError as exc:
        errors: dict[str, str] = {}
        for item in exc.errors():
            loc = item.get("loc", ())
            field = str(loc[0]) if loc else "_form"
            if field not in errors:
                errors[field] = item.get("msg", "Invalid value")
        return None, errors


def form_to_dict(form: FormData) -> dict:
    result: dict = {}
    for key in form.keys():
        values = form.getlist(key)
        if key.endswith("[]"):
            result[key[:-2]] = [v for v in values if v]
        elif len(values) == 1:
            result[key] = values[0]
        else:
            result[key] = values
    return result

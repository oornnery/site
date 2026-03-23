from __future__ import annotations

from pydantic import BaseModel, Field


class SEOMeta(BaseModel):
    title: str
    description: str = Field(max_length=160)
    og_image: str = ""
    og_type: str = "website"
    canonical_url: str = ""
    keywords: list[str] = Field(default_factory=list)

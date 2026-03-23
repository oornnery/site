from pydantic import BaseModel, ConfigDict, Field

from app.models.seo import SEOMeta


class ContactPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    csrf_token: str
    success: str = ""
    errors: dict[str, str] = Field(default_factory=dict)
    form_data: dict[str, str] = Field(default_factory=dict)
    current_path: str = "/contact"

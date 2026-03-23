from pydantic import BaseModel, ConfigDict

from app.models.about import (
    AboutFrontmatter,
    CertificateItem,
    EducationItem,
    SkillGroupItem,
    WorkExperienceItem,
)
from app.models.seo import SEOMeta


class AboutPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    meta: AboutFrontmatter
    hero_html: str
    about_html: str
    work_experience: tuple[WorkExperienceItem, ...] = ()
    education: tuple[EducationItem, ...] = ()
    certificates: tuple[CertificateItem, ...] = ()
    skill_groups: tuple[SkillGroupItem, ...] = ()
    current_path: str = "/about"

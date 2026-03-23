from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field


def _format_period(start: str, end: str) -> str:
    if start and end:
        return f"{start} - {end}"
    return start or end


class WorkExperienceItem(BaseModel):
    title: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    highlights: list[str] = Field(default_factory=list)
    content_html: str = ""

    @computed_field
    @property
    def period(self) -> str:
        return _format_period(self.start_date, self.end_date)


class EducationItem(BaseModel):
    school: str = ""
    degree: str = ""
    start_date: str = ""
    end_date: str = ""
    details_html: str = ""

    @computed_field
    @property
    def period(self) -> str:
        return _format_period(self.start_date, self.end_date)


class CertificateItem(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""
    credential_id: str = ""
    details_html: str = ""


class SkillGroupItem(BaseModel):
    title: str = ""
    skills: list[str] = Field(default_factory=list)


class AboutFrontmatter(BaseModel):
    description: str = ""
    name: str = ""
    role: str = ""
    location: str = ""
    avatar_url: str = ""
    social_links: dict[str, HttpUrl] = Field(default_factory=dict)
    work_experience: list[WorkExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    certificates: list[CertificateItem] = Field(default_factory=list)
    skill_groups: list[SkillGroupItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class AboutContent(BaseModel):
    frontmatter: AboutFrontmatter
    body_markdown: str
    body_html: str
    hero_markdown: str = ""
    hero_html: str = ""
    about_markdown: str = ""
    about_html: str = ""
    work_experience: list[WorkExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    certificates: list[CertificateItem] = Field(default_factory=list)
    skill_groups: list[SkillGroupItem] = Field(default_factory=list)

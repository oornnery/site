from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from app.infrastructure import markdown as markdown_infra


def test_about_loader_parses_frontmatter_and_markdown_sections(
    monkeypatch, tmp_path: Path
) -> None:
    content_dir = tmp_path / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    (content_dir / "about.md").write_text(
        dedent(
            """
            ---
            name: "Test Engineer"
            description: "Backend engineer focused on reliable systems."
            role: "Backend Engineer"
            location: "Sao Paulo, Brazil"
            social_links:
              github: "https://github.com/example"
            work_experience:
              - title: "Senior Engineer"
                company: "Example Co"
                location: "Remote"
                start_date: "2020"
                end_date: "Present"
                highlights:
                  - "improved observability"
                  - "simplified validation contracts"
            education:
              - school: "University of Technology"
                degree: "B.S. in Computer Science"
                start_date: "2014"
                end_date: "2018"
            certificates:
              - name: "AWS Certified Solutions Architect"
                issuer: "Amazon Web Services"
                date: "2023"
                credential_id: "AWS-SAA-123456"
            skill_groups:
              - title: "Backend"
                skills: ["Python", "FastAPI"]
              - title: "Infra"
                skills: ["Docker", "Linux"]
            ---
            I build **reliable** backend systems.

            ## About

            I care about [maintainable delivery](https://example.com).
            """
        ).strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(markdown_infra, "CONTENT_DIR", content_dir)
    markdown_infra._content_cache.clear()

    about = markdown_infra.load_about()

    assert about.frontmatter.name == "Test Engineer"
    assert "<strong>reliable</strong>" in about.hero_html
    assert 'href="https://example.com"' in about.about_html

    assert len(about.work_experience) == 1
    experience = about.work_experience[0]
    assert experience.title == "Senior Engineer"
    assert experience.company == "Example Co"
    assert experience.location == "Remote"
    assert experience.start_date == "2020"
    assert experience.end_date == "Present"
    assert "improved observability" in experience.highlights

    assert len(about.education) == 1
    education = about.education[0]
    assert education.school == "University of Technology"
    assert education.degree == "B.S. in Computer Science"
    assert education.start_date == "2014"
    assert education.end_date == "2018"

    assert len(about.certificates) == 1
    certificate = about.certificates[0]
    assert certificate.name == "AWS Certified Solutions Architect"
    assert certificate.issuer == "Amazon Web Services"
    assert certificate.date == "2023"
    assert certificate.credential_id == "AWS-SAA-123456"

    assert len(about.skill_groups) == 2
    assert about.skill_groups[0].title == "Backend"
    assert about.skill_groups[0].skills == ["Python", "FastAPI"]
    assert about.skill_groups[1].title == "Infra"
    assert about.skill_groups[1].skills == ["Docker", "Linux"]

    markdown_infra._content_cache.clear()


def test_about_loader_allows_missing_optional_fields(
    monkeypatch, tmp_path: Path
) -> None:
    content_dir = tmp_path / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    (content_dir / "about.md").write_text(
        dedent(
            """
            ---
            name: "Test Engineer"
            description: "Backend engineer focused on reliable systems."
            social_links:
              github: "https://github.com/example"
            work_experience:
              - title: "Senior Engineer"
                company: "Example Co"
            education:
              - school: "University of Technology"
            certificates:
              - name: "AWS Certified Solutions Architect"
            skill_groups:
              - title: "Backend"
                skills: ["Python"]
            ---
            Intro paragraph.
            """
        ).strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(markdown_infra, "CONTENT_DIR", content_dir)
    markdown_infra._content_cache.clear()

    about = markdown_infra.load_about()

    experience = about.work_experience[0]
    assert experience.location == ""
    assert experience.start_date == ""
    assert experience.end_date == ""

    education = about.education[0]
    assert education.degree == ""
    assert education.start_date == ""
    assert education.end_date == ""

    certificate = about.certificates[0]
    assert certificate.issuer == ""
    assert certificate.date == ""
    assert certificate.credential_id == ""

    markdown_infra._content_cache.clear()

import logging
import re
from typing import Any

from app.models.schemas import (
    CertificateItem,
    EducationItem,
    SkillGroupItem,
    WorkExperienceItem,
)

logger = logging.getLogger(__name__)

_ABOUT_SECTION_PATTERN = re.compile(r"^\s*##\s+(.+?)\s*$")
_ABOUT_ENTRY_PATTERN = re.compile(r"^\s*###\s+(.+?)\s*$")
_ABOUT_META_PATTERN = re.compile(r"^\s*\*\*(.+?):\*\*\s*(.+?)\s*$")
_ABOUT_LIST_PATTERN = re.compile(r"^\s*[-*+]\s+(.+?)\s*$")


def _render(content: str) -> str:
    """Deferred import wrapper to avoid circular dependency with markdown.py."""
    from app.infrastructure.markdown import render_sanitized_markdown

    return render_sanitized_markdown(content)


def _normalize_about_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _split_markdown_sections(
    content: str, heading_pattern: re.Pattern[str]
) -> tuple[str, list[tuple[str, str]]]:
    preamble_lines: list[str] = []
    sections: list[tuple[str, str]] = []
    current_title = ""
    current_lines: list[str] = []

    for line in content.splitlines():
        match = heading_pattern.match(line)
        if match:
            if current_title:
                sections.append((current_title, "\n".join(current_lines).strip()))
            else:
                preamble_lines = (
                    current_lines.copy() if current_lines else preamble_lines
                )
            current_title = match.group(1).strip()
            current_lines = []
            continue

        if current_title:
            current_lines.append(line)
        else:
            preamble_lines.append(line)

    if current_title:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return "\n".join(preamble_lines).strip(), sections


def _extract_about_metadata(content: str) -> tuple[dict[str, str], str]:
    lines = content.splitlines()
    metadata: dict[str, str] = {}
    index = 0

    while index < len(lines) and not lines[index].strip():
        index += 1

    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue

        match = _ABOUT_META_PATTERN.match(stripped)
        if not match:
            break

        metadata[_normalize_about_key(match.group(1))] = match.group(2).strip()
        index += 1

    while index < len(lines) and not lines[index].strip():
        index += 1

    return metadata, "\n".join(lines[index:]).strip()


def _split_period_value(value: str) -> tuple[str, str]:
    raw = value.strip()
    if not raw:
        return "", ""

    for delimiter in (" - ", " – ", " — "):
        if delimiter in raw:
            start, end = raw.split(delimiter, 1)
            return start.strip(), end.strip()

    return raw, ""


def _resolve_period_metadata(metadata: dict[str, str]) -> tuple[str, str]:
    start = metadata.get("start_date") or metadata.get("start") or ""
    end = metadata.get("end_date") or metadata.get("end") or ""
    if start or end:
        return start.strip(), end.strip()

    return _split_period_value(metadata.get("period") or metadata.get("dates") or "")


def _extract_skill_values(content: str) -> list[str]:
    skills: list[str] = []

    for line in content.splitlines():
        match = _ABOUT_LIST_PATTERN.match(line)
        if not match:
            continue
        value = match.group(1).strip()
        value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
        value = re.sub(r"[*_`]+", "", value)
        value = re.sub(r"\s+", " ", value).strip()
        if value:
            skills.append(value)

    if skills:
        return skills

    compact = " ".join(line.strip() for line in content.splitlines() if line.strip())
    if not compact:
        return []

    fallback_skills: list[str] = []
    for item in compact.split(","):
        candidate = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", item)
        candidate = re.sub(r"[*_`]+", "", candidate)
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if candidate:
            fallback_skills.append(candidate)
    return fallback_skills


def _parse_about_work_experience(content: str) -> list[WorkExperienceItem]:
    _, entries = _split_markdown_sections(content, _ABOUT_ENTRY_PATTERN)
    items: list[WorkExperienceItem] = []

    for title, entry_content in entries:
        metadata, body = _extract_about_metadata(entry_content)
        start_date, end_date = _resolve_period_metadata(metadata)
        items.append(
            WorkExperienceItem(
                title=title.strip(),
                company=metadata.get("company", ""),
                location=metadata.get("location", ""),
                start_date=start_date,
                end_date=end_date,
                content_html=_render(body),
            )
        )

    return items


def _parse_about_education(content: str) -> list[EducationItem]:
    _, entries = _split_markdown_sections(content, _ABOUT_ENTRY_PATTERN)
    items: list[EducationItem] = []

    for title, entry_content in entries:
        metadata, body = _extract_about_metadata(entry_content)
        start_date, end_date = _resolve_period_metadata(metadata)
        items.append(
            EducationItem(
                school=title.strip(),
                degree=metadata.get("degree", ""),
                start_date=start_date,
                end_date=end_date,
                details_html=_render(body),
            )
        )

    return items


def _parse_about_certificates(content: str) -> list[CertificateItem]:
    _, entries = _split_markdown_sections(content, _ABOUT_ENTRY_PATTERN)
    items: list[CertificateItem] = []

    for title, entry_content in entries:
        metadata, body = _extract_about_metadata(entry_content)
        items.append(
            CertificateItem(
                name=title.strip(),
                issuer=metadata.get("issuer", ""),
                date=metadata.get("date", ""),
                credential_id=metadata.get("credential_id", ""),
                details_html=_render(body),
            )
        )

    return items


def _parse_about_skill_groups(content: str) -> list[SkillGroupItem]:
    section_intro, entries = _split_markdown_sections(content, _ABOUT_ENTRY_PATTERN)
    groups: list[SkillGroupItem] = []

    if entries:
        for title, entry_content in entries:
            skills = _extract_skill_values(entry_content)
            if skills:
                groups.append(SkillGroupItem(title=title.strip(), skills=skills))
        return groups

    intro_skills = _extract_skill_values(section_intro)
    if intro_skills:
        groups.append(SkillGroupItem(title="Core", skills=intro_skills))
    return groups


def _parse_about_body(body: str) -> dict[str, Any]:
    hero_markdown, sections = _split_markdown_sections(body, _ABOUT_SECTION_PATTERN)

    section_map = {
        _normalize_about_key(title): content
        for title, content in sections
        if title.strip()
    }

    return {
        "hero_markdown": hero_markdown,
        "hero_html": _render(hero_markdown),
        "about_markdown": section_map.get("about", ""),
        "about_html": _render(section_map.get("about", "")),
        "work_experience": _parse_about_work_experience(
            section_map.get("work_experience", "")
        ),
        "education": _parse_about_education(section_map.get("education", "")),
        "certificates": _parse_about_certificates(section_map.get("certificates", "")),
        "skill_groups": _parse_about_skill_groups(section_map.get("skills", "")),
    }

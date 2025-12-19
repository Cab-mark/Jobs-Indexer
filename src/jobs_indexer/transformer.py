from __future__ import annotations

from typing import Any

from .models import Job, JobIndex, Location, Salary


def _normalize_location(raw: Any) -> Any:
    if raw is None:
        return None
    if isinstance(raw, list):
        return [_normalize_location(item) for item in raw]
    if isinstance(raw, (str, Location)):
        return raw
    if isinstance(raw, dict):
        return Location.model_validate(raw)
    return raw


def _normalize_salary(raw: Any) -> Salary | None:
    if raw is None:
        return None
    return Salary.model_validate(raw)


def apply_index_enhancements(document: dict) -> dict:
    """
    Hook to extend the indexed shape (e.g., normalized search fields).
    Currently a no-op to keep mapping aligned with JobIndex schema.
    """
    return document


def transform_job_to_index(job: Job) -> JobIndex:
    normalized_location = _normalize_location(job.location)
    normalized_salary = _normalize_salary(job.salary)

    target_fields = {
        key: value
        for key, value in {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "companyName": job.companyName,
            "companyId": job.companyId,
            "location": normalized_location,
            "salary": normalized_salary,
            "remote": job.remote,
            "employmentType": job.employmentType,
            "tags": job.tags,
            "categories": job.categories,
            "department": job.department,
            "language": job.language,
            "publishedAt": job.publishedAt,
            "createdAt": job.createdAt,
            "updatedAt": job.updatedAt,
            "expiresAt": job.expiresAt,
            "source": job.source,
        }.items()
        if value is not None
    }

    # Extension hook for derived/index-optimized fields while keeping the base mapping stable.
    enhanced = apply_index_enhancements(target_fields)
    return JobIndex.model_validate(enhanced)

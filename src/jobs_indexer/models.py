from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class Salary(BaseModel):
    minAmount: Optional[float] = Field(None, ge=0)
    maxAmount: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    period: Optional[str] = Field(
        None, description="Period such as hourly, daily, weekly, monthly, yearly."
    )

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class GeoPoint(BaseModel):
    lat: Optional[float] = Field(None, description="Latitude in WGS84")
    lon: Optional[float] = Field(None, description="Longitude in WGS84")

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class Location(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postalCode: Optional[str] = None
    coordinates: Optional[GeoPoint] = None
    remote: Optional[bool] = None

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


LocationField = Union[Location, List[Location], List[str]]


class Job(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    companyName: str = Field(..., description="Display name of the company")
    companyId: Optional[str] = None
    location: Optional[LocationField] = Field(
        None,
        description="Location may be an object or array of objects/strings.",
    )
    salary: Optional[Salary] = None
    remote: Optional[bool] = None
    employmentType: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    department: Optional[str] = None
    language: Optional[str] = None
    applyUrl: Optional[str] = None
    applyDetail: Optional[str] = None
    contacts: Optional[List[str]] = None
    publishedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None
    source: Optional[str] = None

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class JobIndex(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    companyName: str
    companyId: Optional[str] = None
    location: Optional[LocationField] = None
    salary: Optional[Salary] = None
    remote: Optional[bool] = None
    employmentType: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    department: Optional[str] = None
    language: Optional[str] = None
    publishedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None
    source: Optional[str] = None

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

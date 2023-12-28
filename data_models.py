"""
This module contains logic to transform extracted data,
to specially designed classes with relevant data from Adzuna API.
"""

from typing import List, Optional

from pydantic import BaseModel


class AdzunaAd(BaseModel):
    """
    Output class for Adzuna ads.
    (order of attributes could nevertheless be rearranged.)
    """

    title: str
    created: str

    salary_is_predicted: int
    salary_min: Optional[float]
    salary_max: Optional[float]

    latitude: Optional[float]
    longitude: Optional[float]
    area: List[str]
    location: str

    id: str
    adref: str
    redirect_url: str

    company: Optional[
        str
    ]  # It's weird but it caused a bug, as a company wasn't specified
    description: str
    contract_type: Optional[str]
    contract_time: Optional[str]

    # Corresponds to 'category' in job_market_variables sheet
    label: str
    tag: str


def filter_adzuna_ad(ad: dict) -> dict:
    """Filter a dict inputs to fit into an AdzunaAd's instance attributes"""
    return {
        "title": ad.get("title"),
        "created": ad.get("created"),
        "salary_is_predicted": ad.get("salary_is_predicted"),
        "salary_min": ad.get("salary_min"),
        "salary_max": ad.get("salary_max"),
        "latitude": ad.get("latitude"),
        "longitude": ad.get("longitude"),
        "location": ad.get("location", {}).get("display_name"),
        "area": ad.get("location", {}).get("area"),
        "id": str(ad.get("id", "")),  # ❓isn't `int` better? / NA managing
        "adref": ad.get("adref"),
        "redirect_url": ad.get("redirect_url"),
        "company": ad.get("company", {}).get("display_name"),
        "description": ad.get("description"),
        "contract_type": ad.get("contract_type"),
        "contract_time": ad.get("contract_time"),
        "label": ad.get("category", {}).get("label"),
        "tag": ad.get("category", {}).get("tag"),
    }


def model_adzuna_ad_data(ads: List[dict]) -> List[AdzunaAd]:
    """Map filter_adzuna_job to the list of dict inputs."""
    return [AdzunaAd(**filter_adzuna_ad(ad)) for ad in ads]


def is_internship(ad: AdzunaAd) -> bool:
    """Tests if an ad is an internship one"""
    return ("alternance" in ad.title or
            "Alternance" in ad.title or
            "stage" in ad.title or
            "Stage" in ad.title)

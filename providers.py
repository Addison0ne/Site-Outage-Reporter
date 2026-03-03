from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class Provider:
    name: str
    api_url: str
    network_type: str


# NOTE: Endpoints are placeholders where available public outage APIs do not exist.
# Update these URLs and parse logic as required for each provider.
PROVIDERS: list[Provider] = [
    Provider("Telstra 4G", "https://example.com/api/outages/telstra", "4G"),
    Provider("Optus 4G", "https://example.com/api/outages/optus", "4G"),
    Provider("Vodafone 4G", "https://example.com/api/outages/vodafone", "4G"),
    Provider("NBN", "https://example.com/api/outages/nbn", "Fixed"),
]


def fetch_provider_outages(provider: Provider) -> list[dict[str, Any]]:
    """
    Expected API response format:
    {
      "outages": [
        {
          "site_code": "MEL-001",
          "status": "OUTAGE" | "DEGRADED" | "OK",
          "description": "...",
          "started_at": "2026-03-02T01:23:00Z",
          "updated_at": "2026-03-02T03:45:00Z"
        }
      ]
    }
    """
    response = requests.get(provider.api_url, timeout=20)
    response.raise_for_status()
    payload = response.json()
    return payload.get("outages", [])

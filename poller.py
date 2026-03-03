from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from db import SessionLocal, upsert_outage
from providers import PROVIDERS, fetch_provider_outages


def _parse_iso(timestamp: str | None) -> datetime | None:
    if not timestamp:
        return None
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def poll_once() -> dict[str, int]:
    inserted_or_updated = 0
    failures = 0

    db: Session = SessionLocal()
    try:
        for provider in PROVIDERS:
            try:
                outages = fetch_provider_outages(provider)
                for outage in outages:
                    upsert_outage(
                        db=db,
                        provider=provider.name,
                        network_type=provider.network_type,
                        site_code=outage.get("site_code", "UNKNOWN"),
                        status=outage.get("status", "UNKNOWN"),
                        description=outage.get("description", "No description supplied."),
                        started_at=_parse_iso(outage.get("started_at")),
                        updated_at=_parse_iso(outage.get("updated_at")),
                    )
                    inserted_or_updated += 1
            except Exception:
                failures += 1
        db.commit()
    finally:
        db.close()

    return {"updated": inserted_or_updated, "failed_providers": failures}

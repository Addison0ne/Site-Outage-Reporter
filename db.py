from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from config import settings


class Base(DeclarativeBase):
    pass


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_code: Mapped[str] = mapped_column(String(128), index=True)
    site_name: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(16))


class Outage(Base):
    __tablename__ = "outages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(128), index=True)
    network_type: Mapped[str] = mapped_column(String(16))
    site_code: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    description: Mapped[str] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_polled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


engine = create_engine(settings.sqlalchemy_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)


def upsert_outage(
    db: Session,
    provider: str,
    network_type: str,
    site_code: str,
    status: str,
    description: str,
    started_at: datetime | None,
    updated_at: datetime | None,
) -> None:
    existing = db.execute(
        select(Outage).where(Outage.provider == provider, Outage.site_code == site_code)
    ).scalar_one_or_none()

    if existing:
        existing.status = status
        existing.description = description
        existing.started_at = started_at
        existing.updated_at = updated_at
        existing.last_polled_at = datetime.utcnow()
    else:
        db.add(
            Outage(
                provider=provider,
                network_type=network_type,
                site_code=site_code,
                status=status,
                description=description,
                started_at=started_at,
                updated_at=updated_at,
                last_polled_at=datetime.utcnow(),
            )
        )


def get_outages_for_sites(db: Session, site_codes: list[str]) -> list[Outage]:
    if not site_codes:
        return db.execute(select(Outage).order_by(Outage.last_polled_at.desc())).scalars().all()
    return (
        db.execute(
            select(Outage)
            .where(Outage.site_code.in_(site_codes))
            .order_by(Outage.last_polled_at.desc())
        )
        .scalars()
        .all()
    )

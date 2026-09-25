from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_name: Mapped[str] = mapped_column(String(150), default="VEYRA Shop", nullable=False)
    owner_name: Mapped[str | None] = mapped_column(String(150))
    phone: Mapped[str | None] = mapped_column(String(60))
    email: Mapped[str | None] = mapped_column(String(120))
    address: Mapped[str | None] = mapped_column(String(255))
    vat_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    vat_rate: Mapped[float] = mapped_column(Float, default=16.0, nullable=False)
    theme: Mapped[str] = mapped_column(String(40), default="light", nullable=False)
    font_size: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)
    profile_image: Mapped[str | None] = mapped_column(String(255))
    logo_image: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

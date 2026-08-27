"""
SQLAlchemy ORM models for the ShortLink API.
"""

from sqlalchemy import Column, DateTime, Integer, String, func

from app.database import Base


class ShortURL(Base):
    """
    Represents a shortened URL entry.

    Stores the original destination URL alongside a unique
    short code and tracks how many times the link has been
    followed.
    """

    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<ShortURL id={self.id} "
            f"short_code='{self.short_code}' "
            f"clicks={self.clicks}>"
        )

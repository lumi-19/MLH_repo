"""
Database CRUD operations for the ShortLink API.

All database access is abstracted through these functions,
keeping route handlers clean and focused on request/response logic.
"""

from sqlalchemy.orm import Session

from app.models import ShortURL


def create_short_url(db: Session, original_url: str, short_code: str) -> ShortURL:
    """
    Persist a new shortened URL entry.

    Args:
        db: Active database session.
        original_url: The destination URL.
        short_code: The generated unique short code.

    Returns:
        The newly created ShortURL ORM instance (committed and refreshed).
    """
    entry = ShortURL(original_url=original_url, short_code=short_code)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_by_short_code(db: Session, short_code: str) -> ShortURL | None:
    """
    Look up a short URL entry by its code.

    Returns None when no entry matches.
    """
    return db.query(ShortURL).filter(ShortURL.short_code == short_code).first()


def increment_clicks(db: Session, entry: ShortURL) -> ShortURL:
    """
    Increment the click counter for a short URL entry.

    Returns the updated entry.
    """
    entry.clicks += 1
    db.commit()
    db.refresh(entry)
    return entry

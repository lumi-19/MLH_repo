"""
Utility functions for the ShortLink API.

Uses Python's secrets module for cryptographically secure
random short code generation — ensuring unpredictable codes
that cannot be guessed or enumerated.
"""

import secrets
import string

# Base62 alphabet (A-Z, a-z, 0-9) — URL-safe, no special characters
BASE62 = string.ascii_letters + string.digits


def generate_short_code(length: int = 6) -> str:
    """
    Generate a cryptographically random short code.

    Args:
        length: Number of characters in the code (default 6,
                providing 62^6 ≈ 56 billion possible combinations).

    Returns:
        A random URL-safe string of the requested length.
    """
    return "".join(secrets.choice(BASE62) for _ in range(length))

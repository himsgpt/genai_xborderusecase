"""
Shared FastAPI dependencies used across multiple route files.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.database import get_db, AsyncSessionLocal
from ..infrastructure.auth import get_current_user_id

# Re-export so routes can do: from ..api.deps import get_db, get_current_user_id
__all__ = ["get_db", "get_current_user_id"]

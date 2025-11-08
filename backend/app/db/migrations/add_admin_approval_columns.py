"""
Add requested_role and role_approved columns to users table
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models import UserRole
import logging

logger = logging.getLogger(__name__)


async def add_admin_approval_columns():
    """Add requested_role and role_approved columns to users table"""
    async with AsyncSessionLocal() as db:
        try:
            # Add requested_role column (nullable)
            await db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS requested_role VARCHAR(20);
            """))
            
            # Add role_approved column with default True
            await db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS role_approved BOOLEAN DEFAULT TRUE;
            """))
            
            # Update existing users to have role_approved = TRUE
            await db.execute(text("""
                UPDATE users 
                SET role_approved = TRUE 
                WHERE role_approved IS NULL;
            """))
            
            await db.commit()
            logger.info("✅ Successfully added requested_role and role_approved columns to users table")
            
        except Exception as e:
            logger.error(f"❌ Error adding admin approval columns: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(add_admin_approval_columns())

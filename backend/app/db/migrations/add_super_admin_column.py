"""
Add is_super_admin column to users table
"""

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)


async def add_super_admin_column():
    """Add is_super_admin column to users table"""
    async with AsyncSessionLocal() as db:
        try:
            # Add is_super_admin column with default False
            await db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_super_admin BOOLEAN DEFAULT FALSE;
            """))
            
            # Set existing admin user as super admin
            await db.execute(text("""
                UPDATE users 
                SET is_super_admin = TRUE 
                WHERE username = 'admin';
            """))
            
            await db.commit()
            logger.info("✅ Successfully added is_super_admin column to users table")
            
        except Exception as e:
            logger.error(f"❌ Error adding super admin column: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(add_super_admin_column())

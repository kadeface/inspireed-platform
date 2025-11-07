"""
Fix lesson status enum mismatch

This script was used to fix a one-time issue where the PostgreSQL lessonstatus enum
had UPPERCASE values (DRAFT, PUBLISHED, ARCHIVED) but the actual data and Python
enum definition used lowercase values (draft, published, archived).

This caused SQLAlchemy to fail when querying lessons with:
    LookupError: 'published' is not among the defined enum values

The fix has been applied and is also captured in migration 007_fix_lesson_enum_values.py

Usage:
    python scripts/fix_lesson_status_enum.py

Note: This script is idempotent and can be run multiple times safely.
      It will check the current state and only make changes if needed.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def fix_enum():
    """Fix the lesson status enum mismatch"""
    
    async with AsyncSessionLocal() as db:
        print("🔍 Checking current enum values...")
        
        # Check if the enum type exists and what values it has
        result = await db.execute(text("""
            SELECT 
                e.enumlabel 
            FROM 
                pg_enum e
                JOIN pg_type t ON e.enumtypid = t.oid
            WHERE 
                t.typname = 'lessonstatus'
            ORDER BY 
                e.enumsortorder;
        """))
        
        current_values = [row[0] for row in result.fetchall()]
        print(f"Current enum values: {current_values}")
        
        # Check what values are actually in the lessons table
        result = await db.execute(text("""
            SELECT DISTINCT status FROM lessons;
        """))
        
        used_values = [row[0] for row in result.fetchall()]
        print(f"Values used in lessons table: {used_values}")
        
        # Expected values (lowercase, matching Python enum)
        expected_values = ['draft', 'published', 'archived']
        
        # If current enum has uppercase values but data has lowercase, we need to fix it
        if current_values != expected_values:
            print("\n⚠️  Enum mismatch detected. Fixing...")
            
            # Update existing data to use lowercase if needed
            for old_val in used_values:
                new_val = old_val.lower()
                if old_val != new_val:
                    print(f"   Converting '{old_val}' to '{new_val}'...")
                    await db.execute(text(f"""
                        ALTER TABLE lessons 
                        ALTER COLUMN status TYPE VARCHAR;
                    """))
                    await db.execute(text(f"""
                        UPDATE lessons 
                        SET status = '{new_val}' 
                        WHERE status = '{old_val}';
                    """))
            
            # Drop the default value first
            print("   Dropping default value...")
            await db.execute(text("""
                ALTER TABLE lessons 
                ALTER COLUMN status DROP DEFAULT;
            """))
            
            # Drop the old enum type
            print("   Dropping old enum type...")
            await db.execute(text("""
                DROP TYPE IF EXISTS lessonstatus CASCADE;
            """))
            
            # Create new enum type with lowercase values
            print("   Creating new enum type with correct values...")
            await db.execute(text("""
                CREATE TYPE lessonstatus AS ENUM ('draft', 'published', 'archived');
            """))
            
            # Convert the column back to enum
            print("   Converting column to use new enum...")
            await db.execute(text("""
                ALTER TABLE lessons 
                ALTER COLUMN status TYPE lessonstatus 
                USING status::text::lessonstatus;
            """))
            
            # Re-add the default value
            print("   Re-adding default value...")
            await db.execute(text("""
                ALTER TABLE lessons 
                ALTER COLUMN status SET DEFAULT 'draft'::lessonstatus;
            """))
            
            await db.commit()
            print("✅ Enum fixed successfully!")
        else:
            print("✅ Enum is already correct!")


async def main():
    """Main function"""
    try:
        await fix_enum()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


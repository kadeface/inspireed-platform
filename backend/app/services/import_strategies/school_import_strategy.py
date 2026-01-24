"""
School Import Strategy

Strategy for importing school information from Excel files.
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models import Region, School
from .base_strategy import BaseImportStrategy
from ..import_exceptions import ValidationError, EntityNotFoundError


class SchoolImportStrategy(BaseImportStrategy):
    """School import strategy"""

    # Column mapping (supports multiple aliases)
    COLUMN_MAPPING = {
        # Region name
        "区域名称": "region_name",
        "市(区)": "region_name",
        "区域": "region_name",
        "市": "region_name",
        "区": "region_name",
        # School name
        "学校名称": "school_name",
        "学校": "school_name",
        # School code
        "学校代码": "school_code",
        "代码": "school_code",
        # School type
        "学校类型": "school_type",
        "类型": "school_type",
        # Address
        "地址": "address",
        "学校地址": "address",
        # Phone
        "联系电话": "phone",
        "电话": "phone",
        "联系方式": "phone",
        # Email
        "邮箱": "email",
        "Email": "email",
        "email": "email",
        # Principal
        "校长": "principal",
        "校长姓名": "principal",
    }

    REQUIRED_COLUMNS = ["region_name", "school_name"]

    def get_column_mapping(self) -> Dict[str, str]:
        """Return Excel column name to field name mapping"""
        return self.COLUMN_MAPPING

    def get_required_columns(self) -> List[str]:
        """Return list of required field names"""
        return self.REQUIRED_COLUMNS

    async def validate_record(
        self,
        db: AsyncSession,
        record: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate school record

        Args:
            db: Database session
            record: Raw record from Excel
            context: Import context (auto_create_region)

        Returns:
            (is_valid, error_message, validated_data)
        """
        # Check required fields
        region_name = record.get("region_name")
        if not region_name:
            raise ValidationError(
                "区域名称不能为空",
                row_number=record.get("row_number"),
                field="region_name"
            )

        school_name = record.get("school_name")
        if not school_name:
            raise ValidationError(
                "学校名称不能为空",
                row_number=record.get("row_number"),
                field="school_name"
            )

        # Return validated data
        return True, None, {
            "region_name": region_name,
            "school_name": school_name,
            "school_code": record.get("school_code"),
            "school_type": record.get("school_type"),
            "address": record.get("address"),
            "phone": record.get("phone"),
            "email": record.get("email"),
            "principal": record.get("principal"),
            "row_number": record.get("row_number")
        }

    async def import_record(
        self,
        db: AsyncSession,
        validated_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import school record

        Args:
            db: Database session
            validated_data: Validated school data
            context: Import context (auto_create_region)

        Returns:
            Dict with status information
        """
        auto_create_region = context.get("auto_create_region", True)
        region_name = validated_data["region_name"]

        # Find or create region (using cache)
        cache_key = f"region:{region_name}"

        if cache_key in self._cache:
            region = self._cache[cache_key]
            created_region = False
        else:
            region = await self._find_or_create_region(
                db, region_name, auto_create_region
            )

            if not region:
                raise EntityNotFoundError(
                    f"区域 '{region_name}' 不存在且不允许自动创建",
                    row_number=validated_data.get("row_number"),
                    field="region_name"
                )

            # Check if region was just created
            created_region = region.id is None  # Will be set after first flush

            self._cache[cache_key] = region

        # Find or create school
        school, operation = await self._find_or_create_school(
            db, validated_data, int(region.id)
        )

        return {
            "status": operation,
            "id": int(school.id),  # type: ignore
            "type": "school",
            "created_region": 1 if created_region else 0
        }

    async def _find_or_create_region(
        self,
        db: AsyncSession,
        region_name: str,
        auto_create: bool = True
    ) -> Optional[Region]:
        """
        Find or create region

        Args:
            db: Database session
            region_name: Region name
            auto_create: Whether to auto-create if not exists

        Returns:
            Region object, or None if not found and auto_create=False
        """
        # 1. Exact match
        result = await db.execute(
            select(Region).where(Region.name == region_name)
        )
        region = result.scalar_one_or_none()
        if region:
            return region

        # 2. Fuzzy match
        result = await db.execute(
            select(Region).where(Region.name.ilike(f"%{region_name}%"))
        )
        region = result.scalar_one_or_none()
        if region:
            return region

        # 3. Auto-create
        if auto_create:
            # Generate unique code
            region_code = await self._generate_region_code(region_name, db)

            # Infer level
            level = self._infer_region_level(region_name)

            region = Region(
                name=region_name,
                code=region_code,
                level=level,
                is_active=True
            )
            db.add(region)
            await db.flush()
            return region

        return None

    async def _find_or_create_school(
        self,
        db: AsyncSession,
        school_data: Dict[str, Any],
        region_id: int
    ) -> Tuple[Optional[School], str]:
        """
        Find or create school

        Args:
            db: Database session
            school_data: School data dict
            region_id: Region ID

        Returns:
            (School object, operation type: 'created'/'updated'/'skipped')
        """
        school_name = school_data["school_name"]
        school_code = school_data.get("school_code")

        # 1. Match by school code
        if school_code:
            result = await db.execute(
                select(School).where(School.code == school_code)
            )
            school = result.scalar_one_or_none()
            if school:
                # Update optional fields
                updated = False
                for field in ["school_type", "address", "phone", "email", "principal"]:
                    if field in school_data and school_data[field]:
                        setattr(school, field, school_data[field])
                        updated = True
                if updated:
                    await db.flush()
                    return school, "updated"
                return school, "skipped"

        # 2. Match by name + region
        result = await db.execute(
            select(School).where(
                School.name == school_name,
                School.region_id == region_id
            )
        )
        school = result.scalar_one_or_none()
        if school:
            # Update optional fields
            updated = False
            for field in ["school_type", "address", "phone", "email", "principal"]:
                if field in school_data and school_data[field]:
                    setattr(school, field, school_data[field])
                    updated = True
            if updated:
                await db.flush()
                return school, "updated"
            return school, "skipped"

        # 3. Create new school
        # Generate school code if not provided
        if not school_code:
            school_code = await self._generate_school_code(
                school_name, region_id, db
            )

        # Infer school type if not provided
        school_type = school_data.get("school_type")
        if not school_type:
            school_type = "高中"  # Default

        school = School(
            name=school_name,
            code=school_code,
            region_id=region_id,
            school_type=school_type,
            address=school_data.get("address"),
            phone=school_data.get("phone"),
            email=school_data.get("email"),
            principal=school_data.get("principal"),
            is_active=True
        )
        db.add(school)
        await db.flush()
        return school, "created"

    async def _generate_region_code(
        self,
        region_name: str,
        db: AsyncSession
    ) -> str:
        """Generate unique region code"""
        # Use name hash + timestamp
        name_hash = hashlib.md5(region_name.encode()).hexdigest()[:8]
        timestamp = str(int(datetime.now().timestamp()))[-6:]
        code = f"REG_{name_hash}_{timestamp}"

        # Check if exists, append counter if needed
        counter = 1
        while True:
            result = await db.execute(select(Region).where(Region.code == code))
            if not result.scalar_one_or_none():
                break
            code = f"REG_{name_hash}_{timestamp}_{counter}"
            counter += 1

        return code

    def _infer_region_level(self, region_name: str) -> int:
        """Infer region level from name"""
        if "省" in region_name:
            return 1
        elif "市" in region_name:
            return 2
        elif "区" in region_name or "县" in region_name:
            return 3
        else:
            return 3  # Default to district level

    async def _generate_school_code(
        self,
        school_name: str,
        region_id: int,
        db: AsyncSession
    ) -> str:
        """Generate unique school code"""
        # Get region code
        result = await db.execute(select(Region).where(Region.id == region_id))
        region = result.scalar_one_or_none()
        region_code = region.code if region else "REG"

        # Use region code + school name hash
        name_hash = hashlib.md5(school_name.encode()).hexdigest()[:6]
        timestamp = str(int(datetime.now().timestamp()))[-4:]
        code = f"{region_code}_{name_hash}_{timestamp}"

        # Check if exists
        counter = 1
        while True:
            result = await db.execute(select(School).where(School.code == code))
            if not result.scalar_one_or_none():
                break
            code = f"{region_code}_{name_hash}_{timestamp}_{counter}"
            counter += 1

        return code

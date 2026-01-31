"""
Unified classroom query service - single source of truth for classroom access
"""
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Classroom, School, User, UserRole


class ClassroomQueryService:
    """
    Centralized service for querying classrooms.

    This is the ONLY service that should be used to query classrooms
    for both organizational management and lesson publication.
    Ensures consistent filtering logic across the entire application.
    """

    async def get_classrooms_for_user(
        self,
        db: AsyncSession,
        user: User,
        is_active: Optional[bool] = None,
        grade_id: Optional[int] = None,
        school_id: Optional[int] = None,
        region_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[Classroom]:
        """
        Get classrooms accessible to the user based on their role.

        Args:
            db: Database session
            user: The user making the request
            is_active: Filter by active status
            grade_id: Filter by grade
            school_id: Filter by school
            region_id: Filter by region (requires JOIN with School)
            search: Search in classroom name, code, or school name

        Returns:
            List of Classroom objects
        """
        # Build query with School JOIN (needed for region filtering and search)
        query = select(Classroom).join(School)

        # Apply role-based filtering
        role_value = user.role.value if hasattr(user.role, "value") else user.role

        if role_value == UserRole.TEACHER.value:
            # Teachers can only see classrooms from their school
            if user.school_id is None:
                return []  # Teacher not assigned to a school
            query = query.where(Classroom.school_id == user.school_id)

        elif role_value == UserRole.DISTRICT_ADMIN.value:
            # District admins see classrooms from their region
            if user.region_id is not None:
                query = query.where(School.region_id == user.region_id)
            # If no region_id set, return empty (or could return all)

        elif role_value == UserRole.SCHOOL_ADMIN.value:
            # School admins see classrooms from their school only
            if user.school_id is not None:
                query = query.where(School.id == user.school_id)
            else:
                return []  # School admin not assigned to a school

        # ADMIN role: no filtering (can see all classrooms)

        # Apply additional filters
        if is_active is not None:
            query = query.where(Classroom.is_active == is_active)

        if grade_id is not None:
            query = query.where(Classroom.grade_id == grade_id)

        if school_id is not None:
            query = query.where(Classroom.school_id == school_id)

        if region_id is not None:
            query = query.where(School.region_id == region_id)

        if search:
            # Search in classroom name, code, description, and school name
            search_filter = or_(
                Classroom.name.ilike(f"%{search}%"),
                Classroom.code.ilike(f"%{search}%"),
                Classroom.description.ilike(f"%{search}%"),
                School.name.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Execute query
        result = await db.execute(query.order_by(Classroom.grade_id, Classroom.name))
        return list(result.scalars().all())

    async def get_classroom_by_id(
        self,
        db: AsyncSession,
        classroom_id: int,
        user: User,
    ) -> Optional[Classroom]:
        """
        Get a specific classroom if the user has access to it.

        Args:
            db: Database session
            classroom_id: ID of classroom to fetch
            user: User making the request

        Returns:
            Classroom object or None if not found or no access
        """
        classrooms = await self.get_classrooms_for_user(db, user)
        for classroom in classrooms:
            if classroom.id == classroom_id:
                return classroom
        return None

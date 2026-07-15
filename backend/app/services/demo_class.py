from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.classroom_assistant import ClassroomMembership, RoleInClass
from app.models.curriculum import Grade
from app.models.organization import Classroom, Region, School
from app.models.user import User, UserRole

DEMO_SCHOOL_CODE = "DEMO"
DEMO_SCHOOL_NAME = "DEMO School"
DEMO_CLASS_NAME = "Demo Class"
DEMO_CLASS_CODE = "DEMO"
DEMO_REGION_CODE = "DEMO"
DEMO_REGION_NAME = "Demo Region"
DEMO_GRADE_NAME = "高一"
DEMO_PASSWORD = "123456"
DEMO_ACCOUNT_COUNT = 60
# NOTE: must NOT use a "*.local" (or other IANA special-use, e.g. *.test/*.invalid)
# suffix — pydantic's EmailStr (via email-validator) rejects those as reserved,
# which breaks any endpoint serializing a demo user through UserResponse (e.g. /auth/me).
DEMO_EMAIL_DOMAIN = "demo.inspireed.internal"


def demo_username(n: int) -> str:
    return f"st{n:02d}"


def demo_display_name(n: int) -> str:
    return f"ST{n:02d}"


def demo_email(n: int) -> str:
    return f"{demo_username(n)}@{DEMO_EMAIL_DOMAIN}"


def all_demo_usernames() -> list[str]:
    return [demo_username(i) for i in range(1, DEMO_ACCOUNT_COUNT + 1)]


def is_demo_username(username: str) -> bool:
    if len(username) != 4 or not username.startswith("st"):
        return False
    try:
        n = int(username[2:])
    except ValueError:
        return False
    return 1 <= n <= DEMO_ACCOUNT_COUNT


def classify_existing_user(*, username: str, school_code: str | None) -> str:
    """Return 'owned' if user belongs to DEMO school, else 'conflict'."""
    if school_code == DEMO_SCHOOL_CODE:
        return "owned"
    return "conflict"


class DemoClassService:
    """Resolve, provision, and reset the DEMO school / Demo Class fixture."""

    async def resolve_demo_school(self, db: AsyncSession) -> School | None:
        result = await db.execute(select(School).where(School.code == DEMO_SCHOOL_CODE))
        return result.scalar_one_or_none()

    async def resolve_demo_classroom(self, db: AsyncSession) -> Classroom | None:
        school = await self.resolve_demo_school(db)
        if school is None:
            return None
        result = await db.execute(
            select(Classroom).where(
                Classroom.school_id == school.id,
                Classroom.name == DEMO_CLASS_NAME,
            )
        )
        return result.scalar_one_or_none()

    async def is_demo_classroom(self, db: AsyncSession, classroom: Classroom) -> bool:
        demo_classroom = await self.resolve_demo_classroom(db)
        if demo_classroom is not None and classroom.id == demo_classroom.id:
            return True
        result = await db.execute(select(School).where(School.id == classroom.school_id))
        school = result.scalar_one_or_none()
        return school is not None and school.code == DEMO_SCHOOL_CODE

    async def get_status(self, db: AsyncSession) -> dict:
        school = await self.resolve_demo_school(db)
        classroom = await self.resolve_demo_classroom(db)

        ready_accounts = 0
        missing_usernames: list[str] = []
        if classroom is not None:
            result = await db.execute(
                select(User.username)
                .join(ClassroomMembership, ClassroomMembership.user_id == User.id)
                .where(
                    User.username.in_(all_demo_usernames()),
                    ClassroomMembership.classroom_id == classroom.id,
                    ClassroomMembership.is_active == True,  # noqa: E712
                )
            )
            existing_usernames = set(result.scalars().all())
            ready_accounts = len(existing_usernames)
            missing_usernames = [
                username for username in all_demo_usernames() if username not in existing_usernames
            ]
        else:
            missing_usernames = list(all_demo_usernames())

        return {
            "school_ready": school is not None,
            "classroom_ready": classroom is not None,
            "school_id": school.id if school is not None else None,
            "classroom_id": classroom.id if classroom is not None else None,
            "school_name": DEMO_SCHOOL_NAME,
            "classroom_name": DEMO_CLASS_NAME,
            "target_accounts": DEMO_ACCOUNT_COUNT,
            "ready_accounts": ready_accounts,
            "missing_usernames": missing_usernames,
            "account_rule": "st01–st60 / password 123456",
        }

    async def _ensure_region(self, db: AsyncSession) -> Region:
        result = await db.execute(select(Region).where(Region.code == DEMO_REGION_CODE))
        region = result.scalar_one_or_none()
        if region is None:
            region = Region(code=DEMO_REGION_CODE, name=DEMO_REGION_NAME, level=1)
            db.add(region)
            await db.flush()
        return region

    async def _ensure_school(self, db: AsyncSession) -> School:
        school = await self.resolve_demo_school(db)
        if school is None:
            region = await self._ensure_region(db)
            school = School(
                code=DEMO_SCHOOL_CODE,
                name=DEMO_SCHOOL_NAME,
                school_type="高中",
                region_id=region.id,
                is_active=True,
            )
            db.add(school)
            await db.flush()
        return school

    async def _ensure_classroom(self, db: AsyncSession, school: School, grade: Grade) -> Classroom:
        classroom = await self.resolve_demo_classroom(db)
        if classroom is None:
            classroom = Classroom(
                name=DEMO_CLASS_NAME,
                code=DEMO_CLASS_CODE,
                school_id=school.id,
                grade_id=grade.id,
                is_active=True,
                capacity=DEMO_ACCOUNT_COUNT,
            )
            db.add(classroom)
            await db.flush()
        return classroom

    async def provision(self, db: AsyncSession) -> dict:
        result = await db.execute(select(Grade).where(Grade.name == DEMO_GRADE_NAME))
        grade = result.scalar_one_or_none()
        if grade is None:
            raise ValueError("年级「高一」不存在，请先在课程体系中配置年级")

        # Scan all 60 usernames for conflicts BEFORE writing anything, so a
        # conflicting run never creates the DEMO region/school/classroom or
        # any accounts.
        usernames = all_demo_usernames()
        result = await db.execute(select(User).where(User.username.in_(usernames)))
        existing_users_by_username = {user.username: user for user in result.scalars().all()}

        school_ids = {
            user.school_id for user in existing_users_by_username.values() if user.school_id is not None
        }
        school_codes_by_id: dict[int, str | None] = {}
        if school_ids:
            result = await db.execute(select(School).where(School.id.in_(school_ids)))
            school_codes_by_id = {s.id: s.code for s in result.scalars().all()}

        conflicts: list[str] = []
        for n in range(1, DEMO_ACCOUNT_COUNT + 1):
            username = demo_username(n)
            existing = existing_users_by_username.get(username)
            if existing is None:
                continue
            school_code = school_codes_by_id.get(existing.school_id) if existing.school_id else None
            if classify_existing_user(username=username, school_code=school_code) == "conflict":
                conflicts.append(username)

        if conflicts:
            raise ValueError("用户名冲突: " + ",".join(conflicts))

        school = await self._ensure_school(db)
        classroom = await self._ensure_classroom(db, school, grade)

        created_users = 0
        skipped_users = 0
        created_memberships = 0

        for n in range(1, DEMO_ACCOUNT_COUNT + 1):
            username = demo_username(n)
            user = existing_users_by_username.get(username)
            if user is None:
                user = User(
                    email=demo_email(n),
                    username=username,
                    hashed_password=get_password_hash(DEMO_PASSWORD),
                    full_name=demo_display_name(n),
                    role=UserRole.STUDENT,
                    is_active=True,
                    school_id=school.id,
                    grade_id=grade.id,
                    classroom_id=classroom.id,
                )
                db.add(user)
                await db.flush()
                created_users += 1
            else:
                user.school_id = school.id
                user.grade_id = grade.id
                user.classroom_id = classroom.id
                await db.flush()
                skipped_users += 1

            result = await db.execute(
                select(ClassroomMembership).where(
                    ClassroomMembership.classroom_id == classroom.id,
                    ClassroomMembership.user_id == user.id,
                )
            )
            membership = result.scalar_one_or_none()
            if membership is None:
                membership = ClassroomMembership(
                    classroom_id=classroom.id,
                    user_id=user.id,
                    role_in_class=RoleInClass.STUDENT,
                    is_primary_class=True,
                    is_active=True,
                )
                db.add(membership)
                await db.flush()
                created_memberships += 1

        message = f"成功配置 DEMO 班级：新建 {created_users} 个账号，复用 {skipped_users} 个已有账号"

        return {
            "school_id": school.id,
            "classroom_id": classroom.id,
            "created_users": created_users,
            "skipped_users": skipped_users,
            "created_memberships": created_memberships,
            "conflicts": conflicts,
            "message": message,
        }

    async def reset_passwords(self, db: AsyncSession) -> dict:
        classroom = await self.resolve_demo_classroom(db)
        if classroom is None:
            raise ValueError("Demo Class 尚未创建")

        usernames = all_demo_usernames()
        result = await db.execute(
            select(User)
            .outerjoin(ClassroomMembership, ClassroomMembership.user_id == User.id)
            .where(
                User.username.in_(usernames),
                (User.classroom_id == classroom.id)
                | (ClassroomMembership.classroom_id == classroom.id),
            )
        )
        users = list(result.scalars().unique().all())

        new_hash = get_password_hash(DEMO_PASSWORD)
        for user in users:
            user.hashed_password = new_hash
        await db.flush()

        return {
            "reset_count": len(users),
            "message": f"已重置 {len(users)} 个演示账号密码",
        }

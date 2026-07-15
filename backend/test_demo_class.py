from __future__ import annotations

import unittest

from app.services.demo_class import (
    DEMO_ACCOUNT_COUNT,
    DEMO_PASSWORD,
    all_demo_usernames,
    demo_display_name,
    demo_email,
    demo_username,
    is_demo_username,
)


class DemoClassHelpersTests(unittest.TestCase):
    def test_username_padding(self) -> None:
        self.assertEqual(demo_username(1), "st01")
        self.assertEqual(demo_username(60), "st60")

    def test_display_name(self) -> None:
        self.assertEqual(demo_display_name(1), "ST01")
        self.assertEqual(demo_display_name(60), "ST60")

    def test_email(self) -> None:
        self.assertEqual(demo_email(1), "st01@demo.inspireed.local")

    def test_all_usernames_count_and_bounds(self) -> None:
        names = all_demo_usernames()
        self.assertEqual(len(names), DEMO_ACCOUNT_COUNT)
        self.assertEqual(names[0], "st01")
        self.assertEqual(names[-1], "st60")

    def test_is_demo_username(self) -> None:
        self.assertTrue(is_demo_username("st01"))
        self.assertTrue(is_demo_username("st60"))
        self.assertFalse(is_demo_username("st00"))
        self.assertFalse(is_demo_username("st61"))
        self.assertFalse(is_demo_username("student01"))

    def test_password_constant(self) -> None:
        self.assertEqual(DEMO_PASSWORD, "123456")
        self.assertGreaterEqual(len(DEMO_PASSWORD), 6)


class DemoClassServiceLogicTests(unittest.TestCase):
    def test_conflict_detection_helper(self) -> None:
        from app.services.demo_class import classify_existing_user

        # existing is demo-owned when school code DEMO
        self.assertEqual(
            classify_existing_user(username="st01", school_code="DEMO"),
            "owned",
        )
        self.assertEqual(
            classify_existing_user(username="st01", school_code="OTHER"),
            "conflict",
        )
        self.assertEqual(
            classify_existing_user(username="st01", school_code=None),
            "conflict",
        )


class DemoClassPermissionTests(unittest.TestCase):
    def test_demo_classroom_allowed_without_same_school(self) -> None:
        from app.services.demo_class import DEMO_SCHOOL_CODE
        from app.services.permission_service import teacher_may_access_demo_classroom

        self.assertTrue(
            teacher_may_access_demo_classroom(school_code=DEMO_SCHOOL_CODE)
        )
        self.assertFalse(
            teacher_may_access_demo_classroom(school_code="OTHER")
        )
        self.assertFalse(
            teacher_may_access_demo_classroom(school_code=None)
        )


if __name__ == "__main__":
    unittest.main()

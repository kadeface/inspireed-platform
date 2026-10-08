import pytest
from pydantic import ValidationError

from app.api.v1.teacher_ai_assistant import _build_context_lines
from app.schemas.assistant import AssistantContext, AssistantRequest, CourseDesignContext


def test_course_design_context_records_snapshot_identity():
    request = AssistantRequest(
        question="生成课程草案",
        topic="course_design",
        context=AssistantContext(
            course_design_context=CourseDesignContext(
                snapshot_id="math-thinking-g3-cycle-remainder-v1",
                snapshot_version="1.0.0",
                teaching_context='{"title":"周期与余数"}',
            )
        ),
    )
    lines = _build_context_lines(request)
    assert any("math-thinking-g3-cycle-remainder-v1@1.0.0" in line for line in lines)
    assert any("周期与余数" in line for line in lines)


def test_course_design_context_rejects_oversized_payload():
    with pytest.raises(ValidationError):
        CourseDesignContext(
            snapshot_id="snapshot",
            snapshot_version="1.0.0",
            teaching_context="x" * 12001,
        )

"""
数据库模型包
"""

from app.models.user import User, UserRole, StudentType
from app.models.lesson import Lesson, LessonStatus, DifficultyLevel, LessonClassroom
from app.models.cell import Cell, CellType, CognitiveLevel
from app.models.section import Section, SectionType
from app.models.logs import ExecutionLog, QARecord, ExecutionStatus
from app.models.curriculum import Subject, Grade, Course, Chapter, Resource
from app.models.exam_subjects import GradeSubjectConfig
from app.models.organization import Region, School, Classroom
from app.models.room import Room
from app.models.library_asset import LibraryAsset, LibraryAssetVersion
from app.models.favorite import Favorite
from app.models.review import Review
from app.models.learning_path import LearningPath, LearningPathLesson
from app.models.question import (
    Question,
    Answer,
    QuestionVote,
    QuestionStatus,
    AskType,
    AnswererType,
)
from app.models.activity import (
    ActivitySubmission,
    ActivitySubmissionStatus,
    PeerReview,
    PeerReviewStatus,
    ActivityStatistics,
    ActivityItemStatistic,
    FlowchartSnapshot,
    FormativeAssessment,
)
from app.models.classroom_session import (
    ClassSession,
    ClassSessionStatus,
    StudentSessionParticipation,
)
from app.models.classroom_assistant import (
    RoleInClass,
    AttendanceStatus,
    PositiveBehaviorType,
    DisciplineEventType,
    DutyRotationType,
    DutyAssignmentStatus,
    ClassroomMembership,
    AttendanceSession,
    AttendanceEntry,
    PositiveBehavior,
    DisciplineRecord,
    DutyRule,
    DutyAssignment,
)
from app.models.subject_group import (
    SubjectGroup,
    GroupMembership,
    SharedLesson,
    GroupScope,
    MemberRole,
)
from app.models.student_project import (
    StudentProject,
    ProjectStatus,
    ProjectStage,
)
from app.models.project_cell import ProjectCell
from app.models.evaluation import (
    Semester,
    Exam,
    ExamType,
    ExamStatus,
    ExamSubject,
    ExamNumberMapping,
    Score,
    ExamTotalScore,
    DailyPerformanceScore,
    EvaluationMetric,
    MetricType,
    MetricCategory,
    ValueAddedEvaluation,
    EvaluationDetail,
    ImportTask,
    ImportStatus,
)
from app.models.teacher import (
    TeacherTeachingAssignment,
    TeachingAssignmentType,
)
from app.models.teacher_position import TeacherPositionType
from app.models.exam_room import ExamRoom, ExamRoomStudent, ExamProctor

__all__ = [
    "User",
    "UserRole",
    "StudentType",
    "Lesson",
    "LessonStatus",
    "DifficultyLevel",
    "LessonClassroom",
    "Cell",
    "CellType",
    "CognitiveLevel",
    "Section",
    "SectionType",
    "ExecutionLog",
    "QARecord",
    "ExecutionStatus",
    "Subject",
    "Grade",
    "Course",
    "Chapter",
    "Resource",
    "GradeSubjectConfig",
    "LibraryAsset",
    "LibraryAssetVersion",
    "Region",
    "School",
    "Classroom",
    "Room",
    "Favorite",
    "Review",
    "LearningPath",
    "LearningPathLesson",
    "Question",
    "Answer",
    "QuestionVote",
    "QuestionStatus",
    "AskType",
    "AnswererType",
    "ActivitySubmission",
    "ActivitySubmissionStatus",
    "PeerReview",
    "PeerReviewStatus",
    "ActivityStatistics",
    "ActivityItemStatistic",
    "FlowchartSnapshot",
    "FormativeAssessment",
    "SubjectGroup",
    "GroupMembership",
    "SharedLesson",
    "GroupScope",
    "MemberRole",
    "ClassSession",
    "ClassSessionStatus",
    "StudentSessionParticipation",
    "RoleInClass",
    "AttendanceStatus",
    "PositiveBehaviorType",
    "DisciplineEventType",
    "DutyRotationType",
    "DutyAssignmentStatus",
    "ClassroomMembership",
    "AttendanceSession",
    "AttendanceEntry",
    "PositiveBehavior",
    "DisciplineRecord",
    "DutyRule",
    "DutyAssignment",
    "StudentProject",
    "ProjectStatus",
    "ProjectStage",
    "ProjectCell",
    # 增值评价系统
    "Semester",
    "Exam",
    "ExamType",
    "ExamStatus",
    "ExamSubject",
    "ExamNumberMapping",
    "Score",
    "ExamTotalScore",
    "DailyPerformanceScore",
    "EvaluationMetric",
    "MetricType",
    "MetricCategory",
    "ValueAddedEvaluation",
    "EvaluationDetail",
    "ImportTask",
    "ImportStatus",
    # 教师教学任务
    "TeacherTeachingAssignment",
    "TeachingAssignmentType",
    # 教师职务类型
    "TeacherPositionType",
    # 考场
    "ExamRoom",
    "ExamRoomStudent",
    "ExamProctor",
]

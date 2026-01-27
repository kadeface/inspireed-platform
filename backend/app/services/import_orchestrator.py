"""
Import Orchestrator

Orchestrator for coordinating import operations across different strategies.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from .import_strategies.base_strategy import BaseImportStrategy
from .import_strategies.school_import_strategy import SchoolImportStrategy
from .import_strategies.classroom_import_strategy import ClassroomImportStrategy
from .import_strategies.student_import_strategy import StudentImportStrategy
from .import_strategies.student_account_import_strategy import StudentAccountImportStrategy
from .import_strategies.teacher_import_strategy import TeacherImportStrategy
from .import_strategies.city_exam_number_import_strategy import CityExamNumberImportStrategy


logger = logging.getLogger(__name__)


class ImportOrchestrator:
    """
    Orchestrator for import operations

    Coordinates the execution of different import strategies,
    handling the workflow: parse → validate → import
    """

    def __init__(self):
        """Initialize orchestrator with strategy registry"""
        self._strategies = {
            "school": SchoolImportStrategy,
            "classroom": ClassroomImportStrategy,
            "student": StudentImportStrategy,
            "student_account": StudentAccountImportStrategy,
            "teacher": TeacherImportStrategy,
            "city_exam_number": CityExamNumberImportStrategy,
        }

    def get_strategy(self, strategy_type: str) -> BaseImportStrategy:
        """
        Get strategy instance by type

        Args:
            strategy_type: Strategy type (school, classroom, student, teacher)

        Returns:
            Strategy instance

        Raises:
            ValueError: If strategy_type is unknown
        """
        strategy_class = self._strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(
                f"Unknown strategy type: {strategy_type}. "
                f"Valid types: {list(self._strategies.keys())}"
            )
        return strategy_class()

    async def execute_import(
        self,
        db: AsyncSession,
        strategy_type: str,
        file_path: Path,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute import using specified strategy

        Args:
            db: Database session
            strategy_type: Strategy type (school, classroom, student, teacher)
            file_path: Path to Excel file
            context: Strategy-specific context parameters

        Returns:
            Import result dict with keys:
            - total: Total records processed
            - success: Successfully imported records
            - failed: Failed records
            - created: New records created
            - updated: Existing records updated
            - skipped: Records skipped (already exist)
            - errors: List of error dicts (max 100)
        """
        strategy = self.get_strategy(strategy_type)

        try:
            # Execute complete import workflow
            result = await strategy.execute_import(db, file_path, context)

            # Log summary
            logger.info(
                f"Import complete: strategy={strategy_type}, "
                f"total={result['total']}, success={result['success']}, "
                f"failed={result['failed']}, created={result['created']}, "
                f"updated={result['updated']}, skipped={result['skipped']}"
            )

            return result

        finally:
            # Clean up strategy cache
            strategy.clear_cache()

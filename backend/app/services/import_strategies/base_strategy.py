"""
Base Import Strategy

Abstract base class for all import strategies.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from ..import_base import BaseImporter, ParseError
from ..import_exceptions import ImportError, ValidationError, EntityNotFoundError


logger = logging.getLogger(__name__)


class BaseImportStrategy(ABC):
    """
    Abstract base class for import strategies

    All import strategies must inherit from this class and implement
    the abstract methods.
    """

    def __init__(self):
        """Initialize strategy with logger and cache"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cache: Dict[str, Any] = {}  # Per-import cache

    # ========== ABSTRACT METHODS ==========

    @abstractmethod
    def get_column_mapping(self) -> Dict[str, str]:
        """
        Return Excel column name to field name mapping

        Supports multiple column name aliases for the same field.

        Returns:
            Dict mapping Excel column names (Chinese) to field names
        """
        pass

    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """
        Return list of required field names

        Returns:
            List of required field names (not column names)
        """
        pass

    @abstractmethod
    async def validate_record(
        self,
        db: AsyncSession,
        record: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate a single record

        Args:
            db: Database session
            record: Raw record from Excel (with row_number)
            context: Strategy-specific context parameters

        Returns:
            Tuple of (is_valid, error_message, validated_data)

            - is_valid: True if validation passed
            - error_message: Error message if validation failed
            - validated_data: Validated and cleaned data dict

        Raises:
            ValidationError: If validation fails with specific field error
            EntityNotFoundError: If referenced entity doesn't exist
        """
        pass

    @abstractmethod
    async def import_record(
        self,
        db: AsyncSession,
        validated_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import a single validated record

        Args:
            db: Database session
            validated_data: Validated record data
            context: Strategy-specific context parameters

        Returns:
            Dict with status information:
            {
                "status": "created" | "updated" | "skipped",
                "id": entity_id,
                "type": entity_type,
                ... (additional fields)
            }

        Raises:
            ValidationError: If data validation fails during import
            EntityNotFoundError: If referenced entity doesn't exist
        """
        pass

    # ========== OVERRIDABLE METHODS ==========

    def get_batch_size(self) -> int:
        """
        Override to customize batch commit size

        Returns:
            Number of records per batch commit
        """
        return 100

    def clear_cache(self):
        """Clear the per-import cache"""
        self._cache.clear()

    # ========== CONCRETE METHODS ==========

    async def parse_excel(
        self,
        file_path: Path
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Parse Excel file using BaseImporter

        Args:
            file_path: Path to Excel file

        Returns:
            Tuple of (records, errors)

            - records: List of parsed record dicts
            - errors: List of parse error dicts

        Raises:
            ParseError: If Excel file cannot be parsed
        """
        records = []
        errors = []

        try:
            wb, ws = BaseImporter.load_worksheet(file_path)
            headers = BaseImporter.extract_headers(ws)

            column_mapping = self.get_column_mapping()
            column_indices = BaseImporter.build_column_indices(headers, column_mapping)

            required_fields = self.get_required_columns()
            BaseImporter.validate_required_columns(
                column_indices, required_fields, column_mapping
            )

            # Extract data rows
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row):  # Skip empty rows
                    continue

                try:
                    record = BaseImporter.extract_row_data(row, column_indices, row_idx)
                    records.append(record)
                except Exception as e:
                    errors.append({
                        "row": row_idx,
                        "field": None,
                        "message": f"解析行数据失败: {str(e)}"
                    })

            wb.close()
            return records, errors

        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"解析Excel文件失败: {str(e)}")

    async def validate_all_records(
        self,
        db: AsyncSession,
        records: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate all records

        Args:
            db: Database session
            records: List of raw records from Excel
            context: Strategy-specific context parameters

        Returns:
            Tuple of (validated_records, errors)

            - validated_records: List of validated record dicts
            - errors: List of validation error dicts
        """
        validated_records = []
        errors = []

        for record in records:
            try:
                is_valid, error_msg, validated_data = await self.validate_record(
                    db, record, context
                )

                if not is_valid or validated_data is None:
                    errors.append({
                        "row": record.get("row_number", "unknown"),
                        "field": None,
                        "message": error_msg or "验证失败"
                    })
                else:
                    validated_records.append(validated_data)

            except (ValidationError, EntityNotFoundError) as e:
                errors.append(e.to_dict())
            except Exception as e:
                self.logger.error(f"验证失败: {str(e)}", exc_info=True)
                errors.append({
                    "row": record.get("row_number", "unknown"),
                    "field": None,
                    "message": f"验证异常: {str(e)}"
                })

        return validated_records, errors

    async def import_all_records(
        self,
        db: AsyncSession,
        validated_records: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import all validated records with batch commits

        Args:
            db: Database session
            validated_records: List of validated records
            context: Strategy-specific context parameters

        Returns:
            Import result dict:
            {
                "total": int,
                "success": int,
                "failed": int,
                "created": int,
                "updated": int,
                "skipped": int,
                "errors": List[Dict]
            }
        """
        total = len(validated_records)
        success = 0
        failed = 0
        created = 0
        updated = 0
        skipped = 0
        errors = []

        batch_size = self.get_batch_size()

        for i, validated_data in enumerate(validated_records):
            try:
                result = await self.import_record(db, validated_data, context)

                status = result.get("status", "")
                if status == "created":
                    created += 1
                    success += 1
                elif status == "updated":
                    updated += 1
                    success += 1
                elif status == "skipped":
                    skipped += 1
                    success += 1
                else:
                    failed += 1

                # Batch commit
                if (i + 1) % batch_size == 0:
                    await db.commit()
                    self.logger.info(
                        f"Committed batch {(i // batch_size) + 1} "
                        f"({i + 1}/{total} records)"
                    )

            except (ValidationError, EntityNotFoundError) as e:
                failed += 1
                errors.append(e.to_dict())
            except Exception as e:
                failed += 1
                self.logger.error(f"导入失败: {str(e)}", exc_info=True)
                errors.append({
                    "row": validated_data.get("row_number", "unknown"),
                    "field": None,
                    "message": f"导入异常: {str(e)}"
                })

        # Final commit for remaining records
        try:
            await db.commit()
        except Exception as e:
            self.logger.error(f"Final commit failed: {str(e)}", exc_info=True)
            # Add batch commit error to errors list
            errors.append({
                "row": 0,
                "field": None,
                "message": f"提交数据失败: {str(e)}"
            })
            failed = total - success  # Assume all uncommitted records failed

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "errors": errors
        }

    async def execute_import(
        self,
        db: AsyncSession,
        file_path: Path,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute complete import workflow: parse → validate → import

        Args:
            db: Database session
            file_path: Path to Excel file
            context: Strategy-specific context parameters

        Returns:
            Import result dict
        """
        # Phase 1: Parse Excel
        self.logger.info(f"Parsing Excel file: {file_path}")
        records, parse_errors = await self.parse_excel(file_path)

        if parse_errors:
            self.logger.warning(f"Parse errors: {len(parse_errors)}")
            # If there are parse errors, return early with partial results
            return {
                "total": len(records) + len(parse_errors),
                "success": 0,
                "failed": len(parse_errors),
                "created": 0,
                "updated": 0,
                "skipped": 0,
                "errors": parse_errors
            }

        # Phase 2: Validate all records
        self.logger.info(f"Validating {len(records)} records")
        validated_records, validation_errors = await self.validate_all_records(
            db, records, context
        )

        # If all records failed validation, return early
        if not validated_records:
            self.logger.error("All records failed validation")
            return {
                "total": len(records),
                "success": 0,
                "failed": len(validation_errors),
                "created": 0,
                "updated": 0,
                "skipped": 0,
                "errors": validation_errors[:100]
            }

        # Phase 3: Import validated records
        self.logger.info(f"Importing {len(validated_records)} validated records")
        result = await self.import_all_records(db, validated_records, context)

        # Combine parse and validation errors
        all_errors = parse_errors + validation_errors + result["errors"]
        result["errors"] = all_errors[:100]  # Limit to first 100 errors

        self.logger.info(
            f"Import complete: {result['success']} success, "
            f"{result['failed']} failed"
        )

        return result

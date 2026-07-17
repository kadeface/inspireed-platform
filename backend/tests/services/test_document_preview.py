from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.services.document_preview import build_preview_payload


@pytest.fixture()
def resources_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "storage"
    resources = root / "resources"
    resources.mkdir(parents=True)
    monkeypatch.setattr("app.core.config.settings.UPLOAD_DIR", str(root))
    return resources


@pytest.mark.asyncio
async def test_pdf_direct(resources_dir: Path) -> None:
    (resources_dir / "a.pdf").write_bytes(b"%PDF")
    payload = await build_preview_payload(file_ref="a.pdf", title="A")
    assert payload["can_preview_directly"] is True
    assert payload["converted_to_pdf"] is False
    assert payload["file_type"] == "pdf"
    assert payload["preview_url"] == "/uploads/resources/a.pdf"


@pytest.mark.asyncio
async def test_office_converted(resources_dir: Path) -> None:
    (resources_dir / "a.docx").write_bytes(b"x")
    with patch(
        "app.services.document_preview.office_converter_service.get_converted_pdf_url",
        new_callable=AsyncMock,
        return_value="/uploads/resources/a_converted.pdf",
    ):
        payload = await build_preview_payload(file_ref="a.docx")
    assert payload["converted_to_pdf"] is True
    assert payload["preview_url"] == "/uploads/resources/a_converted.pdf"
    assert payload["conversion_error"] is None


@pytest.mark.asyncio
async def test_office_conversion_failure(resources_dir: Path) -> None:
    (resources_dir / "a.xlsx").write_bytes(b"x")
    with patch(
        "app.services.document_preview.office_converter_service.get_converted_pdf_url",
        new_callable=AsyncMock,
        return_value=None,
    ):
        payload = await build_preview_payload(file_ref="a.xlsx")
    assert payload["converted_to_pdf"] is False
    assert payload["conversion_error"]


@pytest.mark.asyncio
async def test_missing_file_office_reports_error(resources_dir: Path) -> None:
    payload = await build_preview_payload(file_ref="missing.docx")
    assert payload["converted_to_pdf"] is False
    assert payload["conversion_error"]

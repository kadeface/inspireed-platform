from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.services.office_converter import (
    OFFICE_EXTENSIONS,
    OfficeConverterService,
    resolve_resource_path,
    converted_pdf_path,
)
from app.utils.resource_url import url_to_filename


@pytest.fixture()
def resources_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "storage"
    resources = root / "resources"
    resources.mkdir(parents=True)
    monkeypatch.setattr("app.core.config.settings.UPLOAD_DIR", str(root))
    return resources


def test_office_extensions_include_excel() -> None:
    assert "xlsx" in OFFICE_EXTENSIONS
    assert "xls" in OFFICE_EXTENSIONS


def test_resolve_bare_filename(resources_dir: Path) -> None:
    f = resources_dir / "abc.docx"
    f.write_bytes(b"x")
    assert resolve_resource_path("abc.docx") == f.resolve()


def test_resolve_uploads_prefix(resources_dir: Path) -> None:
    f = resources_dir / "abc.docx"
    f.write_bytes(b"x")
    assert resolve_resource_path("/uploads/resources/abc.docx") == f.resolve()


def test_reject_path_traversal(resources_dir: Path) -> None:
    assert resolve_resource_path("../etc/passwd") is None
    assert resolve_resource_path("/uploads/resources/../../etc/passwd") is None


def test_reject_external_url(resources_dir: Path) -> None:
    assert resolve_resource_path("https://evil.example/a.docx") is None


def test_reject_external_url_with_uploads_path(resources_dir: Path) -> None:
    f = resources_dir / "a.docx"
    f.write_bytes(b"x")
    assert resolve_resource_path("https://evil.example/uploads/resources/a.docx") is None


def test_basename_from_absolute_url_still_resolves(resources_dir: Path) -> None:
    (resources_dir / "a.docx").write_bytes(b"x")
    ref = url_to_filename("http://evil.example/uploads/resources/a.docx")
    assert ref == "a.docx"
    assert resolve_resource_path(ref) is not None


def test_resolve_uploads_prefix_no_leading_slash(resources_dir: Path) -> None:
    f = resources_dir / "abc.docx"
    f.write_bytes(b"x")
    assert resolve_resource_path("uploads/resources/abc.docx") == f.resolve()


def test_converted_pdf_path_name(resources_dir: Path) -> None:
    src = resources_dir / "note.docx"
    assert converted_pdf_path(src).name == "note_converted.pdf"


@pytest.mark.asyncio
async def test_get_converted_pdf_url_uses_cache(resources_dir: Path) -> None:
    src = resources_dir / "note.docx"
    src.write_bytes(b"x")
    cache = resources_dir / "note_converted.pdf"
    cache.write_bytes(b"%PDF")
    svc = OfficeConverterService()
    with patch.object(svc, "convert_to_pdf", new_callable=AsyncMock) as convert:
        url = await svc.get_converted_pdf_url("note.docx")
    assert url == "/uploads/resources/note_converted.pdf"
    convert.assert_not_called()


@pytest.mark.asyncio
async def test_convert_doc_calls_libreoffice(resources_dir: Path) -> None:
    src = resources_dir / "legacy.doc"
    src.write_bytes(b"x")
    svc = OfficeConverterService()
    out = resources_dir / "legacy_converted.pdf"
    with patch.object(svc, "_has_libreoffice", new_callable=AsyncMock, return_value=True):
        with patch.object(
            svc,
            "_convert_with_libreoffice",
            new_callable=AsyncMock,
            return_value={
                "success": True,
                "error": None,
                "pdf_url": str(out),
                "method": "libreoffice",
            },
        ) as lo:
            result = await svc.convert_to_pdf(str(src), str(out))
    assert result["success"] is True
    lo.assert_awaited()


@pytest.mark.asyncio
async def test_convert_xlsx_fails_without_libreoffice(resources_dir: Path) -> None:
    src = resources_dir / "sheet.xlsx"
    src.write_bytes(b"x")
    svc = OfficeConverterService()
    out = resources_dir / "sheet_converted.pdf"
    with patch.object(svc, "_has_libreoffice", new_callable=AsyncMock, return_value=False):
        result = await svc.convert_to_pdf(str(src), str(out))
    assert result["success"] is False
    assert "LibreOffice" in result["error"]


@pytest.mark.asyncio
async def test_convert_xlsx_calls_libreoffice(resources_dir: Path) -> None:
    src = resources_dir / "sheet.xlsx"
    src.write_bytes(b"x")
    svc = OfficeConverterService()
    out = resources_dir / "sheet_converted.pdf"
    with patch.object(svc, "_has_libreoffice", new_callable=AsyncMock, return_value=True):
        with patch.object(
            svc,
            "_convert_with_libreoffice",
            new_callable=AsyncMock,
            return_value={
                "success": True,
                "error": None,
                "pdf_url": str(out),
                "method": "libreoffice",
            },
        ) as lo:
            result = await svc.convert_to_pdf(str(src), str(out))
    assert result["success"] is True
    lo.assert_awaited()

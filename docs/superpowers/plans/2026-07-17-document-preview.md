# Document Online Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify in-app preview for PDF/images/Word/PPT/Excel across curriculum resources, TipTap attachments, and the teacher library by fixing LibreOffice→PDF conversion (no new preview microservice).

**Architecture:** Harden `OfficeConverterService` to resolve bare filenames and `/uploads/resources/...` into `storage/resources/`, convert `doc/docx/ppt/pptx/xls/xlsx` via LibreOffice with `*_converted.pdf` cache, expose three thin preview APIs that share one response shape, and drive a single frontend preview flow (iframe PDF / img) from those APIs.

**Tech Stack:** FastAPI, existing `office_converter.py` + LibreOffice CLI, Vue 3 + TypeScript, Element Plus patterns already in modals, pytest.

## Global Constraints

- Quality: good enough (Office → PDF); no online editing
- No kkFileView / OnlyOffice / new JVM service
- Office extensions (v1): `doc`, `docx`, `ppt`, `pptx`, `xls`, `xlsx` only
- UX: sync wait with spinner; cache second open
- On preview failure: always offer download when allowed
- Remove Office Online / Google Viewer as primary fallback
- Runtime must have `libreoffice` or `soffice` installed
- `docs/` is gitignored — use `git add -f` for plan/spec commits

**Spec:** `docs/superpowers/specs/2026-07-17-document-preview-design.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `backend/app/services/office_converter.py` | Path resolve, LibreOffice convert, cache, Excel, delete helper |
| `backend/app/services/document_preview.py` | Shared `build_preview_payload(...)` used by all preview APIs |
| `backend/app/api/v1/resources.py` | Extend `GET /resources/{id}/preview` (Excel + normalize URL) |
| `backend/app/api/v1/upload.py` | Add `POST /upload/preview` (file URL → preview) |
| `backend/app/api/v1/library_assets.py` | Add `GET /library/assets/{id}/preview` |
| `backend/tests/services/test_office_converter.py` | Converter unit tests (path, cache, Excel, SSRF reject) |
| `backend/tests/services/test_document_preview.py` | Shared preview payload tests |
| `frontend/src/types/documentPreview.ts` | Shared preview response type |
| `frontend/src/services/documentPreview.ts` | API clients for three preview endpoints |
| `frontend/src/composables/useDocumentPreview.ts` | Load + normalize preview URL for UI |
| `frontend/src/components/Resource/DocumentPreviewModal.vue` | Generic modal: loading / error / PDF iframe / image |
| `frontend/src/components/Resource/ResourcePreviewModal.vue` | Curriculum entry: PDF when converted; drop external viewers |
| `frontend/src/components/Library/AssetDetailModal.vue` | Call library preview for document/pdf |
| `frontend/src/components/Editor/TipTapEditor.vue` | Show「查看」for Office; open DocumentPreviewModal |

---

### Task 1: OfficeConverter path resolve + Excel + LibreOffice binary

**Files:**
- Modify: `backend/app/services/office_converter.py`
- Test: `backend/tests/services/test_office_converter.py`

**Interfaces:**
- Produces:
  - `OFFICE_EXTENSIONS = frozenset({"doc", "docx", "ppt", "pptx", "xls", "xlsx"})`
  - `DIRECT_PREVIEW_EXTENSIONS = frozenset({"pdf", "jpg", "jpeg", "png", "gif", "webp", "svg"})`
  - `resolve_resource_path(file_ref: str) -> Path | None`
  - `converted_pdf_path(source: Path) -> Path`
  - `get_converted_pdf_url(original_file_ref: str) -> str | None` → `/uploads/resources/{stem}_converted.pdf`
  - `delete_converted_pdf(file_ref: str) -> None`
  - Excel via LibreOffice only (no content-extraction fallback for xls/xlsx)

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/services/test_office_converter.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/services/test_office_converter.py -v`

Expected: FAIL (imports / symbols missing)

- [ ] **Step 3: Implement minimal converter changes**

Update `office_converter.py` with:

```python
from pathlib import Path
from app.core.config import settings
from app.utils.resource_url import url_to_filename

OFFICE_EXTENSIONS = frozenset({"doc", "docx", "ppt", "pptx", "xls", "xlsx"})
DIRECT_PREVIEW_EXTENSIONS = frozenset({"pdf", "jpg", "jpeg", "png", "gif", "webp", "svg"})


def _resources_root() -> Path:
    return Path(settings.UPLOAD_DIR).resolve() / "resources"


def resolve_resource_path(file_ref: str) -> Path | None:
    if not file_ref:
        return None
    if file_ref.startswith(("http://", "https://", "ftp://")):
        if "/uploads/resources/" not in file_ref:
            return None
        name = url_to_filename(file_ref)
    else:
        name = url_to_filename(file_ref)
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        return None
    root = _resources_root()
    candidate = (root / name).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate


def converted_pdf_path(source: Path) -> Path:
    return source.with_name(f"{source.stem}_converted.pdf")
```

In `OfficeConverterService`:

- `convert_to_pdf`: add `.xls`/`.xlsx` branch that requires LibreOffice; keep docx/ppt content-extraction fallback when LO missing.
- `_has_libreoffice`: try `libreoffice` then `soffice`; store chosen binary on `self._lo_binary`.
- `_convert_with_libreoffice`: use `getattr(self, "_lo_binary", "libreoffice")`.
- Rewrite `get_converted_pdf_url` to use `resolve_resource_path` + `converted_pdf_path` + cache check.
- Add `delete_converted_pdf(file_ref: str) -> None`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/services/test_office_converter.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/office_converter.py backend/tests/services/test_office_converter.py
git commit -m "fix(preview): resolve storage paths and convert Excel via LibreOffice"
```

---

### Task 2: Shared `build_preview_payload` + curriculum preview API

**Files:**
- Create: `backend/app/services/document_preview.py`
- Modify: `backend/app/api/v1/resources.py` (handler `get_resource_preview`)
- Test: `backend/tests/services/test_document_preview.py`

**Interfaces:**
- Consumes: `resolve_resource_path`, `OFFICE_EXTENSIONS`, `DIRECT_PREVIEW_EXTENSIONS`, `office_converter_service.get_converted_pdf_url`
- Produces: `async def build_preview_payload(*, file_ref: str, title: str | None = None, file_size: int | None = None, page_count: int | None = None, extra: dict | None = None) -> dict`
- Response always includes: `preview_url`, `file_url`, `file_type`, `can_preview_directly`, `converted_to_pdf`, `conversion_error`

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/services/test_document_preview.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/services/test_document_preview.py -v`

Expected: FAIL (module missing)

- [ ] **Step 3: Implement service + wire resources**

```python
# backend/app/services/document_preview.py
from __future__ import annotations

from typing import Any, Optional

from app.services.office_converter import (
    DIRECT_PREVIEW_EXTENSIONS,
    OFFICE_EXTENSIONS,
    office_converter_service,
)
from app.utils.resource_url import url_to_filename


def _ext(file_ref: str) -> str:
    name = url_to_filename(file_ref) or ""
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def _public_url(file_ref: str) -> str:
    return f"/uploads/resources/{url_to_filename(file_ref)}"


async def build_preview_payload(
    *,
    file_ref: str,
    title: Optional[str] = None,
    file_size: Optional[int] = None,
    page_count: Optional[int] = None,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    ext = _ext(file_ref)
    public = _public_url(file_ref)
    payload: dict[str, Any] = {
        "title": title,
        "file_url": public,
        "file_type": ext,
        "file_size": file_size,
        "page_count": page_count,
        "can_preview_directly": ext in DIRECT_PREVIEW_EXTENSIONS,
        "preview_url": public,
        "converted_to_pdf": False,
        "conversion_error": None,
    }
    if extra:
        payload.update(extra)

    if ext in OFFICE_EXTENSIONS:
        try:
            converted = await office_converter_service.get_converted_pdf_url(file_ref)
            if converted:
                payload["preview_url"] = converted
                payload["converted_to_pdf"] = True
            else:
                payload["conversion_error"] = "无法转换文档为PDF格式，请下载原文件查看"
        except Exception as e:
            payload["conversion_error"] = f"转换过程中出现错误: {e}"
    elif ext not in DIRECT_PREVIEW_EXTENSIONS:
        payload["conversion_error"] = (
            f"不支持在线预览的文件类型: .{ext}" if ext else "不支持在线预览"
        )

    return payload
```

Replace body of `get_resource_preview` in `resources.py`:

```python
from app.services.document_preview import build_preview_payload

payload = await build_preview_payload(
    file_ref=cast(str, resource.file_url),
    title=cast(Optional[str], resource.title),
    file_size=cast(Optional[int], resource.file_size),
    page_count=cast(Optional[int], resource.page_count),
    extra={"resource_id": resource.id},
)
return payload
```

- [ ] **Step 4: Run tests**

Run: `cd backend && python -m pytest tests/services/test_document_preview.py tests/services/test_office_converter.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/document_preview.py backend/app/api/v1/resources.py backend/tests/services/test_document_preview.py
git commit -m "feat(preview): share preview payload builder for curriculum resources"
```

---

### Task 3: `POST /upload/preview`

**Files:**
- Modify: `backend/app/api/v1/upload.py`
- Test: append to `backend/tests/services/test_document_preview.py`

**Interfaces:**
- Consumes: `build_preview_payload`, `resolve_resource_path`, `get_current_active_user`
- Produces: `POST /api/v1/upload/preview` body `{ "file_url": string }` → preview payload

- [ ] **Step 1: Add failing coverage for missing files**

```python
@pytest.mark.asyncio
async def test_missing_file_office_reports_error(resources_dir: Path) -> None:
    payload = await build_preview_payload(file_ref="missing.docx")
    assert payload["converted_to_pdf"] is False
    assert payload["conversion_error"]
```

- [ ] **Step 2: Implement endpoint**

```python
# backend/app/api/v1/upload.py
class PreviewRequest(BaseModel):
    file_url: str


@router.post("/preview")
async def preview_uploaded_file(
    body: PreviewRequest,
    current_user: User = Depends(get_current_active_user),
):
    from app.services.document_preview import build_preview_payload
    from app.services.office_converter import resolve_resource_path

    if resolve_resource_path(body.file_url) is None:
        raise HTTPException(404, "文件不可用或不允许预览")
    return await build_preview_payload(file_ref=body.file_url)
```

Mounted at `/upload` → full path `/api/v1/upload/preview`. Keep `POST /upload/` for uploads.

- [ ] **Step 3: Run tests**

Run: `cd backend && python -m pytest tests/services/test_document_preview.py -v`

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/upload.py backend/tests/services/test_document_preview.py
git commit -m "feat(preview): add POST /upload/preview for attachment URLs"
```

---

### Task 4: Library preview API + converted PDF cleanup

**Files:**
- Modify: `backend/app/api/v1/library_assets.py`
- Modify: `backend/app/api/v1/resources.py` (delete path)

**Interfaces:**
- Consumes: same lookup/visibility as `get_library_asset`, `build_preview_payload`, `office_converter_service.delete_converted_pdf`
- Produces: `GET /api/v1/library/assets/{id}/preview`

- [ ] **Step 1: Add preview route**

Mirror auth deps from neighboring `get_library_asset` exactly:

```python
@router.get("/{asset_id}/preview")
async def get_library_asset_preview(
    asset_id: int,
    # same Depends as get_library_asset
):
    asset = ...  # same fetch + 404/403 as get_library_asset
    file_ref = cast(str, asset.public_url or asset.storage_key)
    from app.services.document_preview import build_preview_payload
    return await build_preview_payload(
        file_ref=file_ref,
        title=cast(Optional[str], asset.title),
        file_size=cast(Optional[int], asset.size_bytes),
        extra={"asset_id": asset.id},
    )
```

- [ ] **Step 2: Cleanup on delete / replace**

Wherever library or curriculum deletes the stored file, add:

```python
from app.services.office_converter import office_converter_service
office_converter_service.delete_converted_pdf(old_file_ref)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/library_assets.py backend/app/api/v1/resources.py
git commit -m "feat(preview): add library asset preview and cleanup converted PDFs"
```

---

### Task 5: Frontend types, service, composable

**Files:**
- Create: `frontend/src/types/documentPreview.ts`
- Create: `frontend/src/services/documentPreview.ts`
- Create: `frontend/src/composables/useDocumentPreview.ts`

**Interfaces:**
- `DocumentPreviewInfo`
- `documentPreviewService.getResourcePreview` / `getLibraryPreview` / `getUploadPreview`
- `useDocumentPreview()` → `{ loading, error, info, previewAbsoluteUrl, displayKind, loadFromResource, loadFromLibrary, loadFromFileUrl, reset }`

- [ ] **Step 1: Create files**

```typescript
// frontend/src/types/documentPreview.ts
export interface DocumentPreviewInfo {
  title?: string | null
  file_url: string
  file_type: string
  file_size?: number | null
  page_count?: number | null
  can_preview_directly: boolean
  preview_url: string
  converted_to_pdf: boolean
  conversion_error?: string | null
  resource_id?: number
  asset_id?: number
}
```

```typescript
// frontend/src/services/documentPreview.ts
import api from './api'
import type { DocumentPreviewInfo } from '../types/documentPreview'

export const documentPreviewService = {
  getResourcePreview(resourceId: number) {
    return api.get<DocumentPreviewInfo>(`/resources/${resourceId}/preview`)
  },
  getLibraryPreview(assetId: number) {
    return api.get<DocumentPreviewInfo>(`/library/assets/${assetId}/preview`)
  },
  getUploadPreview(fileUrl: string) {
    return api.post<DocumentPreviewInfo>('/upload/preview', { file_url: fileUrl })
  },
}
```

```typescript
// frontend/src/composables/useDocumentPreview.ts
import { computed, ref } from 'vue'
import { documentPreviewService } from '@/services/documentPreview'
import type { DocumentPreviewInfo } from '@/types/documentPreview'
import { getServerBaseUrl } from '@/utils/url'

export function useDocumentPreview() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const info = ref<DocumentPreviewInfo | null>(null)

  const previewAbsoluteUrl = computed(() => {
    let url = info.value?.preview_url
    if (!url) return null
    if (url.startsWith('/uploads/')) url = `${getServerBaseUrl()}${url}`
    return url
  })

  const displayKind = computed(() => {
    if (!info.value) return 'none'
    if (info.value.converted_to_pdf || info.value.file_type === 'pdf') return 'pdf'
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(info.value.file_type)) return 'image'
    return 'unsupported'
  })

  async function run(loader: () => Promise<DocumentPreviewInfo>) {
    loading.value = true
    error.value = null
    info.value = null
    try {
      const data = await loader()
      info.value = data
      if (data.conversion_error && !data.converted_to_pdf && !data.can_preview_directly) {
        error.value = data.conversion_error
      }
    } catch (e: any) {
      error.value = e?.message || '加载预览失败'
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    info,
    previewAbsoluteUrl,
    displayKind,
    loadFromResource: (id: number) => run(() => documentPreviewService.getResourcePreview(id)),
    loadFromLibrary: (id: number) => run(() => documentPreviewService.getLibraryPreview(id)),
    loadFromFileUrl: (url: string) => run(() => documentPreviewService.getUploadPreview(url)),
    reset: () => {
      loading.value = false
      error.value = null
      info.value = null
    },
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types/documentPreview.ts frontend/src/services/documentPreview.ts frontend/src/composables/useDocumentPreview.ts
git commit -m "feat(preview): add frontend preview client and composable"
```

---

### Task 6: `DocumentPreviewModal` + simplify `ResourcePreviewModal`

**Files:**
- Create: `frontend/src/components/Resource/DocumentPreviewModal.vue`
- Modify: `frontend/src/components/Resource/ResourcePreviewModal.vue`

**Interfaces:**
- Props: `modelValue`, `mode: 'resource' | 'library' | 'file'`, `resourceId?`, `assetId?`, `fileUrl?`, `title?`
- Office success → PDF iframe; remove Office Online / Google Viewer UI

- [ ] **Step 1: Create DocumentPreviewModal**

Use `useDocumentPreview`. On open, call `loadFromResource` / `loadFromLibrary` / `loadFromFileUrl` based on `mode`. Template: loading spinner (with Office hint), error + retry + download, PDF iframe, image. Copy overlay/container CSS from `ResourcePreviewModal` (no visual redesign).

- [ ] **Step 2: Slim ResourcePreviewModal**

```ts
const effectiveFileType = computed(() => {
  if (previewInfo.value?.converted_to_pdf) return 'pdf'
  return fileType.value
})
```

Use `effectiveFileType` for the main preview switch. Delete Office Online / Google Viewer tabs and helpers (`openOfficeOnline`, `openGoogleViewer`). On conversion failure show error + download only.

Alternatively embed `DocumentPreviewModal` for the body and keep create-lesson chrome — either approach is fine if PDF-first behavior matches the spec.

- [ ] **Step 3: Manual check** — curriculum docx → spinner → PDF iframe

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Resource/DocumentPreviewModal.vue frontend/src/components/Resource/ResourcePreviewModal.vue
git commit -m "feat(preview): add DocumentPreviewModal and PDF-first curriculum preview"
```

---

### Task 7: TipTap「查看」for Office

**Files:**
- Modify: `frontend/src/components/Editor/TipTapEditor.vue`

**Interfaces:**
- Consumes: `DocumentPreviewModal` with `mode="file"`
- View button for `pdf|docx?|pptx?|xlsx?`

- [ ] **Step 1: Change file card HTML**

Replace PDF-only view button (~722+) with:

```ts
const previewable = /\.(pdf|docx?|pptx?|xlsx?)$/i.test(originalFilename)
// button:
${previewable ? `<button type="button" class="file-view-btn" data-file-preview-url="${downloadUrl}">查看</button>` : ''}
```

Apply to every file-card builder in this file (upload insert + library PDF insert). Remove `onclick="window.open(...)"`.

- [ ] **Step 2: Click delegation + modal**

```ts
const showDocPreview = ref(false)
const previewFileUrl = ref<string | null>(null)
const previewTitle = ref('')

function onEditorClick(e: MouseEvent) {
  const btn = (e.target as HTMLElement)?.closest?.('.file-view-btn') as HTMLElement | null
  if (!btn) return
  e.preventDefault()
  e.stopPropagation()
  const url = btn.getAttribute('data-file-preview-url')
  if (!url) return
  previewFileUrl.value = url
  previewTitle.value = '文档预览'
  showDocPreview.value = true
}
```

Bind on ProseMirror DOM: `editor.view.dom.addEventListener('click', onEditorClick)` (and remove on destroy).

```vue
<DocumentPreviewModal
  v-model="showDocPreview"
  mode="file"
  :file-url="previewFileUrl"
  :title="previewTitle"
/>
```

- [ ] **Step 3: Manual check** — TipTap xlsx「查看」works

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Editor/TipTapEditor.vue
git commit -m "feat(preview): enable TipTap view button for Office attachments"
```

---

### Task 8: Library `AssetDetailModal`

**Files:**
- Modify: `frontend/src/components/Library/AssetDetailModal.vue`

**Interfaces:**
- For `asset_type` `pdf` | `document`, call `loadFromLibrary(id)` and iframe `previewAbsoluteUrl`

- [ ] **Step 1: Wire composable**

```ts
import { useDocumentPreview } from '@/composables/useDocumentPreview'

const {
  loading: previewLoading,
  error: previewError,
  previewAbsoluteUrl,
  loadFromLibrary,
} = useDocumentPreview()

watch(
  () => asset.value?.id,
  async (id) => {
    if (!id) return
    if (asset.value?.asset_type === 'pdf' || asset.value?.asset_type === 'document') {
      await loadFromLibrary(id)
    }
  },
)
```

Use `previewAbsoluteUrl` for PDF/document iframes; show loading/error; keep original `public_url` as download fallback.

- [ ] **Step 2: Manual check** — library Office asset opens as PDF

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/Library/AssetDetailModal.vue
git commit -m "feat(preview): use converted PDF preview in library asset detail"
```

---

### Task 9: Deploy note + verification

**Files:**
- Modify: project `README.md` Dependencies section **only if it already lists runtime deps**; otherwise add a short module docstring note at top of `office_converter.py`

- [ ] **Step 1: Document requirement**

```text
Document preview (Word/PPT/Excel): install LibreOffice (`libreoffice` or `soffice` on PATH). Without it, Office preview fails; users can still download originals.
```

- [ ] **Step 2: Run backend tests**

Run: `cd backend && python -m pytest tests/services/test_office_converter.py tests/services/test_document_preview.py -v`

Expected: PASS

- [ ] **Step 3: Manual E2E**

- [ ] Curriculum: small docx / pptx / xlsx / pdf preview
- [ ] TipTap「查看」for same types
- [ ] Library detail for Office
- [ ] Second open faster (cache)
- [ ] LibreOffice unavailable → error + download

- [ ] **Step 4: Commit if docs touched**

```bash
git add README.md backend/app/services/office_converter.py
git commit -m "docs: note LibreOffice requirement for document preview"
```

---

## Self-Review (plan vs spec)

| Spec requirement | Task |
|---|---|
| Fix path resolve (bare filename) | Task 1 |
| Excel → PDF | Task 1 |
| Cache `*_converted.pdf` | Task 1 |
| Sync wait UX | Tasks 6–8 |
| Curriculum preview + Excel | Task 2 |
| TipTap / file URL API | Task 3 |
| Library preview API | Task 4 |
| Unified response fields | Task 2 |
| Remove external viewers | Task 6 |
| TipTap Office 查看 | Task 7 |
| Library converted PDF UI | Task 8 |
| Cleanup on delete | Task 4 |
| LibreOffice deploy note | Task 9 |
| No kkFileView / async queue / sheet UI | Out of scope (no tasks) |

Interface names are consistent across tasks: `build_preview_payload`, `resolve_resource_path`, `documentPreviewService`, `useDocumentPreview`, `DocumentPreviewModal`.

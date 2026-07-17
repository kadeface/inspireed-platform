# Task 6 Report: DocumentPreviewModal + simplify ResourcePreviewModal

## Status
Complete

## Commit
`6bc8103` — feat(preview): add DocumentPreviewModal and PDF-first curriculum preview

## What changed

### Created `frontend/src/components/Resource/DocumentPreviewModal.vue`
- Props: `modelValue`, `mode: 'resource' | 'library' | 'file'`, `resourceId?`, `assetId?`, `fileUrl?`, `title?`.
- Uses `useDocumentPreview()`; on open (or when the relevant id/url prop changes) calls `loadFromResource` / `loadFromLibrary` / `loadFromFileUrl` based on `mode`; `reset()` on close.
- States: loading spinner with Office-conversion hint → error (shown for both fetch errors and `conversion_error` cases, since the composable already folds those into `error`) with retry + download → PDF iframe (`displayKind === 'pdf'`, covers both native PDFs and converted Office docs) → image → generic "unsupported, download only" fallback.
- No Office Online / Google Viewer code at all (new file, nothing to remove).
- Overlay/container/header/body CSS copied verbatim from `ResourcePreviewModal` (no visual redesign); trimmed only the parts tied to removed features (tabs, create-lesson footer).
- Not yet wired into any call site — per the brief, this task only creates the component; consumers (TipTap, `AssetDetailModal`, etc.) are follow-up work per the design doc.

### Simplified `frontend/src/components/Resource/ResourcePreviewModal.vue`
- Added `effectiveFileType` computed (PDF if `previewInfo.converted_to_pdf`, else original `fileType`) and `conversionFailed` computed, exactly per the brief's snippet.
- Main preview switch now branches on `effectiveFileType === 'pdf'` for the iframe, so a converted Office doc renders as PDF.
- Deleted the entire Office tab UI (`preview-tabs`, "文件信息"/"在线预览" tabs, Office Online / Google Docs Viewer / "本地应用" preview-method blocks) and the helpers `openOfficeOnline`, `openConvertedPDF`, `openGoogleViewer`, `getOfficeDescription`, and the `activePreviewTab` ref.
- Error container now also triggers on `conversionFailed` (not just fetch `error`), shows the conversion error message, and offers both "重试" (retries conversion or reload, as appropriate) and "下载原文件" — matching "on conversion failure show error + download only."
- Removed now-dead CSS for the deleted tab/office-info markup; kept `.other-file-container` etc. for the (now rarer) generic-unsupported-type fallback.
- Did not migrate this component to `useDocumentPreview`/`documentPreviewService` — kept it on the existing `resourceService.getResource` + `getResourcePreview` calls per the brief's literal Step 2 diff, to keep the change surgical. `canCreateLesson`/create-lesson footer chrome preserved unchanged.

## Verification
- `vue-tsc --noEmit`: clean.
- `eslint` on both files: clean.
- `vite build`: succeeds (no new warnings beyond pre-existing large-chunk warnings).
- Did not run a live "curriculum docx → spinner → PDF iframe" manual browser check (no backend/dev server driven in this session); relied on type-check + build + code review of the request/response contract already verified in Task 5.

## Concerns
- Manual end-to-end check (Step 3 in the brief) not executed live — recommend a quick smoke test against a real docx resource before considering this fully done.
- `DocumentPreviewModal` is currently unused (no import sites yet); wiring it into TipTap/`AssetDetailModal`/other entry points is out of scope here per the brief and design doc's "后续" notes.
- `ResourcePreviewModal` composition vs. embedding `DocumentPreviewModal` for the body: went with the inline `effectiveFileType` approach (the brief's literal Step 2 diff) rather than composing `DocumentPreviewModal`, since `ResourcePreviewModal` needs extra chrome (create-lesson, resource-specific download endpoint) that `DocumentPreviewModal` doesn't have — both were called acceptable in the brief.

## Report path
`/Users/382241106qq.com/inspireed-platform-main/.superpowers/sdd/task-6-report.md`

---

## Review fix: scope `conversionFailed` to Office only

### Status
Complete

### Commit
`fix(preview): scope conversionFailed to Office types only`

### What changed
- **`ResourcePreviewModal.vue`**: `conversionFailed` now requires `fileType === 'office'` in addition to `conversion_error && !converted_to_pdf`. Non-Office types (mp4, zip, txt, …) with a backend `conversion_error` no longer hijack the error UI.
- **`useDocumentPreview.ts`**: `error` is set from `conversion_error` only when `file_type` is an Office extension (`doc/docx/ppt/pptx/xls/xlsx`) and conversion did not succeed. Non-Office unsupported types keep `displayKind === 'unsupported'` and show the download-only panel.

### Template branch verification
| Scenario | ResourcePreviewModal | DocumentPreviewModal |
|---|---|---|
| Office conversion fail | `conversionFailed` → error + retry/download | `error` set → error + retry/download |
| Native PDF | `effectiveFileType === 'pdf'` → iframe | `displayKind === 'pdf'` → iframe |
| Image | `fileType === 'image'` → `<img>` | `displayKind === 'image'` → `<img>` |
| Other (mp4, zip, txt…) | `v-else` → other-file panel | `displayKind === 'unsupported'` → download-only panel |

### Verification
- `vue-tsc --noEmit`: clean.
- Linter on both changed files: clean.

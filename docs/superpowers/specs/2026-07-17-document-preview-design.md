# 电子文档在线预览设计

## 文档信息

| 项 | 内容 |
|---|---|
| 状态 | 已评审（对话确认） |
| 版本 | 1.0 |
| 日期 | 2026-07-17 |
| 相关参考 | [kkFileView](https://github.com/kekingcn/kkFileView)（评估后不采用） |

---

## 1. 背景与目标

平台支持上传 PDF、Word、PPT、Excel 等电子文档，但缺少统一、可靠的在线预览：

- PDF / 图片：多数入口可用浏览器原生展示。
- Word / PPT：已有 LibreOffice→PDF 路径（`office_converter.py` + `GET /resources/{id}/preview`），但路径解析常失败（DB 存裸文件名，converter 只认 `/uploads/resources/...`），且 Excel 未纳入转换。
- TipTap 附件：「查看」仅对 PDF 开放。
- 教师资源库：Office 二进制塞进 iframe 通常无法预览。
- Office Online / Google Viewer：依赖公网可达 URL，内网/学校部署不可靠。

曾评估 kkFileView（Spring Boot 独立预览服务）：格式覆盖广，但需额外 JDK + LibreOffice 容器，与「够用即可、不新增服务」目标不符，本轮不采用。

**成功标准：**

- 课程资源、TipTap 附件、教师资源库三入口，对 PDF / 图片 / Word / PPT / Excel 均可在线预览（Office 类以转 PDF 为准）。
- 不新增独立预览微服务；复用并修复现有 LibreOffice 转换。
- 点开后同步等待（转圈），转换完成直接展示；同文件再次打开走缓存更快。
- 预览失败时仍可下载原文件（在资源允许下载时）。

---

## 2. 范围

### 2.1 包含

- 修复并扩展 `OfficeConverterService`：路径规范化、Excel 支持、转换缓存。
- 统一预览 API 响应语义；课程资源增强、库资源与 TipTap 附件补齐入口。
- 前端统一预览体验：以 `ResourcePreviewModal` 为中枢（或抽出共享逻辑），三入口共用。
- 去掉对 Office Online / Google Viewer 作为主兜底的依赖。
- 部署说明：运行环境需安装 LibreOffice。

### 2.2 不包含

- kkFileView / OnlyOffice / Collabora 等独立预览或编辑服务。
- 在线编辑、协作批注。
- Excel 可筛选/可点格子的前端表格预览（本轮 Excel 也转 PDF）。
- 异步转换任务队列、进度推送、可取消转换。
- 学生知识库二进制文档上传（知识库仍以 Markdown 为主）。
- CAD、压缩包、视频转码等 kkFileView 级扩展格式。

---

## 3. 方案选型

| 方案 | 结论 |
|---|---|
| 1. 修复扩展 LibreOffice→PDF + 统一前端预览 | **采用** |
| 2. 纯前端（vue-office / pdf.js / xlsx） | 不采用：Word/PPT 还原不稳定，与现有转换重复 |
| 3. 独立部署 kkFileView | 不采用：运维成本高，超出「够用」范围；格式暴增时可再评估 |

体验约定：质量「够用即可」；Excel 与 Word/PPT 同转 PDF；UX 为同步等待 + 缓存。

---

## 4. 架构与组件边界

```
前端入口                          统一预览层                         后端
─────────                        ──────────                        ────
ResourcePreviewModal  ─┐
TipTap「查看」         ─┼─→  DocumentPreview（能力复用）  ─→  preview API
AssetDetailModal      ─┘         PDF / 图片 iframe|img          OfficeConverter
ReferenceMaterialCell ─→（可逐步接入）                          storage + 转换缓存
```

### 4.1 后端

- 强化 `OfficeConverterService`：
  - 输入支持裸文件名、`/uploads/resources/{file}`、经 `filename_to_url` 规范化后的引用。
  - 映射到 `storage/resources/` 本地路径；拒绝站外 URL 与路径穿越。
  - 本轮支持的 Office 扩展名固定为：`doc`、`docx`、`ppt`、`pptx`、`xls`、`xlsx`（不含 `xlsm` 等变体，需要时另开迭代）。
  - 主路径：LibreOffice `--headless --convert-to pdf`；结果缓存为同目录 `{stem}_converted.pdf`。
  - 超时约 90s；失败返回可读错误，不抛未处理 500。
- 内容提取 fallback（python-docx / python-pptx 拼简易 PDF）可保留，但不作为成功标准承诺。
- 删除源文件时，若存在对应 `*_converted.pdf`，一并清理（挂到现有删除逻辑）。

### 4.2 前端

- 以现有 `ResourcePreviewModal` 为中枢，或抽出 `useDocumentPreview` / 共享展示块：
  - loading（含「Office 首次转换可能较久」提示）
  - error + 重试 + 下载
  - PDF：iframe；图片：img
- Office 转换成功后按 **PDF** 展示，不再依赖外部在线 Viewer。
- TipTap 文件卡：对 PDF 与上述 Office 类型均显示「查看」。
- `AssetDetailModal`（及后续 `ReferenceMaterialCell`）复用同一套「取 preview_url → 展示」逻辑。

---

## 5. 数据流与 API

### 5.1 预览请求流（同步）

1. 用户点击「查看」。
2. 前端按来源调用对应 preview API（需登录）。
3. 后端解析本站存储引用。
4. PDF / 图片：直接返回可访问 `preview_url`。
5. Office：查 `*_converted.pdf` → 命中则返回；未命中则 LibreOffice 同步转换 → 写缓存 → 返回 PDF URL。
6. 前端 loading → iframe/img 打开 `preview_url`；失败则 error + 下载原文件。

### 5.2 统一响应字段

| 字段 | 含义 |
|---|---|
| `preview_url` | 浏览器最终打开的地址（PDF / 图片） |
| `file_url` | 原文件地址（下载用） |
| `file_type` | 扩展名 |
| `can_preview_directly` | 是否无需转换 |
| `converted_to_pdf` | Office 是否已转为 PDF |
| `conversion_error` | 失败原因（可空） |

可选扩展：`title`、`file_size`、`conversion_method`（与现有课程资源 preview 对齐即可）。

### 5.3 入口

| 场景 | API | 说明 |
|---|---|---|
| 课程资源 | `GET /api/v1/resources/{id}/preview`（已有） | 扩展 Office 列表含 Excel；规范化 `file_url` 再交给 converter |
| 教师资源库 | `GET /api/v1/library-assets/{id}/preview`（新增） | 鉴权沿用库资源可见性；内部复用同一 converter |
| TipTap / 仅有文件 URL | `POST /api/v1/upload/preview`（新增） | Body：`file_url` 或存储文件名；仅允许本站 `storage/resources/`；鉴权同上传 |

### 5.4 Converter 内部契约

- 输入：本站资源引用（裸名 / 相对 path / `/uploads/resources/...`）。
- 输出：`/uploads/resources/{stem}_converted.pdf` 或失败。
- Word / PPT / Excel 共用 LibreOffice 转换路径。

---

## 6. 错误处理与运维

| 情况 | 后端 | 前端 |
|---|---|---|
| 文件不存在 / 非本站路径 | 404 或明确 error | 「文件不可用」 |
| 扩展名不支持 | `conversion_error`，不转换 | 说明不支持 + 下载 |
| LibreOffice 未安装 | 可控失败 | 「预览服务暂不可用」+ 下载 |
| 转换超时 / 进程失败 | `conversion_error` | 重试 + 下载 |
| PDF/图片直链加载失败 | — | 同降级 |
| 未登录 / 无权限 | 401/403 | 现有鉴权提示 |

原则：预览失败永不挡住下载（资源允许下载时）。不把 Office Online / Google Viewer 作为兜底。

运维：运行环境需安装 `libreoffice`（或 `soffice`）；在 README / 部署文档中写明。

---

## 7. 测试要点

### 7.1 后端

1. 路径解析：裸文件名、`/uploads/resources/x.docx` → 正确落到 `storage/resources/`。
2. 缓存：同一文件第二次 preview 不重跑 LibreOffice（可 mock 进程）。
3. 格式：`docx`/`pptx`/`xlsx`（及保留的 `doc`/`ppt`/`xls`）进入转换分支；`pdf`/图片不转换。
4. 安全：`POST /upload/preview` 拒绝外链与路径穿越。
5. LibreOffice 不可用时返回可控失败，不 500 裸奔。

### 7.2 前端

1. 三入口均可打开预览：课程资源、库资源、TipTap 附件。
2. loading → PDF iframe；失败 → 错误 + 下载。
3. TipTap：Office 显示「查看」，不只 PDF。

### 7.3 手工验收

各上传一份小的 docx / pptx / xlsx / pdf：首次转圈后可看，再次打开应更快。

---

## 8. 关键文件（实现导向）

| 区域 | 路径 |
|---|---|
| Office 转换 | `backend/app/services/office_converter.py` |
| 课程预览 API | `backend/app/api/v1/resources.py` |
| 上传 / TipTap 预览 | `backend/app/api/v1/upload.py`（或邻近模块） |
| 库资源预览 | `backend/app/api/v1/library_assets.py` |
| URL 工具 | `backend/app/utils/resource_url.py` |
| 主预览 UI | `frontend/src/components/Resource/ResourcePreviewModal.vue` |
| 库详情 | `frontend/src/components/Library/AssetDetailModal.vue` |
| TipTap | `frontend/src/components/Editor/TipTapEditor.vue` |
| 前端 API | `frontend/src/services/resource.ts` 等 |

---

## 9. 后续可选（本轮不做）

- 若格式需求扩大或转换压力过大，再评估以可插拔方式接入 kkFileView。
- Excel 前端表格预览（如轻量 sheet 组件）作为增强体验。
- 异步转换队列与转换状态轮询。

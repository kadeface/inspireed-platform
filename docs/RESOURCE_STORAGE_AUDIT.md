# 资源存储方式检查报告

## 检查时间
2024年12月（具体日期根据实际检查时间）

## 检查结果摘要

### ✅ 符合预期的部分

1. **文件系统存储**
   - 存储位置：`backend/storage/resources/`
   - 文件命名：UUID格式（如 `683c1f7e-204b-4d3e-b38e-4898e154bcf2.png`）
   - 文件数量：499个文件
   - 状态：✓ 正常

2. **配置设置**
   - `UPLOAD_DIR`: `storage`
   - `RESOURCE_BASE_PATH`: `/uploads/resources`
   - `RESOURCE_BASE_URL`: 未设置（从请求中动态获取）
   - 状态：✓ 正常

3. **上传服务 (`upload_service`)**
   - `upload_file()` 和 `upload_pdf()` 返回文件名（不包含路径）
   - 状态：✓ 正常

4. **上传API (`/upload/`)**
   - 返回完整URL（通过 `filename_to_url` 转换）
   - 状态：✓ 正常

5. **教案API (`/lessons/`)**
   - 在返回前将文件名转换为完整URL
   - 状态：✓ 正常

### ❌ 需要改进的部分

1. **Resource表（旧数据）**
   - 问题：部分记录存储的是绝对路径（`/uploads/resources/xxx.pdf`）
   - 预期：只存储文件名（`xxx.pdf`）
   - 影响：旧数据需要迁移

2. **LibraryAsset表（旧数据）**
   - 问题：`storage_key` 和 `public_url` 存储的是绝对路径（`/uploads/resources/xxx.html`）
   - 预期：只存储文件名（`xxx.html`）
   - 影响：旧数据需要迁移

3. **LibraryAsset创建逻辑**
   - 位置：`backend/app/api/v1/library_assets.py:244-245`
   - 问题：直接使用 `upload_result["file_url"]`（已经是文件名），但可能在某些情况下存储了路径
   - 建议：确保使用 `url_to_filename()` 转换

## 当前存储架构

### 1. 文件系统存储

```
backend/storage/
└── resources/
    ├── {UUID}.png
    ├── {UUID}.pdf
    ├── {UUID}.mp4
    └── ...
```

- 文件命名：UUID格式，保证唯一性
- 存储位置：`backend/storage/resources/`
- 访问路径：`/uploads/resources/{filename}`（通过FastAPI静态文件路由）

### 2. 数据库存储格式

#### 预期格式（新数据）

| 表名 | 字段 | 存储格式 | 示例 |
|------|------|----------|------|
| `resources` | `file_url` | 文件名 | `c9c9f639-1ac3-4c3c-a01b-e4d2a0725bff.pdf` |
| `resources` | `thumbnail_url` | 文件名 | `thumb_c9c9f639-1ac3-4c3c-a01b-e4d2a0725bff.png` |
| `library_assets` | `storage_key` | 文件名 | `d8f2217d-aecf-4efe-a5c5-a365c4b0054b.html` |
| `library_assets` | `public_url` | 文件名 | `d8f2217d-aecf-4efe-a5c5-a365c4b0054b.html` |
| `library_assets` | `thumbnail_url` | 文件名 | `thumb_d8f2217d-aecf-4efe-a5c5-a365c4b0054b.png` |
| `lessons` | `content` (HTML) | 文件名 | `<img src="7a7a6bc2-64fa-4ec7-ae0b-27127fae74ba.png">` |
| `lessons` | `content` (videoUrl) | 文件名 | `346f1e8e-ea87-45ca-8af7-907fad5b82eb.MP4` |

#### 当前格式（部分旧数据）

| 表名 | 字段 | 当前格式 | 问题 |
|------|------|----------|------|
| `resources` | `file_url` | `/uploads/resources/xxx.pdf` | ✗ 包含路径前缀 |
| `library_assets` | `storage_key` | `/uploads/resources/xxx.html` | ✗ 包含路径前缀 |
| `library_assets` | `public_url` | `/uploads/resources/xxx.html` | ✗ 包含路径前缀 |

### 3. API返回格式

所有API在返回前都会将文件名转换为完整URL：

```
完整URL = {动态服务器地址} + {RESOURCE_BASE_PATH} + {文件名}
```

示例：
- 服务器地址：`http://192.168.2.53:8000`
- 路径前缀：`/uploads/resources`
- 文件名：`7a7a6bc2-64fa-4ec7-ae0b-27127fae74ba.png`
- 完整URL：`http://192.168.2.53:8000/uploads/resources/7a7a6bc2-64fa-4ec7-ae0b-27127fae74ba.png`

## 数据流

### 上传流程

```
1. 前端上传文件
   ↓
2. 后端 upload_service.upload_file()
   - 保存文件到 storage/resources/{UUID}.{ext}
   - 返回文件名（如：7a7a6bc2-64fa-4ec7-ae0b-27127fae74ba.png）
   ↓
3. 上传API (/upload/)
   - 接收文件名
   - 使用 filename_to_url() 转换为完整URL
   - 返回完整URL给前端（用于预览）
   ↓
4. 前端保存到数据库
   - 提取文件名（从完整URL中）
   - 保存文件名到数据库
```

### 读取流程

```
1. 前端请求教案/资源
   ↓
2. 后端从数据库读取
   - 获取文件名（如：7a7a6bc2-64fa-4ec7-ae0b-27127fae74ba.png）
   ↓
3. API返回前转换
   - 使用 filename_to_url() 转换为完整URL
   - 返回完整URL给前端
   ↓
4. 前端显示
   - 直接使用完整URL显示图片/视频
```

## 关键代码位置

### 后端

1. **上传服务**
   - `backend/app/services/upload.py`
   - `upload_file()`, `upload_pdf()` - 返回文件名

2. **URL转换工具**
   - `backend/app/utils/resource_url.py`
   - `filename_to_url()` - 文件名 → 完整URL
   - `url_to_filename()` - URL/路径 → 文件名

3. **API端点**
   - `backend/app/api/v1/upload.py` - 上传API
   - `backend/app/api/v1/resources.py` - 资源API
   - `backend/app/api/v1/lessons.py` - 教案API
   - `backend/app/api/v1/library_assets.py` - 资源库API

4. **配置**
   - `backend/app/core/config.py`
   - `RESOURCE_BASE_PATH`, `RESOURCE_BASE_URL`, `UPLOAD_DIR`

### 前端

1. **编辑器组件**
   - `frontend/src/components/Editor/TipTapEditor.vue`
   - `handleImageUpload()`, `handleFileUpload()` - 上传后提取文件名

2. **单元格组件**
   - `frontend/src/components/Cell/TextCell.vue` - 文本单元格
   - `frontend/src/components/Cell/VideoCell.vue` - 视频单元格

## 待完成任务

### 高优先级

1. **数据迁移脚本**
   - 将 `resources` 表中的 `/uploads/resources/xxx` 转换为 `xxx`
   - 将 `library_assets` 表中的 `/uploads/resources/xxx` 转换为 `xxx`
   - 将 `lessons.content` 中的HTML图片URL转换为文件名

2. **LibraryAsset创建逻辑检查**
   - 确保 `storage_key` 和 `public_url` 使用 `url_to_filename()` 转换
   - 位置：`backend/app/api/v1/library_assets.py:244-245`

### 中优先级

1. **验证新上传的数据**
   - 确保所有新上传的资源都按文件名存储
   - 定期运行检查脚本验证

2. **文档更新**
   - 更新开发文档，说明资源存储规范
   - 添加数据迁移指南

## 检查脚本

使用以下脚本检查资源存储格式：

```bash
cd backend
source venv/bin/activate
python scripts/check_resource_storage.py
```

## 总结

- ✅ **新数据**：已按文件名格式存储，符合预期
- ❌ **旧数据**：部分记录仍使用路径格式，需要迁移
- ✅ **API返回**：正确转换为完整URL
- ✅ **文件系统**：使用UUID命名，存储正常

建议优先完成数据迁移脚本，确保所有数据统一使用文件名格式存储。


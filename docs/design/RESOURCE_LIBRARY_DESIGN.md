# 资源库管理系统设计与实现

## 概述

本文档描述了基于现有 InspireEd 系统的资源库管理功能的设计与实现。资源库允许教师、教研员和管理员上传、管理和共享学校级别的教学资源，并支持在课程章节中引用这些资源。

## 核心特性

### 1. 学校级资源库
- **资产隔离**：按 `school_id` 隔离，每个学校拥有独立的资源库
- **权限控制**：学生无法访问资源库接口（403 禁止），只能通过课程上下文访问资源
- **可见性管理**：
  - `teacher_only`：仅上传者可见
  - `school`：全校可见（教研员/管理员可设置）

### 2. 资源类型支持
- PDF 文档
- 视频（MP4, AVI, MOV, WebM）
- 图片（JPG, PNG, GIF, WebP）
- 音频（MP3, WAV, OGG）
- 办公文档（DOC, PPT, XLS）
- 压缩包（ZIP, RAR, 7Z）
- 其他类型

### 3. 资源引用机制
- 课程资源（`Resource`）可以：
  - **直接上传**：传统方式，文件存储在 `file_url`
  - **引用资源库**：通过 `asset_id` 引用资源库资产
- 向后兼容：现有资源不受影响

## 数据模型

### 新增表：`library_assets`

```sql
CREATE TABLE library_assets (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    owner_user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    asset_type VARCHAR(20) NOT NULL,  -- pdf/video/image/audio/document/link/zip/other
    mime_type VARCHAR(100),
    size_bytes INTEGER,
    storage_provider VARCHAR(20) DEFAULT 'local',
    storage_key VARCHAR(500) NOT NULL,
    public_url VARCHAR(500),
    sha256 VARCHAR(64),
    thumbnail_url VARCHAR(500),
    page_count INTEGER,
    duration_seconds INTEGER,
    visibility VARCHAR(20) DEFAULT 'teacher_only',  -- teacher_only/school
    status VARCHAR(20) DEFAULT 'active',  -- active/processing/disabled/deleted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX ix_library_assets_school_updated ON library_assets(school_id, updated_at);
CREATE INDEX ix_library_assets_school_type ON library_assets(school_id, asset_type);
CREATE INDEX ix_library_assets_school_visibility_status ON library_assets(school_id, visibility, status);
CREATE INDEX ix_library_assets_sha256 ON library_assets(sha256);
```

### 扩展表：`resources`

```sql
-- 新增字段
ALTER TABLE resources ADD COLUMN asset_id INTEGER REFERENCES library_assets(id);
CREATE INDEX ix_resources_asset_id ON resources(asset_id);
```

## API 设计

### 资源库 API（`/api/v1/library/assets`）

#### 权限规则
- **必须登录**
- **学生禁止访问**（返回 403）
- **必须有 school_id**
- **查询自动按 school_id 过滤**

#### 端点

##### 1. 列表资产
```
GET /api/v1/library/assets
Query:
  - query: string (搜索标题/描述)
  - asset_type: string (类型筛选)
  - visibility: string (可见性筛选)
  - status: string (状态筛选，默认 active)
  - page: int
  - page_size: int
Response: LibraryAssetListResponse
```

##### 2. 上传资产
```
POST /api/v1/library/assets
Form Data:
  - title: string (required)
  - description: string
  - asset_type: string (可选，自动推断)
  - visibility: string (teacher_only/school)
  - file: File (required)
Response: LibraryAssetUploadResponse
```

##### 3. 获取详情
```
GET /api/v1/library/assets/{id}
Response: LibraryAssetDetail
```

##### 4. 更新资产
```
PATCH /api/v1/library/assets/{id}
Body: LibraryAssetUpdateRequest
Response: LibraryAssetDetail
```

##### 5. 删除资产
```
DELETE /api/v1/library/assets/{id}
Response: { message: string, asset_id: int }
```

##### 6. 查看使用情况
```
GET /api/v1/library/assets/{id}/usages
Response: LibraryAssetUsageResponse
```

### 课程资源 API 扩展（`/api/v1/resources`）

#### 扩展创建接口
```
POST /api/v1/resources/
Form Data:
  - chapter_id: int (required)
  - title: string (required)
  - description: string
  - resource_type: string
  - is_downloadable: bool
  - asset_id: int (可选，与 file 二选一)
  - file: File (可选，与 asset_id 二选一)
```

#### 响应增强
`ResourceResponse` 新增字段：
- `asset_id`: Optional[int]
- `asset`: Optional[LibraryAssetSummary]
- `resolved_file_url`: Optional[str] - 优先使用 file_url，否则使用 asset.public_url

## 前端实现

### 新增页面
- **资源库页面**：`/frontend/src/pages/Teacher/ResourceLibrary.vue`
  - 搜索、筛选、分页
  - 上传新资源
  - 查看资源详情
  - 编辑/删除资源

### 新增组件
1. **AssetPicker**（`/frontend/src/components/Library/AssetPicker.vue`）
   - 资源选择器（用于章节资源引用）
   - 支持搜索、筛选、分页
   - 单选模式

2. **UploadAssetModal**（`/frontend/src/components/Library/UploadAssetModal.vue`）
   - 上传资源到资源库
   - 文件拖拽支持
   - 元数据编辑

3. **AssetDetailModal**（`/frontend/src/components/Library/AssetDetailModal.vue`）
   - 资源详情展示
   - 编辑/删除操作

### 扩展组件
**ChapterResourceUploadModal**（`/frontend/src/components/Curriculum/ChapterResourceUploadModal.vue`）
- 新增 Tab 切换
  - **上传文件**：原有逻辑
  - **从资源库选择**：使用 AssetPicker 选择资产并引用

### 服务层
- **libraryService**（`/frontend/src/services/library.ts`）：资源库 CRUD
- **resourceService**：新增 `createResourceFromAsset()` 方法

## 权限与安全

### 访问控制
| 角色 | 资源库访问 | 上传 | 修改自己的 | 修改他人的 | 删除自己的 | 删除他人的 | 设置全校可见 |
|------|----------|------|-----------|-----------|-----------|-----------|-------------|
| 学生 | ❌ 403 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 教师 | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| 教研员 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 管理员 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 可见性规则
- **teacher_only**：仅上传者可见（教师默认）
- **school**：全校可见（教研员/管理员可设置）
- 教师查询时：自动过滤为"自己上传的" OR "全校可见的"

### 文件访问（MVP）
- 当前使用 `/uploads/resources/*` 静态路由（公开可访问）
- 未来可增强为：
  - MinIO 私有桶 + 签名 URL
  - 后端鉴权下载（`GET /files/{asset_id}`）

## 迁移与兼容

### 数据迁移
运行 Alembic 迁移：
```bash
cd backend
alembic upgrade head
```

### 向后兼容
- 现有资源（`Resource.file_url`）不受影响
- 新资源可选择：
  - 继续直接上传（`file_url`）
  - 引用资源库（`asset_id`）

## 使用流程

### 教师上传资源到资源库
1. 访问资源库页面
2. 点击"上传资源"
3. 填写标题、描述、选择文件
4. 选择可见性（仅自己/全校）
5. 上传

### 教师在章节中引用资源
1. 在课程管理 → 章节列表
2. 点击"上传资源"
3. 切换到"从资源库选择"tab
4. 搜索并选择资源
5. 点击"引用资源"

### 教研员审核与发布
1. 访问资源库
2. 查看教师上传的资源
3. 编辑资源元数据
4. 修改可见性为"全校可见"

## 测试建议

### 单元测试
- [ ] 资源库 API 权限校验
- [ ] 学生访问返回 403
- [ ] 资源引用创建逻辑
- [ ] 可见性过滤规则

### 集成测试
- [ ] 教师上传 → 引用流程
- [ ] 教研员审核流程
- [ ] 资产删除检查引用
- [ ] 跨学校隔离验证

### 手动测试清单
- [ ] 学生尝试访问 `/library/assets` → 403
- [ ] 教师上传资源 → 列表可见
- [ ] 教师设置可见性 → 权限正确
- [ ] 章节引用资源 → 创建成功
- [ ] 课程页展示引用资源 → 学生可访问
- [ ] 旧资源仍可正常访问

## 后续增强

### V2 功能
- [ ] 目录管理（文件夹）
- [ ] 标签系统
- [ ] 批量操作
- [ ] 资源去重（基于 SHA256）
- [ ] 版本管理

### V3 功能
- [ ] 细粒度 ACL
- [ ] 私有文件访问（签名 URL）
- [ ] Office 文档在线预览
- [ ] 视频转码（HLS）
- [ ] 全文检索（向量检索）
- [ ] 资源推荐

## 文件清单

### 后端
- **模型**
  - `backend/app/models/library_asset.py`（新增）
  - `backend/app/models/curriculum.py`（扩展 Resource）
  - `backend/app/models/__init__.py`（导出）

- **Schema**
  - `backend/app/schemas/library_asset.py`（新增）
  - `backend/app/schemas/resource.py`（扩展）

- **API**
  - `backend/app/api/v1/library_assets.py`（新增）
  - `backend/app/api/v1/resources.py`（扩展）
  - `backend/app/api/v1/__init__.py`（注册路由）

- **迁移**
  - `backend/alembic/versions/017_add_library_assets_and_resource_asset_id.py`

### 前端
- **页面**
  - `frontend/src/pages/Teacher/ResourceLibrary.vue`（新增）

- **组件**
  - `frontend/src/components/Library/AssetPicker.vue`（新增）
  - `frontend/src/components/Library/UploadAssetModal.vue`（新增）
  - `frontend/src/components/Library/AssetDetailModal.vue`（新增）
  - `frontend/src/components/Curriculum/ChapterResourceUploadModal.vue`（扩展）

- **服务与类型**
  - `frontend/src/services/library.ts`（新增）
  - `frontend/src/services/resource.ts`（扩展）
  - `frontend/src/types/library.ts`（新增）
  - `frontend/src/types/resource.ts`（扩展）

## 总结

本实现遵循"最短路径 MVP"原则：
- ✅ 后端模型与 API 完整
- ✅ 前端页面与组件可用
- ✅ 权限隔离符合需求
- ✅ 向后兼容现有资源
- ✅ 为未来增强预留扩展点

核心设计亮点：
1. **学校级隔离**：资源库按学校管理
2. **学生保护**：API 级别禁止学生访问
3. **灵活引用**：资源可直接上传或引用资源库
4. **平滑过渡**：与现有系统完全兼容

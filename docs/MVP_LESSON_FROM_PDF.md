# MVP：基于官方教学设计PDF的教案创建方案

## 一、核心理念

### 设计思路
- **官方教学设计：** PDF 格式，只读，不可修改，作为教师的参考资料
- **教师教案：** 教师参考 PDF 后，自己进行模块化设计，创建个性化教案
- **关系：** PDF 是参考文档，教案是独立创作，两者是"参考"而非"模板-实例"关系

### 工作流程
```
浏览课程 → 查看资源 → 下载/预览官方PDF → 参考PDF内容 → 创建模块化教案
   ↓          ↓           ↓                ↓              ↓
选择学科   找到章节    阅读教学设计      理解知识点    添加Cell单元
```

---

## 二、数据模型设计（简化版）

### 2.1 Resource（资源）- 已有，需扩展

```python
class Resource(Base):
    """课程资源"""
    __tablename__ = "resources"
    
    id: int
    chapter_id: int  # 所属章节
    
    # 基本信息
    title: str  # 资源标题，如"集合的概念 - 教学设计"
    description: str
    resource_type: str  # 'pdf', 'video', 'document', 'link'
    
    # PDF 相关字段（新增）
    file_url: str | None  # PDF 文件 URL
    file_size: int | None  # 文件大小（字节）
    page_count: int | None  # PDF 页数
    thumbnail_url: str | None  # 缩略图
    
    # 元数据
    is_official: bool  # 是否官方资源
    is_downloadable: bool  # 是否允许下载
    view_count: int  # 查看次数
    download_count: int  # 下载次数
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
```

### 2.2 Lesson（教师教案）- 已有，需扩展

```python
class Lesson(Base):
    """教师教案"""
    __tablename__ = "lessons"
    
    id: int
    course_id: int  # 所属课程
    teacher_id: int  # 创建教师
    
    # 基本信息
    title: str
    description: str
    content: JSON  # Cell 数组
    tags: List[str]
    
    # 参考资源关联（新增）
    reference_resource_id: int | None  # 参考的官方PDF资源ID
    reference_notes: str | None  # 教师的参考笔记
    
    # 状态
    status: str  # draft/published/archived
    
    # 统计
    cell_count: int  # Cell 数量
    estimated_duration: int  # 预计时长（分钟）
    view_count: int
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None
```

### 2.3 关系图

```
Subject → Grade → Course → Chapter → Resource (PDF教学设计)
                     ↓                       ↑
                   Lesson ──────────────────┘
                 (教师教案)          [参考关系]
                                   reference_resource_id
```

---

## 三、MVP 功能设计

### 3.1 课程结构浏览（增强）

#### 需求
- 在课程结构中显示资源列表
- 区分资源类型（PDF、视频、文档等）
- 显示官方教学设计 PDF
- 提供预览和下载功能

#### UI 设计

```
┌──────────────────────────────────────────────────────────┐
│ 📚 高一数学                                               │
├──────────────────────────────────────────────────────────┤
│ ▼ 第一章：集合与函数                                     │
│   ▼ 📖 1.1 集合的概念                                    │
│      ├─ 📋 官方教学设计                                  │
│      │   • 集合的概念-教学设计.pdf (2.3MB, 8页)          │
│      │     [👁️ 预览] [⬇️ 下载] [📝 参考此资源创建教案]    │
│      │                                                    │
│      ├─ 🎥 视频资源                                      │
│      │   • 集合的概念讲解视频.mp4                        │
│      │     [▶️ 播放]                                     │
│      │                                                    │
│      └─ 📚 我的教案 (3个)                                │
│          • 集合的概念 - 高一(1)班  [编辑]               │
│          • 集合的概念 - 高一(2)班  [编辑]               │
│          • 集合概念深化课          [编辑]               │
│          [➕ 创建新教案]                                 │
└──────────────────────────────────────────────────────────┘
```

#### 组件结构

```vue
<EnhancedCurriculumStructure>
  └─ <ChapterNode>
      └─ <ResourceNode>
          ├─ <PDFResourceItem>  <!-- 新增 -->
          │   - PDF预览
          │   - 下载按钮
          │   - 参考创建按钮
          │
          └─ <LessonListItem>   <!-- 新增 -->
              - 教师的教案列表
```

### 3.2 PDF 预览功能

#### 需求
- 在浏览器中预览 PDF
- 支持翻页、缩放
- 可以边看边创建教案

#### UI 设计

```
┌──────────────────────────────────────────────────────────┐
│ 📋 集合的概念 - 教学设计.pdf              [×] [⬇️] [📝]  │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌───────────────────────────────────────┐              │
│  │                                        │              │
│  │      [PDF 内容显示区域]                │              │
│  │                                        │              │
│  │  一、教学目标                          │              │
│  │    1. 理解集合的概念                   │              │
│  │    2. 掌握集合的表示方法               │              │
│  │    3. ...                              │              │
│  │                                        │              │
│  │  二、教学重点                          │              │
│  │    集合的定义和基本性质                │              │
│  │                                        │              │
│  └───────────────────────────────────────┘              │
│                                                           │
│  [◀️ 上一页]  第 1/8 页  [下一页 ▶️]     [参考此资源创建] │
└──────────────────────────────────────────────────────────┘
```

#### 技术实现
使用 PDF.js 或 Vue-PDF 组件：

```vue
<template>
  <PDFViewer
    :src="pdfUrl"
    @create-lesson="handleCreateFromPDF"
  />
</template>
```

### 3.3 参考 PDF 创建教案

#### 需求
- 从 PDF 资源发起创建教案流程
- 自动关联参考资源
- 预填充课程信息
- 教师可以添加参考笔记

#### UI 设计

```
┌──────────────────────────────────────────────────────────┐
│ 参考官方教学设计创建教案                       [×]        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ ✓ 参考资源                                               │
│   📋 集合的概念-教学设计.pdf                             │
│   章节：高一数学 → 第一章 → 1.1 集合的概念              │
│                                                           │
│ ✏️ 教案信息                                              │
│   教案标题 *                                             │
│   ┌──────────────────────────────────────┐             │
│   │ 集合的概念 - 高一(1)班                │             │
│   └──────────────────────────────────────┘             │
│                                                           │
│   教案描述                                               │
│   ┌──────────────────────────────────────┐             │
│   │ 参考官方教学设计，结合班级实际情况     │             │
│   │ 设计的交互式教学内容                   │             │
│   └──────────────────────────────────────┘             │
│                                                           │
│   参考笔记（可选）                                       │
│   ┌──────────────────────────────────────┐             │
│   │ PDF中的教学目标很完整，需要重点关注    │             │
│   │ 第二部分的实例讲解...                  │             │
│   └──────────────────────────────────────┘             │
│                                                           │
│   标签                                                   │
│   ┌──────────────────────────────────────┐             │
│   │ 集合, 高一, 基础                       │             │
│   └──────────────────────────────────────┘             │
│                                                           │
│   预计时长                                               │
│   ┌─────┐ 分钟                                          │
│   │ 45  │                                               │
│   └─────┘                                               │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                          [取消]  [创建教案]              │
└──────────────────────────────────────────────────────────┘
```

### 3.4 教案编辑器增强

#### 需求
- 显示参考的 PDF 资源信息
- 提供快速访问 PDF 的入口
- 可以随时打开 PDF 参考

#### UI 设计

```
┌──────────────────────────────────────────────────────────┐
│ ← | 集合的概念-高一(1)班 | 已保存 | 保存 | 发布            │
├──────────────────────────────────────────────────────────┤
│ 📋 参考资料：集合的概念-教学设计.pdf                      │
│    [👁️ 查看PDF] [📝 编辑笔记]                  [×关闭]    │
├──────────────────────────────────────────────────────────┤
│  🛠️  │                                                    │
│  工具 │   [文本单元] 课程导入                              │
│  栏   │   根据官方教学设计中的"情境导入"部分，           │
│       │   我设计了一个生活中的实例...                      │
│       │                                                    │
│       │   [➕ 在此添加单元]                               │
│       │                                                    │
│       │   [代码单元] Python 集合演示                       │
│       │   # 参考PDF中的案例，用代码实现                   │
│       │   students = {"张三", "李四", "王五"}             │
└──────────────────────────────────────────────────────────┘
```

### 3.5 PDF 资源管理（管理员功能）

#### 需求
- 管理员可以上传官方教学设计 PDF
- 关联到对应的章节资源
- 设置访问权限

#### UI 设计（管理后台）

```
┌──────────────────────────────────────────────────────────┐
│ 上传官方教学设计                                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ 选择章节 *                                               │
│ [学科 ▼] [年级 ▼] [课程 ▼] [章节 ▼]                     │
│  数学     高一      高一数学   第一章 > 1.1 集合的概念   │
│                                                           │
│ 资源信息                                                 │
│   标题 * ┌────────────────────────────┐                 │
│         │ 集合的概念 - 教学设计       │                 │
│         └────────────────────────────┘                 │
│                                                           │
│   描述   ┌────────────────────────────┐                 │
│         │ 官方标准教学设计文档         │                 │
│         └────────────────────────────┘                 │
│                                                           │
│ 上传 PDF                                                 │
│   ┌────────────────────────────────────────┐            │
│   │  📄 拖拽文件到此处或点击上传            │            │
│   │                                        │            │
│   │      [点击选择文件]                    │            │
│   └────────────────────────────────────────┘            │
│                                                           │
│ 权限设置                                                 │
│   ☑️ 官方资源                                            │
│   ☑️ 允许下载                                            │
│   ☑️ 所有教师可见                                        │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                          [取消]  [上传]                  │
└──────────────────────────────────────────────────────────┘
```

---

## 四、技术实现方案

### 4.1 数据库迁移

```python
# backend/alembic/versions/002_add_pdf_resources.py

def upgrade():
    # 扩展 resources 表
    op.add_column('resources', 
        sa.Column('file_url', sa.String(500), nullable=True))
    op.add_column('resources', 
        sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('resources', 
        sa.Column('page_count', sa.Integer(), nullable=True))
    op.add_column('resources', 
        sa.Column('thumbnail_url', sa.String(500), nullable=True))
    op.add_column('resources', 
        sa.Column('is_downloadable', sa.Boolean(), default=True))
    op.add_column('resources', 
        sa.Column('view_count', sa.Integer(), default=0))
    op.add_column('resources', 
        sa.Column('download_count', sa.Integer(), default=0))
    
    # 扩展 lessons 表
    op.add_column('lessons', 
        sa.Column('reference_resource_id', sa.Integer(), 
                  sa.ForeignKey('resources.id'), nullable=True))
    op.add_column('lessons', 
        sa.Column('reference_notes', sa.Text(), nullable=True))
    op.add_column('lessons', 
        sa.Column('cell_count', sa.Integer(), default=0))
    op.add_column('lessons', 
        sa.Column('estimated_duration', sa.Integer(), nullable=True))
```

### 4.2 后端 API

#### A. 资源相关 API

```python
# backend/app/api/v1/resources.py

@router.get("/chapters/{chapter_id}/resources")
async def get_chapter_resources(
    chapter_id: int,
    resource_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> List[ResourceResponse]:
    """获取章节的资源列表"""
    resources = await resource_service.get_by_chapter(
        chapter_id, 
        resource_type=resource_type
    )
    return resources

@router.get("/resources/{resource_id}")
async def get_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user)
) -> ResourceDetail:
    """获取资源详情"""
    resource = await resource_service.get_by_id(resource_id)
    
    # 增加浏览次数
    await resource_service.increment_view_count(resource_id)
    
    return resource

@router.get("/resources/{resource_id}/download")
async def download_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user)
):
    """下载资源文件"""
    resource = await resource_service.get_by_id(resource_id)
    
    if not resource.is_downloadable:
        raise HTTPException(403, "Resource not downloadable")
    
    # 增加下载次数
    await resource_service.increment_download_count(resource_id)
    
    # 返回文件流或重定向到文件URL
    return FileResponse(resource.file_url)

@router.post("/resources", dependencies=[Depends(require_admin)])
async def create_resource(
    data: ResourceCreate,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin)
) -> ResourceResponse:
    """上传资源（管理员）"""
    
    # 1. 上传文件到存储服务（OSS/S3/本地）
    file_url = await upload_service.upload_file(file)
    
    # 2. 如果是PDF，提取元数据
    if data.resource_type == 'pdf':
        pdf_meta = await extract_pdf_metadata(file)
        data.page_count = pdf_meta.page_count
        data.thumbnail_url = await generate_pdf_thumbnail(file)
    
    # 3. 创建资源记录
    resource = await resource_service.create(data, file_url=file_url)
    
    return resource
```

#### B. 教案相关 API（扩展）

```python
# backend/app/api/v1/lessons.py

@router.post("/lessons/from-resource")
async def create_lesson_from_resource(
    data: CreateLessonFromResourceRequest,
    current_user: User = Depends(get_current_teacher)
) -> LessonResponse:
    """基于参考资源创建教案"""
    
    # 1. 获取资源信息
    resource = await resource_service.get_by_id(data.reference_resource_id)
    
    # 2. 从资源获取课程ID
    chapter = await chapter_service.get_by_id(resource.chapter_id)
    course_id = chapter.course_id
    
    # 3. 创建教案
    lesson = Lesson(
        course_id=course_id,
        teacher_id=current_user.id,
        title=data.title,
        description=data.description,
        reference_resource_id=resource.id,
        reference_notes=data.reference_notes,
        tags=data.tags,
        estimated_duration=data.estimated_duration,
        content=[],  # 空内容，教师自己添加
        status="draft"
    )
    
    await db.save(lesson)
    
    return lesson

@router.get("/lessons/{lesson_id}/reference-resource")
async def get_lesson_reference_resource(
    lesson_id: int,
    current_user: User = Depends(get_current_user)
) -> Optional[ResourceResponse]:
    """获取教案的参考资源"""
    lesson = await lesson_service.get_by_id(lesson_id)
    
    if not lesson.reference_resource_id:
        return None
    
    resource = await resource_service.get_by_id(lesson.reference_resource_id)
    return resource

@router.put("/lessons/{lesson_id}/reference-notes")
async def update_reference_notes(
    lesson_id: int,
    notes: str,
    current_user: User = Depends(get_current_teacher)
) -> LessonResponse:
    """更新参考笔记"""
    lesson = await lesson_service.update(
        lesson_id,
        reference_notes=notes
    )
    return lesson
```

### 4.3 前端服务层

```typescript
// frontend/src/services/resource.ts

export const resourceService = {
  // 获取章节资源列表
  async getChapterResources(
    chapterId: number, 
    resourceType?: string
  ): Promise<Resource[]> {
    const params = resourceType ? { resource_type: resourceType } : {}
    const response = await api.get(
      `/chapters/${chapterId}/resources`, 
      { params }
    )
    return response.data
  },
  
  // 获取资源详情
  async getResource(resourceId: number): Promise<ResourceDetail> {
    const response = await api.get(`/resources/${resourceId}`)
    return response.data
  },
  
  // 获取PDF预览URL
  getPDFPreviewUrl(resourceId: number): string {
    return `${API_BASE_URL}/resources/${resourceId}/preview`
  },
  
  // 下载资源
  async downloadResource(resourceId: number): Promise<Blob> {
    const response = await api.get(
      `/resources/${resourceId}/download`,
      { responseType: 'blob' }
    )
    return response.data
  },
  
  // 上传资源（管理员）
  async uploadResource(
    data: ResourceCreate, 
    file: File
  ): Promise<Resource> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('data', JSON.stringify(data))
    
    const response = await api.post('/resources', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }
}

// frontend/src/services/lesson.ts (扩展)

export const lessonService = {
  // ... 现有方法
  
  // 基于资源创建教案
  async createFromResource(
    data: CreateFromResourceRequest
  ): Promise<Lesson> {
    const response = await api.post('/lessons/from-resource', data)
    return response.data
  },
  
  // 获取教案的参考资源
  async getReferenceResource(lessonId: number): Promise<Resource | null> {
    const response = await api.get(`/lessons/${lessonId}/reference-resource`)
    return response.data
  },
  
  // 更新参考笔记
  async updateReferenceNotes(
    lessonId: number, 
    notes: string
  ): Promise<Lesson> {
    const response = await api.put(
      `/lessons/${lessonId}/reference-notes`,
      { notes }
    )
    return response.data
  }
}
```

### 4.4 前端类型定义

```typescript
// frontend/src/types/resource.ts

export enum ResourceType {
  PDF = 'pdf',
  VIDEO = 'video',
  DOCUMENT = 'document',
  LINK = 'link',
}

export interface Resource {
  id: number
  chapter_id: number
  title: string
  description: string
  resource_type: ResourceType
  
  // PDF 特定字段
  file_url?: string
  file_size?: number  // 字节
  page_count?: number
  thumbnail_url?: string
  
  // 权限和状态
  is_official: boolean
  is_downloadable: boolean
  view_count: number
  download_count: number
  
  created_at: string
  updated_at: string
}

export interface ResourceDetail extends Resource {
  chapter: {
    id: number
    name: string
    course_id: number
  }
  lessons_count: number  // 基于此资源创建的教案数量
}

export interface CreateFromResourceRequest {
  reference_resource_id: number
  title: string
  description?: string
  reference_notes?: string
  tags?: string[]
  estimated_duration?: number
}

// frontend/src/types/lesson.ts (扩展)

export interface Lesson {
  // ... 现有字段
  
  // 新增字段
  reference_resource_id?: number
  reference_resource?: Resource
  reference_notes?: string
  cell_count: number
  estimated_duration?: number
}
```

### 4.5 前端核心组件

#### A. PDF资源列表项

```vue
<!-- frontend/src/components/Resource/PDFResourceItem.vue -->
<template>
  <div class="pdf-resource-item">
    <div class="resource-header">
      <div class="resource-icon">📋</div>
      <div class="resource-info">
        <h4 class="resource-title">{{ resource.title }}</h4>
        <div class="resource-meta">
          <span>{{ formatFileSize(resource.file_size) }}</span>
          <span>{{ resource.page_count }} 页</span>
          <span>{{ resource.view_count }} 次查看</span>
        </div>
      </div>
    </div>
    
    <div class="resource-actions">
      <button @click="handlePreview" class="btn-preview">
        <svg>👁️</svg> 预览
      </button>
      <button 
        v-if="resource.is_downloadable"
        @click="handleDownload" 
        class="btn-download"
      >
        <svg>⬇️</svg> 下载
      </button>
      <button @click="handleCreateLesson" class="btn-create">
        <svg>📝</svg> 参考此资源创建教案
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Resource } from '../../types/resource'
import { resourceService } from '../../services/resource'

interface Props {
  resource: Resource
}

const props = defineProps<Props>()
const emit = defineEmits<{
  preview: [resourceId: number]
  createLesson: [resourceId: number]
}>()

function formatFileSize(bytes?: number): string {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function handlePreview() {
  emit('preview', props.resource.id)
}

async function handleDownload() {
  try {
    const blob = await resourceService.downloadResource(props.resource.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${props.resource.title}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed:', error)
  }
}

function handleCreateLesson() {
  emit('createLesson', props.resource.id)
}
</script>
```

#### B. PDF预览对话框

```vue
<!-- frontend/src/components/Resource/PDFViewerModal.vue -->
<template>
  <div v-if="modelValue" class="modal-overlay" @click.self="close">
    <div class="pdf-viewer-modal">
      <div class="modal-header">
        <h3>📋 {{ resource?.title }}</h3>
        <div class="header-actions">
          <button @click="handleDownload" title="下载">⬇️</button>
          <button @click="handleCreateLesson" title="参考此资源创建教案">
            📝 创建教案
          </button>
          <button @click="close" title="关闭">×</button>
        </div>
      </div>
      
      <div class="modal-body">
        <div class="pdf-container">
          <iframe
            v-if="pdfUrl"
            :src="pdfUrl"
            class="pdf-iframe"
            frameborder="0"
          />
          <div v-else class="loading">
            <div class="spinner"></div>
            <p>加载PDF中...</p>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <div class="page-info">
          <button 
            @click="prevPage" 
            :disabled="currentPage <= 1"
            class="btn-nav"
          >
            ◀️ 上一页
          </button>
          <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
          <button 
            @click="nextPage"
            :disabled="currentPage >= totalPages"
            class="btn-nav"
          >
            下一页 ▶️
          </button>
        </div>
        
        <button @click="handleCreateLesson" class="btn-primary">
          参考此资源创建教案
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Resource } from '../../types/resource'
import { resourceService } from '../../services/resource'

interface Props {
  modelValue: boolean
  resourceId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'create-lesson': [resourceId: number]
}>()

const resource = ref<Resource | null>(null)
const currentPage = ref(1)

const pdfUrl = computed(() => {
  if (!props.resourceId) return null
  return resourceService.getPDFPreviewUrl(props.resourceId)
})

const totalPages = computed(() => resource.value?.page_count || 1)

watch(() => props.resourceId, async (newId) => {
  if (newId) {
    resource.value = await resourceService.getResource(newId)
    currentPage.value = 1
  }
})

function close() {
  emit('update:modelValue', false)
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value--
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value++
}

async function handleDownload() {
  if (!props.resourceId) return
  const blob = await resourceService.downloadResource(props.resourceId)
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${resource.value?.title}.pdf`
  a.click()
  window.URL.revokeObjectURL(url)
}

function handleCreateLesson() {
  emit('create-lesson', props.resourceId)
  close()
}
</script>

<style scoped>
.pdf-iframe {
  width: 100%;
  height: 100%;
  min-height: 600px;
}
</style>
```

#### C. 基于资源创建教案对话框

```vue
<!-- frontend/src/components/Lesson/CreateLessonFromResourceModal.vue -->
<template>
  <div v-if="modelValue" class="modal-overlay" @click.self="close">
    <div class="modal-dialog">
      <div class="modal-header">
        <h3>参考官方教学设计创建教案</h3>
        <button @click="close">×</button>
      </div>
      
      <div class="modal-body">
        <!-- 参考资源信息 -->
        <div class="reference-section">
          <label>✓ 参考资源</label>
          <div class="resource-card">
            <div class="resource-icon">📋</div>
            <div class="resource-info">
              <div class="resource-title">{{ resource?.title }}</div>
              <div class="resource-path">
                章节：{{ chapterPath }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- 教案信息表单 -->
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="title">教案标题 <span class="required">*</span></label>
            <input
              id="title"
              v-model="formData.title"
              type="text"
              required
              placeholder="例如：集合的概念 - 高一(1)班"
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="description">教案描述</label>
            <textarea
              id="description"
              v-model="formData.description"
              rows="3"
              placeholder="简要描述您的教学设计思路..."
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="notes">参考笔记（可选）</label>
            <textarea
              id="notes"
              v-model="formData.reference_notes"
              rows="4"
              placeholder="记录您从PDF中获得的启发、需要重点关注的部分等..."
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="tags">标签</label>
            <input
              id="tags"
              v-model="tagsInput"
              type="text"
              placeholder="用逗号分隔，例如：集合, 高一, 基础"
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="duration">预计时长（分钟）</label>
            <input
              id="duration"
              v-model.number="formData.estimated_duration"
              type="number"
              min="1"
              placeholder="45"
              class="form-control"
            />
          </div>
        </form>
        
        <div class="info-tip">
          <svg>ℹ️</svg>
          <span>创建后，您可以添加文本、代码、问答等多种类型的教学单元</span>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="close" class="btn-secondary">取消</button>
        <button 
          @click="handleSubmit" 
          :disabled="isSubmitting"
          class="btn-primary"
        >
          {{ isSubmitting ? '创建中...' : '创建教案' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { Resource } from '../../types/resource'
import type { CreateFromResourceRequest } from '../../types/resource'
import { resourceService } from '../../services/resource'
import { lessonService } from '../../services/lesson'

interface Props {
  modelValue: boolean
  resourceId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const router = useRouter()
const resource = ref<Resource | null>(null)
const isSubmitting = ref(false)

const formData = ref({
  title: '',
  description: '',
  reference_notes: '',
  estimated_duration: 45,
})

const tagsInput = ref('')

const chapterPath = computed(() => {
  if (!resource.value) return ''
  // TODO: 从完整资源信息中获取路径
  return '高一数学 → 第一章 → 1.1 集合的概念'
})

watch(() => props.resourceId, async (newId) => {
  if (newId) {
    resource.value = await resourceService.getResource(newId)
    // 预填充标题
    formData.value.title = resource.value.title.replace('-教学设计', '')
  }
})

function close() {
  emit('update:modelValue', false)
}

async function handleSubmit() {
  if (!props.resourceId) return
  
  isSubmitting.value = true
  
  try {
    const tags = tagsInput.value
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0)
    
    const requestData: CreateFromResourceRequest = {
      reference_resource_id: props.resourceId,
      title: formData.value.title,
      description: formData.value.description || undefined,
      reference_notes: formData.value.reference_notes || undefined,
      tags: tags.length > 0 ? tags : undefined,
      estimated_duration: formData.value.estimated_duration || undefined,
    }
    
    const lesson = await lessonService.createFromResource(requestData)
    
    // 跳转到编辑器
    router.push(`/teacher/lesson/${lesson.id}`)
    
    close()
  } catch (error) {
    console.error('Failed to create lesson:', error)
    alert('创建教案失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

#### D. 增强课程结构组件

```vue
<!-- frontend/src/components/Curriculum/EnhancedCurriculumStructure.vue -->
<!-- 在现有基础上添加资源展示 -->

<script setup lang="ts">
// ... 现有代码

// 新增：资源相关状态
const selectedChapterId = ref<number | null>(null)
const chapterResources = ref<Resource[]>([])
const showPDFViewer = ref(false)
const selectedPDFId = ref<number | null>(null)
const showCreateModal = ref(false)

// 新增：加载章节资源
async function loadChapterResources(chapterId: number) {
  selectedChapterId.value = chapterId
  chapterResources.value = await resourceService.getChapterResources(chapterId)
}

// 新增：处理章节点击
function handleChapterClick(chapterId: number) {
  loadChapterResources(chapterId)
}

// 新增：预览PDF
function handlePreviewPDF(resourceId: number) {
  selectedPDFId.value = resourceId
  showPDFViewer.value = true
}

// 新增：参考资源创建教案
function handleCreateFromResource(resourceId: number) {
  selectedPDFId.value = resourceId
  showCreateModal.value = true
}
</script>

<template>
  <div class="enhanced-curriculum-structure">
    <!-- 现有的课程树结构 -->
    <CurriculumTree
      @chapter-select="handleChapterClick"
    />
    
    <!-- 新增：资源列表 -->
    <div v-if="selectedChapterId" class="resources-panel">
      <h3>📚 章节资源</h3>
      
      <div class="resource-list">
        <PDFResourceItem
          v-for="resource in chapterResources"
          :key="resource.id"
          :resource="resource"
          @preview="handlePreviewPDF"
          @create-lesson="handleCreateFromResource"
        />
      </div>
    </div>
    
    <!-- PDF预览对话框 -->
    <PDFViewerModal
      v-model="showPDFViewer"
      :resource-id="selectedPDFId!"
      @create-lesson="handleCreateFromResource"
    />
    
    <!-- 创建教案对话框 -->
    <CreateLessonFromResourceModal
      v-model="showCreateModal"
      :resource-id="selectedPDFId!"
    />
  </div>
</template>
```

#### E. 编辑器中的参考资源面板

```vue
<!-- frontend/src/components/Lesson/ReferenceResourcePanel.vue -->
<template>
  <div v-if="resource" class="reference-panel">
    <div class="panel-header">
      <div class="panel-title">
        <svg>📋</svg>
        <span>参考资料：{{ resource.title }}</span>
      </div>
      <div class="panel-actions">
        <button @click="handleViewPDF" class="btn-link">
          👁️ 查看PDF
        </button>
        <button @click="showNotesEditor = !showNotesEditor" class="btn-link">
          📝 {{ showNotesEditor ? '收起笔记' : '编辑笔记' }}
        </button>
        <button @click="emit('close')" class="btn-close">×</button>
      </div>
    </div>
    
    <div v-if="showNotesEditor" class="notes-editor">
      <textarea
        v-model="localNotes"
        placeholder="记录您的参考笔记..."
        rows="6"
        @blur="handleSaveNotes"
      />
      <div class="notes-hint">
        💡 提示：笔记会自动保存
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Resource } from '../../types/resource'
import { lessonService } from '../../services/lesson'

interface Props {
  lessonId: number
  resource: Resource
  notes?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  'view-pdf': [resourceId: number]
}>()

const showNotesEditor = ref(false)
const localNotes = ref(props.notes || '')

watch(() => props.notes, (newNotes) => {
  localNotes.value = newNotes || ''
})

function handleViewPDF() {
  emit('view-pdf', props.resource.id)
}

async function handleSaveNotes() {
  if (localNotes.value === props.notes) return
  
  try {
    await lessonService.updateReferenceNotes(
      props.lessonId,
      localNotes.value
    )
  } catch (error) {
    console.error('Failed to save notes:', error)
  }
}
</script>

<style scoped>
.reference-panel {
  background: #f0f7ff;
  border: 1px solid #b3d9ff;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #1a73e8;
}

.notes-editor {
  margin-top: 12px;
}

.notes-editor textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
}

.notes-hint {
  margin-top: 4px;
  font-size: 12px;
  color: #666;
}
</style>
```

#### F. 增强教案编辑器

```vue
<!-- frontend/src/pages/Teacher/LessonEditor.vue -->
<!-- 在现有基础上添加 -->

<script setup lang="ts">
// ... 现有代码

// 新增：参考资源
const referenceResource = ref<Resource | null>(null)
const showReferencePanel = ref(true)
const showPDFViewer = ref(false)

// 加载教案时，同时加载参考资源
onMounted(async () => {
  const lessonId = Number(route.params.id)
  
  if (!lessonId || isNaN(lessonId)) {
    loadError.value = '无效的教案 ID'
    isLoading.value = false
    return
  }

  try {
    await lessonStore.loadLesson(lessonId)
    lessonTitle.value = currentLesson.value?.title || ''
    
    // 新增：加载参考资源
    if (currentLesson.value?.reference_resource_id) {
      referenceResource.value = await lessonService.getReferenceResource(lessonId)
    }
    
    setTimeout(initSortable, 100)
  } catch (error: any) {
    loadError.value = error.message || '加载教案失败'
  } finally {
    isLoading.value = false
  }
})

function handleViewReferencePDF() {
  showPDFViewer.value = true
}
</script>

<template>
  <div class="lesson-editor">
    <!-- 顶部工具栏 -->
    <nav>...</nav>

    <!-- 主内容区 -->
    <div class="editor-content">
      <CellToolbar v-if="!isPreviewMode" />
      
      <main class="editor-main">
        <div class="container">
          <!-- 新增：参考资源面板 -->
          <ReferenceResourcePanel
            v-if="showReferencePanel && referenceResource && !isPreviewMode"
            :lesson-id="currentLesson!.id"
            :resource="referenceResource"
            :notes="currentLesson?.reference_notes"
            @close="showReferencePanel = false"
            @view-pdf="handleViewReferencePDF"
          />
          
          <!-- Cell 列表 -->
          <div v-if="currentLesson" class="cells-container">
            <!-- ... 现有 Cell 渲染代码 -->
          </div>
        </div>
      </main>
    </div>
    
    <!-- PDF查看器 -->
    <PDFViewerModal
      v-model="showPDFViewer"
      :resource-id="referenceResource?.id"
    />
  </div>
</template>
```

---

## 五、MVP 开发计划

### 第一周：后端基础 + 资源管理

**目标：** 完成资源的数据模型和基础 API

- [ ] Day 1-2: 数据库迁移
  - 扩展 `resources` 表（PDF 字段）
  - 扩展 `lessons` 表（参考资源字段）
  - 编写迁移脚本

- [ ] Day 3-4: 资源 API
  - 实现资源 CRUD
  - 实现文件上传（本地存储或OSS）
  - 实现 PDF 元数据提取

- [ ] Day 5: 教案 API 扩展
  - 实现基于资源创建教案 API
  - 实现参考笔记更新 API

**可交付：** 后端 API 可以上传PDF、创建教案并关联资源

### 第二周：前端资源展示

**目标：** 在课程结构中展示资源，支持预览和下载

- [ ] Day 1-2: 类型定义和服务层
  - 定义 Resource 类型
  - 实现 resourceService
  - 扩展 lessonService

- [ ] Day 3-4: 资源展示组件
  - 实现 PDFResourceItem 组件
  - 增强 EnhancedCurriculumStructure
  - 在章节节点下显示资源列表

- [ ] Day 5: PDF预览
  - 实现 PDFViewerModal 组件
  - 集成 PDF.js 或 vue-pdf
  - 测试预览功能

**可交付：** 教师可以浏览课程，查看PDF资源，预览PDF

### 第三周：创建教案流程

**目标：** 完成从PDF到创建教案的完整流程

- [ ] Day 1-2: 创建教案组件
  - 实现 CreateLessonFromResourceModal
  - 集成到资源列表和PDF预览

- [ ] Day 3-4: 编辑器增强
  - 实现 ReferenceResourcePanel
  - 在编辑器中显示参考资源
  - 实现参考笔记功能

- [ ] Day 5: 测试和优化
  - 完整流程测试
  - UI/UX 优化
  - 性能优化

**可交付：** 教师可以参考PDF创建教案，在编辑器中查看参考资料

### 第四周：管理功能 + 收尾

**目标：** 完成管理员上传功能，整体优化

- [ ] Day 1-2: 管理后台
  - 资源上传界面
  - 资源管理列表
  - 权限控制

- [ ] Day 3-4: 统计和优化
  - 查看/下载统计
  - 基于资源的教案列表
  - 性能优化

- [ ] Day 5: 文档和部署
  - API 文档
  - 用户指南
  - 部署和测试

**可交付：** 完整的 MVP 系统，可投入使用

---

## 六、技术要点

### 6.1 文件存储方案

**方案A：本地存储（开发/小规模）**
```python
# backend/app/services/upload.py

import os
from fastapi import UploadFile
from uuid import uuid4

UPLOAD_DIR = "storage/resources"

async def upload_file(file: UploadFile) -> str:
    # 生成唯一文件名
    ext = file.filename.split('.')[-1]
    filename = f"{uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # 保存文件
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 返回URL
    return f"/storage/resources/{filename}"
```

**方案B：对象存储（生产环境）**
```python
# 使用阿里云OSS、AWS S3等

from oss2 import Auth, Bucket

async def upload_to_oss(file: UploadFile) -> str:
    auth = Auth(access_key_id, access_key_secret)
    bucket = Bucket(auth, endpoint, bucket_name)
    
    filename = f"resources/{uuid4()}.pdf"
    content = await file.read()
    
    bucket.put_object(filename, content)
    
    return f"https://{bucket_name}.{endpoint}/{filename}"
```

### 6.2 PDF 处理

```python
# backend/app/services/pdf_processor.py

import PyPDF2
from PIL import Image
import fitz  # PyMuPDF

async def extract_pdf_metadata(file_path: str) -> dict:
    """提取PDF元数据"""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return {
            'page_count': len(reader.pages),
            'title': reader.metadata.get('/Title', ''),
            'author': reader.metadata.get('/Author', ''),
        }

async def generate_pdf_thumbnail(
    file_path: str, 
    page: int = 0
) -> str:
    """生成PDF缩略图"""
    doc = fitz.open(file_path)
    page = doc[page]
    
    # 渲染为图片
    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
    
    # 保存缩略图
    thumbnail_path = f"storage/thumbnails/{uuid4()}.png"
    pix.save(thumbnail_path)
    
    doc.close()
    
    return thumbnail_path
```

### 6.3 PDF 前端预览

**方案A：使用iframe（简单）**
```vue
<iframe :src="pdfUrl" width="100%" height="600px" />
```

**方案B：使用 vue-pdf（更好控制）**
```bash
npm install vue3-pdf
```

```vue
<template>
  <VuePDF
    :pdf="pdfUrl"
    :page="currentPage"
    @loaded="handleLoaded"
  />
</template>

<script setup>
import { VuePDF } from 'vue3-pdf'
</script>
```

---

## 七、测试场景

### 7.1 教师使用流程测试

1. **浏览课程找到PDF**
   - 登录 → 教师仪表盘
   - 打开课程结构
   - 展开章节，看到PDF资源

2. **预览PDF**
   - 点击"预览"按钮
   - PDF对话框打开
   - 可以翻页、查看内容

3. **创建教案**
   - 点击"参考此资源创建教案"
   - 填写教案信息
   - 添加参考笔记
   - 点击"创建教案"

4. **编辑教案**
   - 自动跳转到编辑器
   - 看到参考资源面板
   - 可以快速查看PDF
   - 添加教学单元
   - 编辑参考笔记

5. **保存和发布**
   - 自动保存
   - 点击发布

### 7.2 管理员使用流程测试

1. **上传PDF**
   - 登录管理后台
   - 选择章节
   - 上传PDF文件
   - 填写标题和描述

2. **管理资源**
   - 查看资源列表
   - 查看统计数据（查看次数、基于此资源的教案数）
   - 编辑/删除资源

---

## 八、总结

### MVP 核心价值

1. **简化流程**
   - PDF作为参考，不可修改，降低复杂度
   - 教师独立创作，灵活度高
   - 关联关系清晰，易于理解

2. **技术实现**
   - 基于现有架构，增量开发
   - 4周可完成MVP
   - 技术风险低

3. **用户体验**
   - 流程自然流畅
   - 操作简单直观
   - 符合教师习惯

### 下一步

1. ✅ 确认技术方案（文件存储方式）
2. ✅ 开始第一周开发（后端基础）
3. ✅ 准备测试数据（示例PDF）

需要我开始实施具体的代码吗？从哪个部分开始？

**文档版本：** v1.0  
**最后更新：** 2025-10-17


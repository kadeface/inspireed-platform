# MVP 开发环境搭建指南

## 🚀 快速开始

### 1. 安装依赖

#### 后端依赖

```bash
cd backend

# 激活虚拟环境（如果还没有）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**新增依赖说明：**
- `PyPDF2` - PDF 元数据提取
- `PyMuPDF` - PDF 缩略图生成
- `aiofiles` - 异步文件操作
- `Pillow` - 图像处理

### 2. 数据库迁移

```bash
# 确保在 backend 目录下
cd backend

# 运行迁移
alembic upgrade head
```

**本次迁移内容：**
- ✅ 创建 `chapters` 表（章节）
- ✅ 创建 `resources` 表（资源）
- ✅ 扩展 `lessons` 表（添加参考资源字段）

### 3. 创建测试数据

```bash
# 在 backend 目录下
python scripts/create_test_data.py
```

**测试数据包含：**
- 📚 高一数学课程
- 📖 第一章：集合与函数
- 📝 1.1 集合的概念（小节）
- 📋 集合的概念 - 教学设计.pdf（官方PDF资源）
- 🎥 集合的概念 - 讲解视频（视频资源）
- 👨‍🏫 示例教案（基于PDF创建的教案）

**测试账号：**
```
邮箱：teacher@test.com
密码：password123
角色：教师
```

### 4. 启动后端服务

```bash
# 在 backend 目录下
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：http://localhost:8000/docs

---

## 📋 Week 1 完成情况

### ✅ 已完成

1. **数据库模型**
   - Chapter（章节）模型
   - Resource（资源）模型
   - 扩展 Lesson（教案）模型
   - 数据库迁移文件

2. **文件上传服务**
   - PDF 上传和元数据提取
   - 自动生成缩略图
   - 文件管理功能
   - 本地存储实现

3. **资源 CRUD API**
   - GET /chapters/{chapter_id}/resources - 获取章节资源列表
   - GET /resources/{resource_id} - 获取资源详情
   - POST /resources - 创建资源（管理员）
   - PUT /resources/{resource_id} - 更新资源
   - DELETE /resources/{resource_id} - 删除资源
   - POST /resources/{resource_id}/download - 下载资源

4. **章节 API**
   - GET /courses/{course_id}/chapters - 获取课程章节（树形）
   - GET /chapters/{chapter_id} - 获取章节详情
   - POST /chapters - 创建章节（管理员）
   - PUT /chapters/{chapter_id} - 更新章节
   - DELETE /chapters/{chapter_id} - 删除章节

5. **教案 API 扩展**
   - POST /lessons/from-resource - 基于资源创建教案
   - GET /lessons/{lesson_id}/reference-resource - 获取参考资源
   - PUT /lessons/{lesson_id}/reference-notes - 更新参考笔记

---

## 🧪 API 测试示例

### 1. 登录获取 Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=teacher@test.com&password=password123"
```

### 2. 获取章节资源列表

```bash
curl -X GET "http://localhost:8000/api/v1/chapters/1/resources" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 查看资源详情

```bash
curl -X GET "http://localhost:8000/api/v1/resources/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 基于资源创建教案

```bash
curl -X POST "http://localhost:8000/api/v1/lessons/from-resource" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reference_resource_id": 1,
    "title": "集合的概念 - 高一(2)班",
    "description": "根据官方教学设计创建的个性化教案",
    "reference_notes": "参考了PDF中的教学目标和重点",
    "tags": ["集合", "高一", "基础"],
    "estimated_duration": 45
  }'
```

### 5. 上传 PDF 资源（管理员）

```bash
curl -X POST "http://localhost:8000/api/v1/resources" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -F "chapter_id=1" \
  -F "title=新教学设计" \
  -F "description=最新版本的教学设计文档" \
  -F "resource_type=pdf" \
  -F "is_official=true" \
  -F "file=@/path/to/your/file.pdf"
```

---

## 📁 文件存储结构

```
backend/
├── storage/              # 文件上传根目录
│   ├── resources/        # 资源文件（PDF、视频等）
│   │   └── *.pdf
│   └── thumbnails/       # PDF 缩略图
│       └── *.png
```

**注意：** `storage/` 目录会自动创建，首次上传文件时生成。

---

## 🔧 配置说明

在 `backend/.env` 或环境变量中配置：

```env
# 文件上传配置
UPLOAD_DIR=storage           # 上传目录
MAX_UPLOAD_SIZE=104857600    # 最大上传大小（100MB）
```

---

## 🐛 常见问题

### 1. PyMuPDF 安装失败

如果 `PyMuPDF` 安装失败，缩略图生成功能会自动跳过，不影响其他功能。

可以尝试：
```bash
pip install --upgrade pip
pip install PyMuPDF
```

### 2. 数据库连接错误

确保 PostgreSQL 服务已启动，并且 `.env` 文件中的数据库配置正确。

```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=inspireed
POSTGRES_PORT=5432
```

### 3. 迁移版本冲突

如果遇到迁移版本问题：

```bash
# 查看当前版本
alembic current

# 回滚到某个版本
alembic downgrade 001

# 重新升级
alembic upgrade head
```

---

## 📊 数据库 ER 图

```
Subject (学科)
  └── Grade (年级)
       └── Course (课程)
            ├── Chapter (章节)
            │    ├── parent_id → Chapter (多级章节)
            │    └── Resource (资源)
            │         └── resource_type: pdf/video/document/link
            │
            └── Lesson (教案)
                 └── reference_resource_id → Resource
```

---

## 🎯 下一步（Week 2）

Week 1 已全部完成！接下来开始前端开发：

1. ✅ 前端类型定义
2. ✅ 前端服务层
3. ✅ PDFResourceItem 组件
4. ✅ PDF 预览对话框

---

## 📚 相关文档

- [MVP 设计方案](./MVP_LESSON_FROM_PDF.md)
- [开发进度](./MVP_PROGRESS.md)
- [教师工作流](./TEACHER_WORKFLOW.md)

---

**最后更新：** 2025-10-17  
**作者：** InspireEd 开发团队


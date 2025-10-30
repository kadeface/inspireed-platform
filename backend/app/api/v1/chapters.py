"""
章节管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import pandas as pd
import io

from app.core.database import get_db
from app.models import Chapter, Course, Resource, User
from app.schemas.chapter import (
    ChapterCreate, ChapterUpdate, ChapterResponse,
    ChapterWithChildren, ChapterListResponse
)
from app.schemas.resource import ResourceListResponse
from app.api.deps import get_current_user, get_current_admin, get_current_researcher

router = APIRouter()


# ==================== 特定路径路由（必须在通用路径之前） ====================

@router.get("/export-template")
async def get_import_template():
    """获取章节导入模板"""
    
    # 创建示例数据
    template_data = [
        {
            'name': '第一章：集合与函数',
            'code': 'chapter-1',
            'description': '介绍集合的基本概念和运算',
            'display_order': 1,
            'parent_code': '',  # 空表示顶级章节
            'is_active': True
        },
        {
            'name': '1.1 集合的概念',
            'code': 'section-1-1',
            'description': '学习集合的定义和表示方法',
            'display_order': 1,
            'parent_code': 'chapter-1',  # 引用父章节的code
            'is_active': True
        },
        {
            'name': '1.2 集合的运算',
            'code': 'section-1-2',
            'description': '掌握集合的交集、并集、补集运算',
            'display_order': 2,
            'parent_code': 'chapter-1',
            'is_active': True
        },
        {
            'name': '第二章：函数',
            'code': 'chapter-2',
            'description': '学习函数的概念和性质',
            'display_order': 2,
            'parent_code': '',
            'is_active': True
        }
    ]
    
    # 创建DataFrame
    df = pd.DataFrame(template_data)
    
    # 转换为Excel字节流
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='章节模板', index=False)
    
    output.seek(0)
    
    # 返回StreamingResponse以便浏览器可以下载文件
    # 使用URL编码的文件名以支持中文
    import urllib.parse
    filename = urllib.parse.quote("章节导入模板.xlsx")
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
    )


@router.post("/batch-import")
async def batch_import_chapters(
    course_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_researcher)
):
    """批量导入章节（仅教研员）"""
    
    # 验证课程是否存在
    course = await db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    
    # 验证文件类型
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(400, f"File must be Excel (.xlsx, .xls) or CSV (.csv). Got: {file.filename}")
    
    try:
        # 读取文件内容
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(400, "Uploaded file is empty")
        
        # 根据文件类型读取数据
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            else:
                df = pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(400, f"Failed to read file: {str(e)}")
        
        # 验证必需的列
        required_columns = ['name', 'code', 'display_order']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(400, f"Missing required columns: {missing_columns}")
        
        # 处理数据
        chapters_to_create = []
        chapter_code_map = {}  # 用于处理父子关系
        
        for index, row in df.iterrows():
            # 基本验证
            if pd.isna(row['name']) or pd.isna(row['code']):
                continue
            
            chapter_data = {
                'course_id': course_id,
                'name': str(row['name']).strip(),
                'code': str(row['code']).strip(),
                'display_order': int(row['display_order']) if not pd.isna(row['display_order']) else 0,
                'description': str(row.get('description', '')).strip() if not pd.isna(row.get('description')) else None,
                'parent_code': str(row.get('parent_code', '')).strip() if not pd.isna(row.get('parent_code')) else None,
                'is_active': bool(row.get('is_active', True)) if not pd.isna(row.get('is_active')) else True
            }
            
            chapters_to_create.append(chapter_data)
        
        # 创建章节
        created_chapters = []
        for chapter_data in chapters_to_create:
            # 处理父章节关系
            parent_id = None
            if chapter_data['parent_code']:
                parent_id = chapter_code_map.get(chapter_data['parent_code'])
                if not parent_id:
                    raise HTTPException(400, f"Parent chapter with code '{chapter_data['parent_code']}' not found or not yet created")
            
            # 创建章节
            chapter = Chapter(
                course_id=chapter_data['course_id'],
                parent_id=parent_id,
                name=chapter_data['name'],
                code=chapter_data['code'],
                description=chapter_data['description'],
                display_order=chapter_data['display_order'],
                is_active=chapter_data['is_active']
            )
            
            db.add(chapter)
            await db.commit()
            await db.refresh(chapter)
            
            # 记录章节代码映射
            chapter_code_map[chapter.code] = chapter.id
            created_chapters.append(chapter)
        
        return {
            "message": f"Successfully imported {len(created_chapters)} chapters",
            "chapters": [ChapterResponse.from_orm(ch) for ch in created_chapters]
        }
        
    except Exception as e:
        raise HTTPException(400, f"Import failed: {str(e)}")


# ==================== 通用路径路由 ====================

@router.get("/courses/{course_id}/chapters", response_model=List[ChapterWithChildren])
async def get_course_chapters(
    course_id: int,
    include_children: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取课程的章节列表（树形结构）"""
    
    # 验证课程是否存在
    course = await db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    
    # 获取所有章节及其资源数量
    query = select(
        Chapter,
        func.count(Resource.id).label('resources_count')
    ).outerjoin(Resource, and_(
        Resource.chapter_id == Chapter.id,
        Resource.is_active == True
    )).where(
        and_(
            Chapter.course_id == course_id,
            Chapter.is_active == True
        )
    ).group_by(Chapter.id).order_by(Chapter.display_order, Chapter.id)
    
    result = await db.execute(query)
    chapters_with_counts = result.all()
    chapters = [row[0] for row in chapters_with_counts]
    resource_counts = {row[0].id: row[1] for row in chapters_with_counts}
    
    # 如果需要树形结构
    if include_children:
        # 构建章节树
        chapter_dict = {ch.id: ChapterWithChildren(
            id=ch.id,
            course_id=ch.course_id,
            parent_id=ch.parent_id,
            name=ch.name,
            code=ch.code,
            description=ch.description,
            display_order=ch.display_order,
            is_active=ch.is_active,
            created_at=ch.created_at,
            updated_at=ch.updated_at,
            children=[],
            resources_count=resource_counts.get(ch.id, 0)
        ) for ch in chapters}
        
        # 构建父子关系
        root_chapters = []
        for chapter in chapters:
            if chapter.parent_id is None:
                root_chapters.append(chapter_dict[chapter.id])
            else:
                if chapter.parent_id in chapter_dict:
                    chapter_dict[chapter.parent_id].children.append(chapter_dict[chapter.id])
        
        return root_chapters
    else:
        return [ChapterWithChildren(
            id=ch.id,
            course_id=ch.course_id,
            parent_id=ch.parent_id,
            name=ch.name,
            code=ch.code,
            description=ch.description,
            display_order=ch.display_order,
            is_active=ch.is_active,
            created_at=ch.created_at,
            updated_at=ch.updated_at,
            children=[],
            resources_count=resource_counts.get(ch.id, 0)
        ) for ch in chapters]


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取章节详情"""
    
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(404, "Chapter not found")
    
    return chapter


@router.post("", response_model=ChapterResponse)
async def create_chapter(
    data: ChapterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建章节（管理员）"""
    
    # 验证课程是否存在
    course = await db.get(Course, data.course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    
    # 如果有父章节，验证父章节是否存在
    if data.parent_id:
        parent = await db.get(Chapter, data.parent_id)
        if not parent:
            raise HTTPException(404, "Parent chapter not found")
        if parent.course_id != data.course_id:
            raise HTTPException(400, "Parent chapter must belong to the same course")
    
    # 创建章节
    chapter = Chapter(**data.model_dump())
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    
    return chapter


@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: int,
    data: ChapterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """更新章节（管理员）"""
    
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(404, "Chapter not found")
    
    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)
    
    await db.commit()
    await db.refresh(chapter)
    
    return chapter


@router.delete("/{chapter_id}")
async def delete_chapter(
    chapter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """删除章节（管理员）"""
    
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(404, "Chapter not found")
    
    # 检查是否有子章节
    result = await db.execute(select(Chapter).where(Chapter.parent_id == chapter_id))
    children = result.scalars().all()
    if children:
        raise HTTPException(400, "Cannot delete chapter with children")
    
    # 检查是否有资源
    result = await db.execute(select(Resource).where(Resource.chapter_id == chapter_id))
    resources = result.scalars().all()
    if resources:
        raise HTTPException(400, "Cannot delete chapter with resources")
    
    await db.delete(chapter)
    await db.commit()
    
    return {"message": "Chapter deleted successfully"}


@router.get("/{chapter_id}/resources", response_model=ResourceListResponse)
async def get_chapter_resources(
    chapter_id: int,
    resource_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取章节的资源列表"""
    
    # 验证章节是否存在
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(404, "Chapter not found")
    
    # 构建查询
    query = select(Resource).where(
        and_(
            Resource.chapter_id == chapter_id,
            Resource.is_active == True
        )
    )
    
    # 按类型筛选
    if resource_type:
        query = query.where(Resource.resource_type == resource_type)
    
    # 排序
    query = query.order_by(Resource.display_order, Resource.created_at.desc())
    
    # 总数
    count_query = select(func.count()).select_from(Resource).where(
        and_(
            Resource.chapter_id == chapter_id,
            Resource.is_active == True
        )
    )
    if resource_type:
        count_query = count_query.where(Resource.resource_type == resource_type)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return ResourceListResponse(
        items=resources,
        total=total,
        page=page,
        page_size=page_size
    )
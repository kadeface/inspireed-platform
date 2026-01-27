# URL存储格式问题分析

## 问题描述

用户发现的HTML内容中，图片URL存储格式为：
```html
<img src="http://192.168.1.102:8000/uploads/resources/4d80f8c8-1e99-46eb-87d0-bb2c5b2f8332.png">
```

**问题**：根据方案2的设计，数据库中应该只存储文件名：
```html
<img src="4d80f8c8-1e99-46eb-87d0-bb2c5b2f8332.png">
```

## 可能的原因

### 1. 旧数据（在实现方案2之前保存的）

最可能的原因是：这些数据是在实现方案2之前保存的。在方案2实施之前，系统可能存储的是完整URL或相对路径。

**验证方法**：
- 检查这些教案的 `updated_at` 时间戳
- 如果是方案2实施之前的日期，说明是旧数据

### 2. 前端保存逻辑未正确执行

虽然 `TipTapEditor.vue` 的 `onUpdate` 中已经实现了 `extractFilename` 函数，但可能在某些情况下没有正确执行：

- 如果HTML内容通过其他方式更新（不是通过 `TipTapEditor` 的 `onUpdate`）
- 如果正则表达式没有匹配到所有URL格式
- 如果用户直接在数据库或其他界面修改了内容

## 解决方案

### 方案A：创建数据迁移脚本（推荐用于旧数据）

创建一个数据迁移脚本，将数据库中所有教案的HTML内容中的完整URL转换为文件名：

```python
# backend/scripts/migrate_lesson_urls_to_filename.py
"""
将教案内容中的完整URL转换为文件名
"""
import asyncio
import re
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.lesson import Lesson
from app.utils.resource_url import url_to_filename

async def migrate_lesson_urls():
    """将教案HTML内容中的URL转换为文件名"""
    async with AsyncSessionLocal() as db:
        # 获取所有教案
        result = await db.execute(select(Lesson))
        lessons = result.scalars().all()
        
        updated_count = 0
        
        for lesson in lessons:
            if not lesson.content or not isinstance(lesson.content, list):
                continue
            
            content_changed = False
            new_content = []
            
            for cell in lesson.content:
                if not isinstance(cell, dict) or cell.get('type') != 'text':
                    new_content.append(cell)
                    continue
                
                cell_content = cell.get('content', {})
                html = cell_content.get('html', '')
                
                if html and '<img' in html:
                    # 提取所有img标签的src
                    def replace_url(match):
                        quote = match.group(1)  # " 或 '
                        url = match.group(2)
                        
                        # 如果是完整URL，提取文件名
                        if url.startswith(('http://', 'https://')):
                            filename = url_to_filename(url)
                            return f'src={quote}{filename}{quote}'
                        elif url.startswith('/uploads/'):
                            filename = url_to_filename(url)
                            return f'src={quote}{filename}{quote}'
                        # 如果已经是文件名，保持不变
                        return match.group(0)
                    
                    # 替换img标签中的src
                    new_html = re.sub(
                        r'src\s*=\s*(["\'])([^"\']+)\1',
                        replace_url,
                        html,
                        flags=re.IGNORECASE
                    )
                    
                    if new_html != html:
                        cell = dict(cell)  # 创建副本
                        cell['content'] = dict(cell_content)
                        cell['content']['html'] = new_html
                        content_changed = True
                
                new_content.append(cell)
            
            if content_changed:
                lesson.content = new_content
                updated_count += 1
                print(f"更新教案 ID={lesson.id}: {lesson.title}")
        
        if updated_count > 0:
            await db.commit()
            print(f"\n总共更新了 {updated_count} 个教案")
        else:
            print("\n没有需要更新的教案")

if __name__ == "__main__":
    asyncio.run(migrate_lesson_urls())
```

### 方案B：修复前端保存逻辑

确保 `TextCell.vue` 的 `handleUpdate` 在保存前也处理URL转换：

```typescript
function handleUpdate() {
  // 在保存前，确保HTML中的URL都是文件名格式
  const cellToSave = { ...props.cell }
  
  if (cellToSave.content?.html) {
    let html = cellToSave.content.html
    
    // 使用与TipTapEditor相同的逻辑提取文件名
    html = html.replace(/<img\s+([^>]*?)>/gi, (match, attrs) => {
      const srcMatch = attrs.match(/\ssrc\s*=\s*(["'])([^"']+)\1/i)
      if (srcMatch) {
        const quote = srcMatch[1]
        let src = srcMatch[2]
        
        if (src.startsWith('blob:') || src.startsWith('data:')) {
          return match
        }
        
        // 提取文件名
        if (src.includes('/uploads/') || src.startsWith('http://') || src.startsWith('https://') || src.startsWith('/')) {
          const filename = extractFilename(src)
          const newSrcAttr = ` src=${quote}${filename}${quote}`
          return match.replace(srcMatch[0], newSrcAttr)
        }
      }
      return match
    })
    
    cellToSave.content.html = html
  }
  
  emit('update', cellToSave)
}
```

## 验证方法

运行数据检查脚本：
```bash
cd backend
source venv/bin/activate
python check_db_html_urls.py
```

查看输出，确认是否还有完整URL格式的数据。

## 建议

1. **对于旧数据**：运行数据迁移脚本，一次性转换所有旧数据
2. **对于新数据**：确保前端保存逻辑正确（TipTapEditor已经处理，但TextCell也需要确保）
3. **测试验证**：
   - 上传新图片
   - 保存教案
   - 检查数据库中的HTML内容，确认只存储文件名
   - 通过API获取教案，确认返回的是完整URL


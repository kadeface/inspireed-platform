# HTML 缩略图生成功能设置

## 概述

系统现在支持为 HTML 交互式课件自动生成缩略图。当上传 HTML 文件时，系统会自动生成一张预览图作为缩略图。

## 安装步骤

### 1. 安装 Playwright Python 包

```bash
pip install playwright==1.40.0
```

或者如果使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 安装浏览器

Playwright 需要安装浏览器才能工作。运行以下命令安装 Chromium：

```bash
playwright install chromium
```

或者安装所有浏览器（包括 Chromium、Firefox 和 WebKit）：

```bash
playwright install
```

### 3. 验证安装

安装完成后，可以测试一下：

```python
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://example.com')
        await browser.close()
    print("Playwright 安装成功！")

import asyncio
asyncio.run(test())
```

## 功能说明

- **自动生成**：上传 HTML 文件时，系统会自动生成缩略图
- **尺寸**：缩略图尺寸为 800x450 像素（16:9 比例）
- **格式**：PNG 格式
- **存储位置**：`/uploads/thumbnails/` 目录

## 故障排除

### Playwright 未安装

如果看到错误信息 "Playwright not installed"，请按照上述步骤安装 Playwright。

### 浏览器未安装

如果看到错误信息 "Executable doesn't exist"，请运行 `playwright install chromium`。

### 权限问题

确保应用有权限：
- 读取 HTML 文件
- 写入缩略图目录
- 执行浏览器进程

## 备选方案

如果无法安装 Playwright，系统会跳过缩略图生成，但不会影响文件上传功能。资源库会显示默认的图标（🎮）而不是缩略图。

## 性能考虑

- 生成缩略图可能需要几秒钟时间
- 建议在生产环境中使用缓存机制
- 对于大量文件，可以考虑异步批量生成缩略图

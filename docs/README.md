# 文档目录结构说明

本目录包含项目中的各类文档和零散文件，已按照用途进行分类整理。

## 目录结构

### 📚 guides/ - 开发指南
包含项目快速开始和开发相关的指南文档：
- `QUICK_START.md` - 快速开始指南
- `QUICK_START_BACKEND.md` - 后端快速开始指南
- `START_SCRIPTS_GUIDE.md` - 启动脚本使用指南

### 🔧 fixes/ - 问题修复文档
包含已知问题的修复说明：
- `FIX_LOGIN_401.md` - 登录 401 错误修复
- `FIX_LOGIN_500.md` - 登录 500 错误修复
- `FIX_LOGIN_ERR_FAILED.md` - 登录失败错误修复
- `BACKEND_RESTART_REQUIRED.md` - 后端重启要求说明
- `ACTIVITY_MODULE_FIX_README.md` - 活动模块修复说明

### 🚀 deployment/ - 部署相关文档
包含各种部署场景的配置和说明：
- `TENCENT_CLOUD_DEPLOYMENT.md` - 腾讯云部署指南
- `DOCKER_COMPOSE_BAKE.md` - Docker Compose 配置说明
- `CLOUDSTUDIO_QUICK_START.md` - CloudStudio 快速开始
- `CLOUDSTUDIO_PREVIEW_OUTPUT.md` - CloudStudio 预览输出说明
- `CLOUDSTUDIO_HTTPS_FIX.md` - CloudStudio HTTPS 修复

### 🐛 debug/ - 调试相关文档
包含调试和问题排查的文档：
- `DEBUG_CHECKLIST.md` - 调试检查清单
- `CONFIG_LOADING_EXPLANATION.md` - 配置加载说明

### 🎮 interactive-content/ - 互动内容
包含各种 HTML 互动游戏和课件：
- `area_model.html` - 面积模型
- `cardinal_ordinal_game.html` - 基数序数游戏
- `elementary-engineering-interactive.html` - 小学工程互动
- `elevator_challenge.html` - 电梯挑战
- `number_line_game.html` - 数轴游戏
- `orchard_assistant.html` - 果园助手
- `staircase_builder.html` - 楼梯构建器
- `html-preview.html` - HTML 预览
- `test-from-remote.html` - 远程测试
- `七孔桥.html` - 七孔桥
- `双主角排队.html` - 双主角排队
- `双主角排队1.html` - 双主角排队1
- `煎饼.html` - 煎饼

### 🧪 tests/ - 测试相关文件
包含测试脚本和测试文件：
- `test_course_export_import.py` - 课程导出导入测试
- `DEBUG_SCRIPT.js` - 调试脚本
- `test-from-remote.html` - 远程测试（如果存在）

### 💡 misc/ - 其他文档
包含其他类型的文档和资源：
- `AI_ASSISTANT_WORKFLOW.md` - AI 助手工作流
- `VIDEO_SCRIPT_2MIN.md` - 2分钟视频脚本
- `X6_MIGRATION_CHECKLIST.md` - X6 迁移检查清单
- `InspireEd 探究式STEM教学系统.md` - InspireEd 探究式STEM教学系统说明
- `assets_tmp_*.png` - 临时资源文件

### 📝 examples/ - 示例代码
包含示例代码文件：
- `app.py` - Flask 应用示例
- `main.py` - 主程序示例
- `languages.py` - 语言数据示例

## 注意事项

1. **启动脚本保留在根目录**：`start.sh`, `stop.sh`, `restart.sh` 等启动脚本保留在项目根目录，便于直接使用。

2. **配置文件保留在根目录**：`package.json`, `README.md` 等核心配置文件保留在根目录。

3. **查找文件**：如果找不到某个文档，请先在此目录结构中查找。

## 整理时间

本文档结构整理于：2025-01-27

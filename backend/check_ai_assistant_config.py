#!/usr/bin/env python3
"""
检查 AI Assistant 配置脚本
用于诊断 AI 助手调用大模型的相关配置问题
"""

import os
import sys
from pathlib import Path

# 添加项目路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_env_file():
    """检查 .env 文件"""
    print("=" * 80)
    print("1. 检查 .env 文件")
    print("=" * 80)
    
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print(f"❌ .env 文件不存在: {env_file}")
        print(f"   请从 env.example 复制并配置: cp {backend_dir / 'env.example'} {env_file}")
        return False
    
    print(f"✅ .env 文件存在: {env_file}")
    
    # 读取并检查 OPENAI_API_KEY
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        
        api_key_line = None
        for line in lines:
            if line.strip().startswith('OPENAI_API_KEY'):
                api_key_line = line.strip()
                break
        
        if api_key_line:
            # 提取值
            if '=' in api_key_line:
                key_value = api_key_line.split('=', 1)[1].strip()
                if key_value and key_value != 'sk-your-openai-api-key' and key_value.strip():
                    masked_key = key_value[:10] + '...' + key_value[-4:] if len(key_value) > 14 else '***'
                    print(f"✅ OPENAI_API_KEY 已配置: {masked_key}")
                    return True
                else:
                    print(f"❌ OPENAI_API_KEY 未正确配置（空值或默认值）")
                    print(f"   当前值: {key_value[:20] if key_value else 'empty'}")
                    return False
            else:
                print(f"❌ OPENAI_API_KEY 格式错误")
                return False
        else:
            print(f"❌ OPENAI_API_KEY 未在 .env 文件中找到")
            return False

def check_settings():
    """检查配置加载"""
    print("\n" + "=" * 80)
    print("2. 检查配置加载")
    print("=" * 80)
    
    try:
        from app.core.config import settings
        
        # 检查 API 密钥
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if api_key and api_key.strip() and api_key != "sk-your-openai-api-key":
            masked_key = api_key[:10] + '...' + api_key[-4:] if len(api_key) > 14 else '***'
            print(f"✅ OPENAI_API_KEY 已加载: {masked_key}")
        else:
            print(f"❌ OPENAI_API_KEY 未加载或无效")
            print(f"   当前值: {api_key[:20] if api_key else 'None'}")
        
        # 检查其他配置
        print(f"📋 OPENAI_BASE_URL: {getattr(settings, 'OPENAI_BASE_URL', 'N/A')}")
        print(f"📋 DEFAULT_AI_MODEL: {getattr(settings, 'DEFAULT_AI_MODEL', 'N/A')}")
        print(f"📋 AI_MAX_TOKENS: {getattr(settings, 'AI_MAX_TOKENS', 'N/A')}")
        print(f"📋 AI_TEMPERATURE: {getattr(settings, 'AI_TEMPERATURE', 'N/A')}")
        
        return bool(api_key and api_key.strip() and api_key != "sk-your-openai-api-key")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_ai_service():
    """检查 AI 服务初始化"""
    print("\n" + "=" * 80)
    print("3. 检查 AI 服务初始化")
    print("=" * 80)
    
    try:
        from app.services.ai_qa import ai_qa_service
        
        api_key = ai_qa_service.openai_api_key
        if api_key and api_key.strip() and api_key != "sk-your-openai-api-key":
            masked_key = api_key[:10] + '...' + api_key[-4:] if len(api_key) > 14 else '***'
            print(f"✅ AI 服务已初始化，API 密钥: {masked_key}")
            print(f"📋 Base URL: {ai_qa_service.openai_base_url}")
            print(f"📋 Default Model: {ai_qa_service.default_model}")
            print(f"📋 Max Tokens: {ai_qa_service.max_tokens}")
            print(f"📋 Temperature: {ai_qa_service.temperature}")
            return True
        else:
            print(f"⚠️  AI 服务已初始化，但 API 密钥未配置")
            print(f"   当前值: {api_key[:20] if api_key else 'None'}")
            print(f"   ⚠️  将使用模拟回答")
            return False
    except Exception as e:
        print(f"❌ AI 服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_routes():
    """检查路由注册"""
    print("\n" + "=" * 80)
    print("4. 检查路由注册")
    print("=" * 80)
    
    try:
        from app.api.v1 import __init__ as v1_init
        from app.api.v1 import teacher_ai_assistant
        
        if hasattr(teacher_ai_assistant, 'router'):
            print(f"✅ teacher_ai_assistant router 已定义")
            
            # 检查路由是否注册
            # 这里我们只能检查 router 是否存在，具体注册需要查看 __init__.py
            print(f"📋 Router 路径: /teacher/assistant")
            print(f"📋 Query 端点: POST /teacher/assistant/query")
            return True
        else:
            print(f"❌ teacher_ai_assistant router 未定义")
            return False
    except Exception as e:
        print(f"❌ 路由检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_imports():
    """检查关键模块导入"""
    print("\n" + "=" * 80)
    print("5. 检查关键模块导入")
    print("=" * 80)
    
    modules = [
        ("app.core.config", "settings"),
        ("app.services.ai_qa", "ai_qa_service"),
        ("app.api.v1.teacher_ai_assistant", "router"),
    ]
    
    all_ok = True
    for module_name, attr_name in modules:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            if hasattr(module, attr_name):
                print(f"✅ {module_name}.{attr_name} 导入成功")
            else:
                print(f"❌ {module_name}.{attr_name} 不存在")
                all_ok = False
        except Exception as e:
            print(f"❌ {module_name} 导入失败: {e}")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("AI Assistant 配置检查工具")
    print("=" * 80 + "\n")
    
    results = []
    
    # 检查 .env 文件
    results.append(("环境变量文件", check_env_file()))
    
    # 检查配置加载
    results.append(("配置加载", check_settings()))
    
    # 检查 AI 服务
    results.append(("AI 服务初始化", check_ai_service()))
    
    # 检查路由
    results.append(("路由注册", check_routes()))
    
    # 检查导入
    results.append(("模块导入", check_imports()))
    
    # 总结
    print("\n" + "=" * 80)
    print("检查总结")
    print("=" * 80)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 所有检查通过！")
    else:
        print("❌ 部分检查失败，请根据上述信息修复问题")
        print("\n修复建议:")
        print("1. 确保 .env 文件存在且包含有效的 OPENAI_API_KEY")
        print("2. 重启后端服务以加载新的环境变量")
        print("3. 检查后端日志以查看详细的错误信息")
    print("=" * 80 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())


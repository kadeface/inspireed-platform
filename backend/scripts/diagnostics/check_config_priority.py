#!/usr/bin/env python3
"""
测试配置加载优先级
验证 .env 文件和 config.py 中默认值的关系
"""

import os
import sys
from pathlib import Path

# 添加项目路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("配置加载优先级测试")
print("=" * 80)
print()

# 检查 .env 文件
env_file = backend_dir / ".env"
print(f"1. 检查 .env 文件: {env_file}")
if env_file.exists():
    print(f"   ✅ .env 文件存在")
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        for line in content.split('\n'):
            if line.strip().startswith('OPENAI_API_KEY'):
                if '=' in line:
                    key_value = line.split('=', 1)[1].strip()
                    if key_value:
                        masked = key_value[:10] + '...' + key_value[-4:] if len(key_value) > 14 else '***'
                        print(f"   📋 .env 中的值: {masked}")
                    else:
                        print(f"   📋 .env 中的值: (空)")
                break
        else:
            print(f"   ⚠️  .env 中未找到 OPENAI_API_KEY")
else:
    print(f"   ❌ .env 文件不存在")

print()

# 检查系统环境变量
print("2. 检查系统环境变量")
env_value = os.environ.get('OPENAI_API_KEY')
if env_value:
    masked = env_value[:10] + '...' + env_value[-4:] if len(env_value) > 14 else '***'
    print(f"   📋 系统环境变量中的值: {masked}")
else:
    print(f"   📋 系统环境变量: (未设置)")

print()

# 检查配置类中的默认值
print("3. 检查 config.py 中的默认值")
print(f"   📋 默认值: OPENAI_API_KEY: str = \"\"")
print(f"   📋 默认值: OPENAI_BASE_URL: str = \"https://api.openai.com/v1\"")
print(f"   📋 默认值: DEFAULT_AI_MODEL: str = \"gpt-3.5-turbo\"")
print(f"   📋 默认值: AI_MAX_TOKENS: int = 20000")
print(f"   📋 默认值: AI_TEMPERATURE: float = 0.7")

print()

# 尝试加载实际配置（需要安装依赖）
print("4. 实际加载的配置值（通过 Settings 类）")
print("-" * 80)
try:
    from app.core.config import settings
    
    print(f"   OPENAI_API_KEY: ", end="")
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if api_key:
        masked = api_key[:10] + '...' + api_key[-4:] if len(api_key) > 14 else '***'
        print(masked)
        print(f"     长度: {len(api_key)} 字符")
        print(f"     来源: ", end="")
        if env_value and api_key == env_value:
            print("✅ 系统环境变量")
        elif env_file.exists() and api_key:
            # 检查是否与 .env 文件中的值匹配
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('OPENAI_API_KEY'):
                        if '=' in line:
                            env_file_value = line.split('=', 1)[1].strip()
                            if api_key == env_file_value:
                                print("✅ .env 文件")
                            else:
                                print("❓ 未知来源（可能是环境变量覆盖）")
                        break
                else:
                    print("❓ 未知来源")
        else:
            print("❌ config.py 默认值（空字符串）")
    else:
        print("(空) - 使用 config.py 默认值")
    
    print(f"   OPENAI_BASE_URL: {getattr(settings, 'OPENAI_BASE_URL', 'N/A')}")
    print(f"   DEFAULT_AI_MODEL: {getattr(settings, 'DEFAULT_AI_MODEL', 'N/A')}")
    print(f"   AI_MAX_TOKENS: {getattr(settings, 'AI_MAX_TOKENS', 'N/A')}")
    print(f"   AI_TEMPERATURE: {getattr(settings, 'AI_TEMPERATURE', 'N/A')}")
    
except ImportError as e:
    print(f"   ❌ 无法导入 settings: {e}")
    print(f"   提示: 需要安装依赖包（pydantic, pydantic-settings）")
except Exception as e:
    print(f"   ❌ 加载配置时出错: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("配置优先级说明")
print("=" * 80)
print()
print("Pydantic Settings 的配置优先级（从高到低）：")
print("  1. 🔝 系统环境变量（最高优先级）")
print("  2. 📄 .env 文件")
print("  3. 📝 config.py 中的默认值（最低优先级）")
print()
print("这意味着：")
print("  • 如果系统环境变量中设置了 OPENAI_API_KEY，会使用系统环境变量的值")
print("  • 如果系统环境变量未设置，但 .env 文件中有值，会使用 .env 文件中的值")
print("  • 如果两者都没有，会使用 config.py 中的默认值（OPENAI_API_KEY = \"\"）")
print()
print("建议：")
print("  ✅ 在 .env 文件中配置 OPENAI_API_KEY（推荐）")
print("  ✅ 不要将 .env 文件提交到版本控制系统（应该在 .gitignore 中）")
print("  ✅ config.py 中的默认值作为后备值，通常应该保持为合理的默认值")
print("=" * 80)

